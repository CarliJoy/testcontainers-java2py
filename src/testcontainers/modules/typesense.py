"""
Typesense container implementation.

This module provides a container for Typesense, a fast and typo-tolerant search engine.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/typesense/src/main/java/org/testcontainers/typesense/TypesenseContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class TypesenseContainer(GenericContainer):
    """
    Typesense search engine container.

    Typesense is a fast, typo-tolerant search engine optimized for instant search
    experiences. It provides an easy-to-use API for building search-as-you-type
    functionality.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/typesense/src/main/java/org/testcontainers/typesense/TypesenseContainer.java

    Example:
        >>> with TypesenseContainer() as typesense:
        ...     host = typesense.get_host()
        ...     port = typesense.get_http_port()
        ...     api_key = typesense.get_api_key()
        ...     # Connect to Typesense using the client library

        >>> # Custom configuration
        >>> typesense = TypesenseContainer("typesense/typesense:27.0")
        >>> typesense.with_api_key("my_secret_api_key")
        >>> typesense.start()
        >>> url = f"http://{typesense.get_host()}:{typesense.get_http_port()}"

    Exposed ports:
        - 8108: HTTP API

    Configuration:
        - Default API key: "testcontainers"
        - Data directory: /tmp (ephemeral)
    """

    # Default configuration
    DEFAULT_IMAGE = "typesense/typesense:27.0"
    DEFAULT_PORT = 8108
    DEFAULT_API_KEY = "testcontainers"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Typesense container.

        Args:
            image: Docker image name (default: typesense/typesense:27.0)
        """
        super().__init__(image)

        self._api_key = self.DEFAULT_API_KEY

        # Expose Typesense HTTP port
        self.with_exposed_ports(self.DEFAULT_PORT)

        # Set data directory (ephemeral for testing)
        self.with_env("TYPESENSE_DATA_DIR", "/tmp")

        # Wait for Typesense to be ready
        # Check the /health endpoint which returns {"ok": true}
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/health")
            .for_port(self.DEFAULT_PORT)
            .for_status_code(200)
            .for_response_predicate(lambda response: '"ok":true' in response)
        )

    def with_api_key(self, api_key: str) -> TypesenseContainer:
        """
        Set the Typesense API key (fluent API).

        The API key is required for all API requests to Typesense.

        Args:
            api_key: API key for authentication

        Returns:
            This container instance
        """
        self._api_key = api_key
        return self

    def start(self) -> TypesenseContainer:  # type: ignore[override]
        """
        Start the Typesense container.

        The API key is set via the TYPESENSE_API_KEY environment variable.

        Returns:
            This container instance
        """
        # Set the API key environment variable
        self.with_env("TYPESENSE_API_KEY", self._api_key)

        super().start()
        return self

    def get_http_port(self) -> str:
        """
        Get the exposed HTTP port as a string.

        Returns:
            HTTP port number as string

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        return str(self.get_mapped_port(self.DEFAULT_PORT))

    def get_port(self) -> int:
        """
        Get the exposed HTTP port as an integer.

        Returns:
            HTTP port number
        """
        return self.get_mapped_port(self.DEFAULT_PORT)

    def get_api_key(self) -> str:
        """
        Get the configured API key.

        Returns:
            API key for authentication
        """
        return self._api_key

    def get_http_address(self) -> str:
        """
        Get the Typesense HTTP address.

        Returns:
            HTTP address in format: http://host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"http://{host}:{port}"
