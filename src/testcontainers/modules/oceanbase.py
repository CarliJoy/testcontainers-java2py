"""
OceanBase database container implementation.

This module provides a container for OceanBase Community Edition database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/oceanbase/src/main/java/org/testcontainers/oceanbase/OceanBaseCEContainer.java
"""

from __future__ import annotations

from enum import Enum

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class OceanBaseMode(Enum):
    """
    OceanBase deployment modes.

    - NORMAL: Use as much hardware resources as possible for deployment,
              all environment variables are available.
    - MINI: Use the minimum hardware resources for deployment,
            all environment variables are available.
    - SLIM: Use minimal hardware resources and pre-built deployment files for quick startup,
            password of user tenant is the only available environment variable.
    """
    NORMAL = "normal"
    MINI = "mini"
    SLIM = "slim"


class OceanBaseCEContainer(JdbcDatabaseContainer):
    """
    OceanBase Community Edition database container.

    This container starts an OceanBase CE database instance with configurable
    deployment mode, tenant name, and credentials.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/oceanbase/src/main/java/org/testcontainers/oceanbase/OceanBaseCEContainer.java

    Example:
        >>> with OceanBaseCEContainer() as oceanbase:
        ...     url = oceanbase.get_jdbc_url()
        ...     username = oceanbase.get_username()
        ...     password = oceanbase.get_password()
        ...     # Connect to OceanBase

        >>> # Custom configuration
        >>> oceanbase = OceanBaseCEContainer("oceanbase/oceanbase-ce:latest")
        >>> oceanbase.with_mode(OceanBaseMode.MINI)
        >>> oceanbase.with_tenant_name("mytenant")
        >>> oceanbase.with_password("mypassword")
        >>> oceanbase.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "oceanbase/oceanbase-ce"
    SQL_PORT = 2881
    RPC_PORT = 2882
    DEFAULT_TENANT_NAME = "test"
    DEFAULT_USER = "root"
    DEFAULT_PASSWORD = ""
    DEFAULT_DATABASE_NAME = "test"

    # Supported JDBC drivers (in order of preference)
    OCEANBASE_JDBC_DRIVER = "com.oceanbase.jdbc.Driver"
    OCEANBASE_LEGACY_JDBC_DRIVER = "com.alipay.oceanbase.jdbc.Driver"
    MYSQL_JDBC_DRIVER = "com.mysql.cj.jdbc.Driver"
    MYSQL_LEGACY_JDBC_DRIVER = "com.mysql.jdbc.Driver"

    SUPPORTED_DRIVERS = [
        OCEANBASE_JDBC_DRIVER,
        OCEANBASE_LEGACY_JDBC_DRIVER,
        MYSQL_JDBC_DRIVER,
        MYSQL_LEGACY_JDBC_DRIVER,
    ]

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an OceanBase CE container.

        Args:
            image: Docker image name (default: oceanbase/oceanbase-ce)
        """
        # Initialize with SQL port, but we'll also expose RPC port
        super().__init__(
            image=image,
            port=self.SQL_PORT,
            username=self.DEFAULT_USER,
            password=self.DEFAULT_PASSWORD,
            dbname=self.DEFAULT_DATABASE_NAME
        )

        self._mode = OceanBaseMode.SLIM
        self._tenant_name = self.DEFAULT_TENANT_NAME
        self._password = self.DEFAULT_PASSWORD

        # Expose both SQL and RPC ports
        self.with_exposed_ports(self.SQL_PORT, self.RPC_PORT)

        # Wait for boot success message
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*boot success!.*")
        )

    def with_mode(self, mode: OceanBaseMode) -> OceanBaseCEContainer:
        """
        Set the OceanBase deployment mode (fluent API).

        Args:
            mode: Deployment mode (NORMAL, MINI, or SLIM)

        Returns:
            This container instance
        """
        self._mode = mode
        return self

    def with_tenant_name(self, tenant_name: str) -> OceanBaseCEContainer:
        """
        Set the tenant name (fluent API).

        Note: Tenant name is not configurable in SLIM mode and will be ignored.

        Args:
            tenant_name: Tenant name

        Returns:
            This container instance
        """
        self._tenant_name = tenant_name
        return self

    def with_password(self, password: str) -> OceanBaseCEContainer:  # type: ignore[override]
        """
        Set the tenant password (fluent API).

        Args:
            password: Tenant password

        Returns:
            This container instance
        """
        self._password = password
        return self

    def start(self) -> OceanBaseCEContainer:  # type: ignore[override]
        """
        Start the OceanBase container with any configured options.

        Returns:
            This container instance
        """
        # Configure environment variables
        self.with_env("MODE", self._mode.value)

        if self._tenant_name != self.DEFAULT_TENANT_NAME:
            if self._mode == OceanBaseMode.SLIM:
                # In SLIM mode, tenant name is not configurable
                # Reset to default to ensure constructed username is correct
                self._tenant_name = self.DEFAULT_TENANT_NAME
            else:
                self.with_env("OB_TENANT_NAME", self._tenant_name)

        self.with_env("OB_TENANT_PASSWORD", self._password)

        super().start()
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name.

        Returns the first available driver from the supported drivers list.

        Returns:
            JDBC driver class name
        """
        # Try to find an available driver
        for driver_class in self.SUPPORTED_DRIVERS:
            try:
                # In Python, we can't check if a Java class exists
                # So we just return the first preferred driver
                # The actual availability should be checked by the application
                return driver_class
            except Exception:
                continue

        # Return the first OceanBase driver as default
        return self.OCEANBASE_JDBC_DRIVER

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL.

        Returns:
            JDBC connection URL
        """
        driver = self.get_driver_class_name()

        # Determine prefix based on driver type
        if self._is_mysql_driver(driver):
            prefix = "jdbc:mysql://"
        else:
            prefix = "jdbc:oceanbase://"

        return f"{prefix}{self.get_host()}:{self.get_port()}/{self.DEFAULT_DATABASE_NAME}"

    def get_database_name(self) -> str:
        """
        Get the database name.

        Returns:
            Database name
        """
        return self.DEFAULT_DATABASE_NAME

    def get_username(self) -> str:
        """
        Get the username including tenant name.

        Returns:
            Username in format: root@tenant_name
        """
        return f"{self.DEFAULT_USER}@{self._tenant_name}"

    def get_password(self) -> str:
        """
        Get the tenant password.

        Returns:
            Tenant password
        """
        return self._password

    def get_test_query_string(self) -> str:
        """
        Get the test query string.

        Returns:
            SQL query for testing connection
        """
        return "SELECT 1"

    def _is_mysql_driver(self, driver_class: str) -> bool:
        """
        Check if the driver is a MySQL driver.

        Args:
            driver_class: Driver class name

        Returns:
            True if MySQL driver, False otherwise
        """
        return driver_class in [self.MYSQL_JDBC_DRIVER, self.MYSQL_LEGACY_JDBC_DRIVER]
