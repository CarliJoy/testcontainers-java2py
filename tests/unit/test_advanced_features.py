"""
Tests for advanced container features: networks, dependencies, file copying, and Socat.
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import tempfile
import os

from testcontainers.core.network import Network, NetworkImpl, new_network, SHARED
from testcontainers.core.generic_container import GenericContainer
from testcontainers.core.socat_container import SocatContainer


class TestNetwork:
    """Tests for Network class."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.networks = Mock()
        return client

    def test_network_creation(self, mock_client):
        """Test network creation."""
        mock_network = Mock()
        mock_network.id = "net123"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                network = NetworkImpl(name="test-network")
                net_id = network.get_id()

                assert net_id == "net123"
                assert mock_client.networks.create.called
                call_kwargs = mock_client.networks.create.call_args[1]
                assert call_kwargs["name"] == "test-network"
                assert call_kwargs["check_duplicate"] is True

    def test_network_with_driver(self, mock_client):
        """Test network with custom driver."""
        mock_network = Mock()
        mock_network.id = "net456"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                network = NetworkImpl(driver="overlay")
                network.get_id()

                call_kwargs = mock_client.networks.create.call_args[1]
                assert call_kwargs["driver"] == "overlay"

    def test_network_with_ipv6(self, mock_client):
        """Test network with IPv6 enabled."""
        mock_network = Mock()
        mock_network.id = "net789"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                network = NetworkImpl(enable_ipv6=True)
                network.get_id()

                call_kwargs = mock_client.networks.create.call_args[1]
                assert call_kwargs["enable_ipv6"] is True

    def test_network_lazy_initialization(self, mock_client):
        """Test network lazy initialization."""
        mock_network = Mock()
        mock_network.id = "netlazy"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                network = NetworkImpl()
                
                # Network not created yet
                assert not mock_client.networks.create.called
                
                # Access ID triggers creation
                net_id = network.get_id()
                assert net_id == "netlazy"
                assert mock_client.networks.create.called
                
                # Subsequent calls don't recreate
                mock_client.networks.create.reset_mock()
                net_id2 = network.get_id()
                assert net_id2 == "netlazy"
                assert not mock_client.networks.create.called

    def test_network_close(self, mock_client):
        """Test network cleanup."""
        mock_network = Mock()
        mock_network.id = "netclose"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                network = NetworkImpl()
                network.get_id()
                
                network.close()
                assert mock_network.remove.called

    def test_network_context_manager(self, mock_client):
        """Test network as context manager."""
        mock_network = Mock()
        mock_network.id = "netctx"
        mock_client.networks.create.return_value = mock_network

        mock_factory = Mock()
        mock_factory.client.return_value = mock_client
        
        with patch('testcontainers.core.network.DockerClientFactory.instance', return_value=mock_factory):
            with patch('testcontainers.core.network.DockerClientFactory.marker_labels', return_value={}):
                with NetworkImpl() as network:
                    net_id = network.get_id()
                    assert net_id == "netctx"
                
                # Should be closed after context
                assert mock_network.remove.called

    def test_shared_network_cannot_be_closed(self):
        """Test that SHARED network cannot be closed by users."""
        # SHARED should not raise on close
        SHARED.close()
        # This is a no-op, just ensure it doesn't error

    def test_new_network_function(self, mock_client):
        """Test new_network helper function."""
        mock_network = Mock()
        mock_network.id = "netnew"
        mock_client.networks.create.return_value = mock_network

        # Don't actually create network, just test the function creates the right object
        network = new_network(name="custom", driver="bridge")
        assert isinstance(network, NetworkImpl)
        assert network._name == "custom"
        assert network._driver == "bridge"


class TestGenericContainerNetworking:
    """Tests for GenericContainer networking features."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        return client

    @pytest.fixture
    def mock_network(self):
        """Mock network."""
        network = Mock(spec=Network)
        network.get_id.return_value = "net123"
        return network

    def test_with_network(self, mock_client, mock_network):
        """Test attaching container to network."""
        container = GenericContainer("test:latest", docker_client=mock_client)
        result = container.with_network(mock_network)
        
        assert result is container
        assert container._network is mock_network

    def test_with_network_aliases(self, mock_client):
        """Test setting network aliases."""
        container = GenericContainer("test:latest", docker_client=mock_client)
        result = container.with_network_aliases("alias1", "alias2")
        
        assert result is container
        assert container._network_aliases == ["alias1", "alias2"]

    @patch('testcontainers.images.remote_image.RemoteDockerImage.resolve')
    def test_start_with_network(self, mock_resolve, mock_client, mock_network):
        """Test starting container with network."""
        mock_resolve.return_value = "test:latest"
        mock_container = Mock()
        mock_container.id = "container123"
        mock_container.status = "running"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        mock_client.containers.create.return_value = mock_container

        container = GenericContainer("test:latest", docker_client=mock_client)
        container.with_network(mock_network)
        container.with_network_aliases("alias1")
        
        with patch('testcontainers.waiting.port.HostPortWaitStrategy.wait_until_ready'):
            container.start()

        # Check that network was used in container creation
        create_kwargs = mock_client.containers.create.call_args[1]
        assert create_kwargs["network"] == "net123"
        assert "networking_config" in create_kwargs
        assert create_kwargs["networking_config"]["net123"]["Aliases"] == ["alias1"]


class TestGenericContainerDependencies:
    """Tests for container dependencies."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        return client

    def test_depends_on(self, mock_client):
        """Test adding dependencies."""
        container1 = GenericContainer("test1:latest", docker_client=mock_client)
        container2 = GenericContainer("test2:latest", docker_client=mock_client)
        container3 = GenericContainer("test3:latest", docker_client=mock_client)
        
        result = container3.depends_on(container1, container2)
        
        assert result is container3
        assert len(container3._dependencies) == 2
        assert container1 in container3._dependencies
        assert container2 in container3._dependencies

    @patch('testcontainers.images.remote_image.RemoteDockerImage.resolve')
    def test_start_starts_dependencies(self, mock_resolve, mock_client):
        """Test that starting container starts its dependencies."""
        mock_resolve.return_value = "test:latest"
        mock_container = Mock()
        mock_container.id = "container123"
        mock_container.status = "running"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        mock_client.containers.create.return_value = mock_container

        # Create dependency
        dependency = Mock(spec=GenericContainer)
        dependency.is_running.return_value = False
        dependency.start.return_value = dependency

        # Create main container with dependency
        container = GenericContainer("test:latest", docker_client=mock_client)
        container.depends_on(dependency)

        with patch('testcontainers.waiting.port.HostPortWaitStrategy.wait_until_ready'):
            container.start()

        # Dependency should be started
        assert dependency.start.called


class TestGenericContainerFileCopying:
    """Tests for file copying operations."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        return client

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_with_copy_file_to_container(self, mock_client):
        """Test adding file copy configuration."""
        container = GenericContainer("test:latest", docker_client=mock_client)
        result = container.with_copy_file_to_container("/host/file", "/container/file")
        
        assert result is container
        assert "/host/file" in container._copy_to_container
        assert container._copy_to_container["/host/file"] == "/container/file"

    @patch('testcontainers.images.remote_image.RemoteDockerImage.resolve')
    def test_copy_files_on_start(self, mock_resolve, mock_client, temp_file):
        """Test that files are copied when container starts."""
        mock_resolve.return_value = "test:latest"
        mock_container = Mock()
        mock_container.id = "container123"
        mock_container.status = "running"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        mock_client.containers.create.return_value = mock_container

        container = GenericContainer("test:latest", docker_client=mock_client)
        container.with_copy_file_to_container(temp_file, "/app/test.txt")

        with patch('testcontainers.waiting.port.HostPortWaitStrategy.wait_until_ready'):
            with patch.object(container, 'copy_file_to_container') as mock_copy:
                container.start()
                
                # Should have called copy
                mock_copy.assert_called_once_with(temp_file, "/app/test.txt")

    def test_copy_file_to_container_not_started(self, mock_client):
        """Test copy file to container fails when not started."""
        container = GenericContainer("test:latest", docker_client=mock_client)
        
        with pytest.raises(RuntimeError, match="Container not started"):
            container.copy_file_to_container("/host/file", "/container/file")

    def test_copy_file_from_container_not_started(self, mock_client):
        """Test copy file from container fails when not started."""
        container = GenericContainer("test:latest", docker_client=mock_client)
        
        with pytest.raises(RuntimeError, match="Container not started"):
            container.copy_file_from_container("/container/file", "/host/file")


class TestGenericContainerModifiers:
    """Tests for container creation modifiers."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        return client

    def test_with_create_container_modifier(self, mock_client):
        """Test adding container modifier."""
        def modifier(kwargs):
            kwargs["hostname"] = "custom-host"
            return kwargs

        container = GenericContainer("test:latest", docker_client=mock_client)
        result = container.with_create_container_modifier(modifier)
        
        assert result is container
        assert len(container._create_container_modifiers) == 1

    @patch('testcontainers.images.remote_image.RemoteDockerImage.resolve')
    def test_modifier_applied_on_create(self, mock_resolve, mock_client):
        """Test that modifiers are applied during container creation."""
        mock_resolve.return_value = "test:latest"
        mock_container = Mock()
        mock_container.id = "container123"
        mock_container.status = "running"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        mock_client.containers.create.return_value = mock_container

        def modifier(kwargs):
            kwargs["hostname"] = "custom-host"
            return kwargs

        container = GenericContainer("test:latest", docker_client=mock_client)
        container.with_create_container_modifier(modifier)

        with patch('testcontainers.waiting.port.HostPortWaitStrategy.wait_until_ready'):
            container.start()

        # Check that modifier was applied
        create_kwargs = mock_client.containers.create.call_args[1]
        assert create_kwargs["hostname"] == "custom-host"


class TestSocatContainer:
    """Tests for SocatContainer."""

    @pytest.fixture
    def mock_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        return client

    def test_socat_init(self, mock_client):
        """Test SocatContainer initialization."""
        socat = SocatContainer()
        assert socat._image._image_name == SocatContainer.DEFAULT_IMAGE
        assert len(socat._targets) == 0

    def test_socat_with_target(self, mock_client):
        """Test adding target to socat."""
        socat = SocatContainer()
        result = socat.with_target(6379, "redis-host")
        
        assert result is socat
        assert 6379 in socat._targets
        assert socat._targets[6379] == "redis-host:6379"
        assert 6379 in socat._exposed_ports

    def test_socat_with_target_different_ports(self, mock_client):
        """Test adding target with different internal port."""
        socat = SocatContainer()
        result = socat.with_target(8080, "web-host", 80)
        
        assert result is socat
        assert 8080 in socat._targets
        assert socat._targets[8080] == "web-host:80"

    def test_socat_multiple_targets(self, mock_client):
        """Test adding multiple targets."""
        socat = SocatContainer()
        socat.with_target(6379, "redis")
        socat.with_target(5432, "postgres")
        
        assert len(socat._targets) == 2
        assert socat._targets[6379] == "redis:6379"
        assert socat._targets[5432] == "postgres:5432"

    @patch('testcontainers.images.remote_image.RemoteDockerImage.resolve')
    def test_socat_start_builds_command(self, mock_resolve, mock_client):
        """Test that socat start builds correct command."""
        mock_resolve.return_value = SocatContainer.DEFAULT_IMAGE
        mock_container = Mock()
        mock_container.id = "socat123"
        mock_container.status = "running"
        mock_container.attrs = {"NetworkSettings": {"Ports": {}}}
        mock_client.containers.create.return_value = mock_container

        socat = SocatContainer()
        socat._docker_client = mock_client
        socat.with_target(6379, "redis")

        with patch('testcontainers.waiting.port.HostPortWaitStrategy.wait_until_ready'):
            socat.start()

        # Check command was built correctly
        assert socat._command is not None
        assert isinstance(socat._command, list)
        assert socat._command[0] == "-c"
        assert "socat TCP-LISTEN:6379,fork,reuseaddr TCP:redis:6379" in socat._command[1]

    def test_socat_start_without_targets_fails(self, mock_client):
        """Test that socat start fails without targets."""
        socat = SocatContainer()
        socat._docker_client = mock_client

        with pytest.raises(ValueError, match="No targets configured"):
            socat.start()
