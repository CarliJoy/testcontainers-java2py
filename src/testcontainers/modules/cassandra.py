"""
Cassandra NoSQL database container wrapper.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/cassandra/src/main/java/org/testcontainers/cassandra/CassandraContainer.java
"""

from __future__ import annotations
from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class CassandraContainer(GenericContainer):
    """
    Wrapper for Cassandra 3.11.2 NoSQL database with CQL protocol.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/cassandra/src/main/java/org/testcontainers/cassandra/CassandraContainer.java
    """

    def __init__(self, image: str = "cassandra:3.11.2"):
        super().__init__(image)
        
        # CQL native transport port
        self._cql_port = 9042
        
        # Cluster topology defaults
        self._datacenter_name = "datacenter1"
        self._cluster_label = "test-cluster"
        
        # Fixed authentication
        self._auth_user = "cassandra"
        self._auth_pass = "cassandra"
        
        self.with_exposed_ports(self._cql_port)
        
        # JVM and cluster environment
        jvm_opts = "-Dcassandra.skip_wait_for_gossip_to_settle=0 -Dcassandra.initial_token=0"
        self.with_env("JVM_OPTS", jvm_opts)
        self.with_env("HEAP_NEWSIZE", "128M")
        self.with_env("MAX_HEAP_SIZE", "1024M")
        self.with_env("CASSANDRA_SNITCH", "GossipingPropertyFileSnitch")
        self.with_env("CASSANDRA_ENDPOINT_SNITCH", "GossipingPropertyFileSnitch")
        self.with_env("CASSANDRA_DC", self._datacenter_name)
        
        # Wait for ready state
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*Startup complete.*"))

    def with_datacenter(self, dc_name: str) -> CassandraContainer:
        """Configure datacenter identifier."""
        self._datacenter_name = dc_name
        self.with_env("CASSANDRA_DC", dc_name)
        return self

    def with_cluster_name(self, cluster_id: str) -> CassandraContainer:
        """Configure cluster identifier."""
        self._cluster_label = cluster_id
        self.with_env("CASSANDRA_CLUSTER_NAME", cluster_id)
        return self

    def get_contact_points(self) -> str:
        """Build contact point connection string."""
        return f"{self.get_host()}:{self.get_mapped_port(self._cql_port)}"

    def get_port(self) -> int:
        """Retrieve mapped CQL port."""
        return self.get_mapped_port(self._cql_port)

    def get_datacenter(self) -> str:
        """Retrieve configured datacenter."""
        return self._datacenter_name

    def get_cluster_name(self) -> str:
        """Retrieve configured cluster name."""
        return self._cluster_label
    
    def get_username(self) -> str:
        """Retrieve default username."""
        return self._auth_user
    
    def get_password(self) -> str:
        """Retrieve default password."""
        return self._auth_pass
