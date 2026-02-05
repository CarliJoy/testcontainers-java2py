"""
Pull policy implementations.

This module provides concrete implementations of ImagePullPolicy.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from testcontainers.images.image_pull_policy import ImagePullPolicy
from testcontainers.images.image_data import ImageData

logger = logging.getLogger(__name__)


class AbstractImagePullPolicy(ABC, ImagePullPolicy):
    """
    Abstract base class for image pull policies.
    
    Provides common functionality for checking local image cache
    and determining whether to pull.
    """
    
    def __init__(self):
        """Initialize the abstract pull policy."""
        self._local_images_cache: dict[str, ImageData] = {}
    
    def should_pull(self, image_name: str) -> bool:
        """
        Determine if an image should be pulled.
        
        Args:
            image_name: The Docker image name
            
        Returns:
            True if the image should be pulled, False otherwise
        """
        # Check if image is in cache
        cached_image_data = self._local_images_cache.get(image_name)
        
        if cached_image_data is None:
            logger.debug(f"{image_name} is not in local cache, should pull")
            return True
        
        # Image exists locally, check if we should pull anyway
        if self._should_pull_cached(image_name, cached_image_data):
            logger.debug(f"Should pull locally available image: {image_name}")
            return True
        else:
            logger.debug(f"Using locally available image: {image_name}")
            return False
    
    @abstractmethod
    def _should_pull_cached(self, image_name: str, local_image_data: ImageData) -> bool:
        """
        Decide whether a locally available image should be pulled.
        
        Args:
            image_name: The Docker image name
            local_image_data: Metadata about the local image
            
        Returns:
            True to pull the image, False to use local
        """
        pass


class AlwaysPullPolicy(ImagePullPolicy):
    """
    Pull policy that always pulls images.
    
    Useful for obtaining the latest version of an image with a static tag
    like 'latest'.
    """
    
    def should_pull(self, image_name: str) -> bool:
        """Always return True to pull the image."""
        logger.debug(f"Unconditionally pulling image: {image_name}")
        return True


class DefaultPullPolicy(AbstractImagePullPolicy):
    """
    Default pull policy.
    
    Pulls images if they don't exist locally, but uses local images
    if they're already available.
    """
    
    def _should_pull_cached(self, image_name: str, local_image_data: ImageData) -> bool:
        """Don't pull if image exists locally."""
        return False


class AgeBasedPullPolicy(AbstractImagePullPolicy):
    """
    Age-based pull policy.
    
    Pulls images if they're older than a specified maximum age.
    """
    
    def __init__(self, max_age: timedelta):
        """
        Initialize with maximum age.
        
        Args:
            max_age: Maximum age before pulling
        """
        super().__init__()
        self._max_age = max_age
    
    def _should_pull_cached(self, image_name: str, local_image_data: ImageData) -> bool:
        """
        Pull if image is older than max age.
        
        Args:
            image_name: The Docker image name
            local_image_data: Metadata about the local image
            
        Returns:
            True if image is too old
        """
        age = datetime.now() - local_image_data.created_at.replace(tzinfo=None)
        return age > self._max_age
