"""
Example conftest.py for using Testcontainers with pytest.

Copy this file to your tests/ directory and customize as needed.
"""

from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
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


def postgres_session() -> Iterator[GenericContainer]:
    """Session-scoped PostgreSQL container."""
    # Import pytest here
    import pytest as pytest_module
    
    @pytest_module.fixture(scope="session")
    def _fixture() -> Iterator[GenericContainer]:
        with GenericContainer("postgres:13") as container:
            container.with_exposed_ports(5432)
            container.with_env("POSTGRES_PASSWORD", "test")
            container.with_env("POSTGRES_DB", "testdb")
            yield container
    return _fixture  # type: ignore[return-value]


def redis_module() -> Iterator[GenericContainer]:
    """Module-scoped Redis container."""
    # Import pytest here
    import pytest as pytest_module
    
    @pytest_module.fixture(scope="module")
    def _fixture() -> Iterator[GenericContainer]:
        with GenericContainer("redis:6") as container:
            container.with_exposed_ports(6379)
            yield container
    return _fixture  # type: ignore[return-value]


def mysql() -> Iterator[GenericContainer]:
    """MySQL container with custom wait strategy."""
    # Import pytest here
    import pytest as pytest_module
    
    @pytest_module.fixture
    def _fixture() -> Iterator[GenericContainer]:
        from testcontainers.waiting import LogMessageWaitStrategy
        
        with GenericContainer("mysql:8") as container:
            container.with_exposed_ports(3306)
            container.with_env("MYSQL_ROOT_PASSWORD", "test")
            container.with_env("MYSQL_DATABASE", "testdb")
            container.with_wait_strategy(
                LogMessageWaitStrategy("port: 3306  MySQL Community Server")
            )
            yield container
    return _fixture  # type: ignore[return-value]


def nginx() -> Iterator[GenericContainer]:
    """Nginx container with volume mount."""
    # Import pytest here
    import pytest as pytest_module
    
    @pytest_module.fixture
    def _fixture() -> Iterator[GenericContainer]:
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
    return _fixture  # type: ignore[return-value]


def postgres_reusable() -> Iterator[GenericContainer]:
    """Reusable PostgreSQL container (persists between test runs)."""
    # Import pytest here
    import pytest as pytest_module
    
    @pytest_module.fixture(scope="session")
    def _fixture() -> Iterator[GenericContainer]:
        with GenericContainer("postgres:13") as container:
            container.with_exposed_ports(5432)
            container.with_env("POSTGRES_PASSWORD", "test")
            container.with_reuse(True)  # Enable container reuse
            yield container
    return _fixture  # type: ignore[return-value]

