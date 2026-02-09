"""
CrateDB database container implementation.

This module provides a container for CrateDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/cratedb/src/main/java/org/testcontainers/cratedb/CrateDBContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.http import HttpWaitStrategy


class CrateDBContainer(JdbcDatabaseContainer):
    """
    CrateDB database container.

    This container starts a CrateDB database instance with configurable
    credentials and database name. CrateDB is compatible with PostgreSQL protocol.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/cratedb/src/main/java/org/testcontainers/cratedb/CrateDBContainer.java

    Supported image: crate

    Exposed ports:
    - Database: 5432 (PostgreSQL protocol)
    - Console: 4200 (HTTP API)

    Example:
        >>> with CrateDBContainer() as cratedb:
        ...     url = cratedb.get_jdbc_url()
        ...     http_port = cratedb.get_http_port()
        ...     # Connect to CrateDB

        >>> # Custom configuration
        >>> cratedb = CrateDBContainer("crate:5.3.1")
        >>> cratedb.with_username("myuser")
        >>> cratedb.with_database_name("mydb")
        >>> cratedb.start()
    """

    DEFAULT_IMAGE = "crate"
    DEFAULT_TAG = "5.3.1"
    CRATEDB_PG_PORT = 5432
    CRATEDB_HTTP_PORT = 4200
    DEFAULT_USERNAME = "crate"
    DEFAULT_PASSWORD = "crate"
    DEFAULT_DATABASE = "crate"

    def __init__(
        self,
        image: str = f"{DEFAULT_IMAGE}:{DEFAULT_TAG}",
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a CrateDB container.

        Args:
            image: Docker image name (default: crate:5.3.1)
            username: Database username (default: crate)
            password: Database password (default: crate)
            dbname: Database name (default: crate)
        """
        super().__init__(
            image=image,
            port=self.CRATEDB_PG_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Expose both PostgreSQL protocol port and HTTP port
        self.with_exposed_ports(self.CRATEDB_PG_PORT)
        self.with_exposed_ports(self.CRATEDB_HTTP_PORT)

        # Set command for single-node discovery
        self.with_command("crate -C discovery.type=single-node")

        # Wait for HTTP endpoint to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/")
            .for_port(self.CRATEDB_HTTP_PORT)
            .for_status_code(200)
        )

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for CrateDB.

        CrateDB uses PostgreSQL wire protocol.

        Returns:
            PostgreSQL JDBC driver class name
        """
        return "org.postgresql.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for CrateDB.

        Returns:
            JDBC connection URL in format: jdbc:postgresql://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:postgresql://{host}:{port}/{self._dbname}"

    def get_http_port(self) -> int:
        """
        Get the mapped HTTP API port.

        Returns:
            Mapped HTTP port number
        """
        return self.get_mapped_port(self.CRATEDB_HTTP_PORT)

    def get_test_query_string(self) -> str:
        """
        Get the test query for validating the CrateDB connection.

        Returns:
            Test query string
        """
        return "SELECT 1"

    def get_connection_string(self) -> str:
        """
        Get the CrateDB connection string (Python native format).

        Returns:
            Connection string in format: postgresql://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"postgresql://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
