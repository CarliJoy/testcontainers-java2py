"""
Image handling for testcontainers.

This module provides functionality for pulling and managing Docker images.
"""

from testcontainers.images.image_pull_policy import ImagePullPolicy
from testcontainers.images.image_data import ImageData
from testcontainers.images.policies import (
    AbstractImagePullPolicy,
    AlwaysPullPolicy,
    DefaultPullPolicy,
    AgeBasedPullPolicy,
)
from testcontainers.images.pull_policy import PullPolicy
from testcontainers.images.remote_image import RemoteDockerImage
from testcontainers.images.substitutor import (
    ImageNameSubstitutor,
    NoOpImageNameSubstitutor,
    PrefixingImageNameSubstitutor,
    ConfigurableImageNameSubstitutor,
    ChainImageNameSubstitutor,
    get_image_name_substitutor,
    set_global_substitutor,
    reset_global_substitutor,
)

__all__ = [
    "ImagePullPolicy",
    "ImageData",
    "AbstractImagePullPolicy",
    "AlwaysPullPolicy",
    "DefaultPullPolicy",
    "AgeBasedPullPolicy",
    "PullPolicy",
    "RemoteDockerImage",
    "ImageNameSubstitutor",
    "NoOpImageNameSubstitutor",
    "PrefixingImageNameSubstitutor",
    "ConfigurableImageNameSubstitutor",
    "ChainImageNameSubstitutor",
    "get_image_name_substitutor",
    "set_global_substitutor",
    "reset_global_substitutor",
]
