"""
Configuration management for testcontainers.

Handles loading configuration from multiple sources:
1. Programmatic configuration (highest priority)
2. Environment variables
3. TOML configuration file
4. Built-in defaults (lowest priority)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import tomli/tomllib for TOML support
try:
    # Python 3.11+
    import tomllib
except ImportError:
    try:
        # Python 3.9-3.10
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


class TestcontainersConfig:
    """Configuration manager for testcontainers."""

    _instance: Optional[TestcontainersConfig] = None
    _config: dict[str, Any]

    def __new__(cls) -> TestcontainersConfig:
        """Singleton pattern to ensure only one config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from all sources."""
        # 1. Load from TOML file if it exists
        config_paths = [
            Path.cwd() / "testcontainers.toml",
            Path.home() / ".testcontainers" / "testcontainers.toml",
        ]

        for config_path in config_paths:
            if config_path.exists():
                logger.debug(f"Loading config from {config_path}")
                self._load_toml(config_path)
                break

        # 2. Environment variables override TOML
        self._load_env_vars()

    def _load_toml(self, path: Path) -> None:
        """Load configuration from a TOML file."""
        if tomllib is None:
            logger.warning(
                "TOML support not available. Install 'tomli' for Python <3.11"
            )
            return

        try:
            with open(path, "rb") as f:
                toml_config = tomllib.load(f)
                self._config.update(toml_config)
                logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        # Hub image name prefix
        if prefix := os.getenv("TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX"):
            if "hub" not in self._config:
                self._config["hub"] = {}
            self._config["hub"]["image_name_prefix"] = prefix
            logger.debug(f"Loaded hub prefix from env: {prefix}")

        # Ryuk (container cleanup) settings
        if ryuk_disabled := os.getenv("TESTCONTAINERS_RYUK_DISABLED"):
            if "ryuk" not in self._config:
                self._config["ryuk"] = {}
            self._config["ryuk"]["disabled"] = ryuk_disabled.lower() in ("true", "1", "yes")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated key.

        Args:
            key: Dot-separated key (e.g., "hub.image_name_prefix")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_hub_image_name_prefix(self) -> Optional[str]:
        """Get the hub image name prefix configuration."""
        return self.get("hub.image_name_prefix")

    def get_image_mapping(self, image_name: str) -> Optional[str]:
        """Get a specific image mapping if configured."""
        return self.get(f"image_mappings.{image_name}")

    def get_all_image_mappings(self) -> dict[str, str]:
        """Get all configured image mappings."""
        mappings = self.get("image_mappings", {})
        return mappings if isinstance(mappings, dict) else {}

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None


def get_config() -> TestcontainersConfig:
    """Get the global configuration instance."""
    return TestcontainersConfig()
