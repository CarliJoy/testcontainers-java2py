"""
Test helpers and utilities for Testcontainers tests.

Provides utility functions for common testing scenarios.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/utility/TestcontainersConfiguration.java
"""

from __future__ import annotations

import functools
import socket
import time
from typing import Any, Callable, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from testcontainers.core import GenericContainer
from testcontainers.core.docker_client import DockerClientFactory

F = TypeVar('F', bound=Callable[..., Any])


def skip_if_docker_unavailable(func: F) -> F:
    """
    Decorator to skip test if Docker is not available.
    
    Example:
        ```python
        @skip_if_docker_unavailable
        def test_requires_docker():
            # This test will be skipped if Docker is unavailable
            pass
        ```
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import pytest here to avoid issues during type checking
        import pytest as pytest_module
        try:
            if not DockerClientFactory.instance().is_docker_available():
                pytest_module.skip("Docker is not available")
        except Exception:
            pytest_module.skip("Could not check Docker availability")
        return func(*args, **kwargs)
    return wrapper  # type: ignore[return-value]


def wait_for_container_ready(
    container: GenericContainer,
    timeout: float = 60.0,
    check_interval: float = 0.5
) -> bool:
    """
    Wait for a container to be ready.
    
    Args:
        container: Container to wait for
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
    
    Returns:
        True if container became ready, False if timeout
    
    Example:
        ```python
        container = GenericContainer("postgres:13")
        container.start()
        assert wait_for_container_ready(container, timeout=30)
        ```
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if container.get_container_info() and container.is_running():
                return True
        except Exception:
            pass
        time.sleep(check_interval)
    
    return False


def wait_for_port(host: str, port: int, timeout: float = 60.0) -> bool:
    """
    Wait for a port to become available.
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if port became available, False if timeout
    
    Example:
        ```python
        container = GenericContainer("redis:6")
        container.with_exposed_ports(6379)
        container.start()
        port = container.get_exposed_port(6379)
        assert wait_for_port("localhost", port, timeout=30)
        ```
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    return False
