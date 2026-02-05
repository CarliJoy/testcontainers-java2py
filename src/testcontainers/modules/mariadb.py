"""
MariaDB container implementation.

This module provides a container for MariaDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mariadb/src/main/java/org/testcontainers/containers/MariaDBContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MariaDBContainer(JdbcDatabaseContainer):
    """
    MariaDB database container.

    This container starts a MariaDB database instance with configurable
    credentials, database name, and configuration options.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mariadb/src/main/java/org/testcontainers/containers/MariaDBContainer.java

    Example:
        >>> with MariaDBContainer() as mariadb:
        ...     url = mariadb.get_jdbc_url()
        ...     host = mariadb.get_host()
        ...     port = mariadb.get_port()
        ...     # Connect to MariaDB

        >>> # Custom configuration
        >>> mariadb = MariaDBContainer("mariadb:11")
        >>> mariadb.with_username("myuser")
        >>> mariadb.with_password("mypass")
        >>> mariadb.with_database_name("mydb")
        >>> mariadb.with_config_option("max_connections", "200")
        >>> mariadb.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "mariadb:11"
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
        Initialize a MariaDB container.

        Args:
            image: Docker image name (default: mariadb:11)
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

        # MariaDB configuration options
        self._config_options: dict[str, str] = {}

        # Set environment variables for MariaDB initialization
        self.with_env("MARIADB_USER", self._username)
        self.with_env("MARIADB_PASSWORD", self._password)
        self.with_env("MARIADB_DATABASE", self._dbname)
        # MariaDB requires a root password
        self.with_env("MARIADB_ROOT_PASSWORD", self._password)

        # Wait for MariaDB to be ready
        # MariaDB logs "ready for connections" when it's ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*ready for connections.*")
        )

    def with_config_option(self, key: str, value: str) -> MariaDBContainer:
        """
        Add a MariaDB configuration option (fluent API).

        Configuration options are passed as command-line arguments to mariadbd.

        Args:
            key: Configuration option name (e.g., "max_connections")
            value: Configuration option value (e.g., "200")

        Returns:
            This container instance
        """
        self._config_options[key] = value
        return self

    def start(self) -> MariaDBContainer:  # type: ignore[override]
        """
        Start the MariaDB container with any configured options.

        Returns:
            This container instance
        """
        # Build command with config options as array to avoid shell injection
        if self._config_options:
            cmd_parts = ["mariadbd"]
            for key, value in self._config_options.items():
                # Use array format to prevent command injection
                cmd_parts.append(f"--{key}={value}")
            self.with_command(cmd_parts)

        super().start()
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for MariaDB.

        Returns:
            MariaDB JDBC driver class name
        """
        return "org.mariadb.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for MariaDB.

        Returns:
            JDBC connection URL in format: jdbc:mariadb://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:mariadb://{host}:{port}/{self._dbname}"

    def get_connection_string(self) -> str:
        """
        Get the MariaDB connection string (Python native format).

        Returns:
            Connection string in format: mariadb://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"mariadb://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
