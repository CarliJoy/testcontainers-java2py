"""
Qdrant container implementation.

This module provides a container for Qdrant vector database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/qdrant/src/main/java/org/testcontainers/qdrant/QdrantContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class QdrantContainer(GenericContainer):
    """
    Qdrant vector database container.

    This container starts a Qdrant instance with configurable API key authentication.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/qdrant/src/main/java/org/testcontainers/qdrant/QdrantContainer.java

    Example:
        >>> with QdrantContainer() as qdrant:
        ...     rest_url = qdrant.get_rest_url()
        ...     grpc_url = qdrant.get_grpc_host_address()
        ...     # Connect to Qdrant

        >>> # With API key authentication
        >>> qdrant = QdrantContainer("qdrant/qdrant:latest")
        >>> qdrant.with_api_key("my-secret-api-key")
        >>> qdrant.start()
        >>> rest_url = qdrant.get_rest_url()

    Security considerations:
        - Default configuration has no authentication
        - For production use, enable API key authentication with with_api_key()
        - Consider using HTTPS/TLS for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "qdrant/qdrant:latest"
    DEFAULT_REST_PORT = 6333
    DEFAULT_GRPC_PORT = 6334

    # Configuration paths
    CONFIG_FILE_PATH = "/qdrant/config/config.yaml"

    # Environment variable for API key
    API_KEY_ENV = "QDRANT__SERVICE__API_KEY"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Qdrant container.

        Args:
            image: Docker image name (default: qdrant/qdrant:latest)
        """
        super().__init__(image)

        self._rest_port = self.DEFAULT_REST_PORT
        self._grpc_port = self.DEFAULT_GRPC_PORT
        self._api_key: str | None = None

        # Expose Qdrant ports
        self.with_exposed_ports(self._rest_port, self._grpc_port)

        # Wait for Qdrant to be ready using the readiness endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/readyz")
            .for_port(self._rest_port)
            .for_status_code(200)
        )

    def with_api_key(self, api_key: str) -> QdrantContainer:
        """
        Set the API key for authentication (fluent API).

        When an API key is set, all requests to Qdrant require authentication.

        Args:
            api_key: API key for authentication

        Returns:
            This container instance

        Security note:
            Use strong API keys for production deployments
        """
        self._api_key = api_key
        self.with_env(self.API_KEY_ENV, api_key)
        return self

    def with_config_file(self, config_file_path: str) -> QdrantContainer:
        """
        Set a custom configuration file from a host path (fluent API).

        Args:
            config_file_path: Path to the YAML configuration file on the host

        Returns:
            This container instance
        """
        self.with_copy_file_to_container(config_file_path, self.CONFIG_FILE_PATH)
        return self

    def get_rest_url(self) -> str:
        """
        Get the Qdrant REST API URL.

        Returns:
            REST API URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._rest_port)
        return f"http://{host}:{port}"

    def get_rest_port(self) -> int:
        """
        Get the exposed REST API port number on the host.

        Returns:
            Host port number mapped to the REST API port
        """
        return self.get_mapped_port(self._rest_port)

    def get_grpc_port(self) -> int:
        """
        Get the exposed gRPC port number on the host.

        Returns:
            Host port number mapped to the gRPC port
        """
        return self.get_mapped_port(self._grpc_port)

    def get_grpc_host_address(self) -> str:
        """
        Get the Qdrant gRPC host address (host:port).

        Returns:
            gRPC host address in format: host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._grpc_port)
        return f"{host}:{port}"

    def get_api_key(self) -> str | None:
        """
        Get the API key if configured.

        Returns:
            API key or None
        """
        return self._api_key
