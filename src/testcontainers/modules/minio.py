"""
MinIO container implementation.

This module provides a container for MinIO S3-compatible object storage.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/minio/src/main/java/org/testcontainers/containers/MinIOContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class MinIOContainer(GenericContainer):
    """
    MinIO S3-compatible object storage container.

    This container starts a MinIO server instance with configurable
    credentials and exposes both API and console ports.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/minio/src/main/java/org/testcontainers/containers/MinIOContainer.java

    Example:
        >>> with MinIOContainer() as minio:
        ...     url = minio.get_url()
        ...     access_key = minio.get_access_key()
        ...     secret_key = minio.get_secret_key()
        ...     # Connect to MinIO

        >>> # With custom credentials
        >>> minio = MinIOContainer("minio/minio:latest")
        >>> minio.with_credentials("myaccesskey", "mysecretkey")
        >>> minio.start()
        >>> url = minio.get_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "minio/minio:latest"
    DEFAULT_API_PORT = 9000
    DEFAULT_CONSOLE_PORT = 9001

    # Default credentials
    DEFAULT_ACCESS_KEY = "minioadmin"
    DEFAULT_SECRET_KEY = "minioadmin"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a MinIO container.

        Args:
            image: Docker image name (default: minio/minio:latest)
        """
        super().__init__(image)

        self._api_port = self.DEFAULT_API_PORT
        self._console_port = self.DEFAULT_CONSOLE_PORT
        self._access_key = self.DEFAULT_ACCESS_KEY
        self._secret_key = self.DEFAULT_SECRET_KEY

        # Expose MinIO ports
        self.with_exposed_ports(self._api_port, self._console_port)

        # Set default command
        self.with_command(["server", "/data", "--console-address", ":9001"])

        # Set environment variables for credentials
        self.with_env("MINIO_ROOT_USER", self._access_key)
        self.with_env("MINIO_ROOT_PASSWORD", self._secret_key)

        # Wait for MinIO to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/minio/health/live")
            .for_port(self._api_port)
            .for_status_code(200)
        )

    def with_credentials(
        self, access_key: str, secret_key: str
    ) -> MinIOContainer:
        """
        Set MinIO access credentials (fluent API).

        Args:
            access_key: MinIO access key (username)
            secret_key: MinIO secret key (password)

        Returns:
            This container instance
        """
        self._access_key = access_key
        self._secret_key = secret_key
        self.with_env("MINIO_ROOT_USER", access_key)
        self.with_env("MINIO_ROOT_PASSWORD", secret_key)
        return self

    def get_url(self) -> str:
        """
        Get the MinIO API URL.

        Returns:
            API URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._api_port)
        return f"http://{host}:{port}"

    def get_console_url(self) -> str:
        """
        Get the MinIO console URL.

        Returns:
            Console URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._console_port)
        return f"http://{host}:{port}"

    def get_access_key(self) -> str:
        """
        Get the MinIO access key.

        Returns:
            Access key (username)
        """
        return self._access_key

    def get_secret_key(self) -> str:
        """
        Get the MinIO secret key.

        Returns:
            Secret key (password)
        """
        return self._secret_key

    def get_port(self) -> int:
        """
        Get the exposed API port number on the host.

        Returns:
            Host port number mapped to the API port
        """
        return self.get_mapped_port(self._api_port)
