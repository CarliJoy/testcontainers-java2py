"""
Apache Solr container implementation.

This module provides a container for Apache Solr search platform.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/solr/src/main/java/org/testcontainers/containers/SolrContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class SolrContainer(GenericContainer):
    """
    Apache Solr search platform container.

    This container starts a Solr instance with optional collection and Zookeeper configuration.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/solr/src/main/java/org/testcontainers/containers/SolrContainer.java

    Example:
        >>> with SolrContainer() as solr:
        ...     url = solr.get_solr_url()
        ...     # Connect to Solr

        >>> # With collection
        >>> solr = SolrContainer("solr:9")
        >>> solr.with_collection("mycollection")
        >>> solr.start()
        >>> url = solr.get_solr_url()

    Security considerations:
        - Default configuration has no authentication
        - For production use, enable authentication and authorization
        - Consider using HTTPS/TLS for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "solr:latest"
    DEFAULT_PORT = 8983

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Solr container.

        Args:
            image: Docker image name (default: solr:latest)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._collection: str | None = None
        self._zookeeper_host: str | None = None

        # Expose Solr port
        self.with_exposed_ports(self._port)

        # Start Solr in cloud mode
        self.with_command(["solr", "start", "-f", "-c"])

        # Wait for Solr to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/solr/admin/info/system")
            .for_port(self._port)
            .for_status_code(200)
        )

    def with_collection(self, collection: str) -> SolrContainer:
        """
        Set the Solr collection to create (fluent API).

        Args:
            collection: Collection name

        Returns:
            This container instance
        """
        self._collection = collection
        return self

    def with_zookeeper(self, zookeeper_host: str) -> SolrContainer:
        """
        Connect to an external Zookeeper instance (fluent API).

        Args:
            zookeeper_host: Zookeeper connection string (host:port)

        Returns:
            This container instance
        """
        self._zookeeper_host = zookeeper_host
        return self

    def start(self) -> SolrContainer:  # type: ignore[override]
        """
        Start the Solr container with configured options.

        Returns:
            This container instance
        """
        # Set Zookeeper host if configured
        if self._zookeeper_host:
            self.with_env("ZK_HOST", self._zookeeper_host)

        super().start()

        # Create collection if specified
        if self._collection:
            self._create_collection(self._collection)

        return self

    def _create_collection(self, collection: str) -> None:
        """
        Create a collection in Solr.

        Args:
            collection: Collection name
        """
        exec_result = self.exec(
            [
                "solr",
                "create",
                "-c",
                collection,
            ]
        )
        if exec_result.exit_code != 0:
            raise RuntimeError(
                f"Failed to create collection '{collection}': {exec_result.output}"
            )

    def get_solr_url(self) -> str:
        """
        Get the Solr base URL.

        Returns:
            Solr URL in format: http://host:port/solr

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"http://{host}:{port}/solr"

    def get_port(self) -> int:
        """
        Get the exposed Solr port number on the host.

        Returns:
            Host port number mapped to the Solr port
        """
        return self.get_mapped_port(self._port)
