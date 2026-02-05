"""
MySQL container implementation.

This module provides a container for MySQL databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MySQLContainer(JdbcDatabaseContainer):
    """
    MySQL database container.

    This container starts a MySQL database instance with configurable
    credentials, database name, and configuration options.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java

    Example:
        >>> with MySQLContainer() as mysql:
        ...     url = mysql.get_jdbc_url()
        ...     host = mysql.get_host()
        ...     port = mysql.get_port()
        ...     # Connect to MySQL

        >>> # Custom configuration
        >>> mysql = MySQLContainer("mysql:8.0")
        >>> mysql.with_username("myuser")
        >>> mysql.with_password("mypass")
        >>> mysql.with_database_name("mydb")
        >>> mysql.with_config_option("max_connections", "200")
        >>> mysql.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "mysql:8"
    DEFAULT_PORT = 3306
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
        Initialize a MySQL container.

        Args:
            image: Docker image name (default: mysql:8)
            username: Database username (default: test)
            password: Database password (default: test)
            dbname: Database name (default: test)
        """
        super().__init__(
            image=image,
            port=self.DEFAULT_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # MySQL configuration options
        self._config_options: dict[str, str] = {}

        # Set environment variables for MySQL initialization
        self.with_env("MYSQL_USER", self._username)
        self.with_env("MYSQL_PASSWORD", self._password)
        self.with_env("MYSQL_DATABASE", self._dbname)
        # MySQL requires a root password
        self.with_env("MYSQL_ROOT_PASSWORD", self._password)

        # Wait for MySQL to be ready
        # MySQL logs "ready for connections" when it's ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*ready for connections.*")
            .with_times(2)  # MySQL logs this twice during startup (once for each phase)
        )

    def with_config_option(self, key: str, value: str) -> MySQLContainer:
        """
        Add a MySQL configuration option (fluent API).

        Configuration options are passed as command-line arguments to mysqld.

        Args:
            key: Configuration option name (e.g., "max_connections")
            value: Configuration option value (e.g., "200")

        Returns:
            This container instance
        """
        self._config_options[key] = value
        return self

    def start(self) -> MySQLContainer:  # type: ignore[override]
        """
        Start the MySQL container with any configured options.

        Returns:
            This container instance
        """
        # Build command with config options
        if self._config_options:
            cmd_parts = ["mysqld"]
            for key, value in self._config_options.items():
                cmd_parts.append(f"--{key}={value}")
            self.with_command(cmd_parts)

        super().start()
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for MySQL.

        Returns:
            MySQL JDBC driver class name
        """
        return "com.mysql.cj.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for MySQL.

        Returns:
            JDBC connection URL in format: jdbc:mysql://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:mysql://{host}:{port}/{self._dbname}"

    def get_connection_string(self) -> str:
        """
        Get the MySQL connection string (Python native format).

        Returns:
            Connection string in format: mysql://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"mysql://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
