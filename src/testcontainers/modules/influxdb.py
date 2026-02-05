"""
InfluxDB container implementation.

This module provides a container for InfluxDB time-series databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/influxdb/src/main/java/org/testcontainers/containers/InfluxDBContainer.java
"""

from __future__ import annotations

import re

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class InfluxDBContainer(GenericContainer):
    """
    InfluxDB time-series database container.

    This container starts an InfluxDB instance with configurable authentication.
    Supports both InfluxDB 1.x and 2.x.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/influxdb/src/main/java/org/testcontainers/containers/InfluxDBContainer.java

    Example:
        >>> # InfluxDB 1.x
        >>> with InfluxDBContainer("influxdb:1.8") as influxdb:
        ...     url = influxdb.get_url()
        ...     # Connect to InfluxDB

        >>> # InfluxDB 2.x
        >>> influxdb = InfluxDBContainer("influxdb:2.7")
        >>> influxdb.with_bucket("mybucket")
        >>> influxdb.start()
        >>> url = influxdb.get_url()
    """

    # Default configuration
    INFLUXDB_PORT = 8086
    DEFAULT_IMAGE = "influxdb:1.4.3"

    # InfluxDB 1.x and 2.x defaults
    DEFAULT_USERNAME = "test-user"
    DEFAULT_PASSWORD = "test-password"
    DEFAULT_DATABASE = None  # v1 only

    # InfluxDB 2.x specific
    DEFAULT_BUCKET = "test-bucket"
    DEFAULT_ORGANIZATION = "test-org"

    # InfluxDB 1.x specific
    DEFAULT_ADMIN = "admin"
    DEFAULT_ADMIN_PASSWORD = "password"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an InfluxDB container.

        Args:
            image: Docker image name (default: influxdb:1.4.3)
        """
        super().__init__(image)

        # Detect version
        version = self._extract_version(image)
        self._is_at_least_major_version_2 = self._compare_version(version, "2.0.0") >= 0

        # Common properties
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD

        # InfluxDB 1.x properties
        self._auth_enabled = True
        self._admin = self.DEFAULT_ADMIN
        self._admin_password = self.DEFAULT_ADMIN_PASSWORD
        self._database: str | None = self.DEFAULT_DATABASE

        # InfluxDB 2.x properties
        self._bucket = self.DEFAULT_BUCKET
        self._organization = self.DEFAULT_ORGANIZATION
        self._retention: str | None = None
        self._admin_token: str | None = None

        # Expose InfluxDB port
        self.with_exposed_ports(self.INFLUXDB_PORT)

        # Set wait strategy - /ping returns 204 No Content
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/ping")
            .for_status_code(204)
            .with_basic_credentials(self._username, self._password)
        )

    def _extract_version(self, image: str) -> str:
        """Extract version from image name."""
        if ":" in image:
            return image.split(":")[-1]
        return "1.4.3"

    def _compare_version(self, version: str, target: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        def normalize(v):
            parts = re.match(r'^(\d+)\.(\d+)(?:\.(\d+))?', v)
            if parts:
                return [int(parts.group(1)), int(parts.group(2)), int(parts.group(3) or 0)]
            return [0, 0, 0]

        v_parts = normalize(version)
        t_parts = normalize(target)

        for i in range(3):
            if v_parts[i] < t_parts[i]:
                return -1
            elif v_parts[i] > t_parts[i]:
                return 1
        return 0

    def _configure(self) -> None:
        """Configure the InfluxDB container based on version."""
        super()._configure()

        if self._is_at_least_major_version_2:
            self._configure_influxdb_v2()
        else:
            self._configure_influxdb_v1()

    def _configure_influxdb_v2(self) -> None:
        """Set InfluxDB 2.x environment variables."""
        self.with_env("DOCKER_INFLUXDB_INIT_MODE", "setup")
        self.with_env("DOCKER_INFLUXDB_INIT_USERNAME", self._username)
        self.with_env("DOCKER_INFLUXDB_INIT_PASSWORD", self._password)
        self.with_env("DOCKER_INFLUXDB_INIT_ORG", self._organization)
        self.with_env("DOCKER_INFLUXDB_INIT_BUCKET", self._bucket)

        if self._retention is not None:
            self.with_env("DOCKER_INFLUXDB_INIT_RETENTION", self._retention)

        if self._admin_token is not None:
            self.with_env("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", self._admin_token)

    def _configure_influxdb_v1(self) -> None:
        """Set InfluxDB 1.x environment variables."""
        self.with_env("INFLUXDB_USER", self._username)
        self.with_env("INFLUXDB_USER_PASSWORD", self._password)
        self.with_env("INFLUXDB_HTTP_AUTH_ENABLED", str(self._auth_enabled).lower())
        self.with_env("INFLUXDB_ADMIN_USER", self._admin)
        self.with_env("INFLUXDB_ADMIN_PASSWORD", self._admin_password)

        if self._database is not None:
            self.with_env("INFLUXDB_DB", self._database)

    def with_username(self, username: str) -> InfluxDBContainer:
        """
        Set username for InfluxDB (fluent API).

        Args:
            username: The username to set for the system's initial super-user

        Returns:
            This container instance
        """
        self._username = username
        return self

    def with_password(self, password: str) -> InfluxDBContainer:
        """
        Set password for InfluxDB (fluent API).

        Args:
            password: The password to set for the system's initial super-user

        Returns:
            This container instance
        """
        self._password = password
        return self

    def with_auth_enabled(self, auth_enabled: bool) -> InfluxDBContainer:
        """
        Enable or disable authentication (InfluxDB 1.x only).

        Args:
            auth_enabled: Enables authentication

        Returns:
            This container instance
        """
        self._auth_enabled = auth_enabled
        return self

    def with_admin(self, admin: str) -> InfluxDBContainer:
        """
        Set admin user (InfluxDB 1.x only).

        Args:
            admin: The name of the admin user to be created

        Returns:
            This container instance
        """
        self._admin = admin
        return self

    def with_admin_password(self, admin_password: str) -> InfluxDBContainer:
        """
        Set admin password (InfluxDB 1.x only).

        Args:
            admin_password: The password for the admin user

        Returns:
            This container instance
        """
        self._admin_password = admin_password
        return self

    def with_database(self, database: str) -> InfluxDBContainer:
        """
        Initialize database with given name (InfluxDB 1.x only).

        Args:
            database: name of the database

        Returns:
            This container instance
        """
        self._database = database
        return self

    def with_organization(self, organization: str) -> InfluxDBContainer:
        """
        Set organization name (InfluxDB 2.x only).

        Args:
            organization: The organization for the initial setup of influxDB

        Returns:
            This container instance
        """
        self._organization = organization
        return self

    def with_bucket(self, bucket: str) -> InfluxDBContainer:
        """
        Initialize bucket with given name (InfluxDB 2.x only).

        Args:
            bucket: name of the bucket

        Returns:
            This container instance
        """
        self._bucket = bucket
        return self

    def with_retention(self, retention: str) -> InfluxDBContainer:
        """
        Set retention in days (InfluxDB 2.x only).

        Args:
            retention: days bucket will retain data (0 is infinite, default is 0)

        Returns:
            This container instance
        """
        self._retention = retention
        return self

    def with_admin_token(self, admin_token: str) -> InfluxDBContainer:
        """
        Set admin token (InfluxDB 2.x only).

        Args:
            admin_token: Authentication token to associate with the admin user

        Returns:
            This container instance
        """
        self._admin_token = admin_token
        return self

    def get_url(self) -> str:
        """
        Get the InfluxDB HTTP API URL.

        Returns:
            HTTP URL in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.INFLUXDB_PORT)
        return f"http://{host}:{port}"

    def get_username(self) -> str:
        """
        Get the InfluxDB username.

        Returns:
            InfluxDB username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the InfluxDB password.

        Returns:
            InfluxDB password
        """
        return self._password

    def get_database(self) -> str | None:
        """
        Get the InfluxDB database name (v1 only).

        Returns:
            Database name or None
        """
        return self._database

    def get_bucket(self) -> str:
        """
        Get the InfluxDB bucket name (v2 only).

        Returns:
            Bucket name
        """
        return self._bucket

    def get_organization(self) -> str:
        """
        Get the InfluxDB organization name (v2 only).

        Returns:
            Organization name
        """
        return self._organization

    def get_retention(self) -> str | None:
        """
        Get the retention setting (v2 only).

        Returns:
            Retention or None
        """
        return self._retention

    def get_admin_token(self) -> str | None:
        """
        Get the InfluxDB admin token (v2 only).

        Returns:
            Admin token or None
        """
        return self._admin_token
