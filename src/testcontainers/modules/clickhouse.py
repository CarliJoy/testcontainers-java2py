"""
ClickHouse container implementation.

This module provides a container for ClickHouse OLAP database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/clickhouse/src/main/java/org/testcontainers/clickhouse/ClickHouseContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.http import HttpWaitStrategy


class ClickHouseContainer(JdbcDatabaseContainer):
    """
    ClickHouse OLAP database container.

    This container starts a ClickHouse database instance with configurable
    credentials and database name. ClickHouse is an open-source column-oriented
    database management system.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/clickhouse/src/main/java/org/testcontainers/clickhouse/ClickHouseContainer.java

    Example:
        >>> with ClickHouseContainer() as clickhouse:
        ...     url = clickhouse.get_jdbc_url()
        ...     http_url = clickhouse.get_http_url()
        ...     # Connect to ClickHouse

        >>> # Custom configuration
        >>> clickhouse = ClickHouseContainer("clickhouse/clickhouse-server:23.3")
        >>> clickhouse.with_username("myuser")
        >>> clickhouse.with_password("mypass")
        >>> clickhouse.with_database_name("mydb")
        >>> clickhouse.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "clickhouse/clickhouse-server:latest"
    DEFAULT_HTTP_PORT = 8123
    DEFAULT_NATIVE_PORT = 9000
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWORD = "test"
    DEFAULT_DATABASE = "default"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a ClickHouse container.

        Args:
            image: Docker image name (default: clickhouse/clickhouse-server:latest)
            username: Database username (default: test)
            password: Database password (default: test)
            dbname: Database name (default: default)
        """
        super().__init__(
            image=image,
            port=self.DEFAULT_HTTP_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Expose both HTTP and native ports
        self.with_exposed_ports(self.DEFAULT_NATIVE_PORT)

        # Set environment variables for ClickHouse initialization
        self.with_env("CLICKHOUSE_DB", self._dbname)
        self.with_env("CLICKHOUSE_USER", self._username)
        self.with_env("CLICKHOUSE_PASSWORD", self._password)

        # Wait for ClickHouse HTTP interface to be ready
        # ClickHouse returns "Ok." at the root path when ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/")
            .for_port(self.DEFAULT_HTTP_PORT)
            .for_status_code(200)
            .for_response_predicate(lambda response: response == "Ok.")
            .with_startup_timeout(60)
        )

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for ClickHouse.

        Returns:
            ClickHouse JDBC driver class name
        """
        return "com.clickhouse.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for ClickHouse.

        Returns:
            JDBC connection URL in format: jdbc:clickhouse://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:clickhouse://{host}:{port}/{self._dbname}"

    def get_http_url(self) -> str:
        """
        Get the HTTP connection URL for ClickHouse.

        Returns:
            HTTP URL in format: http://host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"http://{host}:{port}"

    def get_connection_string(self) -> str:
        """
        Get the ClickHouse connection string (Python native format).

        Returns:
            Connection string in format: clickhouse://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"clickhouse://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
