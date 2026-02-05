"""
Pytest fixture support for Test

containers.

Provides factory functions for creating pytest fixtures that manage
container lifecycle automatically.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/junit-jupiter/src/main/java/org/testcontainers/junit/jupiter/TestcontainersExtension.java
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable

import pytest

from testcontainers.core import GenericContainer

logger = logging.getLogger(__name__)


def container_fixture(
    image: str,
    **container_kwargs: Any,
) -> Callable[..., GenericContainer]:
    """
    Factory function to create pytest fixtures for containers.
    
    This function creates a pytest fixture that manages a container's lifecycle
    automatically. The container is started when the fixture is used and
    stopped after the test completes.
    
    Args:
        image: Docker image name (e.g., "postgres:13")
        **container_kwargs: Keyword arguments to configure the container:
            - ports: Dict of port mappings {container_port: host_port}
            - environment: Dict of environment variables
            - volumes: Dict of volume mounts
            - command: Command to run in container
            - And other GenericContainer configuration options
    
    Returns:
        A pytest fixture function that yields a configured container
    
    Example:
        ```python
        # In conftest.py
        from testcontainers.pytest import container_fixture
        
        postgres = container_fixture(
            "postgres:13",
            ports={5432: None},
            environment={"POSTGRES_PASSWORD": "test"},
            scope="session"  # Optional: session, module, function
        )
        
        # In test file
        def test_database(postgres):
            port = postgres.get_exposed_port(5432)
            # Use database at localhost:{port}
        ```
    """
    # Extract pytest-specific kwargs
    scope = container_kwargs.pop("scope", "function")
    name = container_kwargs.pop("name", None)
    
    # Extract container configuration
    ports = container_kwargs.pop("ports", {})
    environment = container_kwargs.pop("environment", {})
    volumes = container_kwargs.pop("volumes", {})
    command = container_kwargs.pop("command", None)
    network = container_kwargs.pop("network", None)
    network_aliases = container_kwargs.pop("network_aliases", None)
    reuse = container_kwargs.pop("reuse", False)
    
    @pytest.fixture(scope=scope, name=name)
    def _container_fixture() -> GenericContainer:
        """Pytest fixture that manages container lifecycle."""
        logger.info(f"Starting container fixture: {image}")
        
        container = GenericContainer(image)
        
        # Configure container
        for container_port, host_port in ports.items():
            container.with_exposed_ports(container_port)
        
        for key, value in environment.items():
            container.with_env(key, value)
        
        for host_path, container_config in volumes.items():
            if isinstance(container_config, dict):
                container.with_volume_mapping(
                    host_path,
                    container_config.get("bind"),
                    container_config.get("mode", "rw")
                )
            else:
                container.with_volume_mapping(host_path, container_config)
        
        if command:
            container.with_command(command)
        
        if network:
            container.with_network(network)
        
        if network_aliases:
            container.with_network_aliases(*network_aliases)
        
        if reuse:
            container.with_reuse(True)
        
        # Apply any remaining kwargs as configuration
        for key, value in container_kwargs.items():
            method_name = f"with_{key}"
            if hasattr(container, method_name):
                method = getattr(container, method_name)
                if callable(method):
                    method(value)
        
        # Start container
        container.start()
        
        try:
            logger.info(f"Container started: {container.get_container_id()[:12]}")
            yield container
        finally:
            logger.info(f"Stopping container: {container.get_container_id()[:12]}")
            container.stop()
    
    return _container_fixture


def scoped_container(scope: str = "function"):
    """
    Decorator to create a scoped container fixture.
    
    Args:
        scope: Pytest scope (function, class, module, session)
    
    Example:
        ```python
        @scoped_container(scope="session")
        def postgres_session():
            return GenericContainer("postgres:13") \\
                .with_exposed_ports(5432) \\
                .with_env("POSTGRES_PASSWORD", "test")
        ```
    """
    def decorator(func: Callable[[], GenericContainer]) -> Callable:
        @pytest.fixture(scope=scope)
        @functools.wraps(func)
        def wrapper():
            container = func()
            container.start()
            try:
                yield container
            finally:
                container.stop()
        return wrapper
    return decorator
