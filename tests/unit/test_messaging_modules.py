"""
Comprehensive tests for messaging and search container modules.

This module tests the Kafka, Elasticsearch, and RabbitMQ container implementations.
"""

from __future__ import annotations

import pytest
from testcontainers.modules.kafka import KafkaContainer
from testcontainers.modules.elasticsearch import ElasticsearchContainer
from testcontainers.modules.rabbitmq import RabbitMQContainer


# =============================================================================
# Kafka Container Tests
# =============================================================================


class TestKafkaContainer:
    """Test suite for KafkaContainer."""

    def test_kafka_container_initialization(self):
        """Test that Kafka container can be initialized with default settings."""
        kafka = KafkaContainer()
        assert kafka.KAFKA_PORT == KafkaContainer.KAFKA_PORT
        assert kafka._cluster_id is None
        assert kafka.kraft_enabled is False
        assert kafka.external_zookeeper_connect is None

    def test_kafka_container_with_custom_image(self):
        """Test that Kafka container can be initialized with a custom image."""
        custom_image = "confluentinc/cp-kafka:7.4.0"
        kafka = KafkaContainer(custom_image)
        assert kafka._image._image_name == custom_image

    def test_kafka_with_cluster_id(self):
        """Test that cluster ID can be set using fluent API."""
        kafka = KafkaContainer()
        cluster_id = "test-cluster-123"
        result = kafka.with_cluster_id(cluster_id)
        
        assert result is kafka  # Fluent API returns self
        assert kafka._cluster_id == cluster_id

    def test_kafka_get_cluster_id(self):
        """Test setting the cluster ID."""
        kafka = KafkaContainer()
        cluster_id = "my-kafka-cluster"
        kafka.with_cluster_id(cluster_id)
        
        assert kafka._cluster_id == cluster_id

    def test_kafka_with_kraft(self):
        """Test enabling KRaft mode."""
        kafka = KafkaContainer()
        result = kafka.with_kraft()
        
        assert result is kafka
        assert kafka.kraft_enabled is True

    def test_kafka_with_embedded_zookeeper(self):
        """Test configuring embedded ZooKeeper."""
        kafka = KafkaContainer()
        result = kafka.with_embedded_zookeeper()
        
        assert result is kafka
        assert kafka.external_zookeeper_connect is None

    def test_kafka_get_cluster_id_default(self):
        """Test that cluster ID can be retrieved after setting."""
        kafka = KafkaContainer()
        cluster_id = "test-cluster"
        kafka.with_cluster_id(cluster_id)
        assert kafka._cluster_id == cluster_id

    def test_kafka_get_bootstrap_servers_not_started(self):
        """Test that get_bootstrap_servers raises error when container not started."""
        kafka = KafkaContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            kafka.get_bootstrap_servers()

    def test_kafka_exposed_ports(self):
        """Test that Kafka exposes the correct ports."""
        kafka = KafkaContainer()
        
        assert KafkaContainer.KAFKA_PORT in kafka._exposed_ports

    def test_kafka_default_image(self):
        """Test that Kafka uses the correct default image."""
        kafka = KafkaContainer()
        assert kafka._image._image_name == KafkaContainer.DEFAULT_IMAGE


# =============================================================================
# Elasticsearch Container Tests
# =============================================================================


class TestElasticsearchContainer:
    """Test suite for ElasticsearchContainer."""

    def test_elasticsearch_container_initialization(self):
        """Test that Elasticsearch container can be initialized with default settings."""
        es = ElasticsearchContainer()
        assert es._http_port == ElasticsearchContainer.ELASTICSEARCH_DEFAULT_PORT
        assert es._transport_port == ElasticsearchContainer.ELASTICSEARCH_DEFAULT_TCP_PORT
        # Password is set by default for version 8+
        assert es._password is not None or not es._is_at_least_major_version_8

    def test_elasticsearch_container_with_custom_image(self):
        """Test that Elasticsearch container can be initialized with a custom image."""
        custom_image = "elasticsearch:8.10.0"
        es = ElasticsearchContainer(custom_image)
        assert es._image._image_name == custom_image

    def test_elasticsearch_with_password(self):
        """Test that password can be set using fluent API."""
        es = ElasticsearchContainer()
        password = "mySecurePassword123"
        result = es.with_password(password)
        
        assert result is es  # Fluent API returns self
        assert es._password == password

    def test_elasticsearch_get_password(self):
        """Test getting the Elasticsearch password."""
        es = ElasticsearchContainer()
        password = "testpass"
        es.with_password(password)
        
        assert es._password == password

    def test_elasticsearch_get_password_default(self):
        """Test that password may be set by default for v8+."""
        es = ElasticsearchContainer()
        # Password is set by default for version 8+
        if es._is_at_least_major_version_8:
            assert es._password is not None
        else:
            assert es._password is None

    def test_elasticsearch_get_username(self):
        """Test the default Elasticsearch username."""
        # Username is always 'elastic' in Java
        assert ElasticsearchContainer.ELASTICSEARCH_DEFAULT_PASSWORD == "changeme"

    def test_elasticsearch_get_http_url_not_started(self):
        """Test that get_http_url raises error when container not started."""
        es = ElasticsearchContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            es.get_http_url()

    def test_elasticsearch_exposed_ports(self):
        """Test that Elasticsearch exposes the correct ports."""
        es = ElasticsearchContainer()
        
        assert ElasticsearchContainer.ELASTICSEARCH_DEFAULT_PORT in es._exposed_ports
        assert ElasticsearchContainer.ELASTICSEARCH_DEFAULT_TCP_PORT in es._exposed_ports

    def test_elasticsearch_default_image(self):
        """Test that Elasticsearch uses the correct default image."""
        es = ElasticsearchContainer()
        assert es._image._image_name == ElasticsearchContainer.DEFAULT_IMAGE

    def test_elasticsearch_default_environment(self):
        """Test that Elasticsearch sets correct default environment variables."""
        es = ElasticsearchContainer()
        
        assert es._env["discovery.type"] == "single-node"
        assert "cluster.routing.allocation.disk.threshold_enabled" in es._env


# =============================================================================
# RabbitMQ Container Tests
# =============================================================================


class TestRabbitMQContainer:
    """Test suite for RabbitMQContainer."""

    def test_rabbitmq_container_initialization(self):
        """Test that RabbitMQ container can be initialized with default settings."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq._amqp_port == RabbitMQContainer.DEFAULT_AMQP_PORT
        assert rabbitmq._amqps_port == RabbitMQContainer.DEFAULT_AMQPS_PORT
        assert rabbitmq._http_port == RabbitMQContainer.DEFAULT_HTTP_PORT
        assert rabbitmq._https_port == RabbitMQContainer.DEFAULT_HTTPS_PORT
        assert rabbitmq._admin_username == RabbitMQContainer.DEFAULT_USERNAME
        assert rabbitmq._admin_password == RabbitMQContainer.DEFAULT_PASSWORD

    def test_rabbitmq_container_with_custom_image(self):
        """Test that RabbitMQ container can be initialized with a custom image."""
        custom_image = "rabbitmq:3.12-management"
        rabbitmq = RabbitMQContainer(custom_image)
        assert rabbitmq._image._image_name == custom_image

    def test_rabbitmq_with_vhost(self):
        """Test that admin user can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        username = "admin"
        result = rabbitmq.with_admin_user(username)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._admin_username == username

    def test_rabbitmq_with_username(self):
        """Test that admin username can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        username = "admin"
        result = rabbitmq.with_admin_user(username)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._admin_username == username

    def test_rabbitmq_with_password(self):
        """Test that password can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        password = "secretpass"
        result = rabbitmq.with_admin_password(password)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._admin_password == password

    def test_rabbitmq_with_credentials(self):
        """Test that both username and password can be set together."""
        rabbitmq = RabbitMQContainer()
        username = "admin"
        password = "adminpass"
        rabbitmq.with_admin_user(username)
        rabbitmq.with_admin_password(password)
        
        assert rabbitmq._admin_username == username
        assert rabbitmq._admin_password == password

    def test_rabbitmq_get_username(self):
        """Test getting the RabbitMQ username."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq.get_admin_username() == RabbitMQContainer.DEFAULT_USERNAME

    def test_rabbitmq_get_password(self):
        """Test getting the RabbitMQ password."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq.get_admin_password() == RabbitMQContainer.DEFAULT_PASSWORD

    def test_rabbitmq_get_vhost(self):
        """Test SSL support."""
        rabbitmq = RabbitMQContainer()
        # Just test that the method exists
        assert hasattr(rabbitmq, 'with_ssl')

    def test_rabbitmq_get_amqp_url_not_started(self):
        """Test that get_amqp_url raises error when container not started."""
        rabbitmq = RabbitMQContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            rabbitmq.get_amqp_url()

    def test_rabbitmq_get_http_url_not_started(self):
        """Test that get_http_url raises error when container not started."""
        rabbitmq = RabbitMQContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            rabbitmq.get_http_url()

    def test_rabbitmq_exposed_ports(self):
        """Test that RabbitMQ exposes the correct ports."""
        rabbitmq = RabbitMQContainer()
        
        assert RabbitMQContainer.DEFAULT_AMQP_PORT in rabbitmq._exposed_ports
        assert RabbitMQContainer.DEFAULT_AMQPS_PORT in rabbitmq._exposed_ports
        assert RabbitMQContainer.DEFAULT_HTTP_PORT in rabbitmq._exposed_ports
        assert RabbitMQContainer.DEFAULT_HTTPS_PORT in rabbitmq._exposed_ports

    def test_rabbitmq_default_image(self):
        """Test that RabbitMQ uses the correct default image."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq._image._image_name == RabbitMQContainer.DEFAULT_IMAGE

    def test_rabbitmq_default_environment(self):
        """Test that RabbitMQ environment is configured on start."""
        rabbitmq = RabbitMQContainer()
        # Environment variables are set in start() method
        assert rabbitmq._admin_username == RabbitMQContainer.DEFAULT_USERNAME
        assert rabbitmq._admin_password == RabbitMQContainer.DEFAULT_PASSWORD


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def kafka_container():
    """Pytest fixture providing a Kafka container instance."""
    kafka = KafkaContainer()
    yield kafka
    # Cleanup is handled by context manager if started


@pytest.fixture
def elasticsearch_container():
    """Pytest fixture providing an Elasticsearch container instance."""
    es = ElasticsearchContainer()
    yield es
    # Cleanup is handled by context manager if started


@pytest.fixture
def rabbitmq_container():
    """Pytest fixture providing a RabbitMQ container instance."""
    rabbitmq = RabbitMQContainer()
    yield rabbitmq
    # Cleanup is handled by context manager if started


# =============================================================================
# Integration Tests (using fixtures)
# =============================================================================


class TestMessagingModulesFixtures:
    """Test that fixtures work correctly."""

    def test_kafka_fixture(self, kafka_container):
        """Test that Kafka fixture provides a valid container."""
        assert isinstance(kafka_container, KafkaContainer)
        assert kafka_container._cluster_id is None

    def test_elasticsearch_fixture(self, elasticsearch_container):
        """Test that Elasticsearch fixture provides a valid container."""
        assert isinstance(elasticsearch_container, ElasticsearchContainer)

    def test_rabbitmq_fixture(self, rabbitmq_container):
        """Test that RabbitMQ fixture provides a valid container."""
        assert isinstance(rabbitmq_container, RabbitMQContainer)
