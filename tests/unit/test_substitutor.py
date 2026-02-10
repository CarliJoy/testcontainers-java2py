"""Tests for image name substitutor functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from testcontainers.config import TestcontainersConfig, get_config
from testcontainers.images.substitutor import (
    NoOpImageNameSubstitutor,
    PrefixingImageNameSubstitutor,
    ConfigurableImageNameSubstitutor,
    ChainImageNameSubstitutor,
    get_image_name_substitutor,
    set_global_substitutor,
    reset_global_substitutor,
)


@pytest.fixture
def reset_config():
    """Reset configuration before and after each test."""
    TestcontainersConfig.reset()
    reset_global_substitutor()
    yield
    TestcontainersConfig.reset()
    reset_global_substitutor()


class TestNoOpImageNameSubstitutor:
    """Test the no-op substitutor."""

    def test_returns_unchanged(self):
        """NoOp substitutor should return image names unchanged."""
        sub = NoOpImageNameSubstitutor()

        assert sub.substitute("postgres:13") == "postgres:13"
        assert sub.substitute("mysql:8.0") == "mysql:8.0"
        assert sub.substitute("registry.io/custom:latest") == "registry.io/custom:latest"

    def test_describe(self):
        """NoOp substitutor should have a description."""
        sub = NoOpImageNameSubstitutor()
        assert "NoOp" in sub.describe()


class TestPrefixingImageNameSubstitutor:
    """Test the prefixing substitutor."""

    def test_adds_prefix_to_docker_hub_images(self):
        """Should add prefix to Docker Hub images."""
        sub = PrefixingImageNameSubstitutor("registry.corp.com/mirror")

        assert sub.substitute("postgres:13") == "registry.corp.com/mirror/postgres:13"
        assert sub.substitute("mysql:8.0") == "registry.corp.com/mirror/mysql:8.0"
        assert sub.substitute("redis:alpine") == "registry.corp.com/mirror/redis:alpine"

    def test_handles_docker_io_prefix(self):
        """Should handle docker.io/ prefix."""
        sub = PrefixingImageNameSubstitutor("registry.corp.com")

        assert sub.substitute("docker.io/postgres:13") == "registry.corp.com/postgres:13"

    def test_does_not_modify_registry_images(self):
        """Should not modify images that already have a registry."""
        sub = PrefixingImageNameSubstitutor("registry.corp.com/mirror")

        # These already have registries, should be unchanged
        assert sub.substitute("gcr.io/project/image:tag") == "gcr.io/project/image:tag"
        assert sub.substitute("registry.io/custom:latest") == "registry.io/custom:latest"
        assert sub.substitute("quay.io/org/app:v1") == "quay.io/org/app:v1"

    def test_strips_trailing_slash_from_prefix(self):
        """Should handle prefixes with trailing slashes."""
        sub = PrefixingImageNameSubstitutor("registry.corp.com/mirror/")

        assert sub.substitute("postgres:13") == "registry.corp.com/mirror/postgres:13"

    def test_describe(self):
        """Should have a descriptive string."""
        sub = PrefixingImageNameSubstitutor("registry.corp.com")
        desc = sub.describe()

        assert "Prefixing" in desc
        assert "registry.corp.com" in desc


class TestConfigurableImageNameSubstitutor:
    """Test the configurable substitutor."""

    def test_maps_configured_images(self):
        """Should map images according to configuration."""
        mappings = {
            "postgres:13": "registry.corp.com/custom/postgres:13-patched",
            "mysql:8.0": "registry.corp.com/approved/mysql:8.0",
        }
        sub = ConfigurableImageNameSubstitutor(mappings)

        assert (
            sub.substitute("postgres:13")
            == "registry.corp.com/custom/postgres:13-patched"
        )
        assert (
            sub.substitute("mysql:8.0") == "registry.corp.com/approved/mysql:8.0"
        )

    def test_returns_unchanged_for_unmapped_images(self):
        """Should return unmapped images unchanged."""
        mappings = {"postgres:13": "custom/postgres:13"}
        sub = ConfigurableImageNameSubstitutor(mappings)

        assert sub.substitute("mysql:8.0") == "mysql:8.0"
        assert sub.substitute("redis:alpine") == "redis:alpine"

    def test_from_config_loads_mappings(self, reset_config, monkeypatch, tmp_path):
        """Should load mappings from configuration."""
        # Create a test config file
        config_file = tmp_path / "testcontainers.toml"
        config_file.write_text(
            """
[image_mappings]
"postgres:13" = "custom/postgres:13"
"mysql:8.0" = "custom/mysql:8.0"
"""
        )

        # Change to the temp directory so config is found
        monkeypatch.chdir(tmp_path)
        TestcontainersConfig.reset()

        sub = ConfigurableImageNameSubstitutor.from_config()

        assert sub.substitute("postgres:13") == "custom/postgres:13"
        assert sub.substitute("mysql:8.0") == "custom/mysql:8.0"

    def test_describe(self):
        """Should have a descriptive string."""
        mappings = {"postgres:13": "custom/postgres:13"}
        sub = ConfigurableImageNameSubstitutor(mappings)
        desc = sub.describe()

        assert "Configurable" in desc
        assert "1" in desc  # Should show count


class TestChainImageNameSubstitutor:
    """Test the chain substitutor."""

    def test_applies_substitutors_in_sequence(self):
        """Should apply substitutors in order."""
        # First add prefix, then apply specific mapping
        prefix_sub = PrefixingImageNameSubstitutor("registry.corp.com")
        config_sub = ConfigurableImageNameSubstitutor(
            {"registry.corp.com/postgres:13": "custom/postgres:13-special"}
        )

        chain = ChainImageNameSubstitutor(prefix_sub, config_sub)

        # postgres:13 -> registry.corp.com/postgres:13 -> custom/postgres:13-special
        assert chain.substitute("postgres:13") == "custom/postgres:13-special"

    def test_empty_chain_returns_unchanged(self):
        """Should handle empty chain."""
        chain = ChainImageNameSubstitutor()

        assert chain.substitute("postgres:13") == "postgres:13"

    def test_describe(self):
        """Should describe the chain."""
        sub1 = PrefixingImageNameSubstitutor("registry.io")
        sub2 = NoOpImageNameSubstitutor()
        chain = ChainImageNameSubstitutor(sub1, sub2)

        desc = chain.describe()
        assert "Chain" in desc


class TestGlobalSubstitutor:
    """Test global substitutor management."""

    def test_get_default_returns_noop(self, reset_config):
        """Should return NoOp by default."""
        sub = get_image_name_substitutor()

        # Should be NoOp (returns images unchanged)
        assert sub.substitute("postgres:13") == "postgres:13"

    def test_set_global_substitutor(self, reset_config):
        """Should allow setting global substitutor programmatically."""
        custom_sub = PrefixingImageNameSubstitutor("registry.corp.com")
        set_global_substitutor(custom_sub)

        sub = get_image_name_substitutor()
        assert sub.substitute("postgres:13") == "registry.corp.com/postgres:13"

    def test_reset_global_substitutor(self, reset_config):
        """Should allow resetting global substitutor."""
        custom_sub = PrefixingImageNameSubstitutor("registry.corp.com")
        set_global_substitutor(custom_sub)

        reset_global_substitutor()

        sub = get_image_name_substitutor()
        assert sub.substitute("postgres:13") == "postgres:13"  # Back to NoOp

    def test_loads_from_env_variable(self, reset_config, monkeypatch: pytest.MonkeyPatch):
        """Should load prefix from environment variable."""
        monkeypatch.setenv("TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX", "registry.corp.com")
        TestcontainersConfig.reset()

        sub = get_image_name_substitutor()
        assert sub.substitute("postgres:13") == "registry.corp.com/postgres:13"

    def test_loads_from_config_file(self, reset_config, monkeypatch, tmp_path):
        """Should load from config file."""
        config_file = tmp_path / "testcontainers.toml"
        config_file.write_text(
            """
[hub]
image_name_prefix = "registry.corp.com/mirror"
"""
        )

        monkeypatch.chdir(tmp_path)
        TestcontainersConfig.reset()

        sub = get_image_name_substitutor()
        assert sub.substitute("postgres:13") == "registry.corp.com/mirror/postgres:13"

    def test_programmatic_overrides_config(self, reset_config, monkeypatch: pytest.MonkeyPatch):
        """Programmatic setting should override configuration."""
        monkeypatch.setenv("TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX", "registry.env.com")
        TestcontainersConfig.reset()

        # Set programmatically
        custom_sub = PrefixingImageNameSubstitutor("registry.prog.com")
        set_global_substitutor(custom_sub)

        sub = get_image_name_substitutor()
        # Should use programmatic, not env
        assert sub.substitute("postgres:13") == "registry.prog.com/postgres:13"

    def test_creates_chain_with_multiple_configs(
        self, reset_config, monkeypatch, tmp_path
    ):
        """Should create chain when both prefix and mappings are configured."""
        config_file = tmp_path / "testcontainers.toml"
        config_file.write_text(
            """
[hub]
image_name_prefix = "registry.corp.com"

[image_mappings]
"postgres:13" = "custom/postgres:13"
"""
        )

        monkeypatch.chdir(tmp_path)
        TestcontainersConfig.reset()

        sub = get_image_name_substitutor()

        # Mappings are checked first, then prefix is applied
        # mysql:8.0 has no mapping, so prefix is applied -> registry.corp.com/mysql:8.0
        assert sub.substitute("mysql:8.0") == "registry.corp.com/mysql:8.0"
        
        # postgres:13 has a mapping, so it's used directly -> custom/postgres:13
        assert sub.substitute("postgres:13") == "custom/postgres:13"
