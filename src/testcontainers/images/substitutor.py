"""
Image name substitution support.

Provides mechanisms to automatically transform Docker image names before use.
This is useful for:
- Private registry mirroring (avoid Docker Hub rate limits)
- Corporate compliance (use only approved registries)
- Image version control (substitute specific versions)
- Security auditing (log all images used)
"""

from __future__ import annotations

import logging
from typing import Protocol, Optional

from testcontainers.config import get_config

logger = logging.getLogger(__name__)


class ImageNameSubstitutor(Protocol):
    """
    Protocol for image name substitution.

    Implementations can transform Docker image names before they are used.
    """

    def substitute(self, image_name: str) -> str:
        """
        Substitute the given image name with an alternative.

        Args:
            image_name: Original Docker image name

        Returns:
            Substituted image name (or original if no substitution needed)
        """
        ...

    def describe(self) -> str:
        """
        Get a human-readable description of this substitutor.

        Returns:
            Description of what this substitutor does
        """
        ...


class NoOpImageNameSubstitutor:
    """Pass-through substitutor that returns image names unchanged."""

    def substitute(self, image_name: str) -> str:
        """Return the image name unchanged."""
        return image_name

    def describe(self) -> str:
        """Describe this substitutor."""
        return "NoOpImageNameSubstitutor (pass-through)"


class PrefixingImageNameSubstitutor:
    """
    Adds a registry prefix to Docker Hub images.

    This is the most common substitutor for enterprise use, redirecting
    Docker Hub images to a private registry mirror.

    Examples:
        mysql:8.0 -> registry.corp.com/mirror/mysql:8.0
        postgres:13 -> registry.corp.com/mirror/postgres:13
    """

    def __init__(self, prefix: str):
        """
        Initialize with a registry prefix.

        Args:
            prefix: Registry prefix to add (e.g., "registry.corp.com/mirror")
        """
        self.prefix = prefix.rstrip("/")

    def substitute(self, image_name: str) -> str:
        """
        Add prefix to Docker Hub images.

        Args:
            image_name: Original image name

        Returns:
            Prefixed image name if it's a Docker Hub image, otherwise unchanged
        """
        # Only prefix Docker Hub images (no registry specified)
        # Images with registries (containing '/') are left unchanged
        if "/" not in image_name or image_name.startswith("docker.io/"):
            # Remove docker.io/ prefix if present
            clean_name = image_name.replace("docker.io/", "")
            result = f"{self.prefix}/{clean_name}"
            logger.debug(f"Substituted image: {image_name} -> {result}")
            return result

        # Image already has a registry, don't modify
        return image_name

    def describe(self) -> str:
        """Describe this substitutor."""
        return f"PrefixingImageNameSubstitutor(prefix={self.prefix})"


class ConfigurableImageNameSubstitutor:
    """
    Maps specific images to alternatives based on configuration.

    Uses a dictionary to map exact image names to their substitutes.
    This allows fine-grained control over individual images.

    Example mappings:
        postgres:13 -> registry.corp.com/custom/postgres:13-patched
        mysql:8.0 -> registry.corp.com/approved/mysql:8.0
    """

    def __init__(self, mappings: Optional[dict[str, str]] = None):
        """
        Initialize with image mappings.

        Args:
            mappings: Dictionary mapping source images to target images
        """
        self.mappings = mappings or {}

    @classmethod
    def from_config(cls) -> ConfigurableImageNameSubstitutor:
        """
        Create a substitutor from configuration.

        Loads image mappings from testcontainers.toml configuration file.

        Returns:
            ConfigurableImageNameSubstitutor with loaded mappings
        """
        config = get_config()
        mappings = config.get_all_image_mappings()
        return cls(mappings)

    def substitute(self, image_name: str) -> str:
        """
        Substitute based on configured mappings.

        Args:
            image_name: Original image name

        Returns:
            Mapped image name if found in configuration, otherwise original
        """
        if image_name in self.mappings:
            result = self.mappings[image_name]
            logger.debug(f"Substituted image: {image_name} -> {result}")
            return result

        return image_name

    def describe(self) -> str:
        """Describe this substitutor."""
        return f"ConfigurableImageNameSubstitutor(mappings={len(self.mappings)})"


class ChainImageNameSubstitutor:
    """
    Chains multiple substitutors together.

    Applies substitutors in order, passing the output of one as input to the next.
    This allows combining multiple substitution strategies.
    """

    def __init__(self, *substitutors: ImageNameSubstitutor):
        """
        Initialize with a list of substitutors.

        Args:
            *substitutors: Substitutors to chain together
        """
        self.substitutors = list(substitutors)

    def substitute(self, image_name: str) -> str:
        """
        Apply all substitutors in sequence.

        Args:
            image_name: Original image name

        Returns:
            Image name after all substitutions
        """
        result = image_name
        for substitutor in self.substitutors:
            result = substitutor.substitute(result)

        if result != image_name:
            logger.debug(f"Substituted image: {image_name} -> {result}")

        return result

    def describe(self) -> str:
        """Describe this substitutor."""
        descriptions = [s.describe() for s in self.substitutors]
        return f"ChainImageNameSubstitutor({', '.join(descriptions)})"


# Global substitutor instance
_global_substitutor: Optional[ImageNameSubstitutor] = None


def get_image_name_substitutor() -> ImageNameSubstitutor:
    """
    Get the global image name substitutor.

    Returns the configured substitutor based on:
    1. Programmatically set substitutor (highest priority)
    2. Configuration from environment/TOML
    3. Default NoOp substitutor (lowest priority)

    Returns:
        Active ImageNameSubstitutor instance
    """
    global _global_substitutor

    # 1. Return programmatically set substitutor
    if _global_substitutor is not None:
        return _global_substitutor

    # 2. Build from configuration
    config = get_config()
    substitutors: list[ImageNameSubstitutor] = []

    # Check for image mappings configuration first (more specific)
    if mappings := config.get_all_image_mappings():
        logger.info(f"Using {len(mappings)} configured image mappings")
        substitutors.append(ConfigurableImageNameSubstitutor(mappings))

    # Check for hub prefix configuration second (more general)
    if prefix := config.get_hub_image_name_prefix():
        logger.info(f"Using hub image name prefix: {prefix}")
        substitutors.append(PrefixingImageNameSubstitutor(prefix))

    # 3. Return appropriate substitutor
    if len(substitutors) == 0:
        return NoOpImageNameSubstitutor()
    elif len(substitutors) == 1:
        return substitutors[0]
    else:
        return ChainImageNameSubstitutor(*substitutors)


def set_global_substitutor(substitutor: Optional[ImageNameSubstitutor]) -> None:
    """
    Set the global image name substitutor programmatically.

    This overrides any configuration-based substitutor.

    Args:
        substitutor: Substitutor to use globally, or None to reset to config-based
    """
    global _global_substitutor
    _global_substitutor = substitutor

    if substitutor:
        logger.info(f"Set global image name substitutor: {substitutor.describe()}")
    else:
        logger.info("Reset global image name substitutor to configuration-based")


def reset_global_substitutor() -> None:
    """Reset the global substitutor to None (useful for testing)."""
    set_global_substitutor(None)
