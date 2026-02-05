"""
Example conftest.py for using Testcontainers with pytest.

Copy this file to your tests/ directory and customize as needed.
"""

from __future__ import annotations

import pytest

from testcontainers.core import GenericContainer
from testcontainers.pytest import container_fixture


# Simple function-scoped fixture
postgres = container_fixture(
    "postgres:13",
    ports={5432: None},
    environment={"POSTGRES_PASSWORD": "test"},
    scope="function"
)


# Session-scoped fixture (shared across all tests)
@pytest.fixture(scope="session")
def postgres_session():
    """Session-scoped PostgreSQL container."""
    with GenericContainer("postgres:13") as container:
        container.with_exposed_ports(5432)
        container.with_env("POSTGRES_PASSWORD", "test")
        container.with_env("POSTGRES_DB", "testdb")
        yield container


# Module-scoped fixture (shared within a test module)
@pytest.fixture(scope="module")
def redis_module():
    """Module-scoped Redis container."""
    with GenericContainer("redis:6") as container:
        container.with_exposed_ports(6379)
        yield container


# Custom fixture with wait strategy
@pytest.fixture
def mysql():
    """MySQL container with custom wait strategy."""
    from testcontainers.waiting import LogMessageWaitStrategy
    
    with GenericContainer("mysql:8") as container:
        container.with_exposed_ports(3306)
        container.with_env("MYSQL_ROOT_PASSWORD", "test")
        container.with_env("MYSQL_DATABASE", "testdb")
        container.with_wait_strategy(
            LogMessageWaitStrategy("port: 3306  MySQL Community Server")
        )
        yield container


# Fixture with custom configuration
@pytest.fixture
def nginx():
    """Nginx container with volume mount."""
    import tempfile
    import os
    
    # Create temp directory for nginx config
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create simple index.html
        index_path = os.path.join(tmpdir, "index.html")
        with open(index_path, "w") as f:
            f.write("<html><body>Test</body></html>")
        
        with GenericContainer("nginx:alpine") as container:
            container.with_exposed_ports(80)
            container.with_volume_mapping(tmpdir, "/usr/share/nginx/html", "ro")
            yield container


# Reusable container fixture
@pytest.fixture(scope="session")
def postgres_reusable():
    """Reusable PostgreSQL container (persists between test runs)."""
    with GenericContainer("postgres:13") as container:
        container.with_exposed_ports(5432)
        container.with_env("POSTGRES_PASSWORD", "test")
        container.with_reuse(True)  # Enable container reuse
        yield container
