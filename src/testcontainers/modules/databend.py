"""
Databend container module.

Databend is a cloud data warehouse that provides fast analytics.

Example:
    
    .. code-block:: python

        from testcontainers.modules.databend import DatabendContainer

        with DatabendContainer() as databend:
            connection_url = databend.get_connection_url()
            # Use the connection_url to connect to Databend

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/databend/src/main/java/org/testcontainers/databend/DatabendContainer.java
"""

from __future__ import annotations

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.modules.jdbc import JdbcDatabaseContainer


class DatabendContainer(JdbcDatabaseContainer):
    """
    Databend database container.

    Example:

        .. code-block:: python

            from testcontainers.modules.databend import DatabendContainer

            with DatabendContainer() as databend:
                connection_url = databend.get_connection_url()
    """

    def __init__(
        self,
        image: str = "datafuselabs/databend:latest",
        username: str = "databend",
        password: str = "databend",
        dbname: str = "default",
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.username = username
        self.password = password
        self.dbname = dbname
        self.port = 8000

        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("QUERY_DEFAULT_USER", self.username)
        self.with_env("QUERY_DEFAULT_PASSWORD", self.password)

    def get_connection_url(self, **kwargs) -> str:
        """
        Get the connection URL for Databend.

        Returns:
            str: Connection URL in format: jdbc:databend://host:port/database
        """
        return self._create_connection_url(
            dialect="databend",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            port=self.port,
        )

    def _connect(self) -> None:
        """Wait for Databend to be ready by checking HTTP endpoint."""
        import urllib.request
        import time

        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}/"
                response = urllib.request.urlopen(url, timeout=1)
                if response.read().decode() == "Ok.":
                    return
            except Exception:
                if attempt < max_attempts - 1:
                    time.sleep(1)
                    continue
                raise

    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name.

        Returns:
            str: The driver class name
        """
        return "com.databend.jdbc.DatabendDriver"
