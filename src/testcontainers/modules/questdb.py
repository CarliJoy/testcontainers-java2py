"""
QuestDB container implementation.

This module provides a container for QuestDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/questdb/src/main/java/org/testcontainers/containers/QuestDBContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class QuestDBContainer(JdbcDatabaseContainer):
    """
    QuestDB database container.

    This container starts a QuestDB instance with support for PostgreSQL wire protocol,
    HTTP REST API, and InfluxDB Line Protocol (ILP).

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/questdb/src/main/java/org/testcontainers/containers/QuestDBContainer.java

    Supported image: questdb/questdb

    Exposed ports:
    - Postgres: 8812
    - HTTP: 9000
    - ILP: 9009

    Example:
        >>> with QuestDBContainer() as questdb:
        ...     jdbc_url = questdb.get_jdbc_url()
        ...     http_url = questdb.get_http_url()
        ...     ilp_url = questdb.get_ilp_url()
        ...     # Connect to QuestDB

        >>> # Custom configuration
        >>> questdb = QuestDBContainer("questdb/questdb:7.3.10")
        >>> questdb.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "questdb/questdb"
    DEFAULT_DATABASE_NAME = "qdb"
    DEFAULT_COMMIT_LAG_MS = 1000
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "quest"
    
    # Ports
    POSTGRES_PORT = 8812
    REST_PORT = 9000
    ILP_PORT = 9009
    
    # Test query
    TEST_QUERY = "SELECT 1"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a QuestDB container.

        Args:
            image: Docker image name (default: questdb/questdb)
        """
        super().__init__(
            image=image,
            port=self.POSTGRES_PORT,
            username=self.DEFAULT_USERNAME,
            password=self.DEFAULT_PASSWORD,
            dbname=self.DEFAULT_DATABASE_NAME,
        )

        # Expose all QuestDB ports
        self.with_exposed_ports(self.POSTGRES_PORT, self.REST_PORT, self.ILP_PORT)

        # Set commit lag environment variable
        self.with_env("QDB_CAIRO_COMMIT_LAG", str(self.DEFAULT_COMMIT_LAG_MS))

        # Wait for QuestDB to be ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r"(?i).*A server-main enjoy.*")
            .with_times(1)
        )

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for QuestDB.
        
        QuestDB uses the PostgreSQL driver for JDBC connections.

        Returns:
            PostgreSQL JDBC driver class name
        """
        return "org.postgresql.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for QuestDB.

        Returns:
            JDBC connection URL in format: jdbc:postgresql://host:port/database
        """
        host = self.get_host()
        port = self.get_mapped_port(self.POSTGRES_PORT)
        return f"jdbc:postgresql://{host}:{port}/{self._dbname}"

    def get_ilp_url(self) -> str:
        """
        Get the InfluxDB Line Protocol (ILP) URL.

        Returns:
            ILP URL in format: host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.ILP_PORT)
        return f"{host}:{port}"

    def get_http_url(self) -> str:
        """
        Get the HTTP REST API URL.

        Returns:
            HTTP URL in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.REST_PORT)
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed PostgreSQL port number on the host.

        Returns:
            Host port number mapped to the PostgreSQL port
        """
        return self.get_mapped_port(self.POSTGRES_PORT)
