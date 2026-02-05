"""
ChromaDB container implementation.

This module provides a container for ChromaDB vector database.
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class ChromaDBContainer(GenericContainer):
    """
    ChromaDB vector database container.

    This container starts a ChromaDB instance with optional authentication.

    Example:
        >>> with ChromaDBContainer() as chroma:
        ...     url = chroma.get_url()
        ...     # Connect to ChromaDB

        >>> # With authentication token
        >>> chroma = ChromaDBContainer()
        >>> chroma.with_auth_token("my-secret-token")
        >>> chroma.start()
        >>> url = chroma.get_url()

    Security considerations:
        - Default configuration has no authentication
        - For production use, enable token-based authentication
        - Consider using HTTPS/TLS for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "chromadb/chroma:latest"
    DEFAULT_PORT = 8000

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a ChromaDB container.

        Args:
            image: Docker image name (default: chromadb/chroma:latest)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._auth_token: str | None = None

        # Expose ChromaDB port
        self.with_exposed_ports(self._port)

        # Wait for ChromaDB to be ready
        # Check the heartbeat endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/api/v1/heartbeat")
            .for_port(self._port)
            .for_status_code(200)
        )

    def with_auth_token(self, token: str) -> ChromaDBContainer:
        """
        Set the authentication token (fluent API).

        When a token is set, ChromaDB requires authentication for all requests.

        Args:
            token: Authentication token

        Returns:
            This container instance

        Security note:
            Use strong tokens for production deployments
        """
        self._auth_token = token
        return self

    def start(self) -> ChromaDBContainer:  # type: ignore[override]
        """
        Start the ChromaDB container with configured options.

        If an auth token was set, authentication is enabled.

        Returns:
            This container instance
        """
        # Enable authentication if token is set
        if self._auth_token:
            self.with_env("CHROMA_SERVER_AUTHN_CREDENTIALS", self._auth_token)
            self.with_env("CHROMA_SERVER_AUTHN_PROVIDER", "chromadb.auth.token.TokenAuthenticationServerProvider")

        super().start()
        return self

    def get_url(self) -> str:
        """
        Get the ChromaDB URL.

        Returns:
            ChromaDB URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed ChromaDB port number on the host.

        Returns:
            Host port number mapped to the ChromaDB port
        """
        return self.get_mapped_port(self._port)

    def get_auth_token(self) -> str | None:
        """
        Get the authentication token if configured.

        Returns:
            Authentication token or None
        """
        return self._auth_token
