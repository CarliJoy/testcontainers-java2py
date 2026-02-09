"""
MS SQL Server container implementation.

This module provides a container for Microsoft SQL Server databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mssqlserver/src/main/java/org/testcontainers/containers/MSSQLServerContainer.java
"""

from __future__ import annotations

import re

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MSSQLServerContainer(JdbcDatabaseContainer):
    """
    MS SQL Server database container.

    This container starts a Microsoft SQL Server database instance.
    Requires license acceptance via with_accept_license() or
    TESTCONTAINERS_MSSQLSERVER_ACCEPT_EULA environment variable.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mssqlserver/src/main/java/org/testcontainers/containers/MSSQLServerContainer.java

    Example:
        >>> with MSSQLServerContainer().with_accept_license() as mssql:
        ...     url = mssql.get_jdbc_url()
        ...     host = mssql.get_host()
        ...     port = mssql.get_port()
        ...     # Connect to MS SQL Server

        >>> # Custom configuration
        >>> mssql = MSSQLServerContainer("mcr.microsoft.com/mssql/server:2022-latest")
        >>> mssql.with_accept_license()
        >>> mssql.with_password("MyStr0ng_Pass123!")
        >>> mssql.start()

    Security considerations:
        - MS SQL Server requires license acceptance (EULA)
        - Default password meets complexity requirements:
          * At least 8 characters, max 128 characters
          * Must contain characters from 3 of these categories:
            - Uppercase letters (A-Z)
            - Lowercase letters (a-z)
            - Digits (0-9)
            - Non-alphanumeric characters (!@#$%^&*()_+-)
    """

    # Default configuration
    DEFAULT_IMAGE = "mcr.microsoft.com/mssql/server:2022-latest"
    DEFAULT_PORT = 1433
    DEFAULT_USERNAME = "sa"
    DEFAULT_PASSWORD = "A_Str0ng_Required_Password"

    # Password validation patterns
    _PASSWORD_PATTERNS = [
        re.compile(r"[A-Z]+"),
        re.compile(r"[a-z]+"),
        re.compile(r"[0-9]+"),
        re.compile(r"[^a-zA-Z0-9]+", re.IGNORECASE),
    ]

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
    ):
        """
        Initialize a MS SQL Server container.

        Args:
            image: Docker image name (default: mcr.microsoft.com/mssql/server:2022-latest)
            username: Database username (default: sa)
            password: Database password (must meet complexity requirements)

        Raises:
            ValueError: If password doesn't meet complexity requirements
        """
        # Validate password before initialization
        self._check_password_strength(password)

        super().__init__(
            image=image,
            port=self.DEFAULT_PORT,
            username=username,
            password=password,
            dbname="master",  # MS SQL Server uses 'master' as default
        )

        self._license_accepted = False

        # Set environment variables
        self.with_env("MSSQL_SA_PASSWORD", password)

        # Wait for SQL Server to be ready
        # SQL Server logs this when ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*SQL Server is now ready for client connections.*")
            .with_times(1)
        )

    def with_accept_license(self) -> MSSQLServerContainer:
        """
        Accept the MS SQL Server End-User License Agreement (fluent API).

        This sets the ACCEPT_EULA environment variable to Y as required by
        the SQL Server container image.

        Returns:
            This container instance

        See also:
            https://hub.docker.com/_/microsoft-mssql-server
        """
        self._license_accepted = True
        self.with_env("ACCEPT_EULA", "Y")
        return self

    def with_password(self, password: str) -> MSSQLServerContainer:
        """
        Set the SA password (fluent API).

        The password must meet SQL Server complexity requirements:
        - At least 8 characters, max 128 characters
        - Must contain characters from 3 of these 4 categories:
          * Uppercase letters (A-Z)
          * Lowercase letters (a-z)
          * Digits (0-9)
          * Non-alphanumeric characters

        Args:
            password: Database password

        Returns:
            This container instance

        Raises:
            ValueError: If password doesn't meet complexity requirements
        """
        self._check_password_strength(password)
        self._password = password
        self.with_env("MSSQL_SA_PASSWORD", password)
        return self

    def start(self) -> MSSQLServerContainer:  # type: ignore[override]
        """
        Start the MS SQL Server container.

        Returns:
            This container instance

        Raises:
            RuntimeError: If license has not been accepted
        """
        if not self._license_accepted:
            raise RuntimeError(
                "MS SQL Server license must be accepted. Call with_accept_license() "
                "or set TESTCONTAINERS_MSSQLSERVER_ACCEPT_EULA environment variable. "
                "See https://hub.docker.com/_/microsoft-mssql-server"
            )

        super().start()
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for MS SQL Server.

        Returns:
            MS SQL Server JDBC driver class name
        """
        return "com.microsoft.sqlserver.jdbc.SQLServerDriver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for MS SQL Server.

        The URL includes encrypt=false to work with the default container configuration
        without requiring TLS certificates.

        Returns:
            JDBC connection URL in format: jdbc:sqlserver://host:port;encrypt=false
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:sqlserver://{host}:{port};encrypt=false;trustServerCertificate=true"

    def get_connection_string(self) -> str:
        """
        Get the MS SQL Server connection string (Python native format).

        Returns:
            Connection string in format: mssql+pyodbc://user:pass@host:port/master?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
        """
        host = self.get_host()
        port = self.get_port()
        return f"mssql+pyodbc://{self._username}:{self._password}@{host}:{port}/{self._dbname}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"

    @staticmethod
    def _check_password_strength(password: str) -> None:
        """
        Validate password meets SQL Server complexity requirements.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if password is None:
            raise ValueError("Password cannot be None")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(password) > 128:
            raise ValueError("Password can be up to 128 characters long")

        # Check how many password categories are satisfied
        satisfied_categories = sum(
            1 for pattern in MSSQLServerContainer._PASSWORD_PATTERNS if pattern.search(password)
        )

        if satisfied_categories < 3:
            raise ValueError(
                "Password must contain characters from three of the following four categories:\n"
                " - Latin uppercase letters (A through Z)\n"
                " - Latin lowercase letters (a through z)\n"
                " - Base 10 digits (0 through 9)\n"
                " - Non-alphanumeric characters such as: exclamation point (!), "
                "dollar sign ($), number sign (#), or percent (%)"
            )
