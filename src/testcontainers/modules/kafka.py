"""
Kafka container implementation.

This module provides a container for Apache Kafka message broker.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/kafka/src/main/java/org/testcontainers/containers/KafkaContainer.java
"""

from __future__ import annotations

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
    DEFAULT_IMAGE = "confluentinc/cp-kafka:5.4.3"
    KAFKA_PORT = 9093
    ZOOKEEPER_PORT = 2181
    DEFAULT_INTERNAL_TOPIC_RF = "1"
    STARTER_SCRIPT = "/tmp/testcontainers_start.sh"
    MIN_KRAFT_TAG = "7.0.0"
    DEFAULT_CLUSTER_ID = "4L6g3nShT-eMCtK--X86sw"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Kafka container.

        Args:
            image: Docker image name (default: confluentinc/cp-kafka:5.4.3)
        """
        super().__init__(image)

        self.external_zookeeper_connect: str | None = None
        self.kraft_enabled = False
        self._cluster_id: str | None = None

        # Expose Kafka port
        self.with_exposed_ports(self.KAFKA_PORT)
        
        # Set environment variables matching Java implementation
        self.with_env("KAFKA_LISTENERS", f"PLAINTEXT://0.0.0.0:{self.KAFKA_PORT},BROKER://0.0.0.0:9092")
        self.with_env("KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", "BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT")
        self.with_env("KAFKA_INTER_BROKER_LISTENER_NAME", "BROKER")
        
        self.with_env("KAFKA_BROKER_ID", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", self.DEFAULT_INTERNAL_TOPIC_RF)
        self.with_env("KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS", self.DEFAULT_INTERNAL_TOPIC_RF)
        self.with_env("KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", self.DEFAULT_INTERNAL_TOPIC_RF)
        self.with_env("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", self.DEFAULT_INTERNAL_TOPIC_RF)
        self.with_env("KAFKA_LOG_FLUSH_INTERVAL_MESSAGES", str(9223372036854775807))
        self.with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")

        # Set entrypoint and command
        self.with_command(["sh", "-c", f"while [ ! -f {self.STARTER_SCRIPT} ]; do sleep 0.1; done; {self.STARTER_SCRIPT}"])

        # Wait for Kafka to be ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*\[KafkaServer id=\d+\] started.*")
        )

    def with_embedded_zookeeper(self) -> KafkaContainer:
        """Configure Kafka to use embedded ZooKeeper."""
        if self.kraft_enabled:
            raise ValueError("Cannot configure Zookeeper when using Kraft mode")
        self.external_zookeeper_connect = None
        return self

    def with_external_zookeeper(self, connect_string: str) -> KafkaContainer:
        """Configure Kafka to use external ZooKeeper."""
        if self.kraft_enabled:
            raise ValueError("Cannot configure Zookeeper when using Kraft mode")
        self.external_zookeeper_connect = connect_string
        return self

    def with_kraft(self) -> KafkaContainer:
        """Enable KRaft mode (Kafka without ZooKeeper)."""
        if self.external_zookeeper_connect is not None:
            raise ValueError("Cannot configure Kraft mode when Zookeeper configured")
        self.kraft_enabled = True
        return self

    def with_cluster_id(self, cluster_id: str) -> KafkaContainer:
        """
        Set the Kafka cluster ID (fluent API).

        The cluster ID is used in KRaft mode for cluster identification.

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

        Returns:
            This container instance
        """
        # Configure based on mode
        if self.kraft_enabled:
            self._configure_kraft()
        else:
            self._configure_zookeeper()

        # Start the container
        super().start()

        # After container starts, configure advertised listeners
        self._configure_advertised_listeners()

        return self

    def _configure_kraft(self) -> None:
        """Configure Kafka for KRaft mode."""
        if self._cluster_id is None:
            self._cluster_id = self.DEFAULT_CLUSTER_ID
        
        self.with_env("CLUSTER_ID", self._cluster_id)
        self.with_env("KAFKA_NODE_ID", self._env.get("KAFKA_BROKER_ID", "1"))
        
        # Update listener security protocol map
        existing_map = self._env.get("KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", "")
        if "CONTROLLER:PLAINTEXT" not in existing_map:
            self.with_env("KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", f"{existing_map},CONTROLLER:PLAINTEXT")
        
        # Update listeners
        existing_listeners = self._env.get("KAFKA_LISTENERS", "")
        if "CONTROLLER" not in existing_listeners:
            self.with_env("KAFKA_LISTENERS", f"{existing_listeners},CONTROLLER://0.0.0.0:9094")
        
        self.with_env("KAFKA_PROCESS_ROLES", "broker,controller")
        
        controller_quorum_voters = f"{self._env.get('KAFKA_NODE_ID', '1')}@localhost:9094"
        self.with_env("KAFKA_CONTROLLER_QUORUM_VOTERS", controller_quorum_voters)
        self.with_env("KAFKA_CONTROLLER_LISTENER_NAMES", "CONTROLLER")
        
        # Update wait strategy for KRaft
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Transitioning from RECOVERY to RUNNING.*")
        )

    def _configure_zookeeper(self) -> None:
        """Configure Kafka with ZooKeeper."""
        if self.external_zookeeper_connect is None:
            # Use embedded ZooKeeper
            self.with_exposed_ports(self.ZOOKEEPER_PORT)
            self.with_env("KAFKA_ZOOKEEPER_CONNECT", f"localhost:{self.ZOOKEEPER_PORT}")
        else:
            # Use external ZooKeeper
            self.with_env("KAFKA_ZOOKEEPER_CONNECT", self.external_zookeeper_connect)

    def _configure_advertised_listeners(self) -> None:
        """Configure advertised listeners after container starts."""
        if not self._container:
            return
        
        # Get container info
        container_id = self._container.id
        container_info = self._docker_client.api.inspect_container(container_id)
        container_hostname = container_info['Config']['Hostname']
        
        # Build advertised listeners
        bootstrap_servers = self.get_bootstrap_servers()
        broker_listener = f"BROKER://{container_hostname}:9092"
        advertised_listeners = f"{bootstrap_servers},{broker_listener}"
        
        # Build startup script
        command = "#!/bin/bash\n"
        command += f"export KAFKA_ADVERTISED_LISTENERS={advertised_listeners}\n"
        
        # Skip checks for optimization
        if not self.kraft_enabled:
            command += "echo '' > /etc/confluent/docker/ensure \n"
        
        if self.kraft_enabled:
            command += "sed -i '/KAFKA_ZOOKEEPER_CONNECT/d' /etc/confluent/docker/configure\n"
            command += f"echo 'kafka-storage format --ignore-formatted -t \"{self._cluster_id}\" -c /etc/kafka/kafka.properties' >> /etc/confluent/docker/configure\n"
        elif self.external_zookeeper_connect is None:
            # Embedded ZooKeeper
            command += f"echo 'clientPort={self.ZOOKEEPER_PORT}' > /tmp/zookeeper.properties\n"
            command += "echo 'dataDir=/var/lib/zookeeper/data' >> /tmp/zookeeper.properties\n"
            command += "echo 'dataLogDir=/var/lib/zookeeper/log' >> /tmp/zookeeper.properties\n"
            command += "zookeeper-server-start /tmp/zookeeper.properties &\n"
        
        command += "/etc/confluent/docker/run \n"
        
        # Copy startup script to container
        self._docker_client.api.put_archive(
            container_id,
            '/tmp',
            self._create_tar_archive('testcontainers_start.sh', command.encode('utf-8'), 0o777)
        )

    def _create_tar_archive(self, filename: str, content: bytes, mode: int) -> bytes:
        """Create a tar archive with a single file."""
        import io
        import tarfile
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content)
            tarinfo.mode = mode
            tar.addfile(tarinfo, io.BytesIO(content))
        
        return tar_stream.getvalue()

    def get_bootstrap_servers(self) -> str:
        """
        Get the Kafka bootstrap servers connection string.

        This is the primary connection string used by Kafka clients to
        connect to the cluster.

        Returns:
            Bootstrap servers in format: PLAINTEXT://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self.KAFKA_PORT)
        return f"PLAINTEXT://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Kafka port number on the host.

        Returns:
            Host port number mapped to the Kafka port
        """
        return self.get_mapped_port(self.KAFKA_PORT)
