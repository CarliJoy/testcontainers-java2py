"""
Cassandra container implementation.

This module provides a container for Apache Cassandra NoSQL databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/cassandra/src/main/java/org/testcontainers/containers/CassandraContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class CassandraContainer(GenericContainer):
    """
    Cassandra database container.

    This container starts a Cassandra NoSQL database instance.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/cassandra/src/main/java/org/testcontainers/containers/CassandraContainer.java

    Example:
        >>> with CassandraContainer() as cassandra:
        ...     contact_points = cassandra.get_contact_points()
        ...     # Connect to Cassandra

        >>> # Custom configuration
        >>> cassandra = CassandraContainer("cassandra:5")
        >>> cassandra.with_datacenter("dc1")
        >>> cassandra.with_cluster_name("test-cluster")
        >>> cassandra.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "cassandra:5"
    DEFAULT_PORT = 9042
    DEFAULT_DATACENTER = "datacenter1"
    DEFAULT_CLUSTER_NAME = "test-cluster"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Cassandra container.

        Args:
            image: Docker image name (default: cassandra:5)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._datacenter = self.DEFAULT_DATACENTER
        self._cluster_name = self.DEFAULT_CLUSTER_NAME

        # Expose Cassandra CQL port
        self.with_exposed_ports(self._port)

        # Set default environment variables
        self.with_env("CASSANDRA_DC", self._datacenter)
        self.with_env("CASSANDRA_CLUSTER_NAME", self._cluster_name)

        # Wait for Cassandra to be ready
        # Cassandra logs "Startup complete" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Startup complete.*")
        )

    def with_datacenter(self, datacenter: str) -> CassandraContainer:
        """
        Set the Cassandra datacenter name (fluent API).

        Args:
            datacenter: Datacenter name

        Returns:
            This container instance
        """
        self._datacenter = datacenter
        self.with_env("CASSANDRA_DC", datacenter)
        return self

    def with_cluster_name(self, cluster_name: str) -> CassandraContainer:
        """
        Set the Cassandra cluster name (fluent API).

        Args:
            cluster_name: Cluster name

        Returns:
            This container instance
        """
        self._cluster_name = cluster_name
        self.with_env("CASSANDRA_CLUSTER_NAME", cluster_name)
        return self

    def get_contact_points(self) -> str:
        """
        Get the Cassandra contact points (host:port).

        Returns:
            Contact points in format: host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Cassandra port number on the host.

        Returns:
            Host port number mapped to the Cassandra port
        """
        return self.get_mapped_port(self._port)

    def get_datacenter(self) -> str:
        """
        Get the Cassandra datacenter name.

        Returns:
            Datacenter name
        """
        return self._datacenter

    def get_cluster_name(self) -> str:
        """
        Get the Cassandra cluster name.

        Returns:
            Cluster name
        """
        return self._cluster_name
