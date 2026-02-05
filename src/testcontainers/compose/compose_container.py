"""Docker Compose support for Testcontainers.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/ComposeContainer.java
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Any

import yaml

from testcontainers.core.docker_client import DockerClientFactory
from testcontainers.waiting import WaitStrategy

logger = logging.getLogger(__name__)


class ComposeContainer:
    """Testcontainers implementation for Docker Compose.
    
    This uses Docker Compose V2 (via `docker compose` command).
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/ComposeContainer.java
    """
    
    def __init__(
        self,
        *compose_files: str | Path,
        project_name: Optional[str] = None,
    ) -> None:
        """Initialize the Compose container.
        
        Args:
            compose_files: One or more Docker Compose files
            project_name: Optional project name (auto-generated if not provided)
        """
        if not compose_files:
            raise ValueError("At least one compose file must be provided")
        
        self._compose_files = [Path(f) for f in compose_files]
        self._project_name = project_name or self._generate_project_name()
        self._env: dict[str, str] = {}
        self._services: list[str] = []
        self._pull = True
        self._build = False
        self._remove_volumes = True
        self._service_wait_strategies: dict[str, WaitStrategy] = {}
        self._started = False
        
        # Validate files exist
        for f in self._compose_files:
            if not f.exists():
                raise FileNotFoundError(f"Compose file not found: {f}")
    
    @staticmethod
    def _generate_project_name() -> str:
        """Generate a unique project name."""
        import random
        import string
        chars = string.ascii_lowercase + string.digits
        return "tc" + "".join(random.choices(chars, k=8))
    
    def with_env(self, key: str, value: str) -> ComposeContainer:
        """Set an environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            This container for method chaining
        """
        self._env[key] = value
        return self
    
    def with_services(self, *services: str) -> ComposeContainer:
        """Specify which services to start.
        
        If not specified, all services will be started.
        
        Args:
            services: Service names to start
            
        Returns:
            This container for method chaining
        """
        self._services = list(services)
        return self
    
    def with_pull(self, pull: bool = True) -> ComposeContainer:
        """Enable or disable pulling images.
        
        Args:
            pull: Whether to pull images
            
        Returns:
            This container for method chaining
        """
        self._pull = pull
        return self
    
    def with_build(self, build: bool = True) -> ComposeContainer:
        """Enable or disable building images.
        
        Args:
            build: Whether to build images
            
        Returns:
            This container for method chaining
        """
        self._build = build
        return self
    
    def with_remove_volumes(self, remove: bool = True) -> ComposeContainer:
        """Enable or disable removing volumes on stop.
        
        Args:
            remove: Whether to remove volumes
            
        Returns:
            This container for method chaining
        """
        self._remove_volumes = remove
        return self
    
    def wait_for_service(
        self, service: str, wait_strategy: WaitStrategy
    ) -> ComposeContainer:
        """Set a wait strategy for a specific service.
        
        Args:
            service: Service name
            wait_strategy: Wait strategy to use
            
        Returns:
            This container for method chaining
        """
        self._service_wait_strategies[service] = wait_strategy
        return self
    
    def start(self) -> None:
        """Start the Docker Compose environment."""
        if self._started:
            return
        
        logger.info(
            "Starting Docker Compose project '%s' with %d file(s)",
            self._project_name,
            len(self._compose_files),
        )
        
        # Build command
        cmd = self._build_compose_command()
        
        # Pull images if requested
        if self._pull:
            logger.info("Pulling images for project '%s'", self._project_name)
            self._run_compose(cmd + ["pull"])
        
        # Build images if requested
        if self._build:
            logger.info("Building images for project '%s'", self._project_name)
            self._run_compose(cmd + ["build"])
        
        # Start services
        logger.info("Starting services for project '%s'", self._project_name)
        up_cmd = cmd + ["up", "-d"]
        
        if self._services:
            up_cmd.extend(self._services)
        
        self._run_compose(up_cmd)
        self._started = True
        
        # Wait for services
        if self._service_wait_strategies:
            self._wait_for_services()
    
    def stop(self) -> None:
        """Stop the Docker Compose environment."""
        if not self._started:
            return
        
        logger.info("Stopping Docker Compose project '%s'", self._project_name)
        
        cmd = self._build_compose_command()
        down_cmd = cmd + ["down"]
        
        if self._remove_volumes:
            down_cmd.append("--volumes")
        
        self._run_compose(down_cmd)
        self._started = False
    
    def get_service_host(self, service: str, port: int) -> str:
        """Get the host for a service.
        
        Args:
            service: Service name
            port: Internal port number
            
        Returns:
            Host address
        """
        # For Docker Compose, services are accessible on localhost
        client = DockerClientFactory.get_client()
        return client.gateway_ip or "localhost"
    
    def get_service_port(self, service: str, port: int) -> int:
        """Get the mapped port for a service.
        
        Args:
            service: Service name
            port: Internal port number
            
        Returns:
            Mapped port number
        """
        # Get container for service
        container_name = f"{self._project_name}-{service}-1"
        
        try:
            client = DockerClientFactory.get_client()
            container = client.inspect_container(container_name)
            
            # Find the port mapping
            port_bindings = container.get("NetworkSettings", {}).get("Ports", {})
            port_key = f"{port}/tcp"
            
            if port_key in port_bindings and port_bindings[port_key]:
                return int(port_bindings[port_key][0]["HostPort"])
            
            raise ValueError(f"Port {port} not exposed for service {service}")
            
        except Exception as e:
            logger.error("Failed to get port for service %s: %s", service, e)
            raise
    
    def _build_compose_command(self) -> list[str]:
        """Build the base docker compose command."""
        cmd = ["docker", "compose"]
        
        # Add project name
        cmd.extend(["-p", self._project_name])
        
        # Add compose files
        for f in self._compose_files:
            cmd.extend(["-f", str(f.absolute())])
        
        return cmd
    
    def _run_compose(self, cmd: list[str]) -> None:
        """Run a docker compose command."""
        env = os.environ.copy()
        env.update(self._env)
        
        logger.debug("Running: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            
            if result.stdout:
                logger.debug("Output: %s", result.stdout)
                
        except subprocess.CalledProcessError as e:
            logger.error("Command failed: %s", e.stderr)
            raise RuntimeError(f"Docker Compose command failed: {e.stderr}") from e
    
    def _wait_for_services(self) -> None:
        """Wait for services to be ready."""
        for service, strategy in self._service_wait_strategies.items():
            logger.info("Waiting for service '%s' to be ready", service)
            
            # Create a target wrapper for the service
            target = ComposeServiceTarget(self, service)
            strategy.wait_until_ready(target)
    
    def __enter__(self) -> ComposeContainer:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()


class ComposeServiceTarget:
    """Wrapper to make a Compose service look like a WaitStrategyTarget.
    
    This is a simplified implementation that provides basic functionality.
    """
    
    def __init__(self, compose: ComposeContainer, service: str) -> None:
        """Initialize the service target.
        
        Args:
            compose: The compose container
            service: Service name
        """
        self._compose = compose
        self._service = service
        self._container_name = f"{compose._project_name}-{service}-1"
    
    def get_host(self) -> str:
        """Get the host for this service."""
        return self._compose.get_service_host(self._service, 0)
    
    def get_exposed_port(self, port: int) -> int:
        """Get the mapped port for this service."""
        return self._compose.get_service_port(self._service, port)
    
    def get_container_info(self) -> dict[str, Any]:
        """Get container info."""
        client = DockerClientFactory.get_client()
        return client.inspect_container(self._container_name)
    
    def exec_in_container(self, *command: str) -> Any:
        """Execute a command in the service container."""
        client = DockerClientFactory.get_client()
        container = client.get_container(self._container_name)
        return container.exec_run(command)
    
    def get_logs(self) -> tuple[bytes, bytes]:
        """Get container logs."""
        client = DockerClientFactory.get_client()
        container = client.get_container(self._container_name)
        logs = container.logs()
        return logs, b""  # Simplified: return all as stdout
