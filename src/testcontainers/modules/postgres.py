"""
PostgreSQL container implementation.

This module provides a container for PostgreSQL databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/postgresql/src/main/java/org/testcontainers/containers/PostgreSQLContainer.java
"""

from __future__ import annotations

from datetime import timedelta

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class PostgreSQLContainer(JdbcDatabaseContainer):
    """
    PostgreSQL database container.

    This container starts a PostgreSQL database instance with configurable
    credentials and database name.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/postgresql/src/main/java/org/testcontainers/containers/PostgreSQLContainer.java

    Example:
        >>> with PostgreSQLContainer() as postgres:
        ...     url = postgres.get_jdbc_url()
        ...     host = postgres.get_host()
        ...     port = postgres.get_port()
        ...     # Connect to PostgreSQL

        >>> # Custom configuration
        >>> postgres = PostgreSQLContainer("postgres:15")
        >>> postgres.with_username("myuser")
        >>> postgres.with_password("mypass")
        >>> postgres.with_database_name("mydb")
        >>> postgres.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "postgres:9.6.12"
    POSTGRESQL_PORT = 5432
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWORD = "test"
    DEFAULT_DATABASE = "test"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a PostgreSQL container.

        Args:
            image: Docker image name (default: postgres:9.6.12)
            username: Database username (default: test)
            password: Database password (default: test)
            dbname: Database name (default: test)
        """
        super().__init__(
            image=image,
            port=self.POSTGRESQL_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Explicitly add exposed port like Java does
        self.with_exposed_ports(self.POSTGRESQL_PORT)

        # Set command with fsync=off like Java does
        self.with_command(["postgres", "-c", "fsync=off"])

        # Set environment variables for PostgreSQL initialization
        self.with_env("POSTGRES_USER", self._username)
        self.with_env("POSTGRES_PASSWORD", self._password)
        self.with_env("POSTGRES_DB", self._dbname)

        # Wait for PostgreSQL to be ready with timeout matching Java (60 seconds)
        # PostgreSQL logs "database system is ready to accept connections" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*database system is ready to accept connections.*")
            .with_times(2)  # PostgreSQL logs this twice during startup
            .with_startup_timeout(timedelta(seconds=60))
        )

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for PostgreSQL.

        Returns:
            PostgreSQL JDBC driver class name
        """
        return "org.postgresql.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for PostgreSQL.

        Returns:
            JDBC connection URL in format: jdbc:postgresql://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:postgresql://{host}:{port}/{self._dbname}"

    def get_connection_string(self) -> str:
        """
        Get the PostgreSQL connection string (Python native format).

        Returns:
            Connection string in format: postgresql://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"postgresql://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
