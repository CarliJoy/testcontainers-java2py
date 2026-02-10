"""
SqlAlchemy wait strategy for database containers.

This module provides a wait strategy that tests database connectivity using SqlAlchemy,
similar to Java's JDBC connection testing in JdbcDatabaseContainer.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/database-commons/src/main/java/org/testcontainers/containers/JdbcDatabaseContainer.java
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable

from testcontainers.waiting.wait_strategy import AbstractWaitStrategy

if TYPE_CHECKING:
    from testcontainers.waiting.wait_strategy import WaitStrategyTarget


class SqlAlchemyWaitStrategy(AbstractWaitStrategy):
    """
    Wait strategy that tests database connectivity using SqlAlchemy.

    This strategy mimics Java's JdbcDatabaseContainer.waitUntilContainerStarted() method,
    which repeatedly attempts to connect to the database and execute a test query.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/database-commons/src/main/java/org/testcontainers/containers/JdbcDatabaseContainer.java

    Example:
        >>> from testcontainers.modules.postgres import PostgreSQLContainer
        >>> from testcontainers.waiting.sqlalchemy import SqlAlchemyWaitStrategy
        >>> postgres = PostgreSQLContainer()
        >>> postgres.waiting_for(
        ...     SqlAlchemyWaitStrategy()
        ...     .with_query("SELECT 1")
        ...     .with_startup_timeout(timedelta(seconds=60))
        ... )
    """

    def __init__(self) -> None:
        """Initialize the SqlAlchemy wait strategy."""
        super().__init__()
        self._test_query: str = "SELECT 1"
        self._connection_url_provider: Callable[[WaitStrategyTarget], str] | None = None
        self._sleep_time: float = 0.1  # 100ms between retries, matching Java

    def with_query(self, query: str) -> SqlAlchemyWaitStrategy:
        """
        Set the test query to execute.

        Args:
            query: SQL query to test database connectivity (default: "SELECT 1")

        Returns:
            This wait strategy for method chaining
        """
        self._test_query = query
        return self

    def with_connection_url_provider(
        self, provider: Callable[[WaitStrategyTarget], str]
    ) -> SqlAlchemyWaitStrategy:
        """
        Set a custom connection URL provider function.

        By default, the strategy will call get_connection_string() on the target.
        Use this to provide a custom URL format if needed.

        Args:
            provider: Function that takes a WaitStrategyTarget and returns a connection URL

        Returns:
            This wait strategy for method chaining
        """
        self._connection_url_provider = provider
        return self

    def _wait_until_ready(self) -> None:
        """
        Wait until database is ready by testing connection with SqlAlchemy.

        This mimics Java's waitUntilContainerStarted() method:
        - Repeatedly tries to open a connection and execute test query
        - Retries until timeout is reached
        - Sleeps 100ms between attempts

        Raises:
            TimeoutError: If database doesn't become ready within timeout
            ImportError: If sqlalchemy is not installed
        """
        try:
            from sqlalchemy import create_engine, text
        except ImportError as e:
            raise ImportError(
                "SqlAlchemy is required for SqlAlchemyWaitStrategy. "
                "Install it with: pip install sqlalchemy"
            ) from e

        if self._wait_strategy_target is None:
            raise RuntimeError("Wait strategy target not set")

        # Get connection URL from target
        if self._connection_url_provider:
            connection_url = self._connection_url_provider(self._wait_strategy_target)
        elif hasattr(self._wait_strategy_target, "get_connection_string"):
            connection_url = self._wait_strategy_target.get_connection_string()  # type: ignore
        else:
            raise RuntimeError(
                "Target must have get_connection_string() method or use "
                "with_connection_url_provider()"
            )

        start_time = time.time()
        timeout_seconds = self._startup_timeout.total_seconds()
        last_exception: Exception | None = None

        while (time.time() - start_time) < timeout_seconds:
            # Wait for container to be running first
            if not self._wait_strategy_target.is_running():
                time.sleep(self._sleep_time)
                continue

            try:
                # Try to connect and execute test query
                # Use pool_pre_ping=False and connect_args with short timeout to fail fast
                engine = create_engine(
                    connection_url,
                    pool_pre_ping=False,
                    connect_args={"connect_timeout": 5},
                )

                with engine.connect() as connection:
                    # Execute test query
                    result = connection.execute(text(self._test_query))
                    result.fetchone()  # Consume the result
                    connection.close()

                engine.dispose()

                # Success! Database is ready
                return

            except Exception as e:
                # Store exception and retry
                last_exception = e
                time.sleep(self._sleep_time)

        # Timeout reached
        error_msg = (
            f"Container is started but database connection failed after "
            f"{timeout_seconds} seconds. URL: {connection_url}"
        )
        if last_exception:
            raise TimeoutError(error_msg) from last_exception
        raise TimeoutError(error_msg)
