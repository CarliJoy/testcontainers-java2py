"""
Generic container implementation.

This module provides the main GenericContainer class for running Docker containers.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import stat
import time
from datetime import timedelta
from typing import Optional, Any, Sequence, TYPE_CHECKING

from docker import DockerClient

if TYPE_CHECKING:
    from testcontainers.core.network import Network
from docker.models.containers import Container as DockerContainer
from docker.errors import NotFound, APIError

from testcontainers.core.docker_client import DockerClientFactory
from testcontainers.core.container import Container, ExecResult
from testcontainers.core.container_state import ContainerState
from testcontainers.core.container_types import BindMode, InternetProtocol
from testcontainers.waiting.wait_strategy import WaitStrategy, WaitStrategyTarget
from testcontainers.waiting.port import HostPortWaitStrategy
from testcontainers.images import RemoteDockerImage, PullPolicy

logger = logging.getLogger(__name__)


class GenericContainer(Container["GenericContainer"], ContainerState, WaitStrategyTarget):
    """
    Generic Docker container that can be started and controlled.
    
    This is the base class for all testcontainers. It provides core functionality
    for managing Docker containers including lifecycle, port mappings, environment
    variables, volumes, and wait strategies.
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/GenericContainer.java
    
    Example:
        >>> container = GenericContainer("nginx:latest")
        >>> container.with_exposed_ports(80)
        >>> container.start()
        >>> port = container.get_exposed_port(80)
        >>> # Use the container
        >>> container.stop()
    """
    
    CONTAINER_RUNNING_TIMEOUT_SEC = 30
    INTERNAL_HOST_HOSTNAME = "host.testcontainers.internal"
    HASH_LABEL = "org.testcontainers.hash"
    COPIED_FILES_HASH_LABEL = "org.testcontainers.copied_files.hash"
    
    def __init__(
        self,
        image: str | RemoteDockerImage,
        docker_client: Optional[DockerClient] = None,
    ):
        """
        Initialize a generic container.
        
        Args:
            image: Docker image name or RemoteDockerImage instance
            docker_client: Docker client to use (defaults to lazy client)
        """
        # Image handling
        if isinstance(image, str):
            self._image = RemoteDockerImage(image)
        else:
            self._image = image
        
        # Docker client
        self._docker_client = docker_client or DockerClientFactory.lazy_client()
        
        # Container state
        self._container: Optional[DockerContainer] = None
        self._container_id: Optional[str] = None
        
        # Configuration
        self._exposed_ports: list[int] = []
        self._port_bindings: dict[int, int] = {}
        self._env: dict[str, str] = {}
        self._volumes: dict[str, dict[str, str]] = {}
        self._command: Optional[str | list[str]] = None
        self._entrypoint: Optional[str | list[str]] = None
        self._working_dir: Optional[str] = None
        self._name: Optional[str] = None
        self._labels: dict[str, str] = {}
        self._network_mode: Optional[str] = None
        self._network: Optional[Network] = None
        self._network_aliases: list[str] = []
        self._privileged: bool = False
        
        # Dependencies
        self._dependencies: list[Container] = []
        
        # File copying
        self._copy_to_container: dict[str, str] = {}  # source -> container_path
        
        # Container modifiers
        self._create_container_modifiers: list = []
        
        # Container reuse
        self._should_be_reused: bool = False
        self._reused: bool = False
        
        # Wait strategy
        self._wait_strategy: WaitStrategy = HostPortWaitStrategy()
        
        # Startup timeout
        self._startup_timeout = timedelta(seconds=60)
    
    def with_exposed_ports(self, *ports: int) -> GenericContainer:
        """
        Expose container ports (fluent API).
        
        Args:
            ports: Port numbers to expose
            
        Returns:
            This container instance
        """
        for port in ports:
            if port not in self._exposed_ports:
                self._exposed_ports.append(port)
        return self
    
    def with_bind_ports(self, container_port: int, host_port: int) -> GenericContainer:
        """
        Bind a container port to a specific host port (fluent API).
        
        Args:
            container_port: Port inside the container
            host_port: Port on the host
            
        Returns:
            This container instance
        """
        self._port_bindings[container_port] = host_port
        if container_port not in self._exposed_ports:
            self._exposed_ports.append(container_port)
        return self
    
    def with_env(self, key: str, value: str) -> GenericContainer:
        """
        Set an environment variable (fluent API).
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            This container instance
        """
        self._env[key] = value
        return self
    
    def with_volume_mapping(
        self,
        host_path: str,
        container_path: str,
        mode: BindMode = BindMode.READ_WRITE,
    ) -> GenericContainer:
        """
        Mount a host path into the container (fluent API).
        
        Args:
            host_path: Path on the host
            container_path: Path in the container
            mode: Mount mode (READ_ONLY or READ_WRITE)
            
        Returns:
            This container instance
        """
        self._volumes[host_path] = {
            "bind": container_path,
            "mode": mode.value,
        }
        return self
    
    def with_command(self, command: str | list[str]) -> GenericContainer:
        """
        Override the container command (fluent API).
        
        Args:
            command: Command to run (string or list)
            
        Returns:
            This container instance
        """
        self._command = command
        return self
    
    def with_entrypoint(self, entrypoint: str | list[str]) -> GenericContainer:
        """
        Override the container entrypoint (fluent API).
        
        Args:
            entrypoint: Entrypoint to use (string or list)
            
        Returns:
            This container instance
        """
        self._entrypoint = entrypoint
        return self
    
    def with_working_directory(self, working_dir: str) -> GenericContainer:
        """
        Set the working directory (fluent API).
        
        Args:
            working_dir: Working directory path
            
        Returns:
            This container instance
        """
        self._working_dir = working_dir
        return self
    
    def with_name(self, name: str) -> GenericContainer:
        """
        Set the container name (fluent API).
        
        Args:
            name: Container name
            
        Returns:
            This container instance
        """
        self._name = name
        return self
    
    def with_labels(self, **labels: str) -> GenericContainer:
        """
        Add labels to the container (fluent API).
        
        Args:
            labels: Key-value pairs of labels
            
        Returns:
            This container instance
        """
        self._labels.update(labels)
        return self
    
    def with_network_mode(self, network_mode: str) -> GenericContainer:
        """
        Set the network mode (fluent API).
        
        Args:
            network_mode: Network mode (e.g., "bridge", "host", "none")
            
        Returns:
            This container instance
        """
        self._network_mode = network_mode
        return self
    
    def with_privileged_mode(self, privileged: bool = True) -> GenericContainer:
        """
        Run container in privileged mode (fluent API).
        
        Args:
            privileged: Whether to run in privileged mode
            
        Returns:
            This container instance
        """
        self._privileged = privileged
        return self
    
    def with_network(self, network: Network) -> GenericContainer:
        """
        Connect container to a network (fluent API).
        
        Args:
            network: Network instance to connect to
            
        Returns:
            This container instance
        """
        self._network = network
        return self
    
    def with_network_aliases(self, *aliases: str) -> GenericContainer:
        """
        Set network aliases for the container (fluent API).
        
        Args:
            aliases: Network aliases for the container
            
        Returns:
            This container instance
        """
        self._network_aliases.extend(aliases)
        return self
    
    def depends_on(self, *containers: Container) -> GenericContainer:
        """
        Add container dependencies (fluent API).
        
        This ensures that the specified containers are started before this container.
        
        Args:
            containers: Container instances to depend on
            
        Returns:
            This container instance
        """
        self._dependencies.extend(containers)
        return self
    
    def with_copy_file_to_container(self, source: str, target: str) -> GenericContainer:
        """
        Copy a file or directory to the container before starting (fluent API).
        
        Args:
            source: Source path on host
            target: Target path in container
            
        Returns:
            This container instance
        """
        self._copy_to_container[source] = target
        return self
    
    def with_create_container_modifier(self, modifier: Any) -> GenericContainer:
        """
        Add a container creation modifier (fluent API).
        
        Modifiers allow custom configuration of the container before creation.
        
        Args:
            modifier: Callable that modifies container creation parameters
            
        Returns:
            This container instance
        """
        self._create_container_modifiers.append(modifier)
        return self
    
    def with_reuse(self, reuse: bool) -> GenericContainer:
        """
        Enable or disable container reuse (fluent API).
        
        When enabled, the container will search for existing containers with matching
        configuration and reuse them instead of creating new ones. This requires
        TESTCONTAINERS_REUSE_ENABLE=true in the environment or [reuse] enabled=true
        in testcontainers.toml.
        
        Args:
            reuse: Whether to enable container reuse
            
        Returns:
            This container instance
        """
        self._should_be_reused = reuse
        return self
    
    def waiting_for(self, wait_strategy: WaitStrategy) -> GenericContainer:
        """
        Set the wait strategy (fluent API).
        
        Args:
            wait_strategy: Strategy to determine when container is ready
            
        Returns:
            This container instance
        """
        self._wait_strategy = wait_strategy
        return self
    
    def start(self) -> GenericContainer:
        """
        Start the container.
        
        Returns:
            This container instance
            
        Raises:
            Exception: If container fails to start
        """
        if self._container is not None:
            logger.warning("Container already started")
            return self
        
        try:
            # Start dependencies first
            for dependency in self._dependencies:
                if not dependency.is_running():
                    logger.info(f"Starting dependency container: {dependency}")
                    dependency.start()
            
            # Resolve image (pull if necessary)
            image_name = self._image.resolve()
            logger.info(f"Creating container for image: {image_name}")
            
            # Prepare port bindings
            ports = {}
            if self._port_bindings:
                # Specific bindings
                for container_port, host_port in self._port_bindings.items():
                    ports[f"{container_port}/tcp"] = host_port
            elif self._exposed_ports:
                # Auto-assign ports
                for port in self._exposed_ports:
                    ports[f"{port}/tcp"] = None  # None means auto-assign
            
            # Add testcontainers labels
            labels = dict(self._labels)
            labels.update(DockerClientFactory.marker_labels())
            
            # Prepare network configuration
            network = None
            networking_config = None
            if self._network:
                network = self._network.get_id()
                if self._network_aliases:
                    networking_config = {
                        network: {
                            "Aliases": self._network_aliases
                        }
                    }
            
            # Create container
            create_kwargs = {
                "image": image_name,
                "command": self._command,
                "entrypoint": self._entrypoint,
                "environment": self._env,
                "ports": ports,
                "volumes": self._volumes,
                "working_dir": self._working_dir,
                "name": self._name,
                "labels": labels,
                "privileged": self._privileged,
                "detach": True,
            }
            
            # Add network configuration
            if network:
                create_kwargs["network"] = network
                if networking_config:
                    create_kwargs["networking_config"] = networking_config
            elif self._network_mode:
                create_kwargs["network_mode"] = self._network_mode
            
            # Apply container modifiers
            for modifier in self._create_container_modifiers:
                if callable(modifier):
                    create_kwargs = modifier(create_kwargs) or create_kwargs
            
            # Check for container reuse
            reused = False
            if self._should_be_reused:
                # Import config here to avoid circular import
                from testcontainers.config import TestcontainersConfig
                
                if TestcontainersConfig.get_instance().environment_supports_reuse():
                    # Add reuse labels
                    copied_files_hash = self._hash_copied_files()
                    create_kwargs["labels"][self.COPIED_FILES_HASH_LABEL] = copied_files_hash
                    
                    config_hash = self._hash_configuration(create_kwargs)
                    
                    # Try to find existing container
                    existing_container_id = self._find_container_for_reuse(config_hash)
                    
                    if existing_container_id:
                        # Reuse existing container
                        logger.info(f"Reusing container with ID: {existing_container_id}")
                        self._container = self._docker_client.containers.get(existing_container_id)
                        self._container_id = existing_container_id
                        reused = True
                    else:
                        # No existing container, add hash label for future reuse
                        logger.debug(f"No reusable container found, will create new one with hash: {config_hash}")
                        create_kwargs["labels"][self.HASH_LABEL] = config_hash
                else:
                    logger.debug("Container reuse requested but not supported by environment")
            
            # Create new container if not reused
            if not reused:
                self._container = self._docker_client.containers.create(**create_kwargs)
                self._container_id = self._container.id
                logger.info(f"Container created: {self._container_id}")
                
                # Copy files to container before starting
                for source, target in self._copy_to_container.items():
                    logger.debug(f"Copying {source} to {target} in container")
                    self.copy_file_to_container(source, target)
                
                # Call starting hook
                container_info = self._container.attrs
                self.container_is_starting(container_info, reused=False)
                
                # Start container
                self._container.start()
                logger.info(f"Container started: {self._container_id}")
                
                # Reload to get port mappings
                self._container.reload()
                
                # Call started hook
                container_info = self._container.attrs
                self.container_is_started(container_info, reused=False)
            else:
                # Container was reused, just call hooks
                container_info = self._container.attrs
                self.container_is_starting(container_info, reused=True)
                self.container_is_started(container_info, reused=True)
                
                # Reload to ensure we have latest info
                self._container.reload()
            
            # Mark as reused for future reference
            self._reused = reused
            
            # Wait for container to be ready
            logger.debug(f"Waiting for container to be ready")
            self._wait_strategy.wait_until_ready(self)
            
            logger.info(f"Container ready: {self._container_id}")
            return self
            
        except Exception as e:
            logger.error(f"Failed to start container: {e}", exc_info=e)
            # Cleanup on failure (but not if reused)
            if self._container and not reused:
                try:
                    self._container.remove(force=True)
                except Exception:
                    pass
                self._container = None
                self._container_id = None
            raise
    
    def stop(self, timeout: int = 10) -> None:
        """
        Stop the container.
        
        Args:
            timeout: Timeout in seconds before forcefully killing
        """
        if self._container is None:
            logger.warning("Container not started")
            return
        
        try:
            logger.info(f"Stopping container: {self._container_id}")
            self._container.stop(timeout=timeout)
            logger.info(f"Container stopped: {self._container_id}")
        except NotFound:
            logger.warning(f"Container not found: {self._container_id}")
        except Exception as e:
            logger.error(f"Error stopping container: {e}", exc_info=e)
            raise
    
    def remove(self, force: bool = True) -> None:
        """
        Remove the container.
        
        Args:
            force: Whether to force removal
        """
        if self._container is None:
            return
        
        try:
            logger.info(f"Removing container: {self._container_id}")
            self._container.remove(force=force)
            logger.info(f"Container removed: {self._container_id}")
        except NotFound:
            logger.warning(f"Container not found: {self._container_id}")
        except Exception as e:
            logger.error(f"Error removing container: {e}", exc_info=e)
        finally:
            self._container = None
            self._container_id = None
    
    def __enter__(self) -> GenericContainer:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
        self.remove()
    
    def close(self) -> None:
        """Close and cleanup the container (AutoCloseable pattern)."""
        self.stop()
        self.remove()
    
    # Container protocol methods
    
    def get_container_id(self) -> str:
        """Get the container ID."""
        if self._container_id is None:
            raise RuntimeError("Container not started")
        return self._container_id
    
    def get_exposed_port(self, port: int) -> int:
        """
        Get the host port mapped to a container port.
        
        Args:
            port: Container port number
            
        Returns:
            Host port number
        """
        if self._container is None:
            raise RuntimeError("Container not started")
        
        self._container.reload()
        port_key = f"{port}/tcp"
        
        if port_key not in self._container.attrs["NetworkSettings"]["Ports"]:
            raise KeyError(f"Port {port} not exposed")
        
        bindings = self._container.attrs["NetworkSettings"]["Ports"][port_key]
        if not bindings:
            raise KeyError(f"Port {port} not mapped")
        
        return int(bindings[0]["HostPort"])
    
    def exec(
        self,
        command: str | list[str],
        **kwargs: Any,
    ) -> ExecResult:
        """
        Execute a command in the container.
        
        Args:
            command: Command to execute
            kwargs: Additional arguments for exec_run
            
        Returns:
            ExecResult with exit code and output
        """
        if self._container is None:
            raise RuntimeError("Container not started")
        
        exit_code, output = self._container.exec_run(command, **kwargs)
        
        # Decode output if it's bytes
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        
        # For simplicity, put all output in stdout
        return ExecResult(exit_code=exit_code, stdout=output, stderr="")
    
    # ContainerState methods
    
    def is_running(self) -> bool:
        """Check if container is running."""
        if self._container is None:
            return False
        
        try:
            self._container.reload()
            return self._container.status == "running"
        except NotFound:
            return False
    
    def is_healthy(self) -> bool:
        """Check if container is healthy."""
        if self._container is None:
            return False
        
        try:
            self._container.reload()
            health = self._container.attrs.get("State", {}).get("Health", {})
            return health.get("Status") == "healthy"
        except NotFound:
            return False
    
    def get_logs(self) -> tuple[bytes, bytes]:
        """
        Get container logs.
        
        Returns:
            Tuple of (stdout, stderr)
        """
        if self._container is None:
            raise RuntimeError("Container not started")
        
        stdout = self._container.logs(stdout=True, stderr=False)
        stderr = self._container.logs(stdout=False, stderr=True)
        return (stdout, stderr)
    
    # WaitStrategyTarget methods
    
    def get_mapped_port(self, port: int) -> int:
        """Get mapped host port (alias for get_exposed_port)."""
        return self.get_exposed_port(port)
    
    def get_host(self) -> str:
        """Get the host where container is running."""
        # For now, assume localhost
        # TODO: Handle remote Docker hosts
        return "localhost"
    
    def get_container_info(self) -> dict:
        """Get container info."""
        if self._container is None:
            raise RuntimeError("Container not started")
        
        self._container.reload()
        return self._container.attrs
    
    # File operations
    
    def copy_file_to_container(self, source: str, target: str) -> None:
        """
        Copy a file or directory from the host to the container.
        
        Args:
            source: Source path on host
            target: Target path in container
        """
        import tarfile
        import io
        import os
        
        if self._container is None:
            raise RuntimeError("Container not started")
        
        # Create a tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add file or directory to tar
            arcname = os.path.basename(source)
            tar.add(source, arcname=arcname)
        
        tar_stream.seek(0)
        
        # Extract to container
        target_dir = os.path.dirname(target)
        if not target_dir:
            target_dir = "/"
        
        self._container.put_archive(target_dir, tar_stream.getvalue())
        logger.debug(f"Copied {source} to {target} in container {self._container_id}")
    
    def copy_file_from_container(self, source: str, target: str) -> None:
        """
        Copy a file or directory from the container to the host.
        
        Args:
            source: Source path in container
            target: Target path on host
        """
        import tarfile
        import io
        
        if self._container is None:
            raise RuntimeError("Container not started")
        
        # Get tar stream from container
        bits, stat = self._container.get_archive(source)
        
        # Write tar stream to target
        tar_stream = io.BytesIO()
        for chunk in bits:
            tar_stream.write(chunk)
        tar_stream.seek(0)
        
        # Extract from tar
        with tarfile.open(fileobj=tar_stream) as tar:
            tar.extractall(path=target)
        
        logger.debug(f"Copied {source} from container {self._container_id} to {target}")
    
    def container_is_starting(self, container_info: dict[str, Any], reused: bool) -> None:
        """
        Hook called when container is starting (before start command).
        
        Override this method to perform custom actions when the container is starting.
        
        Args:
            container_info: Container inspection information
            reused: True if container is being reused, False if newly created
        """
        pass
    
    def container_is_started(self, container_info: dict[str, Any], reused: bool) -> None:
        """
        Hook called when container has started (after start command).
        
        Override this method to perform custom actions after the container has started.
        
        Args:
            container_info: Container inspection information
            reused: True if container was reused, False if newly created
        """
        pass
    
    def _hash_configuration(self, create_kwargs: dict[str, Any]) -> str:
        """
        Calculate hash of container configuration.
        
        Args:
            create_kwargs: Container creation parameters
            
        Returns:
            SHA-256 hash of the configuration
        """
        # Extract and normalize relevant configuration
        config = {
            "image": create_kwargs.get("image"),
            "command": create_kwargs.get("command"),
            "entrypoint": create_kwargs.get("entrypoint"),
            "environment": sorted((k, v) for k, v in (create_kwargs.get("environment") or {}).items()),
            "ports": sorted(str(k) for k in (create_kwargs.get("ports") or {}).keys()),
            "volumes": sorted((k, v.get("bind"), v.get("mode")) for k, v in (create_kwargs.get("volumes") or {}).items()),
            "working_dir": create_kwargs.get("working_dir"),
            "privileged": create_kwargs.get("privileged"),
            "network_mode": create_kwargs.get("network_mode"),
            "network": create_kwargs.get("network"),
            # Exclude name and labels from hash as they may vary
        }
        
        # Convert to JSON and hash
        config_json = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(config_json.encode()).hexdigest()
    
    def _hash_copied_files(self) -> str:
        """
        Calculate hash of files to be copied to container.
        
        Returns:
            SHA-256 hash of files configuration
        """
        if not self._copy_to_container:
            return hashlib.sha256(b"").hexdigest()
        
        hasher = hashlib.sha256()
        
        # Sort for deterministic hashing
        for source, target in sorted(self._copy_to_container.items()):
            # Add target path
            hasher.update(target.encode())
            
            # Add file content and metadata
            if os.path.exists(source):
                # Get file stats
                file_stat = os.stat(source)
                hasher.update(str(file_stat.st_mode).encode())
                
                if os.path.isfile(source):
                    # Hash file content
                    with open(source, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hasher.update(chunk)
                elif os.path.isdir(source):
                    # Hash directory contents recursively
                    for root, dirs, files in os.walk(source):
                        # Sort for deterministic order
                        for name in sorted(dirs + files):
                            path = os.path.join(root, name)
                            rel_path = os.path.relpath(path, source)
                            hasher.update(rel_path.encode())
                            
                            if os.path.isfile(path):
                                # Hash file metadata
                                file_stat = os.stat(path)
                                hasher.update(str(file_stat.st_mode).encode())
                                
                                # Hash file content
                                with open(path, "rb") as f:
                                    for chunk in iter(lambda: f.read(4096), b""):
                                        hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _find_container_for_reuse(self, config_hash: str) -> Optional[str]:
        """
        Find an existing container that can be reused.
        
        Args:
            config_hash: Configuration hash to match
            
        Returns:
            Container ID if found, None otherwise
        """
        try:
            # Search for containers with matching hash label
            filters = {
                "label": [f"{self.HASH_LABEL}={config_hash}"],
                "status": "running"
            }
            
            containers = self._docker_client.containers.list(filters=filters)
            
            if containers:
                container_id = containers[0].id
                logger.info(f"Found reusable container: {container_id}")
                return container_id
            
        except Exception as e:
            logger.warning(f"Error searching for reusable container: {e}")
        
        return None
