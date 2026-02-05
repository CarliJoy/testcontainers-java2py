"""
Kafka container implementation.

This module provides a container for Apache Kafka message broker.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/kafka/src/main/java/org/testcontainers/containers/KafkaContainer.java
"""

from __future__ import annotations

import uuid
from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class KafkaContainer(GenericContainer):
    """
    Kafka message broker container.

    This container starts an Apache Kafka instance using the Confluent Platform
    distribution. It configures both internal and external listeners for
    communication within Docker networks and from the host machine.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/kafka/src/main/java/org/testcontainers/containers/KafkaContainer.java

    Example:
        >>> with KafkaContainer() as kafka:
        ...     bootstrap_servers = kafka.get_bootstrap_servers()
        ...     # Connect to Kafka

        >>> # With custom cluster ID
        >>> kafka = KafkaContainer("confluentinc/cp-kafka:7.5.0")
        >>> kafka.with_cluster_id("test-cluster")
        >>> kafka.start()
        >>> bootstrap_servers = kafka.get_bootstrap_servers()

    Security considerations:
        - Default configuration does not enable authentication
        - For production use, consider enabling SASL/SSL authentication
        - Kafka runs in KRaft mode (without ZooKeeper)
    """

    # Default configuration
    DEFAULT_IMAGE = "confluentinc/cp-kafka:7.5.0"
    DEFAULT_KAFKA_PORT = 9092
    DEFAULT_INTERNAL_KAFKA_PORT = 9093

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Kafka container.

        Args:
            image: Docker image name (default: confluentinc/cp-kafka:7.5.0)
        """
        super().__init__(image)

        self._kafka_port = self.DEFAULT_KAFKA_PORT
        self._internal_kafka_port = self.DEFAULT_INTERNAL_KAFKA_PORT
        self._cluster_id: str | None = None

        # Expose Kafka port
        self.with_exposed_ports(self._kafka_port)
        
        # Set basic environment variables
        # These will be supplemented in start()
        self.with_env("KAFKA_BROKER_ID", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
        self.with_env("KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", "1")
        self.with_env("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "1")
        self.with_env("KAFKA_LOG_FLUSH_INTERVAL_MESSAGES", "10000000")
        self.with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")

        # Wait for Kafka to be ready
        # Kafka logs this message when it's ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*\[KafkaServer id=\d+\] started.*")
        )

    def with_cluster_id(self, cluster_id: str) -> KafkaContainer:
        """
        Set the Kafka cluster ID (fluent API).

        The cluster ID is used in KRaft mode for cluster identification.
        If not set, a random UUID will be generated.

        Args:
            cluster_id: Kafka cluster ID

        Returns:
            This container instance
        """
        self._cluster_id = cluster_id
        return self

    def start(self) -> KafkaContainer:  # type: ignore[override]
        """
        Start the Kafka container with configured options.

        This method configures Kafka to run in KRaft mode (without ZooKeeper)
        and sets up both internal and external listeners. The advertised
        listeners are configured to work with the dynamically assigned port.

        Returns:
            This container instance
        """
        # Generate cluster ID if not provided
        if self._cluster_id is None:
            self._cluster_id = str(uuid.uuid4())

        # Configure KRaft mode (Kafka without ZooKeeper)
        self.with_env("KAFKA_PROCESS_ROLES", "broker,controller")
        self.with_env("KAFKA_NODE_ID", "1")
        self.with_env("KAFKA_CONTROLLER_QUORUM_VOTERS", f"1@localhost:9093")
        self.with_env("KAFKA_CONTROLLER_LISTENER_NAMES", "CONTROLLER")
        self.with_env("CLUSTER_ID", self._cluster_id)
        
        # Configure listeners
        self.with_env(
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP",
            "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
        )
        
        # Internal listeners
        self.with_env(
            "KAFKA_LISTENERS",
            f"PLAINTEXT://0.0.0.0:{self._internal_kafka_port},"
            f"CONTROLLER://0.0.0.0:9093,"
            f"PLAINTEXT_HOST://0.0.0.0:{self._kafka_port}"
        )
        
        self.with_env("KAFKA_INTER_BROKER_LISTENER_NAME", "PLAINTEXT")

        # Start the container
        super().start()

        return self

    def get_bootstrap_servers(self) -> str:
        """
        Get the Kafka bootstrap servers connection string.

        This is the primary connection string used by Kafka clients to
        connect to the cluster.

        Returns:
            Bootstrap servers in format: host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._kafka_port)
        return f"{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Kafka port number on the host.

        Returns:
            Host port number mapped to the Kafka port
        """
        return self.get_mapped_port(self._kafka_port)

    def get_cluster_id(self) -> str | None:
        """
        Get the Kafka cluster ID.

        Returns:
            Kafka cluster ID or None if not set
        """
        return self._cluster_id
