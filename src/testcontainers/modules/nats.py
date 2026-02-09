"""
NATS container implementation.

This module provides a container for NATS messaging system.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/nats/src/main/java/org/testcontainers/containers/NatsContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class NATSContainer(GenericContainer):
    """
    NATS messaging system container.

    This container starts a NATS server with client and monitoring ports.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/nats/src/main/java/org/testcontainers/containers/NatsContainer.java

    Example:
        >>> with NATSContainer() as nats:
        ...     url = nats.get_connection_url()
        ...     monitoring_url = nats.get_monitoring_url()
        ...     # Connect to NATS

        >>> # With custom image
        >>> nats = NATSContainer("nats:2.10")
        >>> nats.start()
        >>> url = nats.get_connection_url()

    Security considerations:
        - Default configuration has no authentication
        - For production use, enable authentication with credentials
        - Consider using TLS for production deployments
        - Monitoring endpoint exposes server information
    """

    # Default configuration
    DEFAULT_IMAGE = "nats:latest"
    DEFAULT_CLIENT_PORT = 4222
    DEFAULT_MONITORING_PORT = 8222

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a NATS container.

        Args:
            image: Docker image name (default: nats:latest)
        """
        super().__init__(image)

        self._client_port = self.DEFAULT_CLIENT_PORT
        self._monitoring_port = self.DEFAULT_MONITORING_PORT

        # Expose NATS ports
        self.with_exposed_ports(self._client_port, self._monitoring_port)

        # Wait for NATS to be ready
        # NATS logs "Server is ready" when ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Server is ready.*")
        )

    def get_connection_url(self) -> str:
        """
        Get the NATS connection URL for client connections.

        Returns:
            Connection URL in format: nats://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._client_port)
        return f"nats://{host}:{port}"

    def get_monitoring_url(self) -> str:
        """
        Get the NATS monitoring HTTP URL.

        The monitoring endpoint provides server statistics and health information.

        Returns:
            Monitoring URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._monitoring_port)
        return f"http://{host}:{port}"

    def get_client_port(self) -> int:
        """
        Get the exposed client port number on the host.

        Returns:
            Host port number mapped to the client port
        """
        return self.get_mapped_port(self._client_port)

    def get_monitoring_port(self) -> int:
        """
        Get the exposed monitoring port number on the host.

        Returns:
            Host port number mapped to the monitoring port
        """
        return self.get_mapped_port(self._monitoring_port)

    def get_port(self) -> int:
        """
        Get the exposed client port number on the host.

        Alias for get_client_port().

        Returns:
            Host port number mapped to the client port
        """
        return self.get_client_port()
