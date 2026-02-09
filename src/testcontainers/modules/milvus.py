"""
Milvus container implementation.

This module provides a container for Milvus vector database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/milvus/src/main/java/org/testcontainers/milvus/MilvusContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class MilvusContainer(GenericContainer):
    """
    Milvus vector database container.

    This container provides access to Milvus for vector similarity search and AI applications.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/milvus/src/main/java/org/testcontainers/milvus/MilvusContainer.java

    Example:
        >>> with MilvusContainer() as milvus:
        ...     endpoint = milvus.get_endpoint()
        ...     # Connect to Milvus

        >>> # Custom image with external etcd
        >>> milvus = MilvusContainer("milvusdb/milvus:v2.3.0")
        >>> milvus.with_etcd_endpoint("etcd:2379")
        >>> milvus.start()

    Supported image:
        - milvusdb/milvus

    Exposed ports:
        - 9091 (Management/Health port)
        - 19530 (HTTP port)
    """

    DEFAULT_IMAGE = "milvusdb/milvus"
    MANAGEMENT_PORT = 9091
    HTTP_PORT = 19530

    # Embedded etcd configuration content
    _EMBED_ETCD_YAML = """listen-client-urls: http://0.0.0.0:2379
advertise-client-urls: http://0.0.0.0:2379
"""

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Milvus container.

        Args:
            image: Docker image name (default: milvusdb/milvus)
        """
        super().__init__(image)

        self._etcd_endpoint: str | None = None

        # Expose ports
        self.with_exposed_ports(self.MANAGEMENT_PORT, self.HTTP_PORT)

        # Wait for Milvus to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/healthz")
            .for_port(self.MANAGEMENT_PORT)
        )

        # Set default command
        self.with_command(["milvus", "run", "standalone"])

        # Set local storage type
        self.with_env("COMMON_STORAGETYPE", "local")

    def with_etcd_endpoint(self, etcd_endpoint: str) -> MilvusContainer:
        """
        Set an external etcd endpoint.

        Args:
            etcd_endpoint: External etcd endpoint

        Returns:
            This container instance
        """
        self._etcd_endpoint = etcd_endpoint
        return self

    def _configure(self) -> None:
        """
        Configure the container environment before starting.

        This is called automatically during container startup.
        """
        if self._etcd_endpoint is None:
            # Use embedded etcd
            self.with_env("ETCD_USE_EMBED", "true")
            self.with_env("ETCD_DATA_DIR", "/var/lib/milvus/etcd")
            self.with_env("ETCD_CONFIG_PATH", "/milvus/configs/embedEtcd.yaml")

            # Create embedEtcd.yaml configuration in container
            # We'll use a bind mount or copy the file
            import tempfile
            import os

            # Create temporary file with etcd config
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
                f.write(self._EMBED_ETCD_YAML)
                temp_path = f.name

            self.with_volume_mapping(temp_path, "/milvus/configs/embedEtcd.yaml")
            self._temp_etcd_config = temp_path
        else:
            # Use external etcd
            self.with_env("ETCD_ENDPOINTS", self._etcd_endpoint)

    def start(self) -> MilvusContainer:  # type: ignore[override]
        """
        Start the Milvus container.

        Returns:
            This container instance
        """
        self._configure()
        super().start()
        return self

    def stop(self, **kwargs) -> None:  # type: ignore[override]
        """
        Stop the Milvus container and clean up temporary files.

        Args:
            **kwargs: Additional arguments passed to the parent stop method
        """
        super().stop(**kwargs)

        # Clean up temporary etcd config file if it exists
        if hasattr(self, "_temp_etcd_config"):
            import os

            try:
                os.unlink(self._temp_etcd_config)
            except (OSError, FileNotFoundError):
                pass

    def get_endpoint(self) -> str:
        """
        Get the Milvus endpoint URL.

        Returns:
            Milvus endpoint in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self.HTTP_PORT)}"
