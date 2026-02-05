"""
InfluxDB container implementation.

This module provides a container for InfluxDB time-series databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/influxdb/src/main/java/org/testcontainers/containers/InfluxDBContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class InfluxDBContainer(GenericContainer):
    """
    InfluxDB time-series database container.

    This container starts an InfluxDB instance with configurable authentication.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/influxdb/src/main/java/org/testcontainers/containers/InfluxDBContainer.java

    Example:
        >>> with InfluxDBContainer() as influxdb:
        ...     url = influxdb.get_url()
        ...     # Connect to InfluxDB

        >>> # Custom configuration
        >>> influxdb = InfluxDBContainer("influxdb:2.7")
        >>> influxdb.with_authentication("admin", "mypassword", "myorg", "mybucket")
        >>> influxdb.start()
        >>> url = influxdb.get_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "influxdb:2.7"
    DEFAULT_PORT = 8086
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "password"
    DEFAULT_ORG = "test-org"
    DEFAULT_BUCKET = "test-bucket"
    DEFAULT_ADMIN_TOKEN = "test-token"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an InfluxDB container.

        Args:
            image: Docker image name (default: influxdb:2.7)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD
        self._org = self.DEFAULT_ORG
        self._bucket = self.DEFAULT_BUCKET
        self._admin_token = self.DEFAULT_ADMIN_TOKEN

        # Expose InfluxDB port
        self.with_exposed_ports(self._port)

        # Set default environment variables for InfluxDB 2.x
        self.with_env("DOCKER_INFLUXDB_INIT_MODE", "setup")
        self.with_env("DOCKER_INFLUXDB_INIT_USERNAME", self._username)
        self.with_env("DOCKER_INFLUXDB_INIT_PASSWORD", self._password)
        self.with_env("DOCKER_INFLUXDB_INIT_ORG", self._org)
        self.with_env("DOCKER_INFLUXDB_INIT_BUCKET", self._bucket)
        self.with_env("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", self._admin_token)

        # Wait for InfluxDB to be ready
        # InfluxDB logs "Listening" or "ready" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*(Listening|ready).*")
        )

    def with_authentication(
        self,
        username: str,
        password: str,
        org: str,
        bucket: str,
        admin_token: str | None = None,
    ) -> InfluxDBContainer:
        """
        Configure InfluxDB authentication (fluent API).

        Args:
            username: InfluxDB username
            password: InfluxDB password
            org: Organization name
            bucket: Initial bucket name
            admin_token: Admin token (optional, auto-generated if None)

        Returns:
            This container instance
        """
        self._username = username
        self._password = password
        self._org = org
        self._bucket = bucket
        if admin_token:
            self._admin_token = admin_token

        self.with_env("DOCKER_INFLUXDB_INIT_USERNAME", username)
        self.with_env("DOCKER_INFLUXDB_INIT_PASSWORD", password)
        self.with_env("DOCKER_INFLUXDB_INIT_ORG", org)
        self.with_env("DOCKER_INFLUXDB_INIT_BUCKET", bucket)
        self.with_env("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", self._admin_token)

        return self

    def get_url(self) -> str:
        """
        Get the InfluxDB HTTP API URL.

        Returns:
            HTTP URL in format: http://host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed InfluxDB port number on the host.

        Returns:
            Host port number mapped to the InfluxDB port
        """
        return self.get_mapped_port(self._port)

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

    def get_org(self) -> str:
        """
        Get the InfluxDB organization name.

        Returns:
            Organization name
        """
        return self._org

    def get_bucket(self) -> str:
        """
        Get the InfluxDB bucket name.

        Returns:
            Bucket name
        """
        return self._bucket

    def get_admin_token(self) -> str:
        """
        Get the InfluxDB admin token.

        Returns:
            Admin token
        """
        return self._admin_token
