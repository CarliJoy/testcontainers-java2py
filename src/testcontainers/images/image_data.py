"""
Image data and metadata.

This module provides the ImageData class for storing Docker image metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ImageData:
    """
    Container for Docker image metadata.
    
    Attributes:
        created_at: When the image was created
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/images/ImageData.java
    """
    
    created_at: datetime
    
    @classmethod
    def from_inspect_response(cls, inspect_response: dict) -> ImageData:
        """
        Create ImageData from a Docker inspect response.
        
        Args:
            inspect_response: Docker inspect image response
            
        Returns:
            ImageData instance
        """
        created = inspect_response.get("Created", "")
        if not created:
            created_at = datetime.fromtimestamp(0)
        else:
            # Parse ISO format datetime
            try:
                created_at = datetime.fromisoformat(created.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                created_at = datetime.fromtimestamp(0)
        
        return cls(created_at=created_at)
    
    @classmethod
    def from_image_dict(cls, image_dict: dict) -> ImageData:
        """
        Create ImageData from a Docker image dictionary.
        
        Args:
            image_dict: Docker image dictionary (from images.list())
            
        Returns:
            ImageData instance
        """
        created = image_dict.get("Created")
        if created is None:
            created_at = datetime.fromtimestamp(0)
        else:
            # Created is usually a Unix timestamp
            try:
                created_at = datetime.fromtimestamp(created)
            except (ValueError, TypeError):
                created_at = datetime.fromtimestamp(0)
        
        return cls(created_at=created_at)
