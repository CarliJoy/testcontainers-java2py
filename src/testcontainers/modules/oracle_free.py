"""
Oracle Database Free container implementation.

This module provides a container for Oracle Database Free edition.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/oracle-free/src/main/java/org/testcontainers/oracle/OracleContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class OracleFreeContainer(JdbcDatabaseContainer):
    """
    Oracle Database Free container.

    This container starts an Oracle Database Free instance. Oracle Database Free
    is the free edition of Oracle Database, suitable for development and testing.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/oracle-free/src/main/java/org/testcontainers/oracle/OracleContainer.java

    Example:
        >>> with OracleFreeContainer() as oracle:
        ...     url = oracle.get_jdbc_url()
        ...     host = oracle.get_host()
        ...     port = oracle.get_port()
        ...     # Connect to Oracle Database

        >>> # Using SID instead of service name
        >>> oracle = OracleFreeContainer()
        >>> oracle.with_using_sid()
        >>> oracle.start()

        >>> # Custom configuration
        >>> oracle = OracleFreeContainer("gvenzl/oracle-free:latest")
        >>> oracle.with_username("myuser")
        >>> oracle.with_password("mypass")
        >>> oracle.with_database_name("mydb")
        >>> oracle.start()

    Notes:
        - Default credentials: test/test
        - Default database: freepdb1
        - Default SID: free
        - System users (system, sys) cannot be used as application usernames
        - Database name cannot be set to 'freepdb1' (reserved as default)
        - When using SID mode, connects to SID instead of pluggable database
    """

    # Default configuration
    DEFAULT_IMAGE = "gvenzl/oracle-free:slim"
    DEFAULT_PORT = 1521
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWORD = "test"
    DEFAULT_DATABASE = "freepdb1"
    DEFAULT_SID = "free"
    DEFAULT_SYSTEM_USER = "system"
    DEFAULT_SYS_USER = "sys"

    # Restricted usernames
    _SYSTEM_USERS = [DEFAULT_SYSTEM_USER, DEFAULT_SYS_USER]

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize an Oracle Database Free container.

        Args:
            image: Docker image name (default: gvenzl/oracle-free:slim)
            username: Application user username (default: test)
            password: Application user password (default: test)
            dbname: Database name (default: freepdb1)

        Raises:
            ValueError: If username is a system user or database name is 'freepdb1'
        """
        super().__init__(
            image=image,
            port=self.DEFAULT_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        self._using_sid = False

        # Wait for Oracle to be ready
        # Oracle Database logs this when it's ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*DATABASE IS READY TO USE!.*")
            .with_times(1)
        )

    def with_username(self, username: str) -> OracleFreeContainer:
        """
        Set the application user username (fluent API).

        System users (system, sys) cannot be used.

        Args:
            username: Application user username

        Returns:
            This container instance

        Raises:
            ValueError: If username is empty or a system user
        """
        if not username:
            raise ValueError("Username cannot be null or empty")

        if username.lower() in self._SYSTEM_USERS:
            raise ValueError(f"Username cannot be one of {self._SYSTEM_USERS}")

        self._username = username
        return self

    def with_password(self, password: str) -> OracleFreeContainer:
        """
        Set the password (fluent API).

        Args:
            password: Password for application user and system users

        Returns:
            This container instance

        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be null or empty")

        self._password = password
        return self

    def with_database_name(self, dbname: str) -> OracleFreeContainer:
        """
        Set the database name (fluent API).

        The database name cannot be set to 'freepdb1' as it's the default.

        Args:
            dbname: Database name

        Returns:
            This container instance

        Raises:
            ValueError: If database name is empty or 'freepdb1'
        """
        if not dbname:
            raise ValueError("Database name cannot be null or empty")

        if dbname.lower() == self.DEFAULT_DATABASE.lower():
            raise ValueError(f"Database name cannot be set to {self.DEFAULT_DATABASE}")

        self._dbname = dbname
        return self

    def with_using_sid(self) -> OracleFreeContainer:
        """
        Configure the container to use SID instead of service name (fluent API).

        When using SID mode, the JDBC URL connects to the SID directly instead
        of a pluggable database, and the username will be 'system' instead of
        the application user.

        Returns:
            This container instance
        """
        self._using_sid = True
        return self

    def start(self) -> OracleFreeContainer:  # type: ignore[override]
        """
        Start the Oracle Database Free container.

        Environment variables are set for:
        - ORACLE_PASSWORD: Password for system users and application user
        - ORACLE_DATABASE: Database name (if not default)
        - APP_USER: Application user name
        - APP_USER_PASSWORD: Application user password

        Returns:
            This container instance
        """
        # Set environment variables for Oracle initialization
        self.with_env("ORACLE_PASSWORD", self._password)

        # Only set ORACLE_DATABASE if different than the default
        if self._dbname != self.DEFAULT_DATABASE:
            self.with_env("ORACLE_DATABASE", self._dbname)

        self.with_env("APP_USER", self._username)
        self.with_env("APP_USER_PASSWORD", self._password)

        super().start()
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for Oracle Database.

        Returns:
            Oracle JDBC driver class name
        """
        return "oracle.jdbc.OracleDriver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for Oracle Database.

        Returns URL with SID format if with_using_sid() was called,
        otherwise returns URL with service name format.

        Returns:
            JDBC connection URL in format:
            - SID mode: jdbc:oracle:thin:@host:port:sid
            - Service mode: jdbc:oracle:thin:@host:port/database
        """
        host = self.get_host()
        port = self.get_port()

        if self._using_sid:
            return f"jdbc:oracle:thin:@{host}:{port}:{self.DEFAULT_SID}"
        else:
            return f"jdbc:oracle:thin:@{host}:{port}/{self._dbname}"

    def get_connection_string(self) -> str:
        """
        Get the Oracle connection string (Python native format).

        Returns:
            Connection string compatible with cx_Oracle/python-oracledb
        """
        host = self.get_host()
        port = self.get_port()
        username = self.get_username()

        if self._using_sid:
            return f"oracle://{username}:{self._password}@{host}:{port}/?service_name={self.DEFAULT_SID}"
        else:
            return f"oracle://{username}:{self._password}@{host}:{port}/?service_name={self._dbname}"

    def get_username(self) -> str:
        """
        Get the username for database connections.

        When using SID mode, returns 'system' since application users
        are tied to pluggable databases. Otherwise returns the configured
        application username.

        Returns:
            Username for connections
        """
        if self._using_sid:
            return self.DEFAULT_SYSTEM_USER
        return self._username

    def get_test_query_string(self) -> str:
        """
        Get the test query string for Oracle Database.

        Returns:
            Test query string
        """
        return "SELECT 1 FROM DUAL"
