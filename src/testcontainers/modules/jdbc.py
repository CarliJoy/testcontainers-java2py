"""
JDBC database container base class.

This module provides the base JdbcDatabaseContainer class for database containers
that support JDBC-style connections.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/database-commons/src/main/java/org/testcontainers/containers/JdbcDatabaseContainer.java
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Dict

from testcontainers.core.generic_container import GenericContainer


class JdbcDatabaseContainer(GenericContainer):
    """
    Base class for JDBC database containers.

    This class provides common functionality for database containers including
    credential management, database configuration, and JDBC URL generation.

    Subclasses should implement:
    - get_driver_class_name() - Return the JDBC driver class name
    - get_jdbc_url() - Return the JDBC connection URL

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/database-commons/src/main/java/org/testcontainers/containers/JdbcDatabaseContainer.java

    Example:
        >>> from testcontainers.modules.postgres import PostgreSQLContainer
        >>> with PostgreSQLContainer() as postgres:
        ...     url = postgres.get_jdbc_url()
        ...     # Connect using url
    """

    def __init__(
        self,
        image: str,
        port: int = 5432,
        username: str = "test",
        password: str = "test",
        dbname: str = "test",
    ):
        """
        Initialize a JDBC database container.

        Args:
            image: Docker image name
            port: Database port number
            username: Database username
            password: Database password
            dbname: Database name
        """
        super().__init__(image)
        self._port = port
        self._username = username
        self._password = password
        self._dbname = dbname
        self._url_parameters: Dict[str, str] = {}
        self._init_scripts: list[str] = []

        # Expose the database port
        self.with_exposed_ports(self._port)

    def with_username(self, username: str) -> JdbcDatabaseContainer:
        """
        Set the database username (fluent API).

        Args:
            username: Database username

        Returns:
            This container instance
        """
        self._username = username
        return self

    def with_password(self, password: str) -> JdbcDatabaseContainer:
        """
        Set the database password (fluent API).

        Args:
            password: Database password

        Returns:
            This container instance
        """
        self._password = password
        return self

    def with_database_name(self, dbname: str) -> JdbcDatabaseContainer:
        """
        Set the database name (fluent API).

        Args:
            dbname: Database name

        Returns:
            This container instance
        """
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
            Database password
        """
        return self._password

    def get_database_name(self) -> str:
        """
        Get the database name.

        Returns:
            Database name
        """
        return self._dbname

    @abstractmethod
    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name.

        Subclasses must implement this to return the appropriate driver name.

        Returns:
            JDBC driver class name
        """
        pass

    @abstractmethod
    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL.

        Subclasses must implement this to return the database-specific URL.

        Returns:
            JDBC connection URL
        """
        pass

    def get_connection_url(self) -> str:
        """
        Get the connection URL (alias for get_jdbc_url).

        Returns:
            Connection URL
        """
        return self.get_jdbc_url()

    def get_port(self) -> int:
        """
        Get the exposed database port number on the host.

        Returns:
            Host port number mapped to the database port
        """
        return self.get_mapped_port(self._port)

    def with_url_param(self, key: str, value: str) -> JdbcDatabaseContainer:
        """
        Add a URL parameter to the JDBC connection URL (fluent API).

        This method allows adding custom JDBC URL parameters like SSL settings,
        timeouts, character encoding, etc.

        Args:
            key: Parameter name
            value: Parameter value

        Returns:
            This container instance

        Example:
            >>> container.with_url_param("useSSL", "false")
            >>> container.with_url_param("connectTimeout", "5000")
        """
        self._url_parameters[key] = value
        return self

    def with_init_script(self, script_path: str) -> JdbcDatabaseContainer:
        """
        Add an initialization script to run when the database starts (fluent API).

        The script will be executed after the database is ready. This is useful
        for creating schemas, inserting test data, etc.

        Args:
            script_path: Path to the SQL script file

        Returns:
            This container instance

        Example:
            >>> container.with_init_script("init.sql")
        """
        self._init_scripts = [script_path]
        return self

    def with_init_scripts(self, *script_paths: str) -> JdbcDatabaseContainer:
        """
        Add multiple initialization scripts to run when the database starts (fluent API).

        Scripts will be executed in the order provided.

        Args:
            *script_paths: Paths to SQL script files

        Returns:
            This container instance

        Example:
            >>> container.with_init_scripts("schema.sql", "data.sql")
        """
        self._init_scripts = list(script_paths)
        return self

    def _construct_url_parameters(self, start_char: str = "?", delimiter: str = "&") -> str:
        """
        Construct URL parameters string from the configured parameters.

        This is a helper method for subclasses to build JDBC URLs with parameters.

        Args:
            start_char: Character to start the parameters (default: "?")
            delimiter: Character to separate parameters (default: "&")

        Returns:
            URL parameters string, or empty string if no parameters

        Example:
            >>> # With parameters: {"useSSL": "false", "connectTimeout": "5000"}
            >>> # Returns: "?useSSL=false&connectTimeout=5000"
        """
        if not self._url_parameters:
            return ""

        params = [f"{key}={value}" for key, value in self._url_parameters.items()]
        return start_char + delimiter.join(params)
