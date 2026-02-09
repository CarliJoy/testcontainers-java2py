"""
Apache Pulsar container implementation.

This module provides a container for Apache Pulsar distributed messaging platform.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/pulsar/src/main/java/org/testcontainers/containers/PulsarContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class PulsarContainer(GenericContainer):
    """
    Apache Pulsar distributed messaging platform container.

    This container starts a Pulsar standalone instance with broker and HTTP service.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/pulsar/src/main/java/org/testcontainers/containers/PulsarContainer.java

    Example:
        >>> with PulsarContainer() as pulsar:
        ...     broker_url = pulsar.get_pulsar_broker_url()
        ...     http_url = pulsar.get_http_service_url()
        ...     # Connect to Pulsar

        >>> # With custom image
        >>> pulsar = PulsarContainer("apachepulsar/pulsar:3.1.0")
        >>> pulsar.start()
        >>> broker_url = pulsar.get_pulsar_broker_url()

    Security considerations:
        - Default configuration has no authentication
        - For production use, enable authentication and authorization
        - Consider using TLS for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "apachepulsar/pulsar:latest"
    DEFAULT_BROKER_PORT = 6650
    DEFAULT_HTTP_PORT = 8080

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Pulsar container.

        Args:
            image: Docker image name (default: apachepulsar/pulsar:latest)
        """
        super().__init__(image)

        self._broker_port = self.DEFAULT_BROKER_PORT
        self._http_port = self.DEFAULT_HTTP_PORT

        # Expose Pulsar ports
        self.with_exposed_ports(self._broker_port, self._http_port)

        # Start Pulsar in standalone mode
        self.with_command(["bin/pulsar", "standalone"])

        # Wait for Pulsar to be ready - check admin API
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/admin/v2/clusters")
            .for_port(self._http_port)
            .for_status_code(200)
        )

    def get_pulsar_broker_url(self) -> str:
        """
        Get the Pulsar broker URL for client connections.

        Returns:
            Broker URL in format: pulsar://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._broker_port)
        return f"pulsar://{host}:{port}"

    def get_http_service_url(self) -> str:
        """
        Get the Pulsar HTTP service URL for admin API.

        Returns:
            HTTP URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._http_port)
        return f"http://{host}:{port}"

    def get_broker_port(self) -> int:
        """
        Get the exposed broker port number on the host.

        Returns:
            Host port number mapped to the broker port
        """
        return self.get_mapped_port(self._broker_port)

    def get_http_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self._http_port)

    def get_port(self) -> int:
        """
        Get the exposed broker port number on the host.

        Alias for get_broker_port().

        Returns:
            Host port number mapped to the broker port
        """
        return self.get_broker_port()
