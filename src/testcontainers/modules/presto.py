"""
Presto container implementation.

This module provides a container for Presto SQL query engine.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/presto/src/main/java/org/testcontainers/containers/PrestoContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class PrestoContainer(JdbcDatabaseContainer):
    """
    Presto SQL query engine container.

    This container provides access to Presto (now TrinoDB) for distributed SQL queries.

    Note: Presto is deprecated. Use TrinoContainer instead.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/presto/src/main/java/org/testcontainers/containers/PrestoContainer.java

    Example:
        >>> with PrestoContainer() as presto:
        ...     jdbc_url = presto.get_jdbc_url()
        ...     # Connect to Presto

        >>> # Custom image
        >>> presto = PrestoContainer("ghcr.io/trinodb/presto:344")
        >>> presto.with_username("admin")
        >>> presto.with_database_name("myschema")
        >>> presto.start()

    Supported image:
        - ghcr.io/trinodb/presto
    """

    DEFAULT_IMAGE = "ghcr.io/trinodb/presto"
    DEFAULT_TAG = "344"
    PRESTO_PORT = 8080

    def __init__(self, image: str = f"{DEFAULT_IMAGE}:{DEFAULT_TAG}"):
        """
        Initialize a Presto container.

        Args:
            image: Docker image name (default: ghcr.io/trinodb/presto:344)
        """
        super().__init__(image, port=self.PRESTO_PORT, username="test", password="", dbname="")

        self._catalog: str | None = None

        # Wait for Presto to be ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*======== SERVER STARTED ========.*")
            .with_times(1)
            .with_startup_timeout(60)
        )

    def with_username(self, username: str) -> PrestoContainer:
        """
        Set the database username (fluent API).

        Args:
            username: Database username

        Returns:
            This container instance
        """
        self._username = username
        return self

    def with_database_name(self, dbname: str) -> PrestoContainer:
        """
        Set the catalog/database name (fluent API).

        Args:
            dbname: Catalog name

        Returns:
            This container instance
        """
        self._catalog = dbname
        self._dbname = dbname
        return self

    def get_username(self) -> str:
        """
        Get the database username.

        Returns:
            Database username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the database password.

        Presto does not support password authentication without TLS.

        Returns:
            Empty string
        """
        return ""

    def get_database_name(self) -> str:
        """
        Get the catalog name.

        Returns:
            Catalog name
        """
        return self._catalog or ""

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name.

        Returns:
            JDBC driver class name
        """
        return "io.prestosql.jdbc.PrestoDriver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL.

        Returns:
            JDBC connection URL
        """
        return f"jdbc:presto://{self.get_host()}:{self.get_port()}/{self._catalog or ''}"

    def get_test_query_string(self) -> str:
        """
        Get a test query string.

        Returns:
            Test query string
        """
        return "SELECT count(*) FROM tpch.tiny.nation"
