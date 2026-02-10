"""Tests for Qdrant, Weaviate, MockServer, and Toxiproxy container modules."""

from __future__ import annotations

import pytest
from testcontainers.modules.qdrant import QdrantContainer
from testcontainers.modules.weaviate import WeaviateContainer
from testcontainers.modules.mockserver import MockServerContainer
from testcontainers.modules.toxiproxy import ToxiproxyContainer


# Qdrant Tests

class TestQdrantContainer:
    """Tests for QdrantContainer."""

    def test_qdrant_init_defaults(self):
        """Test Qdrant container initialization with defaults."""
        qdrant = QdrantContainer()

        assert qdrant._rest_port == 6333
        assert qdrant._grpc_port == 6334
        assert qdrant._api_key is None
        assert 6333 in qdrant._exposed_ports
        assert 6334 in qdrant._exposed_ports

    def test_qdrant_init_custom_image(self):
        """Test Qdrant container initialization with custom image."""
        qdrant = QdrantContainer(image="qdrant/qdrant:v1.5.0")

        assert qdrant._image.image_name == "qdrant/qdrant:v1.5.0"

    def test_qdrant_with_api_key(self):
        """Test setting API key with fluent API."""
        qdrant = QdrantContainer()
        result = qdrant.with_api_key("my-secret-key")

        assert result is qdrant
        assert qdrant._api_key == "my-secret-key"
        assert qdrant._env["QDRANT__SERVICE__API_KEY"] == "my-secret-key"

    def test_qdrant_with_config_file(self):
        """Test setting config file with fluent API."""
        qdrant = QdrantContainer()
        result = qdrant.with_config_file("/path/to/config.yaml")

        assert result is qdrant

    def test_qdrant_get_rest_url(self, monkeypatch):
        """Test getting REST API URL."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        qdrant = QdrantContainer()
        qdrant._container = True  # Mock container started
        url = qdrant.get_rest_url()

        assert url == "http://localhost:32768"

    def test_qdrant_get_rest_url_not_started(self):
        """Test getting REST URL when container not started."""
        qdrant = QdrantContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            qdrant.get_rest_url()

    def test_qdrant_get_rest_port(self, monkeypatch):
        """Test getting REST port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        qdrant = QdrantContainer()
        port = qdrant.get_rest_port()

        assert port == 32768

    def test_qdrant_get_grpc_port(self, monkeypatch):
        """Test getting gRPC port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32769
        )

        qdrant = QdrantContainer()
        port = qdrant.get_grpc_port()

        assert port == 32769

    def test_qdrant_get_grpc_host_address(self, monkeypatch):
        """Test getting gRPC host address."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32769
        )

        qdrant = QdrantContainer()
        address = qdrant.get_grpc_host_address()

        assert address == "localhost:32769"

    def test_qdrant_get_api_key(self):
        """Test getting API key."""
        qdrant = QdrantContainer()
        assert qdrant.get_api_key() is None

        qdrant.with_api_key("test-key")
        assert qdrant.get_api_key() == "test-key"


# Weaviate Tests

class TestWeaviateContainer:
    """Tests for WeaviateContainer."""

    def test_weaviate_init_defaults(self):
        """Test Weaviate container initialization with defaults."""
        weaviate = WeaviateContainer()

        assert weaviate._http_port == 8080
        assert weaviate._grpc_port == 50051
        assert 8080 in weaviate._exposed_ports
        assert 50051 in weaviate._exposed_ports
        assert weaviate._env["AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED"] == "true"
        assert weaviate._env["PERSISTENCE_DATA_PATH"] == "/var/lib/weaviate"

    def test_weaviate_init_custom_image(self):
        """Test Weaviate container initialization with custom image."""
        weaviate = WeaviateContainer(image="semitechnologies/weaviate:1.22.0")

        assert weaviate._image.image_name == "semitechnologies/weaviate:1.22.0"

    def test_weaviate_with_env(self):
        """Test setting environment variable with fluent API."""
        weaviate = WeaviateContainer()
        result = weaviate.with_env("TEST_KEY", "TEST_VALUE")

        assert result is weaviate
        assert weaviate._env["TEST_KEY"] == "TEST_VALUE"

    def test_weaviate_get_http_url(self, monkeypatch):
        """Test getting HTTP URL."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        weaviate = WeaviateContainer()
        weaviate._container = True  # Mock container started
        url = weaviate.get_http_url()

        assert url == "http://localhost:32768"

    def test_weaviate_get_http_url_not_started(self):
        """Test getting HTTP URL when container not started."""
        weaviate = WeaviateContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            weaviate.get_http_url()

    def test_weaviate_get_http_host_address(self, monkeypatch):
        """Test getting HTTP host address."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        weaviate = WeaviateContainer()
        address = weaviate.get_http_host_address()

        assert address == "localhost:32768"

    def test_weaviate_get_http_port(self, monkeypatch):
        """Test getting HTTP port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        weaviate = WeaviateContainer()
        port = weaviate.get_http_port()

        assert port == 32768

    def test_weaviate_get_grpc_port(self, monkeypatch):
        """Test getting gRPC port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32769
        )

        weaviate = WeaviateContainer()
        port = weaviate.get_grpc_port()

        assert port == 32769

    def test_weaviate_get_grpc_host_address(self, monkeypatch):
        """Test getting gRPC host address."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32769
        )

        weaviate = WeaviateContainer()
        address = weaviate.get_grpc_host_address()

        assert address == "localhost:32769"


# MockServer Tests

class TestMockServerContainer:
    """Tests for MockServerContainer."""

    def test_mockserver_init_defaults(self):
        """Test MockServer container initialization with defaults."""
        mockserver = MockServerContainer()

        assert mockserver._port == 1080
        assert 1080 in mockserver._exposed_ports

    def test_mockserver_init_custom_image(self):
        """Test MockServer container initialization with custom image."""
        mockserver = MockServerContainer(image="mockserver/mockserver:5.15.0")

        assert mockserver._image.image_name == "mockserver/mockserver:5.15.0"

    def test_mockserver_get_endpoint(self, monkeypatch):
        """Test getting HTTP endpoint."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        mockserver = MockServerContainer()
        mockserver._container = True  # Mock container started
        endpoint = mockserver.get_endpoint()

        assert endpoint == "http://localhost:32768"

    def test_mockserver_get_endpoint_not_started(self):
        """Test getting endpoint when container not started."""
        mockserver = MockServerContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            mockserver.get_endpoint()

    def test_mockserver_get_secure_endpoint(self, monkeypatch):
        """Test getting HTTPS endpoint."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        mockserver = MockServerContainer()
        mockserver._container = True  # Mock container started
        endpoint = mockserver.get_secure_endpoint()

        assert endpoint == "https://localhost:32768"

    def test_mockserver_get_secure_endpoint_not_started(self):
        """Test getting secure endpoint when container not started."""
        mockserver = MockServerContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            mockserver.get_secure_endpoint()

    def test_mockserver_get_server_port(self, monkeypatch):
        """Test getting server port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        mockserver = MockServerContainer()
        port = mockserver.get_server_port()

        assert port == 32768

    def test_mockserver_get_url(self, monkeypatch):
        """Test getting URL (alias for get_endpoint)."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        mockserver = MockServerContainer()
        mockserver._container = True  # Mock container started
        url = mockserver.get_url()

        assert url == "http://localhost:32768"


# Toxiproxy Tests

class TestToxiproxyContainer:
    """Tests for ToxiproxyContainer."""

    def test_toxiproxy_init_defaults(self):
        """Test Toxiproxy container initialization with defaults."""
        toxiproxy = ToxiproxyContainer()

        assert toxiproxy._control_port == 8474
        assert 8474 in toxiproxy._exposed_ports
        # Check that proxied ports are exposed
        assert 8666 in toxiproxy._exposed_ports
        assert 8697 in toxiproxy._exposed_ports

    def test_toxiproxy_init_custom_image(self):
        """Test Toxiproxy container initialization with custom image."""
        toxiproxy = ToxiproxyContainer(image="ghcr.io/shopify/toxiproxy:2.5.0")

        assert toxiproxy._image.image_name == "ghcr.io/shopify/toxiproxy:2.5.0"

    def test_toxiproxy_get_control_port(self, monkeypatch):
        """Test getting control port."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        toxiproxy = ToxiproxyContainer()
        port = toxiproxy.get_control_port()

        assert port == 32768

    def test_toxiproxy_get_control_url(self, monkeypatch):
        """Test getting control URL."""
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_host",
            lambda self: "localhost"
        )
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            lambda self, port: 32768
        )

        toxiproxy = ToxiproxyContainer()
        toxiproxy._container = True  # Mock container started
        url = toxiproxy.get_control_url()

        assert url == "http://localhost:32768"

    def test_toxiproxy_get_control_url_not_started(self):
        """Test getting control URL when container not started."""
        toxiproxy = ToxiproxyContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            toxiproxy.get_control_url()

    def test_toxiproxy_get_proxy_port(self, monkeypatch):
        """Test getting proxy port."""
        call_tracker = {"called_with": None}
        
        def mock_get_mapped_port(self, port):
            call_tracker["called_with"] = port
            return 32769
        
        monkeypatch.setattr(
            "testcontainers.core.generic_container.GenericContainer.get_mapped_port",
            mock_get_mapped_port
        )

        toxiproxy = ToxiproxyContainer()
        port = toxiproxy.get_proxy_port(8666)

        assert port == 32769
        assert call_tracker["called_with"] == 8666

    def test_toxiproxy_get_proxy_port_invalid_range(self):
        """Test getting proxy port with invalid port number."""
        toxiproxy = ToxiproxyContainer()

        with pytest.raises(ValueError, match="outside the valid range"):
            toxiproxy.get_proxy_port(8665)

        with pytest.raises(ValueError, match="outside the valid range"):
            toxiproxy.get_proxy_port(8698)

    def test_toxiproxy_proxied_ports_range(self):
        """Test that all proxied ports are exposed."""
        toxiproxy = ToxiproxyContainer()

        for port in range(8666, 8698):
            assert port in toxiproxy._exposed_ports
