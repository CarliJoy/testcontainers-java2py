"""
SocatContainer - TCP proxy container for exposing ports.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/SocatContainer.java
"""

from __future__ import annotations

import logging
import secrets

from testcontainers.core.generic_container import GenericContainer

logger = logging.getLogger(__name__)


class SocatContainer(GenericContainer):
    """
    A socat container used as a TCP proxy.
    
    Enables any TCP port of another container to be exposed publicly,
    even if that container does not make the port public itself.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/SocatContainer.java
    
    Example:
        >>> target_container = GenericContainer("redis:6")
        >>> target_container.start()
        >>> 
        >>> socat = SocatContainer()
        >>> socat.with_target(6379, target_container.get_container_name())
        >>> socat.start()
        >>> 
        >>> # Access Redis through socat's exposed port
        >>> host_port = socat.get_exposed_port(6379)
    """

    DEFAULT_IMAGE = "alpine/socat:1.7.4.3-r0"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a socat container.
        
        Args:
            image: Docker image to use (defaults to alpine/socat)
        """
        super().__init__(image)
        
        # Target configurations: exposed_port -> "host:port"
        self._targets: dict[int, str] = {}
        
        # Configure container
        self.with_create_container_modifier(lambda kwargs: {**kwargs, "entrypoint": "/bin/sh"})
        
        # Generate unique name
        random_suffix = secrets.token_hex(4)
        self.with_name(f"testcontainers-socat-{random_suffix}")

    def with_target(
        self,
        exposed_port: int,
        host: str,
        internal_port: int | None = None,
    ) -> SocatContainer:
        """
        Configure socat to proxy to a target (fluent API).
        
        Args:
            exposed_port: Port to expose on socat container
            host: Target host (e.g., container name or IP)
            internal_port: Target port (defaults to exposed_port)
            
        Returns:
            This socat container instance
        """
        if internal_port is None:
            internal_port = exposed_port
        
        self.with_exposed_ports(exposed_port)
        self._targets[exposed_port] = f"{host}:{internal_port}"
        
        return self

    def start(self) -> SocatContainer:
        """
        Start the socat container.
        
        Configures the socat command based on targets and then starts.
        
        Returns:
            This socat container instance
        """
        # Build socat command from targets
        if not self._targets:
            raise ValueError("No targets configured. Use with_target() to add targets.")
        
        # Build command: socat TCP-LISTEN:port,fork,reuseaddr TCP:host:port & ...
        socat_commands = []
        for exposed_port, target in self._targets.items():
            socat_cmd = f"socat TCP-LISTEN:{exposed_port},fork,reuseaddr TCP:{target}"
            socat_commands.append(socat_cmd)
        
        # Join with & to run multiple socat instances
        full_command = " & ".join(socat_commands)
        
        # Set as container command
        self.with_command(["-c", full_command])
        
        # Start container
        return super().start()
