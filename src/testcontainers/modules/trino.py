"""
Trino container implementation.

This module provides a container for Trino SQL query engine (fork of Presto).

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/trino/src/main/java/org/testcontainers/trino/TrinoContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer


class TrinoContainer(JdbcDatabaseContainer):
    """
    Trino SQL query engine container.

    This container provides access to Trino for distributed SQL queries.
    Trino is a fork of Presto.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/trino/src/main/java/org/testcontainers/trino/TrinoContainer.java

    Example:
        >>> with TrinoContainer() as trino:
        ...     jdbc_url = trino.get_jdbc_url()
        ...     # Connect to Trino

        >>> # Custom image
        >>> trino = TrinoContainer("trinodb/trino:352")
        >>> trino.with_username("admin")
        >>> trino.with_database_name("myschema")
        >>> trino.start()

    Supported image:
        - trinodb/trino

    Exposed ports:
        - 8080
    """

    DEFAULT_IMAGE = "trinodb/trino"
    DEFAULT_TAG = "352"
    TRINO_PORT = 8080

    def __init__(self, image: str = f"{DEFAULT_IMAGE}:{DEFAULT_TAG}"):
        """
        Initialize a Trino container.

        Args:
            image: Docker image name (default: trinodb/trino:352)
        """
        super().__init__(image, port=self.TRINO_PORT, username="test", password="", dbname="")

        self._catalog: str | None = None

    def with_username(self, username: str) -> TrinoContainer:
        """
        Set the database username (fluent API).

        Args:
            username: Database username

        Returns:
            This container instance
        """
        self._username = username
        return self

    def with_database_name(self, dbname: str) -> TrinoContainer:
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
        return "io.trino.jdbc.TrinoDriver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL.

        Returns:
            JDBC connection URL
        """
        return f"jdbc:trino://{self.get_host()}:{self.get_port()}/{self._catalog or ''}"

    def get_test_query_string(self) -> str:
        """
        Get a test query string.

        Returns:
            Test query string
        """
        return "SELECT count(*) FROM tpch.tiny.nation"
