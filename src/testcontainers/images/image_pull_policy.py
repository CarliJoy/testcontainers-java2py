"""
Image pull policy interface and implementations.

This module provides the ImagePullPolicy protocol for determining when
to pull Docker images.
"""

from __future__ import annotations

from typing import Protocol


class ImagePullPolicy(Protocol):
    """
    Protocol for image pull policies.
    
    An image pull policy determines whether an image should be pulled
    from a registry, even if it exists locally.
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/images/ImagePullPolicy.java
    """
    
    def should_pull(self, image_name: str) -> bool:
        """
        Determine if an image should be pulled.
        
        Args:
            image_name: The Docker image name
            
        Returns:
            True if the image should be pulled, False otherwise
        """
        ...
