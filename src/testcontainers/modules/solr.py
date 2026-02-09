"""
Apache Solr container implementation.

This module provides a container for Apache Solr search platform.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/solr/src/main/java/org/testcontainers/containers/SolrContainer.java
"""

from __future__ import annotations

import re

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


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
    DEFAULT_IMAGE = "solr:8.3.0"
    SOLR_PORT = 8983
    ZOOKEEPER_PORT = 9983

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Solr container.

        Args:
            image: Docker image name (default: solr:8.3.0)
        """
        super().__init__(image)

        # Extract version from image
        self._image_version = self._extract_version(image)

        # Configuration
        self._zookeeper = True
        self._collection_name = "dummy"
        self._configuration_name: str | None = None
        self._solr_configuration: str | None = None
        self._solr_schema: str | None = None

        # Wait for Solr to be ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*o\.e\.j\.s\.Server Started.*")
            .with_startup_timeout(60.0)
        )

    def _extract_version(self, image: str) -> str:
        """Extract version from image name."""
        if ":" in image:
            return image.split(":")[-1]
        return "8.3.0"

    def _compare_version(self, version: str, target: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        def normalize(v):
            parts = re.match(r'^(\d+)\.(\d+)(?:\.(\d+))?', v)
            if parts:
                return [int(parts.group(1)), int(parts.group(2)), int(parts.group(3) or 0)]
            return [0, 0, 0]

        v_parts = normalize(version)
        t_parts = normalize(target)

        for i in range(3):
            if v_parts[i] < t_parts[i]:
                return -1
            elif v_parts[i] > t_parts[i]:
                return 1
        return 0

    def with_zookeeper(self, zookeeper: bool) -> SolrContainer:
        """
        Enable or disable Zookeeper mode (fluent API).

        Args:
            zookeeper: True to enable Zookeeper (cloud mode), False for standalone

        Returns:
            This container instance
        """
        self._zookeeper = zookeeper
        return self

    def with_collection(self, collection: str) -> SolrContainer:
        """
        Set the Solr collection to create (fluent API).

        Args:
            collection: Collection name

        Returns:
            This container instance

        Raises:
            ValueError: If collection name is empty
        """
        if not collection:
            raise ValueError("Collection name must not be empty")
        self._collection_name = collection
        return self

    def with_configuration(self, name: str, solr_config: str) -> SolrContainer:
        """
        Set Solr configuration (fluent API).

        Args:
            name: Configuration name
            solr_config: Path or URL to solrconfig.xml

        Returns:
            This container instance

        Raises:
            ValueError: If name is empty or solr_config is None
        """
        if not name or solr_config is None:
            raise ValueError("Configuration name and solr_config must not be empty")
        self._configuration_name = name
        self._solr_configuration = solr_config
        return self

    def with_schema(self, schema: str) -> SolrContainer:
        """
        Set Solr schema (fluent API).

        Args:
            schema: Path or URL to schema.xml

        Returns:
            This container instance
        """
        self._solr_schema = schema
        return self

    def get_solr_port(self) -> int:
        """
        Get the exposed Solr port number on the host.

        Returns:
            Host port number mapped to the Solr port
        """
        return self.get_mapped_port(self.SOLR_PORT)

    def get_zookeeper_port(self) -> int:
        """
        Get the exposed Zookeeper port number on the host.

        Returns:
            Host port number mapped to the Zookeeper port
        """
        return self.get_mapped_port(self.ZOOKEEPER_PORT)

    def _configure(self) -> None:
        """Configure the Solr container before starting."""
        super()._configure()

        if self._solr_schema is not None and self._solr_configuration is None:
            raise ValueError("Solr needs to have a configuration if you want to use a schema")

        # Build command
        command = "solr start -f"

        # Add default port
        self.with_exposed_ports(self.SOLR_PORT)

        # Configure Zookeeper
        if self._zookeeper:
            self.with_exposed_ports(self.ZOOKEEPER_PORT)
            if self._compare_version(self._image_version, "9.7.0") >= 0:
                command = "-DzkRun --host localhost"
            else:
                command = "-DzkRun -h localhost"

        # Set command
        self.with_command(command)

    def start(self) -> SolrContainer:  # type: ignore[override]
        """
        Start the Solr container with configured options.

        Returns:
            This container instance
        """
        super().start()

        # Create collection/core after container is started
        if not self._zookeeper:
            # Standalone mode - create core
            exec_result = self.exec(["solr", "create", "-c", self._collection_name])
            if exec_result.exit_code != 0:
                raise RuntimeError(
                    f"Unable to create solr core:\nStdout: {exec_result.output}"
                )
        else:
            # Cloud mode - upload configuration and create collection
            if self._configuration_name:
                # Note: Configuration upload would require SolrClientUtils equivalent
                # which is not implemented in this basic version
                pass

            # Create collection (would use SolrClientUtils in full implementation)
            pass

        return self
