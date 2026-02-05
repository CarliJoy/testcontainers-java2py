"""Tests for GenericContainer."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import Mock, MagicMock, patch, call

import pytest

from testcontainers.core import GenericContainer, BindMode
from testcontainers.waiting import HostPortWaitStrategy, LogMessageWaitStrategy
from testcontainers.images import RemoteDockerImage, AlwaysPullPolicy


class TestGenericContainerInit:
    """Tests for GenericContainer initialization."""
    
    def test_init_with_string_image(self):
        """Test initialization with string image name."""
        container = GenericContainer("nginx:latest")
        
        assert isinstance(container._image, RemoteDockerImage)
        assert container._image.image_name == "nginx:latest"
        assert container._container is None
    
    def test_init_with_remote_image(self):
        """Test initialization with RemoteDockerImage."""
        image = RemoteDockerImage("postgres:13")
        container = GenericContainer(image)
        
        assert container._image is image
    
    def test_init_with_custom_client(self):
        """Test initialization with custom Docker client."""
        mock_client = Mock()
        container = GenericContainer("nginx:latest", docker_client=mock_client)
        
        assert container._docker_client is mock_client


class TestGenericContainerFluentAPI:
    """Tests for GenericContainer fluent API."""
    
    def test_with_exposed_ports(self):
        """Test exposing ports."""
        container = GenericContainer("nginx:latest")
        result = container.with_exposed_ports(80, 443)
        
        assert result is container  # Fluent API
        assert 80 in container._exposed_ports
        assert 443 in container._exposed_ports
    
    def test_with_bind_ports(self):
        """Test binding ports."""
        container = GenericContainer("nginx:latest")
        result = container.with_bind_ports(80, 8080)
        
        assert result is container
        assert container._port_bindings[80] == 8080
        assert 80 in container._exposed_ports
    
    def test_with_env(self):
        """Test setting environment variables."""
        container = GenericContainer("postgres:13")
        result = container.with_env("POSTGRES_PASSWORD", "secret")
        
        assert result is container
        assert container._env["POSTGRES_PASSWORD"] == "secret"
    
    def test_with_volume_mapping(self):
        """Test volume mapping."""
        container = GenericContainer("nginx:latest")
        result = container.with_volume_mapping(
            "/host/path",
            "/container/path",
            BindMode.READ_ONLY
        )
        
        assert result is container
        assert "/host/path" in container._volumes
        assert container._volumes["/host/path"]["bind"] == "/container/path"
        assert container._volumes["/host/path"]["mode"] == "ro"
    
    def test_with_command(self):
        """Test command override."""
        container = GenericContainer("alpine:latest")
        result = container.with_command("echo hello")
        
        assert result is container
        assert container._command == "echo hello"
    
    def test_with_command_list(self):
        """Test command override with list."""
        container = GenericContainer("alpine:latest")
        result = container.with_command(["echo", "hello"])
        
        assert result is container
        assert container._command == ["echo", "hello"]
    
    def test_with_entrypoint(self):
        """Test entrypoint override."""
        container = GenericContainer("nginx:latest")
        result = container.with_entrypoint("/bin/sh")
        
        assert result is container
        assert container._entrypoint == "/bin/sh"
    
    def test_with_working_directory(self):
        """Test working directory."""
        container = GenericContainer("alpine:latest")
        result = container.with_working_directory("/app")
        
        assert result is container
        assert container._working_dir == "/app"
    
    def test_with_name(self):
        """Test container name."""
        container = GenericContainer("nginx:latest")
        result = container.with_name("my-nginx")
        
        assert result is container
        assert container._name == "my-nginx"
    
    def test_with_labels(self):
        """Test container labels."""
        container = GenericContainer("nginx:latest")
        result = container.with_labels(app="myapp", version="1.0")
        
        assert result is container
        assert container._labels["app"] == "myapp"
        assert container._labels["version"] == "1.0"
    
    def test_with_network_mode(self):
        """Test network mode."""
        container = GenericContainer("nginx:latest")
        result = container.with_network_mode("host")
        
        assert result is container
        assert container._network_mode == "host"
    
    def test_with_privileged_mode(self):
        """Test privileged mode."""
        container = GenericContainer("nginx:latest")
        result = container.with_privileged_mode()
        
        assert result is container
        assert container._privileged is True
    
    def test_waiting_for(self):
        """Test wait strategy."""
        container = GenericContainer("nginx:latest")
        strategy = LogMessageWaitStrategy().with_regex(".*ready.*")
        result = container.waiting_for(strategy)
        
        assert result is container
        assert container._wait_strategy is strategy


class TestGenericContainerLifecycle:
    """Tests for GenericContainer lifecycle methods."""
    
    @patch('testcontainers.core.generic_container.DockerClientFactory')
    def test_start_creates_and_starts_container(self, mock_factory):
        """Test that start creates and starts the container."""
        # Setup mocks
        mock_client = Mock()
        mock_container = Mock()
        mock_container.id = "test-container-id"
        mock_container.status = "running"
        mock_container.attrs = {
            "NetworkSettings": {
                "Ports": {}
            }
        }
        
        mock_client.containers.create.return_value = mock_container
        mock_factory.lazy_client.return_value = mock_client
        mock_factory.marker_labels.return_value = {"testcontainers": "true"}
        
        # Create container with a mock wait strategy that doesn't wait
        container = GenericContainer("nginx:latest", docker_client=mock_client)
        container._wait_strategy = Mock()
        
        # Mock image resolution
        with patch.object(container._image, 'resolve', return_value="nginx:latest"):
            container.start()
        
        # Verify container was created and started
        assert mock_client.containers.create.called
        assert mock_container.start.called
        assert container._container is mock_container
        assert container._container_id == "test-container-id"
    
    @patch('testcontainers.core.generic_container.DockerClientFactory')
    def test_start_with_port_bindings(self, mock_factory):
        """Test start with port bindings."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.id = "test-id"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        
        mock_client.containers.create.return_value = mock_container
        
        container = GenericContainer("nginx:latest", docker_client=mock_client)
        container.with_bind_ports(80, 8080)
        container._wait_strategy = Mock()
        
        with patch.object(container._image, 'resolve', return_value="nginx:latest"):
            container.start()
        
        # Check that create was called with port bindings
        call_kwargs = mock_client.containers.create.call_args[1]
        assert "80/tcp" in call_kwargs["ports"]
        assert call_kwargs["ports"]["80/tcp"] == 8080
    
    @patch('testcontainers.core.generic_container.DockerClientFactory')
    def test_start_with_environment(self, mock_factory):
        """Test start with environment variables."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.id = "test-id"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        
        mock_client.containers.create.return_value = mock_container
        
        container = GenericContainer("postgres:13", docker_client=mock_client)
        container.with_env("POSTGRES_PASSWORD", "secret")
        container._wait_strategy = Mock()
        
        with patch.object(container._image, 'resolve', return_value="postgres:13"):
            container.start()
        
        # Check environment was passed
        call_kwargs = mock_client.containers.create.call_args[1]
        assert call_kwargs["environment"]["POSTGRES_PASSWORD"] == "secret"
    
    def test_stop_stops_container(self):
        """Test that stop stops the container."""
        mock_container = Mock()
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        container._container_id = "test-id"
        
        container.stop()
        
        assert mock_container.stop.called
    
    def test_stop_without_container(self):
        """Test stop without started container."""
        container = GenericContainer("nginx:latest")
        
        # Should not raise
        container.stop()
    
    def test_remove_removes_container(self):
        """Test that remove removes the container."""
        mock_container = Mock()
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        container._container_id = "test-id"
        
        container.remove()
        
        assert mock_container.remove.called
        assert container._container is None
    
    def test_close_stops_and_removes(self):
        """Test close method."""
        mock_container = Mock()
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        container._container_id = "test-id"
        
        container.close()
        
        assert mock_container.stop.called
        assert mock_container.remove.called


class TestGenericContainerContextManager:
    """Tests for context manager support."""
    
    @patch('testcontainers.core.generic_container.DockerClientFactory')
    def test_context_manager(self, mock_factory):
        """Test using container as context manager."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.id = "test-id"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        
        mock_client.containers.create.return_value = mock_container
        mock_factory.marker_labels.return_value = {}
        
        container = GenericContainer("nginx:latest", docker_client=mock_client)
        container._wait_strategy = Mock()
        
        with patch.object(container._image, 'resolve', return_value="nginx:latest"):
            with container as c:
                assert c is container
                assert c._container is mock_container
        
        # After exiting, container should be stopped and removed
        assert mock_container.stop.called
        assert mock_container.remove.called


class TestGenericContainerMethods:
    """Tests for GenericContainer methods."""
    
    def test_get_container_id(self):
        """Test getting container ID."""
        container = GenericContainer("nginx:latest")
        container._container_id = "abc123"
        
        assert container.get_container_id() == "abc123"
    
    def test_get_container_id_not_started(self):
        """Test getting container ID when not started."""
        container = GenericContainer("nginx:latest")
        
        with pytest.raises(RuntimeError, match="Container not started"):
            container.get_container_id()
    
    def test_get_exposed_port(self):
        """Test getting exposed port."""
        mock_container = Mock()
        mock_container.attrs = {
            "NetworkSettings": {
                "Ports": {
                    "80/tcp": [{"HostPort": "32768"}]
                }
            }
        }
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        port = container.get_exposed_port(80)
        
        assert port == 32768
    
    def test_get_exposed_port_not_mapped(self):
        """Test getting unmapped port."""
        mock_container = Mock()
        mock_container.attrs = {
            "NetworkSettings": {
                "Ports": {
                    "80/tcp": None
                }
            }
        }
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        with pytest.raises(KeyError, match="not mapped"):
            container.get_exposed_port(80)
    
    def test_exec(self):
        """Test executing command."""
        mock_container = Mock()
        mock_container.exec_run.return_value = (0, b"hello world")
        
        container = GenericContainer("alpine:latest")
        container._container = mock_container
        
        result = container.exec("echo hello")
        
        assert result.exit_code == 0
        assert result.stdout == "hello world"
        assert result.stderr == ""
    
    def test_is_running(self):
        """Test checking if running."""
        mock_container = Mock()
        mock_container.status = "running"
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        assert container.is_running() is True
    
    def test_is_running_stopped(self):
        """Test checking if running when stopped."""
        mock_container = Mock()
        mock_container.status = "exited"
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        assert container.is_running() is False
    
    def test_is_healthy(self):
        """Test checking if healthy."""
        mock_container = Mock()
        mock_container.attrs = {
            "State": {
                "Health": {
                    "Status": "healthy"
                }
            }
        }
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        assert container.is_healthy() is True
    
    def test_get_logs(self):
        """Test getting logs."""
        mock_container = Mock()
        mock_container.logs.side_effect = [b"stdout logs", b"stderr logs"]
        
        container = GenericContainer("nginx:latest")
        container._container = mock_container
        
        stdout, stderr = container.get_logs()
        
        assert stdout == b"stdout logs"
        assert stderr == b"stderr logs"
    
    def test_get_host(self):
        """Test getting host."""
        container = GenericContainer("nginx:latest")
        
        assert container.get_host() == "localhost"
