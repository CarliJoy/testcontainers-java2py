"""Tests for container reuse functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

from testcontainers.core import GenericContainer
from testcontainers.config import TestcontainersConfig


@pytest.fixture
def reset_config():
    """Reset configuration before and after each test."""
    TestcontainersConfig.reset()
    yield
    TestcontainersConfig.reset()


@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client."""
    client = Mock()
    
    # Mock containers.create
    mock_container = Mock()
    mock_container.id = "test-container-id"
    mock_container.attrs = {"Id": "test-container-id", "State": {"Running": True}}
    mock_container.start = Mock()
    mock_container.reload = Mock()
    mock_container.stop = Mock()
    mock_container.remove = Mock()
    
    client.containers.create = Mock(return_value=mock_container)
    client.containers.list = Mock(return_value=[])
    client.containers.get = Mock(return_value=mock_container)
    
    return client


class TestContainerReuse:
    """Test container reuse functionality."""
    
    def test_with_reuse_enables_reuse(self):
        """Test that with_reuse() sets the reuse flag."""
        container = GenericContainer("test:latest")
        assert container._should_be_reused is False
        
        container.with_reuse(True)
        assert container._should_be_reused is True
        
        container.with_reuse(False)
        assert container._should_be_reused is False
    
    def test_reuse_disabled_by_default(self, reset_config):
        """Test that reuse is disabled by default."""
        config = TestcontainersConfig.get_instance()
        assert config.environment_supports_reuse() is False
    
    def test_reuse_enabled_via_environment(self, reset_config):
        """Test enabling reuse via environment variable."""
        with patch.dict(os.environ, {"TESTCONTAINERS_REUSE_ENABLE": "true"}):
            TestcontainersConfig.reset()
            config = TestcontainersConfig.get_instance()
            assert config.environment_supports_reuse() is True
    
    def test_reuse_disabled_via_environment(self, reset_config):
        """Test disabling reuse via environment variable."""
        with patch.dict(os.environ, {"TESTCONTAINERS_REUSE_ENABLE": "false"}):
            TestcontainersConfig.reset()
            config = TestcontainersConfig.get_instance()
            assert config.environment_supports_reuse() is False
    
    def test_hash_configuration_consistent(self, mock_docker_client):
        """Test that configuration hash is consistent for same config."""
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        container.with_env("KEY", "value")
        container.with_exposed_ports(8080)
        
        create_kwargs = {
            "image": "test:latest",
            "environment": {"KEY": "value"},
            "ports": {"8080/tcp": None},
        }
        
        hash1 = container._hash_configuration(create_kwargs)
        hash2 = container._hash_configuration(create_kwargs)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest
    
    def test_hash_configuration_different_for_different_config(self, mock_docker_client):
        """Test that configuration hash differs for different configs."""
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        create_kwargs1 = {
            "image": "test:latest",
            "environment": {"KEY": "value1"},
        }
        
        create_kwargs2 = {
            "image": "test:latest",
            "environment": {"KEY": "value2"},
        }
        
        hash1 = container._hash_configuration(create_kwargs1)
        hash2 = container._hash_configuration(create_kwargs2)
        
        assert hash1 != hash2
    
    def test_hash_copied_files_empty(self, mock_docker_client):
        """Test hash of empty copied files."""
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        file_hash = container._hash_copied_files()
        assert len(file_hash) == 64  # SHA-256 hex digest
    
    def test_hash_copied_files_with_file(self, mock_docker_client):
        """Test hash of copied files includes file content."""
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            container.with_copy_file_to_container(temp_file, "/app/test.txt")
            
            hash1 = container._hash_copied_files()
            
            # Modify file content
            with open(temp_file, "w") as f:
                f.write("different content")
            
            hash2 = container._hash_copied_files()
            
            assert hash1 != hash2
        finally:
            os.unlink(temp_file)
    
    def test_hash_copied_files_with_permissions(self, mock_docker_client):
        """Test hash of copied files includes file permissions."""
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            container.with_copy_file_to_container(temp_file, "/app/test.txt")
            
            # Get hash with current permissions
            hash1 = container._hash_copied_files()
            
            # Change permissions
            os.chmod(temp_file, 0o755)
            
            # Get hash after permission change
            hash2 = container._hash_copied_files()
            
            # Hashes should be different
            assert hash1 != hash2
        finally:
            os.unlink(temp_file)
    
    @patch("testcontainers.core.generic_container.DockerClientFactory")
    def test_find_container_for_reuse_finds_existing(self, mock_factory, mock_docker_client):
        """Test finding an existing container for reuse."""
        # Mock existing container
        existing_container = Mock()
        existing_container.id = "existing-container-id"
        mock_docker_client.containers.list = Mock(return_value=[existing_container])
        
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        found_id = container._find_container_for_reuse("test-hash")
        
        assert found_id == "existing-container-id"
        mock_docker_client.containers.list.assert_called_once()
    
    @patch("testcontainers.core.generic_container.DockerClientFactory")
    def test_find_container_for_reuse_returns_none_if_not_found(self, mock_factory, mock_docker_client):
        """Test that find_container_for_reuse returns None if no match."""
        mock_docker_client.containers.list = Mock(return_value=[])
        
        container = GenericContainer("test:latest", docker_client=mock_docker_client)
        
        found_id = container._find_container_for_reuse("test-hash")
        
        assert found_id is None

