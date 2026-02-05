"""Tests for image handling."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

import pytest

from testcontainers.images import (
    ImagePullPolicy,
    ImageData,
    AbstractImagePullPolicy,
    AlwaysPullPolicy,
    DefaultPullPolicy,
    AgeBasedPullPolicy,
    PullPolicy,
    RemoteDockerImage,
)


class TestImageData:
    """Tests for ImageData class."""
    
    def test_create_from_inspect_response(self):
        """Test creating ImageData from inspect response."""
        inspect_response = {
            "Created": "2023-01-15T10:30:00Z"
        }
        
        image_data = ImageData.from_inspect_response(inspect_response)
        
        assert isinstance(image_data.created_at, datetime)
        assert image_data.created_at.year == 2023
        assert image_data.created_at.month == 1
    
    def test_create_from_inspect_response_empty(self):
        """Test creating ImageData with empty created date."""
        inspect_response = {"Created": ""}
        
        image_data = ImageData.from_inspect_response(inspect_response)
        
        # Should default to epoch
        assert image_data.created_at == datetime.fromtimestamp(0)
    
    def test_create_from_image_dict(self):
        """Test creating ImageData from image dictionary."""
        image_dict = {
            "Created": 1673779800  # Unix timestamp
        }
        
        image_data = ImageData.from_image_dict(image_dict)
        
        assert isinstance(image_data.created_at, datetime)
    
    def test_create_from_image_dict_none(self):
        """Test creating ImageData with None created."""
        image_dict = {"Created": None}
        
        image_data = ImageData.from_image_dict(image_dict)
        
        assert image_data.created_at == datetime.fromtimestamp(0)


class TestAlwaysPullPolicy:
    """Tests for AlwaysPullPolicy."""
    
    def test_always_returns_true(self):
        """Test that AlwaysPullPolicy always returns True."""
        policy = AlwaysPullPolicy()
        
        assert policy.should_pull("nginx:latest") is True
        assert policy.should_pull("postgres:13") is True
        assert policy.should_pull("redis:alpine") is True


class TestDefaultPullPolicy:
    """Tests for DefaultPullPolicy."""
    
    def test_should_pull_when_not_cached(self):
        """Test pull when image not in cache."""
        policy = DefaultPullPolicy()
        
        # Image not in cache should be pulled
        assert policy.should_pull("nginx:latest") is True
    
    def test_should_not_pull_when_cached(self):
        """Test don't pull when image is cached."""
        policy = DefaultPullPolicy()
        
        # Add to cache
        image_data = ImageData(created_at=datetime.now())
        policy._local_images_cache["nginx:latest"] = image_data
        
        # Should not pull cached image
        assert policy.should_pull("nginx:latest") is False


class TestAgeBasedPullPolicy:
    """Tests for AgeBasedPullPolicy."""
    
    def test_pull_old_image(self):
        """Test pull when image is too old."""
        max_age = timedelta(days=7)
        policy = AgeBasedPullPolicy(max_age)
        
        # Add old image to cache
        old_date = datetime.now() - timedelta(days=10)
        image_data = ImageData(created_at=old_date)
        policy._local_images_cache["nginx:latest"] = image_data
        
        # Should pull old image
        assert policy.should_pull("nginx:latest") is True
    
    def test_dont_pull_recent_image(self):
        """Test don't pull when image is recent."""
        max_age = timedelta(days=7)
        policy = AgeBasedPullPolicy(max_age)
        
        # Add recent image to cache
        recent_date = datetime.now() - timedelta(days=3)
        image_data = ImageData(created_at=recent_date)
        policy._local_images_cache["nginx:latest"] = image_data
        
        # Should not pull recent image
        assert policy.should_pull("nginx:latest") is False


class TestPullPolicy:
    """Tests for PullPolicy factory."""
    
    def test_default_policy(self):
        """Test getting default policy."""
        policy = PullPolicy.default_policy()
        
        assert isinstance(policy, DefaultPullPolicy)
    
    def test_always_pull(self):
        """Test getting always pull policy."""
        policy = PullPolicy.always_pull()
        
        assert isinstance(policy, AlwaysPullPolicy)
    
    def test_age_based(self):
        """Test getting age-based policy."""
        max_age = timedelta(days=30)
        policy = PullPolicy.age_based(max_age)
        
        assert isinstance(policy, AgeBasedPullPolicy)
        assert policy._max_age == max_age


class TestRemoteDockerImage:
    """Tests for RemoteDockerImage."""
    
    def test_initialization(self):
        """Test basic initialization."""
        image = RemoteDockerImage("nginx:latest")
        
        assert image.image_name == "nginx:latest"
        assert image._resolved_image_name is None
    
    def test_with_pull_policy(self):
        """Test setting pull policy with fluent API."""
        image = RemoteDockerImage("nginx:latest")
        policy = AlwaysPullPolicy()
        
        result = image.with_pull_policy(policy)
        
        assert result is image  # Fluent API
        assert image._pull_policy is policy
    
    def test_string_representation(self):
        """Test string representation."""
        image = RemoteDockerImage("nginx:latest")
        
        assert "nginx:latest" in str(image)
        assert "resolving" in str(image)
    
    def test_repr(self):
        """Test repr representation."""
        image = RemoteDockerImage("nginx:latest")
        
        assert "RemoteDockerImage" in repr(image)
        assert "nginx:latest" in repr(image)
    
    @patch.object(RemoteDockerImage, '_pull_image')
    def test_resolve_with_pull(self, mock_pull):
        """Test resolve when policy says to pull."""
        mock_client = Mock()
        policy = AlwaysPullPolicy()
        
        image = RemoteDockerImage("nginx:latest", pull_policy=policy, docker_client=mock_client)
        
        result = image.resolve()
        
        assert result == "nginx:latest"
        mock_pull.assert_called_once()
    
    def test_resolve_without_pull(self):
        """Test resolve when policy says not to pull."""
        mock_client = Mock()
        
        # Use a policy that won't pull
        policy = Mock(spec=ImagePullPolicy)
        policy.should_pull.return_value = False
        
        image = RemoteDockerImage("nginx:latest", pull_policy=policy, docker_client=mock_client)
        
        result = image.resolve()
        
        assert result == "nginx:latest"
        # Should not call docker client if not pulling
        mock_client.images.pull.assert_not_called()
    
    def test_resolve_caches_result(self):
        """Test that resolve caches the result."""
        mock_client = Mock()
        policy = Mock(spec=ImagePullPolicy)
        policy.should_pull.return_value = False
        
        image = RemoteDockerImage("nginx:latest", pull_policy=policy, docker_client=mock_client)
        
        # Call resolve twice
        result1 = image.resolve()
        result2 = image.resolve()
        
        assert result1 == result2
        # Should only check policy once
        assert policy.should_pull.call_count == 1
    
    def test_pull_image_parses_name_with_tag(self):
        """Test that _pull_image correctly parses image name with tag."""
        mock_client = Mock()
        mock_client.images.pull.return_value = None
        
        image = RemoteDockerImage("nginx:1.21", docker_client=mock_client)
        
        image._pull_image(timeout_seconds=10)
        
        mock_client.images.pull.assert_called_once_with("nginx", tag="1.21")
    
    def test_pull_image_parses_name_without_tag(self):
        """Test that _pull_image defaults to 'latest' when no tag."""
        mock_client = Mock()
        mock_client.images.pull.return_value = None
        
        image = RemoteDockerImage("nginx", docker_client=mock_client)
        
        image._pull_image(timeout_seconds=10)
        
        mock_client.images.pull.assert_called_once_with("nginx", tag="latest")
