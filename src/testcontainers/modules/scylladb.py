"""
ScyllaDB NoSQL database container implementation.

This module provides a container for ScyllaDB, a Cassandra-compatible database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/scylladb/src/main/java/org/testcontainers/scylladb/ScyllaDBContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class ScyllaDBContainer(GenericContainer):
    """
    ScyllaDB NoSQL database container.

    ScyllaDB is a Cassandra-compatible NoSQL database with CQL protocol support.
    This container starts a ScyllaDB instance in developer mode.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/scylladb/src/main/java/org/testcontainers/scylladb/ScyllaDBContainer.java

    Example:
        >>> with ScyllaDBContainer() as scylla:
        ...     host, port = scylla.get_contact_point()
        ...     # Connect to ScyllaDB

        >>> # With Alternator (DynamoDB-compatible API)
        >>> scylla = ScyllaDBContainer("scylladb/scylla:5.4")
        >>> scylla.with_alternator()
        >>> scylla.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "scylladb/scylla"
    CQL_PORT = 9042
    SHARD_AWARE_PORT = 19042
    ALTERNATOR_PORT = 8000

    # Default command
    DEFAULT_COMMAND = "--developer-mode=1 --overprovisioned=1"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a ScyllaDB container.

        Args:
            image: Docker image name (default: scylladb/scylla)
        """
        super().__init__(image)

        self._alternator_enabled = False

        # Expose CQL and shard-aware ports
        self.with_exposed_ports(self.CQL_PORT, self.SHARD_AWARE_PORT)

        # Set default command
        self.with_command(self.DEFAULT_COMMAND)

        # Wait for ScyllaDB to be ready
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*initialization completed\..*"))

    def start(self) -> ScyllaDBContainer:
        """Start the container with alternator configuration if enabled."""
        # If Alternator is enabled, add port and update command before starting
        if self._alternator_enabled:
            self.with_exposed_ports(self.ALTERNATOR_PORT)
            new_command = (
                f"{self.DEFAULT_COMMAND} "
                f"--alternator-port={self.ALTERNATOR_PORT} "
                f"--alternator-write-isolation=always"
            )
            self.with_command(new_command)
        
        return super().start()

    def with_alternator(self) -> ScyllaDBContainer:
        """
        Enable Alternator (DynamoDB-compatible API).

        Must be called before the container is started.

        Returns:
            Self for method chaining
        """
        self._alternator_enabled = True
        return self

    def get_contact_point(self) -> tuple[str, int]:
        """
        Get the contact point for connecting to ScyllaDB.

        Returns:
            Tuple of (host, port) for CQL connections
        """
        return (self.get_host(), self.get_mapped_port(self.CQL_PORT))

    def get_shard_aware_contact_point(self) -> tuple[str, int]:
        """
        Get the shard-aware contact point for connecting to ScyllaDB.

        Returns:
            Tuple of (host, port) for shard-aware CQL connections
        """
        return (self.get_host(), self.get_mapped_port(self.SHARD_AWARE_PORT))

    def get_alternator_endpoint(self) -> str:
        """
        Get the Alternator endpoint URL.

        Returns:
            HTTP URL for Alternator (DynamoDB-compatible) API

        Raises:
            RuntimeError: If Alternator is not enabled
        """
        if not self._alternator_enabled:
            raise RuntimeError("Alternator is not enabled")
        return f"http://{self.get_host()}:{self.get_mapped_port(self.ALTERNATOR_PORT)}"
