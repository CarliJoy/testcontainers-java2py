"""
CockroachDB container implementation.

This module provides a container for CockroachDB distributed SQL database.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/cockroachdb/src/main/java/org/testcontainers/containers/CockroachContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.http import HttpWaitStrategy
from testcontainers.waiting.shell import ShellStrategy
from testcontainers.waiting.wait_all import WaitAllStrategy


class CockroachDBContainer(JdbcDatabaseContainer):
    """
    CockroachDB distributed SQL database container.

    This container starts a CockroachDB instance in insecure single-node mode
    with configurable credentials and database name. CockroachDB is a distributed
    SQL database built on a transactional and strongly-consistent key-value store.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/cockroachdb/src/main/java/org/testcontainers/containers/CockroachContainer.java

    Example:
        >>> with CockroachDBContainer() as cockroach:
        ...     url = cockroach.get_jdbc_url()
        ...     host = cockroach.get_host()
        ...     port = cockroach.get_port()
        ...     # Connect to CockroachDB

        >>> # Custom configuration
        >>> cockroach = CockroachDBContainer("cockroachdb/cockroach:v23.1.0")
        >>> cockroach.with_username("myuser")
        >>> cockroach.with_password("mypass")
        >>> cockroach.with_database_name("mydb")
        >>> cockroach.start()

    Note:
        - CockroachDB uses PostgreSQL wire protocol, so the JDBC driver is PostgreSQL
        - Versions below 22.1.0 do not support environment variable configuration
        - Default mode is insecure (no TLS) for testing purposes
    """

    # Default configuration
    DEFAULT_IMAGE = "cockroachdb/cockroach:v23.1.0"
    DEFAULT_DB_PORT = 26257
    DEFAULT_REST_API_PORT = 8080
    DEFAULT_USERNAME = "root"
    DEFAULT_PASSWORD = ""
    DEFAULT_DATABASE = "postgres"

    # Version check for environment variable support
    MIN_VERSION_WITH_ENV_VARS = "22.1.0"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a CockroachDB container.

        Args:
            image: Docker image name (default: cockroachdb/cockroach:v23.1.0)
            username: Database username (default: root)
            password: Database password (default: empty string)
            dbname: Database name (default: postgres)
        """
        super().__init__(
            image=image,
            port=self.DEFAULT_DB_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Expose both database and REST API ports
        self.with_exposed_ports(self.DEFAULT_REST_API_PORT)

        # Check version for environment variable support
        self._supports_env_vars = self._check_version_support(image)

        if self._supports_env_vars:
            # Set environment variables for CockroachDB initialization (v22.1.0+)
            self.with_env("COCKROACH_USER", self._username)
            self.with_env("COCKROACH_PASSWORD", self._password)
            self.with_env("COCKROACH_DATABASE", self._dbname)

        # Set default command for single-node insecure mode
        # If password is set, use secure mode (not insecure)
        if self._password:
            self.with_command(["start-single-node"])
        else:
            self.with_command(["start-single-node", "--insecure"])

        # Wait for CockroachDB to be ready
        # Use both HTTP health check and shell command for v22.1.0+
        wait_strategy = WaitAllStrategy()
        wait_strategy.with_strategy(
            HttpWaitStrategy()
            .for_path("/health")
            .for_port(self.DEFAULT_REST_API_PORT)
            .for_status_code(200)
            .with_startup_timeout(60)
        )

        if self._supports_env_vars:
            # Wait for initialization file to be created
            wait_strategy.with_strategy(
                ShellStrategy().with_command("[ -f ./init_success ] || { exit 1; }")
            )

        self.waiting_for(wait_strategy.with_startup_timeout(60))

    def _check_version_support(self, image: str) -> bool:
        """
        Check if the image version supports environment variable configuration.

        Args:
            image: Docker image name with optional version tag

        Returns:
            True if version >= 22.1.0, False otherwise
        """
        # Extract version from image (e.g., "cockroachdb/cockroach:v23.1.0")
        if ":" not in image:
            return True  # Assume latest version supports env vars

        version_part = image.split(":")[-1]
        if version_part.startswith("v"):
            version_part = version_part[1:]  # Remove 'v' prefix

        try:
            # Simple version comparison for major.minor.patch
            version_components = version_part.split(".")[:2]
            major = int(version_components[0])
            minor = int(version_components[1]) if len(version_components) > 1 else 0

            min_components = self.MIN_VERSION_WITH_ENV_VARS.split(".")
            min_major = int(min_components[0])
            min_minor = int(min_components[1])

            return (major, minor) >= (min_major, min_minor)
        except (ValueError, IndexError):
            # If we can't parse version, assume it's recent
            return True

    def with_username(self, username: str) -> CockroachDBContainer:
        """
        Set the database username (fluent API).

        Args:
            username: Database username

        Returns:
            This container instance

        Raises:
            UnsupportedOperationException: If version < 22.1.0
        """
        if not self._supports_env_vars:
            raise RuntimeError(
                "Setting a username is not supported in versions below 22.1.0"
            )
        self._username = username
        self.with_env("COCKROACH_USER", self._username)
        return self

    def with_password(self, password: str) -> CockroachDBContainer:
        """
        Set the database password (fluent API).

        Args:
            password: Database password

        Returns:
            This container instance

        Raises:
            UnsupportedOperationException: If version < 22.1.0
        """
        if not self._supports_env_vars:
            raise RuntimeError(
                "Setting a password is not supported in versions below 22.1.0"
            )
        self._password = password
        self.with_env("COCKROACH_PASSWORD", self._password)
        return self

    def with_database_name(self, dbname: str) -> CockroachDBContainer:
        """
        Set the database name (fluent API).

        Args:
            dbname: Database name

        Returns:
            This container instance

        Raises:
            UnsupportedOperationException: If version < 22.1.0
        """
        if not self._supports_env_vars:
            raise RuntimeError(
                "Setting a database name is not supported in versions below 22.1.0"
            )
        self._dbname = dbname
        self.with_env("COCKROACH_DATABASE", self._dbname)
        return self

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for CockroachDB.

        CockroachDB uses the PostgreSQL wire protocol, so it uses the
        PostgreSQL JDBC driver.

        Returns:
            PostgreSQL JDBC driver class name
        """
        return "org.postgresql.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for CockroachDB.

        Returns:
            JDBC connection URL in format: jdbc:postgresql://host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"jdbc:postgresql://{host}:{port}/{self._dbname}"

    def get_connection_string(self) -> str:
        """
        Get the CockroachDB connection string (Python native format).

        Returns:
            Connection string in format: postgresql://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        if self._password:
            return f"postgresql://{self._username}:{self._password}@{host}:{port}/{self._dbname}"
        else:
            return f"postgresql://{self._username}@{host}:{port}/{self._dbname}"
