"""
TiDB distributed SQL database container implementation.

This module provides a container for TiDB distributed SQL database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/tidb/src/main/java/org/testcontainers/tidb/TiDBContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.http import HttpWaitStrategy


class TiDBContainer(JdbcDatabaseContainer):
    """
    TiDB distributed SQL database container.

    TiDB is MySQL-compatible and uses the MySQL JDBC driver.
    This container starts a TiDB instance with MySQL protocol support.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/tidb/src/main/java/org/testcontainers/tidb/TiDBContainer.java

    Example:
        >>> with TiDBContainer() as tidb:
        ...     url = tidb.get_jdbc_url()
        ...     host = tidb.get_host()
        ...     port = tidb.get_port()
        ...     # Connect to TiDB

        >>> # Custom image version
        >>> tidb = TiDBContainer("pingcap/tidb:v7.5.0")
        >>> tidb.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "pingcap/tidb"
    TIDB_PORT = 4000
    REST_API_PORT = 10080

    # Fixed credentials (TiDB doesn't support custom credentials in Docker)
    DEFAULT_USERNAME = "root"
    DEFAULT_PASSWORD = ""
    DEFAULT_DATABASE = "test"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a TiDB container.

        Args:
            image: Docker image name (default: pingcap/tidb)
        """
        super().__init__(
            image=image,
            port=self.TIDB_PORT,
            username=self.DEFAULT_USERNAME,
            password=self.DEFAULT_PASSWORD,
            dbname=self.DEFAULT_DATABASE,
        )

        # Expose both database and REST API ports
        self.with_exposed_ports(self.TIDB_PORT, self.REST_API_PORT)

        # Wait for TiDB to be ready via HTTP status endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/status")
            .for_port(self.REST_API_PORT)
            .for_status_code(200)
            .with_startup_timeout(60.0)
        )

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for TiDB.

        TiDB uses the MySQL JDBC driver.

        Returns:
            MySQL JDBC driver class name
        """
        return "com.mysql.cj.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for TiDB.

        Returns:
            JDBC connection URL in format: jdbc:mysql://host:port/database?useSSL=false&allowPublicKeyRetrieval=true
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:mysql://{host}:{port}/{self._dbname}?useSSL=false&allowPublicKeyRetrieval=true"

    def get_connection_string(self) -> str:
        """
        Get the TiDB connection string (Python native format).

        Returns:
            Connection string in format: mysql://root@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        # Empty password, so no password in connection string
        return f"mysql://{self._username}@{host}:{port}/{self._dbname}"

    def with_database_name(self, dbname: str) -> TiDBContainer:
        """
        Set database name.

        Note: The TiDB docker image does not currently support custom database names.
        This method will raise an exception.

        Args:
            dbname: Database name

        Raises:
            NotImplementedError: TiDB doesn't support custom database names
        """
        raise NotImplementedError("The TiDB docker image does not currently support this")

    def with_username(self, username: str) -> TiDBContainer:
        """
        Set username.

        Note: The TiDB docker image does not currently support custom usernames.
        This method will raise an exception.

        Args:
            username: Username

        Raises:
            NotImplementedError: TiDB doesn't support custom usernames
        """
        raise NotImplementedError("The TiDB docker image does not currently support this")

    def with_password(self, password: str) -> TiDBContainer:
        """
        Set password.

        Note: The TiDB docker image does not currently support custom passwords.
        This method will raise an exception.

        Args:
            password: Password

        Raises:
            NotImplementedError: TiDB doesn't support custom passwords
        """
        raise NotImplementedError("The TiDB docker image does not currently support this")
