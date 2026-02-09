"""
OrientDB container implementation.

This module provides a container for OrientDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/orientdb/src/main/java/org/testcontainers/containers/OrientDBContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class OrientDBContainer(GenericContainer):
    """
    OrientDB database container.

    This container starts an OrientDB instance with binary and HTTP endpoints.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/orientdb/src/main/java/org/testcontainers/containers/OrientDBContainer.java

    Supported image: orientdb

    Exposed ports:
    - Database: 2424
    - Studio: 2480

    Example:
        >>> with OrientDBContainer() as orientdb:
        ...     server_url = orientdb.get_server_url()
        ...     db_url = orientdb.get_db_url()
        ...     # Connect to OrientDB

        >>> # Custom configuration
        >>> orientdb = OrientDBContainer("orientdb:3.2.15")
        >>> orientdb.with_database_name("mydb")
        >>> orientdb.with_server_password("mypassword")
        >>> orientdb.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "orientdb:3.0.24-tp3"
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "admin"
    DEFAULT_SERVER_PASSWORD = "root"
    DEFAULT_DATABASE_NAME = "testcontainers"
    
    # Ports
    DEFAULT_BINARY_PORT = 2424
    DEFAULT_HTTP_PORT = 2480
    
    # Test query
    TEST_QUERY = "SELECT FROM V"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an OrientDB container.

        Args:
            image: Docker image name (default: orientdb:3.0.24-tp3)
        """
        super().__init__(image)

        self._database_name = self.DEFAULT_DATABASE_NAME
        self._server_password = self.DEFAULT_SERVER_PASSWORD
        self._script_path = None

        # Expose OrientDB ports
        self.with_exposed_ports(self.DEFAULT_BINARY_PORT, self.DEFAULT_HTTP_PORT)

        # Set server password environment variable
        self.with_env("ORIENTDB_ROOT_PASSWORD", self._server_password)

        # Wait for OrientDB Studio to be available
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*OrientDB Studio available.*")
            .with_times(1)
        )

    def get_database_name(self) -> str:
        """
        Get the database name.

        Returns:
            Database name
        """
        return self._database_name

    def get_test_query_string(self) -> str:
        """
        Get the test query string for OrientDB.

        Returns:
            Test query string
        """
        return self.TEST_QUERY

    def with_database_name(self, database_name: str) -> OrientDBContainer:
        """
        Set the database name (fluent API).

        Args:
            database_name: Database name

        Returns:
            This container instance
        """
        self._database_name = database_name
        return self

    def with_server_password(self, server_password: str) -> OrientDBContainer:
        """
        Set the server password (fluent API).

        Args:
            server_password: Server root password

        Returns:
            This container instance
        """
        self._server_password = server_password
        # Update environment variable
        self.with_env("ORIENTDB_ROOT_PASSWORD", server_password)
        return self

    def with_script_path(self, script_path: str) -> OrientDBContainer:
        """
        Set the initialization script path (fluent API).

        Args:
            script_path: Path to initialization script

        Returns:
            This container instance
        """
        self._script_path = script_path
        return self

    def get_server_url(self) -> str:
        """
        Get the OrientDB server URL.

        Returns:
            Server URL in format: remote:host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.DEFAULT_BINARY_PORT)
        return f"remote:{host}:{port}"

    def get_db_url(self) -> str:
        """
        Get the OrientDB database URL.

        Returns:
            Database URL in format: remote:host:port/database
        """
        return f"{self.get_server_url()}/{self._database_name}"

    def get_port(self) -> int:
        """
        Get the exposed binary port number on the host.

        Returns:
            Host port number mapped to the binary port
        """
        return self.get_mapped_port(self.DEFAULT_BINARY_PORT)

    def get_http_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self.DEFAULT_HTTP_PORT)
