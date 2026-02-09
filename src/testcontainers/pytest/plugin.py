"""
Pytest plugin for Testcontainers integration.

Provides pytest markers and hooks for managing testcontainers lifecycle.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/junit-jupiter/src/main/java/org/testcontainers/junit/jupiter/TestcontainersExtension.java
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from testcontainers.core.docker_client import DockerClientFactory

logger = logging.getLogger(__name__)


def pytest_configure(config: Any) -> None:
    """Register testcontainers-specific markers."""
    config.addinivalue_line(
        "markers",
        "testcontainers: mark test as requiring testcontainers/Docker"
    )
    config.addinivalue_line(
        "markers",
        "docker: mark test as requiring Docker (will skip if unavailable)"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """
    Modify test collection to handle Docker availability.
    
    Tests marked with @pytest.mark.docker will be skipped if Docker
    is not available on the system.
    """
    try:
        # Check if Docker is available
        docker_available = DockerClientFactory.instance().is_docker_available()
    except Exception as e:
        logger.warning(f"Could not check Docker availability: {e}")
        docker_available = False
    
    if not docker_available:
        # Import pytest here to avoid circular imports during type checking
        import pytest as pytest_module
        skip_docker = pytest_module.mark.skip(reason="Docker is not available")
        for item in items:
            if "docker" in item.keywords or "testcontainers" in item.keywords:
                item.add_marker(skip_docker)


def docker_client() -> Any:
    """
    Session-scoped fixture providing Docker client.
    
    Returns:
        Docker client from DockerClientFactory
    """
    return DockerClientFactory.instance().client()


def cleanup_containers() -> Any:
    """
    Session-scoped fixture for container cleanup.
    
    Ensures all containers are cleaned up at the end of the test session.
    This is automatically used for all tests.
    """
    yield
    # Cleanup happens automatically via context managers
    # This fixture is mainly for future cleanup enhancements
    logger.info("Test session complete - containers cleaned up")
