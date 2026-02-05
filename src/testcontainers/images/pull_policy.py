"""
Pull policy factory and utilities.

This module provides convenience methods for creating common pull policies.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from testcontainers.images.image_pull_policy import ImagePullPolicy
from testcontainers.images.policies import (
    DefaultPullPolicy,
    AlwaysPullPolicy,
    AgeBasedPullPolicy,
)

logger = logging.getLogger(__name__)


class PullPolicy:
    """
    Factory for creating common image pull policies.
    """
    
    _default_policy: ImagePullPolicy | None = None
    
    @classmethod
    def default_policy(cls) -> ImagePullPolicy:
        """
        Get the default pull policy.
        
        Returns:
            Default ImagePullPolicy instance
        """
        if cls._default_policy is None:
            cls._default_policy = DefaultPullPolicy()
            logger.info(f"Image pull policy will be performed by: {cls._default_policy.__class__.__name__}")
        
        return cls._default_policy
    
    @classmethod
    def always_pull(cls) -> ImagePullPolicy:
        """
        Get a policy that always pulls images.
        
        Returns:
            AlwaysPullPolicy instance
        """
        return AlwaysPullPolicy()
    
    @classmethod
    def age_based(cls, max_age: timedelta) -> ImagePullPolicy:
        """
        Get an age-based pull policy.
        
        Args:
            max_age: Maximum age before pulling
            
        Returns:
            AgeBasedPullPolicy instance
        """
        return AgeBasedPullPolicy(max_age)
