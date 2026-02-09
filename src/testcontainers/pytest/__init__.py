"""
Pytest integration for Testcontainers.

This module provides pytest fixtures, markers, and helpers for using
testcontainers in your test suite.

Example usage:
    ```python
    import pytest
    from testcontainers.pytest import container_fixture
    
    # Create a fixture
    postgres = container_fixture(
        "postgres:13",
        ports={5432: None},
        environment={"POSTGRES_PASSWORD": "test"}
    )
    
    @pytest.mark.testcontainers
    def test_database(postgres):
        port = postgres.get_exposed_port(5432)
        # Use database...
    ```

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/junit-jupiter/
"""

from __future__ import annotations

from testcontainers.pytest.pytest_support import container_fixture
from testcontainers.pytest.test_helpers import (
    skip_if_docker_unavailable,
    wait_for_container_ready,
)

__all__ = [
    "container_fixture",
    "skip_if_docker_unavailable",
    "wait_for_container_ready",
]
