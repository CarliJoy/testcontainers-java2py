"""
Comprehensive tests for infrastructure container modules.

This module tests the NGINX, LocalStack, MinIO, Vault, and Memcached container implementations.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from testcontainers.modules.nginx import NGINXContainer
from testcontainers.modules.localstack import LocalStackContainer
from testcontainers.modules.minio import MinIOContainer
from testcontainers.modules.vault import VaultContainer
from testcontainers.modules.memcached import MemcachedContainer


# =============================================================================
# NGINX Container Tests
# =============================================================================


class TestNGINXContainer:
    """Test suite for NGINXContainer."""

    def test_nginx_container_initialization(self):
        """Test that NGINX container can be initialized with default settings."""
        nginx = NGINXContainer()
        assert nginx._http_listen_port == 80

    def test_nginx_container_with_custom_image(self):
        """Test that NGINX container can be initialized with a custom image."""
        custom_image = "nginx:alpine"
        nginx = NGINXContainer(custom_image)
        assert nginx._image._image_name == custom_image

    def test_nginx_with_custom_config(self):
        """Test that custom content can be set using fluent API."""
        nginx = NGINXContainer()
        content_path = "/path/to/html"
        result = nginx.with_custom_content(content_path)
        
        assert result is nginx  # Fluent API returns self

    def test_nginx_with_https(self):
        """Test nginx exposed ports."""
        nginx = NGINXContainer()
        
        assert 80 in nginx._exposed_ports

    def test_nginx_get_base_url_with_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Test that get_base_url generates correct URL with mocked container."""
        nginx = NGINXContainer()
        nginx._container = MagicMock()
        
        monkeypatch.setattr(nginx, 'get_host', lambda: 'localhost')
        monkeypatch.setattr(nginx, 'get_mapped_port', lambda port: 80)
        url = nginx.get_base_url("http", 80)
        
        assert url == "http://localhost:80"

    def test_nginx_command_configuration(self):
        """Test nginx container has command set correctly."""
        nginx = NGINXContainer()
        
        assert nginx._command == ["nginx", "-g", "daemon off;"]

    def test_nginx_exposed_ports(self):
        """Test that NGINX exposes the correct ports."""
        nginx = NGINXContainer()
        
        assert 80 in nginx._exposed_ports

    def test_nginx_default_image(self):
        """Test that NGINX uses the correct default image."""
        nginx = NGINXContainer()
        assert "nginx:1.9.4" in nginx._image._image_name


# =============================================================================
# LocalStack Container Tests
# =============================================================================


class TestLocalStackContainer:
    """Test suite for LocalStackContainer."""

    def test_localstack_container_initialization(self):
        """Test that LocalStack container can be initialized with default settings."""
        localstack = LocalStackContainer()
        assert localstack._edge_port == 4566
        assert localstack._enabled_services == []

    def test_localstack_container_with_custom_image(self):
        """Test that LocalStack container can be initialized with a custom image."""
        custom_image = "localstack/localstack:2.0"
        localstack = LocalStackContainer(custom_image)
        assert localstack._image._image_name == custom_image

    def test_localstack_with_services(self):
        """Test that services can be set using fluent API."""
        localstack = LocalStackContainer()
        result = localstack.with_services("s3", "dynamodb", "sqs")
        
        assert result is localstack  # Fluent API returns self
        assert "s3" in localstack._enabled_services
        assert "dynamodb" in localstack._enabled_services

    def test_localstack_with_services_empty(self):
        """Test that empty services list can be set."""
        localstack = LocalStackContainer()
        result = localstack.with_services()
        
        assert result is localstack
        assert localstack._enabled_services == []

    def test_localstack_get_url_with_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Test that get_url generates correct URL with mocked container."""
        localstack = LocalStackContainer()
        localstack._container = MagicMock()
        
        monkeypatch.setattr(localstack, 'get_host', lambda: 'localhost')
        monkeypatch.setattr(localstack, 'get_mapped_port', lambda port: 4566)
        url = localstack.get_url()
        
        assert url == "http://localhost:4566"

    def test_localstack_exposed_ports(self):
        """Test that LocalStack exposes the correct ports."""
        localstack = LocalStackContainer()
        
        assert 4566 in localstack._exposed_ports

    def test_localstack_default_image(self):
        """Test that LocalStack uses the correct default image."""
        localstack = LocalStackContainer()
        assert "localstack/localstack:0.11.2" in localstack._image._image_name


# =============================================================================
# MinIO Container Tests
# =============================================================================


class TestMinIOContainer:
    """Test suite for MinIOContainer."""

    def test_minio_container_initialization(self):
        """Test that MinIO container can be initialized with default settings."""
        minio = MinIOContainer()
        assert minio._api_port == MinIOContainer.DEFAULT_API_PORT
        assert minio._console_port == MinIOContainer.DEFAULT_CONSOLE_PORT
        assert minio._access_key == MinIOContainer.DEFAULT_ACCESS_KEY
        assert minio._secret_key == MinIOContainer.DEFAULT_SECRET_KEY

    def test_minio_container_with_custom_image(self):
        """Test that MinIO container can be initialized with a custom image."""
        custom_image = "minio/minio:RELEASE-2023-12-01T00-00-00Z"
        minio = MinIOContainer(custom_image)
        assert minio._image._image_name == custom_image

    def test_minio_with_credentials(self):
        """Test that credentials can be set using fluent API."""
        minio = MinIOContainer()
        access_key = "myaccesskey"
        secret_key = "mysecretkey123"
        result = minio.with_credentials(access_key, secret_key)
        
        assert result is minio  # Fluent API returns self
        assert minio._access_key == access_key
        assert minio._secret_key == secret_key
        assert minio._env["MINIO_ROOT_USER"] == access_key
        assert minio._env["MINIO_ROOT_PASSWORD"] == secret_key

    def test_minio_get_access_key(self):
        """Test getting the MinIO access key."""
        minio = MinIOContainer()
        assert minio.get_access_key() == MinIOContainer.DEFAULT_ACCESS_KEY

    def test_minio_get_secret_key(self):
        """Test getting the MinIO secret key."""
        minio = MinIOContainer()
        assert minio.get_secret_key() == MinIOContainer.DEFAULT_SECRET_KEY

    def test_minio_get_url_not_started(self):
        """Test that get_url raises error when container not started."""
        minio = MinIOContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            minio.get_url()

    def test_minio_get_console_url_not_started(self):
        """Test that get_console_url raises error when container not started."""
        minio = MinIOContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            minio.get_console_url()

    def test_minio_exposed_ports(self):
        """Test that MinIO exposes the correct ports."""
        minio = MinIOContainer()
        
        assert MinIOContainer.DEFAULT_API_PORT in minio._exposed_ports
        assert MinIOContainer.DEFAULT_CONSOLE_PORT in minio._exposed_ports

    def test_minio_default_image(self):
        """Test that MinIO uses the correct default image."""
        minio = MinIOContainer()
        assert minio._image._image_name == MinIOContainer.DEFAULT_IMAGE

    def test_minio_default_environment(self):
        """Test that MinIO sets correct default environment variables."""
        minio = MinIOContainer()
        
        assert minio._env["MINIO_ROOT_USER"] == MinIOContainer.DEFAULT_ACCESS_KEY
        assert minio._env["MINIO_ROOT_PASSWORD"] == MinIOContainer.DEFAULT_SECRET_KEY


# =============================================================================
# Vault Container Tests
# =============================================================================


class TestVaultContainer:
    """Test suite for VaultContainer."""

    def test_vault_container_initialization(self):
        """Test that Vault container can be initialized with default settings."""
        vault = VaultContainer()
        assert vault._port == VaultContainer.DEFAULT_PORT
        assert vault._root_token == VaultContainer.DEFAULT_ROOT_TOKEN

    def test_vault_container_with_custom_image(self):
        """Test that Vault container can be initialized with a custom image."""
        custom_image = "hashicorp/vault:1.15"
        vault = VaultContainer(custom_image)
        assert vault._image._image_name == custom_image

    def test_vault_with_root_token(self):
        """Test that root token can be set using fluent API."""
        vault = VaultContainer()
        token = "my-custom-token"
        result = vault.with_root_token(token)
        
        assert result is vault  # Fluent API returns self
        assert vault._root_token == token
        assert vault._env["VAULT_DEV_ROOT_TOKEN_ID"] == token

    def test_vault_get_token(self):
        """Test getting the Vault root token."""
        vault = VaultContainer()
        token = "test-token-123"
        vault.with_root_token(token)
        
        assert vault.get_token() == token

    def test_vault_get_token_default(self):
        """Test that default token is returned when not customized."""
        vault = VaultContainer()
        assert vault.get_token() == VaultContainer.DEFAULT_ROOT_TOKEN

    def test_vault_get_url_not_started(self):
        """Test that get_url raises error when container not started."""
        vault = VaultContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            vault.get_url()

    def test_vault_exposed_ports(self):
        """Test that Vault exposes the correct ports."""
        vault = VaultContainer()
        
        assert VaultContainer.DEFAULT_PORT in vault._exposed_ports

    def test_vault_default_image(self):
        """Test that Vault uses the correct default image."""
        vault = VaultContainer()
        assert vault._image._image_name == VaultContainer.DEFAULT_IMAGE

    def test_vault_default_environment(self):
        """Test that Vault sets correct default environment variables."""
        vault = VaultContainer()
        
        assert vault._env["VAULT_DEV_ROOT_TOKEN_ID"] == VaultContainer.DEFAULT_ROOT_TOKEN
        assert vault._env["VAULT_DEV_LISTEN_ADDRESS"] == f"0.0.0.0:{VaultContainer.DEFAULT_PORT}"


# =============================================================================
# Memcached Container Tests
# =============================================================================


class TestMemcachedContainer:
    """Test suite for MemcachedContainer."""

    def test_memcached_container_initialization(self):
        """Test that Memcached container can be initialized with default settings."""
        memcached = MemcachedContainer()
        assert memcached._port == MemcachedContainer.DEFAULT_PORT

    def test_memcached_container_with_custom_image(self):
        """Test that Memcached container can be initialized with a custom image."""
        custom_image = "memcached:1.6-alpine"
        memcached = MemcachedContainer(custom_image)
        assert memcached._image._image_name == custom_image

    def test_memcached_get_connection_url_not_started(self):
        """Test that get_connection_url raises error when container not started."""
        memcached = MemcachedContainer()
        
        with pytest.raises(RuntimeError, match="Container not started"):
            memcached.get_connection_url()

    def test_memcached_exposed_ports(self):
        """Test that Memcached exposes the correct ports."""
        memcached = MemcachedContainer()
        
        assert MemcachedContainer.DEFAULT_PORT in memcached._exposed_ports

    def test_memcached_default_image(self):
        """Test that Memcached uses the correct default image."""
        memcached = MemcachedContainer()
        assert memcached._image._image_name == MemcachedContainer.DEFAULT_IMAGE

    def test_memcached_port_configuration(self):
        """Test that Memcached port is properly configured."""
        memcached = MemcachedContainer()
        assert memcached._port == 11211

    def test_memcached_wait_strategy(self):
        """Test that Memcached has a wait strategy configured."""
        memcached = MemcachedContainer()
        assert memcached._wait_strategy is not None


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def nginx_container():
    """Pytest fixture providing an NGINX container instance."""
    nginx = NGINXContainer()
    yield nginx
    # Cleanup is handled by context manager if started


@pytest.fixture
def localstack_container():
    """Pytest fixture providing a LocalStack container instance."""
    localstack = LocalStackContainer()
    yield localstack
    # Cleanup is handled by context manager if started


@pytest.fixture
def minio_container():
    """Pytest fixture providing a MinIO container instance."""
    minio = MinIOContainer()
    yield minio
    # Cleanup is handled by context manager if started


@pytest.fixture
def vault_container():
    """Pytest fixture providing a Vault container instance."""
    vault = VaultContainer()
    yield vault
    # Cleanup is handled by context manager if started


@pytest.fixture
def memcached_container():
    """Pytest fixture providing a Memcached container instance."""
    memcached = MemcachedContainer()
    yield memcached
    # Cleanup is handled by context manager if started


# =============================================================================
# Integration Tests (using fixtures)
# =============================================================================


class TestInfrastructureModulesFixtures:
    """Test that fixtures work correctly."""

    def test_nginx_fixture(self, nginx_container):
        """Test that NGINX fixture provides a valid container."""
        assert isinstance(nginx_container, NGINXContainer)

    def test_localstack_fixture(self, localstack_container):
        """Test that LocalStack fixture provides a valid container."""
        assert isinstance(localstack_container, LocalStackContainer)
        assert localstack_container._enabled_services == []

    def test_minio_fixture(self, minio_container):
        """Test that MinIO fixture provides a valid container."""
        assert isinstance(minio_container, MinIOContainer)
        assert minio_container._access_key == MinIOContainer.DEFAULT_ACCESS_KEY

    def test_vault_fixture(self, vault_container):
        """Test that Vault fixture provides a valid container."""
        assert isinstance(vault_container, VaultContainer)
        assert vault_container._root_token == VaultContainer.DEFAULT_ROOT_TOKEN

    def test_memcached_fixture(self, memcached_container):
        """Test that Memcached fixture provides a valid container."""
        assert isinstance(memcached_container, MemcachedContainer)
        assert memcached_container._port == MemcachedContainer.DEFAULT_PORT
