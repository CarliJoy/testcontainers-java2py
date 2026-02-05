"""
Comprehensive tests for search and message queue container modules.

This module tests the SolrContainer, PulsarContainer, NATSContainer,
ActiveMQContainer, and ChromaDBContainer implementations.
"""

from __future__ import annotations

import pytest
from testcontainers.modules.solr import SolrContainer
from testcontainers.modules.pulsar import PulsarContainer
from testcontainers.modules.nats import NATSContainer
from testcontainers.modules.activemq import ActiveMQContainer
from testcontainers.modules.chromadb import ChromaDBContainer


# =============================================================================
# Solr Container Tests
# =============================================================================


class TestSolrContainer:
    """Test suite for SolrContainer."""

    def test_solr_container_initialization(self):
        """Test that Solr container can be initialized with default settings."""
        solr = SolrContainer()
        assert solr._port == SolrContainer.DEFAULT_PORT
        assert solr._collection is None
        assert solr._zookeeper_host is None

    def test_solr_container_with_custom_image(self):
        """Test that Solr container can be initialized with a custom image."""
        custom_image = "solr:9.4.0"
        solr = SolrContainer(custom_image)
        assert solr._image._image_name == custom_image

    def test_solr_with_collection(self):
        """Test that collection can be set using fluent API."""
        solr = SolrContainer()
        collection = "test_collection"
        result = solr.with_collection(collection)

        assert result is solr  # Fluent API returns self
        assert solr._collection == collection

    def test_solr_with_zookeeper(self):
        """Test that Zookeeper host can be set using fluent API."""
        solr = SolrContainer()
        zk_host = "zookeeper:2181"
        result = solr.with_zookeeper(zk_host)

        assert result is solr  # Fluent API returns self
        assert solr._zookeeper_host == zk_host

    def test_solr_get_solr_url_not_started(self):
        """Test that get_solr_url raises error when container not started."""
        solr = SolrContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            solr.get_solr_url()

    def test_solr_exposed_ports(self):
        """Test that Solr exposes the correct ports."""
        solr = SolrContainer()
        assert SolrContainer.DEFAULT_PORT in solr._exposed_ports

    def test_solr_default_image(self):
        """Test that Solr uses the correct default image."""
        solr = SolrContainer()
        assert solr._image._image_name == SolrContainer.DEFAULT_IMAGE

    def test_solr_command_set(self):
        """Test that Solr container has the correct command."""
        solr = SolrContainer()
        # Command should be set to start Solr in cloud mode
        assert solr._command == ["solr", "start", "-f", "-c"]


# =============================================================================
# Pulsar Container Tests
# =============================================================================


class TestPulsarContainer:
    """Test suite for PulsarContainer."""

    def test_pulsar_container_initialization(self):
        """Test that Pulsar container can be initialized with default settings."""
        pulsar = PulsarContainer()
        assert pulsar._broker_port == PulsarContainer.DEFAULT_BROKER_PORT
        assert pulsar._http_port == PulsarContainer.DEFAULT_HTTP_PORT

    def test_pulsar_container_with_custom_image(self):
        """Test that Pulsar container can be initialized with a custom image."""
        custom_image = "apachepulsar/pulsar:3.1.0"
        pulsar = PulsarContainer(custom_image)
        assert pulsar._image._image_name == custom_image

    def test_pulsar_get_pulsar_broker_url_not_started(self):
        """Test that get_pulsar_broker_url raises error when container not started."""
        pulsar = PulsarContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            pulsar.get_pulsar_broker_url()

    def test_pulsar_get_http_service_url_not_started(self):
        """Test that get_http_service_url raises error when container not started."""
        pulsar = PulsarContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            pulsar.get_http_service_url()

    def test_pulsar_exposed_ports(self):
        """Test that Pulsar exposes the correct ports."""
        pulsar = PulsarContainer()

        assert PulsarContainer.DEFAULT_BROKER_PORT in pulsar._exposed_ports
        assert PulsarContainer.DEFAULT_HTTP_PORT in pulsar._exposed_ports

    def test_pulsar_default_image(self):
        """Test that Pulsar uses the correct default image."""
        pulsar = PulsarContainer()
        assert pulsar._image._image_name == PulsarContainer.DEFAULT_IMAGE

    def test_pulsar_command_set(self):
        """Test that Pulsar container has the correct command."""
        pulsar = PulsarContainer()
        assert pulsar._command == ["bin/pulsar", "standalone"]


# =============================================================================
# NATS Container Tests
# =============================================================================


class TestNATSContainer:
    """Test suite for NATSContainer."""

    def test_nats_container_initialization(self):
        """Test that NATS container can be initialized with default settings."""
        nats = NATSContainer()
        assert nats._client_port == NATSContainer.DEFAULT_CLIENT_PORT
        assert nats._monitoring_port == NATSContainer.DEFAULT_MONITORING_PORT

    def test_nats_container_with_custom_image(self):
        """Test that NATS container can be initialized with a custom image."""
        custom_image = "nats:2.10.0"
        nats = NATSContainer(custom_image)
        assert nats._image._image_name == custom_image

    def test_nats_get_connection_url_not_started(self):
        """Test that get_connection_url raises error when container not started."""
        nats = NATSContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            nats.get_connection_url()

    def test_nats_get_monitoring_url_not_started(self):
        """Test that get_monitoring_url raises error when container not started."""
        nats = NATSContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            nats.get_monitoring_url()

    def test_nats_exposed_ports(self):
        """Test that NATS exposes the correct ports."""
        nats = NATSContainer()

        assert NATSContainer.DEFAULT_CLIENT_PORT in nats._exposed_ports
        assert NATSContainer.DEFAULT_MONITORING_PORT in nats._exposed_ports

    def test_nats_default_image(self):
        """Test that NATS uses the correct default image."""
        nats = NATSContainer()
        assert nats._image._image_name == NATSContainer.DEFAULT_IMAGE


# =============================================================================
# ActiveMQ Container Tests
# =============================================================================


class TestActiveMQContainer:
    """Test suite for ActiveMQContainer."""

    def test_activemq_container_initialization(self):
        """Test that ActiveMQ container can be initialized with default settings."""
        activemq = ActiveMQContainer()
        assert activemq._openwire_port == ActiveMQContainer.DEFAULT_OPENWIRE_PORT
        assert activemq._web_console_port == ActiveMQContainer.DEFAULT_WEB_CONSOLE_PORT
        assert activemq._username == ActiveMQContainer.DEFAULT_USERNAME
        assert activemq._password == ActiveMQContainer.DEFAULT_PASSWORD

    def test_activemq_container_with_custom_image(self):
        """Test that ActiveMQ container can be initialized with a custom image."""
        custom_image = "apache/activemq-classic:5.18.0"
        activemq = ActiveMQContainer(custom_image)
        assert activemq._image._image_name == custom_image

    def test_activemq_with_credentials(self):
        """Test that credentials can be set using fluent API."""
        activemq = ActiveMQContainer()
        username = "myuser"
        password = "mypassword"
        result = activemq.with_credentials(username, password)

        assert result is activemq  # Fluent API returns self
        assert activemq._username == username
        assert activemq._password == password

    def test_activemq_get_username(self):
        """Test getting the username."""
        activemq = ActiveMQContainer()
        assert activemq.get_username() == ActiveMQContainer.DEFAULT_USERNAME

    def test_activemq_get_password(self):
        """Test getting the password."""
        activemq = ActiveMQContainer()
        assert activemq.get_password() == ActiveMQContainer.DEFAULT_PASSWORD

    def test_activemq_get_broker_url_not_started(self):
        """Test that get_broker_url raises error when container not started."""
        activemq = ActiveMQContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            activemq.get_broker_url()

    def test_activemq_get_web_console_url_not_started(self):
        """Test that get_web_console_url raises error when container not started."""
        activemq = ActiveMQContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            activemq.get_web_console_url()

    def test_activemq_exposed_ports(self):
        """Test that ActiveMQ exposes the correct ports."""
        activemq = ActiveMQContainer()

        assert ActiveMQContainer.DEFAULT_OPENWIRE_PORT in activemq._exposed_ports
        assert ActiveMQContainer.DEFAULT_WEB_CONSOLE_PORT in activemq._exposed_ports

    def test_activemq_default_image(self):
        """Test that ActiveMQ uses the correct default image."""
        activemq = ActiveMQContainer()
        assert activemq._image._image_name == ActiveMQContainer.DEFAULT_IMAGE


# =============================================================================
# ChromaDB Container Tests
# =============================================================================


class TestChromaDBContainer:
    """Test suite for ChromaDBContainer."""

    def test_chromadb_container_initialization(self):
        """Test that ChromaDB container can be initialized with default settings."""
        chroma = ChromaDBContainer()
        assert chroma._port == ChromaDBContainer.DEFAULT_PORT
        assert chroma._auth_token is None

    def test_chromadb_container_with_custom_image(self):
        """Test that ChromaDB container can be initialized with a custom image."""
        custom_image = "chromadb/chroma:0.4.0"
        chroma = ChromaDBContainer(custom_image)
        assert chroma._image._image_name == custom_image

    def test_chromadb_with_auth_token(self):
        """Test that auth token can be set using fluent API."""
        chroma = ChromaDBContainer()
        token = "my-secret-token"
        result = chroma.with_auth_token(token)

        assert result is chroma  # Fluent API returns self
        assert chroma._auth_token == token

    def test_chromadb_get_auth_token(self):
        """Test getting the auth token."""
        chroma = ChromaDBContainer()
        token = "test-token-123"
        chroma.with_auth_token(token)

        assert chroma.get_auth_token() == token

    def test_chromadb_get_auth_token_default(self):
        """Test that auth token is None when not set."""
        chroma = ChromaDBContainer()
        assert chroma.get_auth_token() is None

    def test_chromadb_get_url_not_started(self):
        """Test that get_url raises error when container not started."""
        chroma = ChromaDBContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            chroma.get_url()

    def test_chromadb_exposed_ports(self):
        """Test that ChromaDB exposes the correct ports."""
        chroma = ChromaDBContainer()
        assert ChromaDBContainer.DEFAULT_PORT in chroma._exposed_ports

    def test_chromadb_default_image(self):
        """Test that ChromaDB uses the correct default image."""
        chroma = ChromaDBContainer()
        assert chroma._image._image_name == ChromaDBContainer.DEFAULT_IMAGE
