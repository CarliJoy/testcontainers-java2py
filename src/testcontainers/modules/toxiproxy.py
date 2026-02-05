"""
Toxiproxy container implementation.

This module provides a container for Toxiproxy network fault injection tool.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/toxiproxy/src/main/java/org/testcontainers/containers/ToxiproxyContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class ToxiproxyContainer(GenericContainer):
    """
    Toxiproxy network fault injection container.

    This container starts a Toxiproxy instance for simulating network conditions
    and testing application resilience to network failures.

    Toxiproxy allows you to inject latency, bandwidth limitations, connection cuts,
    and other network faults into your tests.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/toxiproxy/src/main/java/org/testcontainers/containers/ToxiproxyContainer.java

    Example:
        >>> with ToxiproxyContainer() as toxiproxy:
        ...     control_port = toxiproxy.get_control_port()
        ...     # Use toxiproxy-python client to create proxies
        ...     from toxiproxy import Toxiproxy
        ...     client = Toxiproxy(f"http://localhost:{control_port}")

        >>> # Custom image
        >>> toxiproxy = ToxiproxyContainer("ghcr.io/shopify/toxiproxy:2.5.0")
        >>> toxiproxy.start()
        >>> control_url = toxiproxy.get_control_url()

    Security considerations:
        - Toxiproxy is for testing only, not production use
        - Control API has no authentication by default
        - Use in isolated test environments only
    """

    # Default configuration
    DEFAULT_IMAGE = "ghcr.io/shopify/toxiproxy:2.5.0"
    DEFAULT_CONTROL_PORT = 8474

    # Port range for proxied connections (32 ports available)
    FIRST_PROXIED_PORT = 8666
    LAST_PROXIED_PORT = 8666 + 31

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Toxiproxy container.

        Args:
            image: Docker image name (default: ghcr.io/shopify/toxiproxy:2.5.0)
        """
        super().__init__(image)

        self._control_port = self.DEFAULT_CONTROL_PORT

        # Expose Toxiproxy control port
        self.with_exposed_ports(self._control_port)

        # Expose ports for proxied connections (up to 32 proxies)
        for port in range(self.FIRST_PROXIED_PORT, self.LAST_PROXIED_PORT + 1):
            self.with_exposed_ports(port)

        # Wait for Toxiproxy to be ready using the version endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/version")
            .for_port(self._control_port)
            .for_status_code(200)
        )

    def get_control_port(self) -> int:
        """
        Get the exposed Toxiproxy control API port number on the host.

        The control port is used to configure proxies and toxics via the HTTP API.

        Returns:
            Host port number mapped to the control port
        """
        return self.get_mapped_port(self._control_port)

    def get_control_url(self) -> str:
        """
        Get the Toxiproxy control API URL.

        Returns:
            Control API URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._control_port)
        return f"http://{host}:{port}"

    def get_proxy_port(self, original_port: int) -> int:
        """
        Get the mapped host port for a specific proxied port.

        Args:
            original_port: The original container port (between 8666 and 8697)

        Returns:
            Host port number mapped to the proxied port

        Raises:
            ValueError: If the port is outside the valid range
        """
        if original_port < self.FIRST_PROXIED_PORT or original_port > self.LAST_PROXIED_PORT:
            raise ValueError(
                f"Port {original_port} is outside the valid range "
                f"({self.FIRST_PROXIED_PORT}-{self.LAST_PROXIED_PORT})"
            )
        return self.get_mapped_port(original_port)
