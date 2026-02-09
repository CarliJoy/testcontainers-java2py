"""
YugabyteDB container implementations.

This module provides containers for YugabyteDB with both YSQL and YCQL APIs.

Java sources:
- YSQL: https://github.com/testcontainers/testcontainers-java/blob/main/modules/yugabytedb/src/main/java/org/testcontainers/containers/YugabyteDBYSQLContainer.java
- YCQL: https://github.com/testcontainers/testcontainers-java/blob/main/modules/yugabytedb/src/main/java/org/testcontainers/containers/YugabyteDBYCQLContainer.java
"""

from __future__ import annotations

import time
from datetime import timedelta

from testcontainers.core.generic_container import GenericContainer
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.modules.jdbc import JdbcDatabaseContainer


class YugabyteDBYSQLContainer(JdbcDatabaseContainer):
    """
    YugabyteDB YSQL API container.

    This container starts a YugabyteDB instance with the YSQL (PostgreSQL-compatible) API.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/yugabytedb/src/main/java/org/testcontainers/containers/YugabyteDBYSQLContainer.java

    Supported image: yugabytedb/yugabyte

    Exposed ports:
    - YSQL: 5433
    - Master dashboard: 7000
    - Tserver dashboard: 9000

    Example:
        >>> with YugabyteDBYSQLContainer() as yugabyte:
        ...     jdbc_url = yugabyte.get_jdbc_url()
        ...     # Connect to YugabyteDB

        >>> # Custom configuration
        >>> yugabyte = YugabyteDBYSQLContainer("yugabytedb/yugabyte:2.18.0.0")
        >>> yugabyte.with_username("myuser")
        >>> yugabyte.with_password("mypass")
        >>> yugabyte.with_database_name("mydb")
        >>> yugabyte.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "yugabytedb/yugabyte"
    YSQL_PORT = 5433
    MASTER_DASHBOARD_PORT = 7000
    TSERVER_DASHBOARD_PORT = 9000
    JDBC_DRIVER_CLASS = "com.yugabyte.Driver"
    JDBC_CONNECT_PREFIX = "jdbc:yugabytedb"
    ENTRYPOINT = "bin/yugabyted start --background=false"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = "yugabyte",
        password: str = "yugabyte",
        dbname: str = "yugabyte",
    ):
        """
        Initialize a YugabyteDB YSQL container.

        Args:
            image: Docker image name (default: yugabytedb/yugabyte)
            username: Database username (default: yugabyte)
            password: Database password (default: yugabyte)
            dbname: Database name (default: yugabyte)
        """
        super().__init__(
            image=image,
            port=self.YSQL_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Expose YugabyteDB ports
        self.with_exposed_ports(self.YSQL_PORT, self.MASTER_DASHBOARD_PORT, self.TSERVER_DASHBOARD_PORT)

        # Set command
        self.with_command(self.ENTRYPOINT)

        # Configure environment variables
        self.with_env("YSQL_DB", self._dbname)
        self.with_env("YSQL_USER", self._username)
        self.with_env("YSQL_PASSWORD", self._password)

    def start(self) -> YugabyteDBYSQLContainer:  # type: ignore[override]
        """
        Start the YugabyteDB container with custom wait strategy.

        Returns:
            This container instance
        """
        super().start()
        
        # Custom wait strategy for YSQL
        self._wait_for_ysql_ready()
        
        return self

    def _wait_for_ysql_ready(self) -> None:
        """
        Wait for YSQL to be ready with extended probe.
        
        This matches the Java YugabyteDBYSQLWaitStrategy implementation.
        """
        max_attempts = 60
        probe_create = "CREATE TABLE IF NOT EXISTS YB_SAMPLE(k int, v int, primary key(k, v))"
        probe_drop = "DROP TABLE IF EXISTS YB_SAMPLE"
        
        for attempt in range(max_attempts):
            try:
                # Try to execute the probe queries
                result = self.exec(
                    [
                        "bin/ysqlsh",
                        "-h", "localhost",
                        "-p", str(self.YSQL_PORT),
                        "-U", self._username,
                        "-d", self._dbname,
                        "-c", probe_create,
                    ]
                )
                
                if result[0] == 0:
                    # Drop the test table
                    self.exec(
                        [
                            "bin/ysqlsh",
                            "-h", "localhost",
                            "-p", str(self.YSQL_PORT),
                            "-U", self._username,
                            "-d", self._dbname,
                            "-c", probe_drop,
                        ]
                    )
                    return
            except Exception:
                pass
            
            time.sleep(1)
        
        raise RuntimeError(f"YugabyteDB YSQL not ready after {max_attempts} attempts")

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for YugabyteDB.

        Returns:
            YugabyteDB JDBC driver class name
        """
        return self.JDBC_DRIVER_CLASS

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for YugabyteDB YSQL.

        Returns:
            JDBC connection URL in format: jdbc:yugabytedb://host:port/database
        """
        host = self.get_host()
        port = self.get_mapped_port(self.YSQL_PORT)
        return f"{self.JDBC_CONNECT_PREFIX}://{host}:{port}/{self._dbname}"

    def get_test_query_string(self) -> str:
        """
        Get the test query string for YugabyteDB.

        Returns:
            Test query string
        """
        return "SELECT 1"

    def get_port(self) -> int:
        """
        Get the exposed YSQL port number on the host.

        Returns:
            Host port number mapped to the YSQL port
        """
        return self.get_mapped_port(self.YSQL_PORT)


class YugabyteDBYCQLContainer(GenericContainer):
    """
    YugabyteDB YCQL API container.

    This container starts a YugabyteDB instance with the YCQL (Cassandra-compatible) API.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/yugabytedb/src/main/java/org/testcontainers/containers/YugabyteDBYCQLContainer.java

    Supported image: yugabytedb/yugabyte

    Exposed ports:
    - YCQL: 9042
    - Master dashboard: 7000
    - Tserver dashboard: 9000

    Example:
        >>> with YugabyteDBYCQLContainer() as yugabyte:
        ...     contact_point = yugabyte.get_contact_point()
        ...     local_dc = yugabyte.get_local_dc()
        ...     # Connect to YugabyteDB

        >>> # Custom configuration
        >>> yugabyte = YugabyteDBYCQLContainer("yugabytedb/yugabyte:2.18.0.0")
        >>> yugabyte.with_keyspace_name("mykeyspace")
        >>> yugabyte.with_username("myuser")
        >>> yugabyte.with_password("mypass")
        >>> yugabyte.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "yugabytedb/yugabyte"
    YCQL_PORT = 9042
    MASTER_DASHBOARD_PORT = 7000
    TSERVER_DASHBOARD_PORT = 9000
    ENTRYPOINT = "bin/yugabyted start --background=false"
    LOCAL_DC = "datacenter1"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a YugabyteDB YCQL container.

        Args:
            image: Docker image name (default: yugabytedb/yugabyte)
        """
        super().__init__(image)

        self._keyspace = None
        self._username = None
        self._password = None
        self._init_script = None

        # Expose YugabyteDB ports
        self.with_exposed_ports(self.YCQL_PORT, self.MASTER_DASHBOARD_PORT, self.TSERVER_DASHBOARD_PORT)

        # Set command
        self.with_command(self.ENTRYPOINT)

    def start(self) -> YugabyteDBYCQLContainer:  # type: ignore[override]
        """
        Start the YugabyteDB container.

        Returns:
            This container instance
        """
        # Configure environment variables before starting
        if self._keyspace:
            self.with_env("YCQL_KEYSPACE", self._keyspace)
        if self._username:
            self.with_env("YCQL_USER", self._username)
        if self._password:
            self.with_env("YCQL_PASSWORD", self._password)

        super().start()
        
        # Custom wait strategy for YCQL
        self._wait_for_ycql_ready()
        
        return self

    def _wait_for_ycql_ready(self) -> None:
        """
        Wait for YCQL to be ready.
        
        This matches the Java YugabyteDBYCQLWaitStrategy implementation.
        """
        max_attempts = 60
        
        for attempt in range(max_attempts):
            try:
                # Try to connect to YCQL
                result = self.exec(
                    [
                        "bin/ycqlsh",
                        "-e", "DESCRIBE KEYSPACES",
                    ]
                )
                
                if result[0] == 0:
                    return
            except Exception:
                pass
            
            time.sleep(1)
        
        raise RuntimeError(f"YugabyteDB YCQL not ready after {max_attempts} attempts")

    def with_keyspace_name(self, keyspace: str) -> YugabyteDBYCQLContainer:
        """
        Set the keyspace name (fluent API).

        Args:
            keyspace: Keyspace name

        Returns:
            This container instance
        """
        self._keyspace = keyspace
        return self

    def with_username(self, username: str) -> YugabyteDBYCQLContainer:
        """
        Set the username (fluent API).

        Args:
            username: Username

        Returns:
            This container instance
        """
        self._username = username
        return self

    def with_password(self, password: str) -> YugabyteDBYCQLContainer:
        """
        Set the password (fluent API).

        Args:
            password: Password

        Returns:
            This container instance
        """
        self._password = password
        return self

    def with_init_script(self, init_script: str) -> YugabyteDBYCQLContainer:
        """
        Set the initialization script path (fluent API).

        Args:
            init_script: Path to initialization script

        Returns:
            This container instance
        """
        self._init_script = init_script
        return self

    def get_contact_point(self) -> tuple[str, int]:
        """
        Get the YCQL contact point.

        Returns:
            Tuple of (host, port)
        """
        return (self.get_host(), self.get_mapped_port(self.YCQL_PORT))

    def get_local_dc(self) -> str:
        """
        Get the local datacenter name.

        Returns:
            Local datacenter name
        """
        return self.LOCAL_DC

    def get_username(self) -> str | None:
        """
        Get the username.

        Returns:
            Username or None
        """
        return self._username

    def get_password(self) -> str | None:
        """
        Get the password.

        Returns:
            Password or None
        """
        return self._password

    def get_keyspace(self) -> str | None:
        """
        Get the keyspace name.

        Returns:
            Keyspace name or None
        """
        return self._keyspace

    def get_port(self) -> int:
        """
        Get the exposed YCQL port number on the host.

        Returns:
            Host port number mapped to the YCQL port
        """
        return self.get_mapped_port(self.YCQL_PORT)
