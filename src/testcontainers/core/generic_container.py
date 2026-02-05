"""
Generic container implementation.

This module provides the main GenericContainer class for running Docker containers.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Optional, Any, Sequence

from docker import DockerClient
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
        self._privileged: bool = False
        
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
            
            # Create container
            self._container = self._docker_client.containers.create(
                image_name,
                command=self._command,
                entrypoint=self._entrypoint,
                environment=self._env,
                ports=ports,
                volumes=self._volumes,
                working_dir=self._working_dir,
                name=self._name,
                labels=labels,
                network_mode=self._network_mode,
                privileged=self._privileged,
                detach=True,
            )
            
            self._container_id = self._container.id
            logger.info(f"Container created: {self._container_id}")
            
            # Start container
            self._container.start()
            logger.info(f"Container started: {self._container_id}")
            
            # Reload to get port mappings
            self._container.reload()
            
            # Wait for container to be ready
            logger.debug(f"Waiting for container to be ready")
            self._wait_strategy.wait_until_ready(self)
            
            logger.info(f"Container ready: {self._container_id}")
            return self
            
        except Exception as e:
            logger.error(f"Failed to start container: {e}", exc_info=e)
            # Cleanup on failure
            if self._container:
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
