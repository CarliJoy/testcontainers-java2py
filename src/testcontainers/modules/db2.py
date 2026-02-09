"""
DB2 database container implementation.

This module provides a container for IBM DB2 databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/db2/src/main/java/org/testcontainers/containers/Db2Container.java
"""

from __future__ import annotations

from datetime import timedelta

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class Db2Container(JdbcDatabaseContainer):
    """
    IBM DB2 database container.

    This container starts an IBM DB2 database instance with configurable
    credentials and database name. Requires license acceptance.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/db2/src/main/java/org/testcontainers/containers/Db2Container.java

    Supported images: icr.io/db2_community/db2, ibmcom/db2

    Exposed ports:
    - Database: 50000

    Example:
        >>> with Db2Container("icr.io/db2_community/db2:latest") as db2:
        ...     db2.accept_license()
        ...     url = db2.get_jdbc_url()
        ...     # Connect to DB2

        >>> # Custom configuration
        >>> db2 = Db2Container("ibmcom/db2:11.5.0.0a")
        >>> db2.accept_license()
        >>> db2.with_username("myuser")
        >>> db2.with_password("mypass123")
        >>> db2.with_database_name("mydb")
        >>> db2.start()
    """

    DEFAULT_IMAGE = "ibmcom/db2"
    DEFAULT_TAG = "11.5.0.0a"
    DB2_PORT = 50000
    DEFAULT_USERNAME = "db2inst1"
    DEFAULT_PASSWORD = "foobar1234"  # Default from Java - change for production
    DEFAULT_DATABASE = "test"

    def __init__(
        self,
        image: str = f"{DEFAULT_IMAGE}:{DEFAULT_TAG}",
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a DB2 container.

        Args:
            image: Docker image name (default: ibmcom/db2:11.5.0.0a)
            username: Database username (default: db2inst1)
            password: Database password (default: foobar1234)
            dbname: Database name (default: test)
        """
        super().__init__(
            image=image,
            port=self.DB2_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        self.with_exposed_ports(self.DB2_PORT)

        # Add IPC capabilities required by DB2
        def add_capabilities(create_kwargs):
            if "host_config" not in create_kwargs:
                create_kwargs["host_config"] = {}
            if "cap_add" not in create_kwargs["host_config"]:
                create_kwargs["host_config"]["cap_add"] = []
            create_kwargs["host_config"]["cap_add"].extend(["IPC_LOCK", "IPC_OWNER"])
            return create_kwargs

        self.with_create_container_modifier(add_capabilities)

        # Configure environment variables
        self.with_env("DBNAME", dbname)
        self.with_env("DB2INSTANCE", username)
        self.with_env("DB2INST1_PASSWORD", password)
        # These settings help the DB2 container start faster
        self.with_env("AUTOCONFIG", "false")
        self.with_env("ARCHIVE_LOGS", "false")

        # Wait for DB2 to complete setup (can take up to 10 minutes)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Setup has completed\..*")
            .with_startup_timeout(timedelta(minutes=10))
        )

    def accept_license(self) -> Db2Container:
        """
        Accept the IBM DB2 license.

        This must be called to use the container, as described at:
        https://hub.docker.com/r/ibmcom/db2

        Returns:
            This container instance for method chaining
        """
        self.with_env("LICENSE", "accept")
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for DB2.

        Returns:
            DB2 JDBC driver class name
        """
        return "com.ibm.db2.jcc.DB2Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for DB2.

        Returns:
            JDBC connection URL in format: jdbc:db2://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:db2://{host}:{port}/{self._dbname}"

    def get_test_query_string(self) -> str:
        """
        Get the test query for validating the DB2 connection.

        Returns:
            Test query string
        """
        return "SELECT 1 FROM SYSIBM.SYSDUMMY1"
