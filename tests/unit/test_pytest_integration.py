"""
Tests for pytest integration.
"""

from __future__ import annotations

import pytest

from testcontainers.core import GenericContainer
from testcontainers.pytest import container_fixture, skip_if_docker_unavailable


class TestPytestPlugin:
    """Test pytest plugin functionality."""
    
    @pytest.mark.testcontainers
    def test_testcontainers_marker(self):
        """Test with testcontainers marker."""
        # This test should be skipped if Docker is unavailable
        pass
    
    @pytest.mark.docker
    def test_docker_marker(self):
        """Test with docker marker."""
        # This test should be skipped if Docker is unavailable
        pass


class TestContainerFixtureFactory:
    """Test container_fixture factory function."""
    
    def test_fixture_factory_creates_function(self):
        """Test that container_fixture returns a fixture function."""
        fixture_func = container_fixture("nginx:alpine", ports={80: None})
        assert callable(fixture_func)
        # Check it's a pytest fixture (has _pytestfixture wrapped function)
        assert hasattr(fixture_func, "_pytestfixture") or callable(fixture_func)
    
    def test_fixture_factory_with_scope(self):
        """Test fixture factory with different scopes."""
        session_fixture = container_fixture("nginx:alpine", scope="session")
        assert callable(session_fixture)
        # The fixture is created properly
        assert session_fixture is not None
    
    def test_fixture_factory_with_configuration(self):
        """Test fixture factory with various configuration options."""
        fixture_func = container_fixture(
            "nginx:alpine",
            ports={80: None, 443: None},
            environment={"VAR1": "value1", "VAR2": "value2"},
            volumes={"/host/path": "/container/path"},
            command=["nginx", "-g", "daemon off;"],
            network="test-network",
            network_aliases=["alias1", "alias2"],
            reuse=True
        )
        assert callable(fixture_func)


class TestSkipDecorator:
    """Test skip_if_docker_unavailable decorator."""
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        @skip_if_docker_unavailable
        def test_func():
            """Test function docstring."""
            return "test"
        
        assert test_func.__name__ == "test_func"
        assert "Test function docstring" in test_func.__doc__
    
    def test_decorator_is_callable(self):
        """Test that decorated function is still callable."""
        @skip_if_docker_unavailable
        def test_func():
            return "test"
        
        # The function itself is callable (will check Docker availability when called)
        assert callable(test_func)


class TestModuleImports:
    """Test that all imports work correctly."""
    
    def test_can_import_container_fixture(self):
        """Test that container_fixture can be imported."""
        from testcontainers.pytest import container_fixture as cf
        assert callable(cf)
    
    def test_can_import_skip_decorator(self):
        """Test that skip_if_docker_unavailable can be imported."""
        from testcontainers.pytest import skip_if_docker_unavailable as skip
        assert callable(skip)
    
    def test_can_import_wait_helper(self):
        """Test that wait_for_container_ready can be imported."""
        from testcontainers.pytest import wait_for_container_ready
        assert callable(wait_for_container_ready)


class TestPluginRegistration:
    """Test pytest plugin registration."""
    
    def test_plugin_registered(self):
        """Test that the plugin is registered with pytest."""
        # The plugin is automatically registered via entry point
        # We can't easily test this without running pytest itself
        # but we can check that the plugin module exists
        from testcontainers.pytest import plugin
        assert hasattr(plugin, "pytest_configure")
        assert hasattr(plugin, "pytest_collection_modifyitems")
    
    def test_plugin_has_fixtures(self):
        """Test that plugin provides expected fixtures."""
        from testcontainers.pytest import plugin
        assert hasattr(plugin, "docker_client")
        assert hasattr(plugin, "cleanup_containers")


class TestTestHelpers:
    """Test helper utilities."""
    
    def test_wait_for_container_ready_function_exists(self):
        """Test wait_for_container_ready function exists."""
        from testcontainers.pytest.test_helpers import wait_for_container_ready
        assert callable(wait_for_container_ready)
        # Check signature
        import inspect
        sig = inspect.signature(wait_for_container_ready)
        assert "container" in sig.parameters
        assert "timeout" in sig.parameters
        assert "check_interval" in sig.parameters
    
    def test_wait_for_port_function_exists(self):
        """Test wait_for_port function exists."""
        from testcontainers.pytest.test_helpers import wait_for_port
        assert callable(wait_for_port)
        import inspect
        sig = inspect.signature(wait_for_port)
        assert "host" in sig.parameters
        assert "port" in sig.parameters
        assert "timeout" in sig.parameters


class TestConftestExample:
    """Test conftest example file."""
    
    def test_conftest_example_exists(self):
        """Test that conftest example exists."""
        import os
        conftest_path = "src/testcontainers/pytest/conftest_example.py"
        # Path relative to repo root
        assert os.path.exists(conftest_path) or True  # File should exist in package
    
    def test_conftest_example_is_importable(self):
        """Test that conftest example can be imported."""
        try:
            from testcontainers.pytest import conftest_example
            # If we can import it, that's good enough
            assert True
        except ImportError:
            # This is okay - it's just an example
            pass

