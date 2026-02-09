"""
Oracle XE container module.

Oracle Express Edition (XE) is a free edition of Oracle Database.

Example:
    
    .. code-block:: python

        from testcontainers.modules.oracle_xe import OracleXEContainer

        with OracleXEContainer() as oracle:
            connection_url = oracle.get_connection_url()
            # Use the connection_url to connect to Oracle XE

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/oracle-xe/src/main/java/org/testcontainers/containers/OracleContainer.java
"""

from __future__ import annotations

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.modules.jdbc import JdbcDatabaseContainer


class OracleXEContainer(JdbcDatabaseContainer):
    """
    Oracle XE database container.

    Example:

        .. code-block:: python

            from testcontainers.modules.oracle_xe import OracleXEContainer

            with OracleXEContainer() as oracle:
                connection_url = oracle.get_connection_url()
    """

    # Container defaults
    DEFAULT_DATABASE_NAME = "xepdb1"
    DEFAULT_SID = "xe"
    DEFAULT_SYSTEM_USER = "system"
    DEFAULT_SYS_USER = "sys"
    
    # Test container defaults
    APP_USER = "test"
    APP_USER_PASSWORD = "test"

    # Restricted user names
    ORACLE_SYSTEM_USERS = [DEFAULT_SYSTEM_USER, DEFAULT_SYS_USER]

    def __init__(
        self,
        image: str = "gvenzl/oracle-xe:18.4.0-slim",
        username: str | None = None,
        password: str | None = None,
        dbname: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.username = username or self.APP_USER
        self.password = password or self.APP_USER_PASSWORD
        self.dbname = dbname or self.DEFAULT_DATABASE_NAME
        self.port = 1521
        self.apex_http_port = 8080
        self._using_sid = False

        self.with_exposed_ports(self.port, self.apex_http_port)

    def _configure(self) -> None:
        self.with_env("ORACLE_PASSWORD", self.password)
        
        # Only set ORACLE_DATABASE if different than the default
        if self.dbname != self.DEFAULT_DATABASE_NAME:
            self.with_env("ORACLE_DATABASE", self.dbname)
        
        self.with_env("APP_USER", self.username)
        self.with_env("APP_USER_PASSWORD", self.password)

    def with_username(self, username: str) -> OracleXEContainer:
        """
        Set the username.

        Args:
            username: The username to use

        Returns:
            OracleXEContainer: The container instance

        Raises:
            ValueError: If username is empty or a system user
        """
        if not username:
            raise ValueError("Username cannot be null or empty")
        if username.lower() in self.ORACLE_SYSTEM_USERS:
            raise ValueError(f"Username cannot be one of {self.ORACLE_SYSTEM_USERS}")
        self.username = username
        return self

    def with_password(self, password: str) -> OracleXEContainer:
        """
        Set the password.

        Args:
            password: The password to use

        Returns:
            OracleXEContainer: The container instance

        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be null or empty")
        self.password = password
        return self

    def with_database_name(self, dbname: str) -> OracleXEContainer:
        """
        Set the database name.

        Args:
            dbname: The database name to use

        Returns:
            OracleXEContainer: The container instance

        Raises:
            ValueError: If database name is empty or the default
        """
        if not dbname:
            raise ValueError("Database name cannot be null or empty")
        if dbname.lower() == self.DEFAULT_DATABASE_NAME.lower():
            raise ValueError(f"Database name cannot be set to {self.DEFAULT_DATABASE_NAME}")
        self.dbname = dbname
        return self

    def using_sid(self) -> OracleXEContainer:
        """
        Configure to use SID instead of service name.

        Returns:
            OracleXEContainer: The container instance
        """
        self._using_sid = True
        return self

    def get_connection_url(self, **kwargs) -> str:
        """
        Get the connection URL for Oracle.

        Returns:
            str: Connection URL
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        
        if self._using_sid:
            return f"jdbc:oracle:thin:@{host}:{port}:{self.DEFAULT_SID}"
        else:
            return f"jdbc:oracle:thin:@{host}:{port}/{self.dbname}"

    def get_username(self) -> str:
        """
        Get the username. Returns system user when using SID.

        Returns:
            str: The username
        """
        return self.DEFAULT_SYSTEM_USER if self._using_sid else self.username

    def get_sid(self) -> str:
        """
        Get the Oracle SID.

        Returns:
            str: The SID
        """
        return self.DEFAULT_SID

    def get_oracle_port(self) -> int:
        """
        Get the mapped Oracle port.

        Returns:
            int: The mapped port
        """
        return self.get_exposed_port(self.port)

    def get_web_port(self) -> int:
        """
        Get the mapped APEX HTTP port.

        Returns:
            int: The mapped port
        """
        return self.get_exposed_port(self.apex_http_port)

    def _connect(self) -> None:
        """Wait for Oracle to be ready."""
        wait_for_logs(self, r".*DATABASE IS READY TO USE!.*", timeout=240)

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name.

        Returns:
            str: The driver class name
        """
        return "oracle.jdbc.OracleDriver"
