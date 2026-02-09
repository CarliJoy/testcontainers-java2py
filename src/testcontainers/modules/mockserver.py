"""
MockServer container implementation.

This module provides a container for MockServer API mocking tool.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mockserver/src/main/java/org/testcontainers/containers/MockServerContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MockServerContainer(GenericContainer):
    """
    MockServer API mocking container.

    This container starts a MockServer instance for mocking HTTP/HTTPS APIs
    during testing.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mockserver/src/main/java/org/testcontainers/containers/MockServerContainer.java

    Example:
        >>> with MockServerContainer() as mockserver:
        ...     endpoint = mockserver.get_endpoint()
        ...     # Setup mock expectations and test

        >>> # With specific version
        >>> mockserver = MockServerContainer("mockserver/mockserver:5.15.0")
        >>> mockserver.start()
        >>> endpoint = mockserver.get_endpoint()
        >>> secure_endpoint = mockserver.get_secure_endpoint()

    Security considerations:
        - MockServer is for testing only, not production use
        - Supports both HTTP and HTTPS endpoints
        - Be careful with test data and credentials in mocked responses
    """

    # Default configuration
    DEFAULT_IMAGE = "mockserver/mockserver:5.15.0"
    DEFAULT_PORT = 1080

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a MockServer container.

        Args:
            image: Docker image name (default: mockserver/mockserver:5.15.0)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT

        # Expose MockServer port
        self.with_exposed_ports(self._port)

        # Set command to start MockServer on the default port
        self.with_command(f"-serverPort {self._port}")

        # Wait for MockServer to be ready by checking the log
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(f".*started on port: {self._port}.*")
        )

    def get_endpoint(self) -> str:
        """
        Get the MockServer HTTP endpoint URL.

        Returns:
            HTTP endpoint URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"http://{host}:{port}"

    def get_secure_endpoint(self) -> str:
        """
        Get the MockServer HTTPS endpoint URL.

        MockServer supports HTTPS on the same port as HTTP.

        Returns:
            HTTPS endpoint URL in format: https://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"https://{host}:{port}"

    def get_server_port(self) -> int:
        """
        Get the exposed MockServer port number on the host.

        Returns:
            Host port number mapped to the MockServer port
        """
        return self.get_mapped_port(self._port)

    def get_url(self) -> str:
        """
        Get the MockServer HTTP URL (alias for get_endpoint).

        Returns:
            HTTP URL in format: http://host:port
        """
        return self.get_endpoint()
