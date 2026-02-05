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
        assert kafka._kafka_port == KafkaContainer.DEFAULT_KAFKA_PORT
        assert kafka._internal_kafka_port == KafkaContainer.DEFAULT_INTERNAL_KAFKA_PORT
        assert kafka._cluster_id is None

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
        """Test getting the cluster ID."""
        kafka = KafkaContainer()
        cluster_id = "my-kafka-cluster"
        kafka.with_cluster_id(cluster_id)
        
        assert kafka.get_cluster_id() == cluster_id

    def test_kafka_get_cluster_id_default(self):
        """Test that cluster ID is None when not set."""
        kafka = KafkaContainer()
        assert kafka.get_cluster_id() is None

    def test_kafka_get_bootstrap_servers_not_started(self):
        """Test that get_bootstrap_servers raises error when container not started."""
        kafka = KafkaContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            kafka.get_bootstrap_servers()

    def test_kafka_exposed_ports(self):
        """Test that Kafka exposes the correct ports."""
        kafka = KafkaContainer()
        
        assert KafkaContainer.DEFAULT_KAFKA_PORT in kafka._exposed_ports

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
        assert es._http_port == ElasticsearchContainer.DEFAULT_HTTP_PORT
        assert es._transport_port == ElasticsearchContainer.DEFAULT_TRANSPORT_PORT
        assert es._password is None

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
        
        assert es.get_password() == password

    def test_elasticsearch_get_password_default(self):
        """Test that password is None when not set."""
        es = ElasticsearchContainer()
        assert es.get_password() is None

    def test_elasticsearch_get_username(self):
        """Test getting the Elasticsearch username."""
        es = ElasticsearchContainer()
        assert es.get_username() == ElasticsearchContainer.DEFAULT_USERNAME

    def test_elasticsearch_get_http_url_not_started(self):
        """Test that get_http_url raises error when container not started."""
        es = ElasticsearchContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            es.get_http_url()

    def test_elasticsearch_exposed_ports(self):
        """Test that Elasticsearch exposes the correct ports."""
        es = ElasticsearchContainer()
        
        assert ElasticsearchContainer.DEFAULT_HTTP_PORT in es._exposed_ports
        assert ElasticsearchContainer.DEFAULT_TRANSPORT_PORT in es._exposed_ports

    def test_elasticsearch_default_image(self):
        """Test that Elasticsearch uses the correct default image."""
        es = ElasticsearchContainer()
        assert es._image._image_name == ElasticsearchContainer.DEFAULT_IMAGE

    def test_elasticsearch_default_environment(self):
        """Test that Elasticsearch sets correct default environment variables."""
        es = ElasticsearchContainer()
        
        assert es._env["discovery.type"] == "single-node"
        assert es._env["xpack.security.enabled"] == "false"
        assert "ES_JAVA_OPTS" in es._env


# =============================================================================
# RabbitMQ Container Tests
# =============================================================================


class TestRabbitMQContainer:
    """Test suite for RabbitMQContainer."""

    def test_rabbitmq_container_initialization(self):
        """Test that RabbitMQ container can be initialized with default settings."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq._amqp_port == RabbitMQContainer.DEFAULT_AMQP_PORT
        assert rabbitmq._management_port == RabbitMQContainer.DEFAULT_MANAGEMENT_PORT
        assert rabbitmq._username == RabbitMQContainer.DEFAULT_USERNAME
        assert rabbitmq._password == RabbitMQContainer.DEFAULT_PASSWORD
        assert rabbitmq._vhost == RabbitMQContainer.DEFAULT_VHOST

    def test_rabbitmq_container_with_custom_image(self):
        """Test that RabbitMQ container can be initialized with a custom image."""
        custom_image = "rabbitmq:3.12-management"
        rabbitmq = RabbitMQContainer(custom_image)
        assert rabbitmq._image._image_name == custom_image

    def test_rabbitmq_with_vhost(self):
        """Test that vhost can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        vhost = "myvhost"
        result = rabbitmq.with_vhost(vhost)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._vhost == vhost
        assert rabbitmq._env["RABBITMQ_DEFAULT_VHOST"] == vhost

    def test_rabbitmq_with_username(self):
        """Test that username can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        username = "admin"
        result = rabbitmq.with_username(username)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._username == username
        assert rabbitmq._env["RABBITMQ_DEFAULT_USER"] == username

    def test_rabbitmq_with_password(self):
        """Test that password can be set using fluent API."""
        rabbitmq = RabbitMQContainer()
        password = "secretpass"
        result = rabbitmq.with_password(password)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._password == password
        assert rabbitmq._env["RABBITMQ_DEFAULT_PASS"] == password

    def test_rabbitmq_with_credentials(self):
        """Test that both username and password can be set together."""
        rabbitmq = RabbitMQContainer()
        username = "admin"
        password = "adminpass"
        result = rabbitmq.with_credentials(username, password)
        
        assert result is rabbitmq  # Fluent API returns self
        assert rabbitmq._username == username
        assert rabbitmq._password == password

    def test_rabbitmq_get_username(self):
        """Test getting the RabbitMQ username."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq.get_username() == RabbitMQContainer.DEFAULT_USERNAME

    def test_rabbitmq_get_password(self):
        """Test getting the RabbitMQ password."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq.get_password() == RabbitMQContainer.DEFAULT_PASSWORD

    def test_rabbitmq_get_vhost(self):
        """Test getting the RabbitMQ vhost."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq.get_vhost() == RabbitMQContainer.DEFAULT_VHOST

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
        assert RabbitMQContainer.DEFAULT_MANAGEMENT_PORT in rabbitmq._exposed_ports

    def test_rabbitmq_default_image(self):
        """Test that RabbitMQ uses the correct default image."""
        rabbitmq = RabbitMQContainer()
        assert rabbitmq._image._image_name == RabbitMQContainer.DEFAULT_IMAGE

    def test_rabbitmq_default_environment(self):
        """Test that RabbitMQ sets correct default environment variables."""
        rabbitmq = RabbitMQContainer()
        
        assert rabbitmq._env["RABBITMQ_DEFAULT_USER"] == RabbitMQContainer.DEFAULT_USERNAME
        assert rabbitmq._env["RABBITMQ_DEFAULT_PASS"] == RabbitMQContainer.DEFAULT_PASSWORD
        assert rabbitmq._env["RABBITMQ_DEFAULT_VHOST"] == RabbitMQContainer.DEFAULT_VHOST


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
        assert elasticsearch_container._password is None

    def test_rabbitmq_fixture(self, rabbitmq_container):
        """Test that RabbitMQ fixture provides a valid container."""
        assert isinstance(rabbitmq_container, RabbitMQContainer)
        assert rabbitmq_container._vhost == RabbitMQContainer.DEFAULT_VHOST
