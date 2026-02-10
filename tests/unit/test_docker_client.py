"""Tests for docker_client module."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, MagicMock

from testcontainers.core.docker_client import (
    DockerClientFactory,
    DockerClientWrapper,
    LazyDockerClient,
)


class TestDockerClientWrapper:
    """Tests for DockerClientWrapper class."""

    def test_wrapper_delegates_to_client(self):
        """Test that wrapper delegates attribute access to underlying client."""
        mock_client = Mock()
        mock_client.containers = Mock()
        
        wrapper = DockerClientWrapper(mock_client)
        
        # Access should be delegated
        assert wrapper.containers is mock_client.containers

    def test_wrapper_close_raises_error(self):
        """Test that closing wrapper raises an error."""
        mock_client = Mock()
        wrapper = DockerClientWrapper(mock_client)
        
        with pytest.raises(RuntimeError, match="You should never close the global DockerClient"):
            wrapper.close()

    def test_wrapper_client_property(self):
        """Test client property returns underlying client."""
        mock_client = Mock()
        wrapper = DockerClientWrapper(mock_client)
        
        assert wrapper.client is mock_client


class TestLazyDockerClient:
    """Tests for LazyDockerClient class."""

    def test_lazy_client_defers_initialization(self):
        """Test that lazy client doesn't initialize until accessed."""
        mock_factory = Mock(spec=DockerClientFactory)
        
        lazy_client = LazyDockerClient(mock_factory)
        
        # Factory should not be called yet
        mock_factory.client.assert_not_called()

    def test_lazy_client_initializes_on_access(self):
        """Test that lazy client initializes when accessed."""
        mock_factory = Mock(spec=DockerClientFactory)
        mock_client = Mock()
        mock_client.containers = Mock()
        mock_factory.client.return_value = mock_client
        
        lazy_client = LazyDockerClient(mock_factory)
        
        # Access an attribute - should trigger initialization
        _ = lazy_client.containers
        
        # Factory should have been called
        mock_factory.client.assert_called_once()

    def test_lazy_client_str(self):
        """Test string representation."""
        mock_factory = Mock(spec=DockerClientFactory)
        lazy_client = LazyDockerClient(mock_factory)
        
        assert str(lazy_client) == "LazyDockerClient"


@pytest.fixture
def reset_factory():
    """Fixture to reset factory before and after each test."""
    DockerClientFactory.reset()
    yield
    DockerClientFactory.reset()


class TestDockerClientFactory:
    """Tests for DockerClientFactory class."""

    def test_singleton_instance(self, reset_factory):
        """Test that factory returns same instance."""
        instance1 = DockerClientFactory.instance()
        instance2 = DockerClientFactory.instance()
        
        assert instance1 is instance2

    def test_lazy_client_creation(self, reset_factory):
        """Test lazy client factory method."""
        lazy_client = DockerClientFactory.lazy_client()
        
        assert isinstance(lazy_client, LazyDockerClient)

    def test_marker_labels(self, reset_factory):
        """Test marker labels creation."""
        labels = DockerClientFactory.marker_labels()
        
        assert "org.testcontainers" in labels
        assert labels["org.testcontainers"] == "true"
        assert labels["org.testcontainers.lang"] == "python"
        assert "org.testcontainers.version" in labels

    def test_client_creation_success(self, reset_factory, monkeypatch):
        """Test successful client creation."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.info.return_value = {
            'ServerVersion': '20.10.0',
            'OperatingSystem': 'Linux',
            'MemTotal': 16000000000,
        }
        mock_client.version.return_value = {
            'ApiVersion': '1.41',
        }
        
        mock_from_env = MagicMock(return_value=mock_client)
        monkeypatch.setattr('testcontainers.core.docker_client.docker.from_env', mock_from_env)
        
        factory = DockerClientFactory.instance()
        client = factory.client()
        
        assert client is not None
        mock_from_env.assert_called_once()
        mock_client.ping.assert_called_once()

    def test_client_creation_cached(self, reset_factory, monkeypatch):
        """Test that client is cached after first creation."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.info.return_value = {
            'ServerVersion': '20.10.0',
            'OperatingSystem': 'Linux',
            'MemTotal': 16000000000,
        }
        mock_client.version.return_value = {
            'ApiVersion': '1.41',
        }
        
        mock_from_env = MagicMock(return_value=mock_client)
        monkeypatch.setattr('testcontainers.core.docker_client.docker.from_env', mock_from_env)
        
        factory = DockerClientFactory.instance()
        client1 = factory.client()
        client2 = factory.client()
        
        assert client1 is client2
        # Should only create once
        assert mock_from_env.call_count == 1

    def test_is_docker_available_true(self, reset_factory, monkeypatch):
        """Test is_docker_available returns True when Docker is available."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.info.return_value = {
            'ServerVersion': '20.10.0',
            'OperatingSystem': 'Linux',
            'MemTotal': 16000000000,
        }
        mock_client.version.return_value = {
            'ApiVersion': '1.41',
        }
        
        mock_from_env = MagicMock(return_value=mock_client)
        monkeypatch.setattr('testcontainers.core.docker_client.docker.from_env', mock_from_env)
        
        factory = DockerClientFactory.instance()
        
        assert factory.is_docker_available() is True

    def test_is_docker_available_false(self, reset_factory, monkeypatch):
        """Test is_docker_available returns False when Docker is not available."""
        mock_from_env = MagicMock(side_effect=Exception("Docker not available"))
        monkeypatch.setattr('testcontainers.core.docker_client.docker.from_env', mock_from_env)
        
        factory = DockerClientFactory.instance()
        
        assert factory.is_docker_available() is False

    def test_cached_failure(self, reset_factory, monkeypatch):
        """Test that failures are cached and re-raised."""
        mock_from_env = MagicMock(side_effect=Exception("Docker not available"))
        monkeypatch.setattr('testcontainers.core.docker_client.docker.from_env', mock_from_env)
        
        factory = DockerClientFactory.instance()
        
        # First call should fail
        with pytest.raises(Exception, match="Docker not available"):
            factory.client()
        
        # Second call should raise the same cached exception
        with pytest.raises(Exception, match="Docker not available"):
            factory.client()
        
        # Should only try once
        assert mock_from_env.call_count == 1

    def test_docker_host_ip_localhost_default(self, reset_factory):
        """Test that default Docker host IP is localhost."""
        factory = DockerClientFactory()
        ip = factory._determine_docker_host_ip()
        
        assert ip == 'localhost'

    def test_docker_host_ip_from_env(self, reset_factory, monkeypatch):
        """Test Docker host IP extraction from DOCKER_HOST env var."""
        monkeypatch.setenv('DOCKER_HOST', 'tcp://192.168.1.100:2375')
        factory = DockerClientFactory()
        ip = factory._determine_docker_host_ip()
        
        assert ip == '192.168.1.100'
