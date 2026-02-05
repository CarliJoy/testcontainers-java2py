"""
Weaviate container implementation.

This module provides a container for Weaviate vector database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/weaviate/src/main/java/org/testcontainers/weaviate/WeaviateContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class WeaviateContainer(GenericContainer):
    """
    Weaviate vector database container.

    This container starts a Weaviate instance with configurable authentication
    and persistence settings.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/weaviate/src/main/java/org/testcontainers/weaviate/WeaviateContainer.java

    Example:
        >>> with WeaviateContainer() as weaviate:
        ...     http_url = weaviate.get_http_url()
        ...     grpc_url = weaviate.get_grpc_host_address()
        ...     # Connect to Weaviate

        >>> # Custom configuration
        >>> weaviate = WeaviateContainer("semitechnologies/weaviate:latest")
        >>> weaviate.start()
        >>> http_url = weaviate.get_http_url()

    Security considerations:
        - Default configuration enables anonymous access for testing
        - For production use, configure proper authentication
        - Consider using HTTPS/TLS for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "cr.weaviate.io/semitechnologies/weaviate:latest"
    DEFAULT_HTTP_PORT = 8080
    DEFAULT_GRPC_PORT = 50051

    # Default environment variables
    DEFAULT_PERSISTENCE_PATH = "/var/lib/weaviate"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Weaviate container.

        Args:
            image: Docker image name (default: cr.weaviate.io/semitechnologies/weaviate:latest)
        """
        super().__init__(image)

        self._http_port = self.DEFAULT_HTTP_PORT
        self._grpc_port = self.DEFAULT_GRPC_PORT

        # Expose Weaviate ports
        self.with_exposed_ports(self._http_port, self._grpc_port)

        # Default environment variables
        # Enable anonymous access by default for easier testing
        self.with_env("AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED", "true")
        
        # Set persistence path
        self.with_env("PERSISTENCE_DATA_PATH", self.DEFAULT_PERSISTENCE_PATH)

        # Wait for Weaviate to be ready using the readiness endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/v1/.well-known/ready")
            .for_port(self._http_port)
            .for_status_code(200)
        )

    def with_env(self, key: str, value: str) -> WeaviateContainer:  # type: ignore[override]
        """
        Set an environment variable (fluent API).

        Args:
            key: Environment variable name
            value: Environment variable value

        Returns:
            This container instance
        """
        super().with_env(key, value)
        return self

    def get_http_url(self) -> str:
        """
        Get the Weaviate HTTP URL.

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

    def get_http_host_address(self) -> str:
        """
        Get the Weaviate HTTP host address (host:port).

        Returns:
            HTTP host address in format: host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._http_port)
        return f"{host}:{port}"

    def get_http_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self._http_port)

    def get_grpc_port(self) -> int:
        """
        Get the exposed gRPC port number on the host.

        Returns:
            Host port number mapped to the gRPC port
        """
        return self.get_mapped_port(self._grpc_port)

    def get_grpc_host_address(self) -> str:
        """
        Get the Weaviate gRPC host address (host:port).

        Returns:
            gRPC host address in format: host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._grpc_port)
        return f"{host}:{port}"
