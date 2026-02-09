"""
CouchDB container implementation.

This module provides a container for CouchDB document databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchdb/src/main/java/org/testcontainers/containers/CouchDBContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class CouchDBContainer(GenericContainer):
    """
    CouchDB document database container.

    This container starts a CouchDB instance with configurable authentication.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchdb/src/main/java/org/testcontainers/containers/CouchDBContainer.java

    Example:
        >>> with CouchDBContainer() as couchdb:
        ...     url = couchdb.get_url()
        ...     # Connect to CouchDB

        >>> # Custom configuration
        >>> couchdb = CouchDBContainer("couchdb:3")
        >>> couchdb.with_authentication("admin", "mypassword")
        >>> couchdb.start()
        >>> url = couchdb.get_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "couchdb:3"
    DEFAULT_PORT = 5984
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "password"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a CouchDB container.

        Args:
            image: Docker image name (default: couchdb:3)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD

        # Expose CouchDB port
        self.with_exposed_ports(self._port)

        # Set default authentication
        self.with_env("COUCHDB_USER", self._username)
        self.with_env("COUCHDB_PASSWORD", self._password)

        # Wait for CouchDB to be ready
        # CouchDB logs "Apache CouchDB has started" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Apache CouchDB has started.*")
        )

    def with_authentication(
        self,
        username: str,
        password: str,
    ) -> CouchDBContainer:
        """
        Configure CouchDB authentication (fluent API).

        Args:
            username: CouchDB username
            password: CouchDB password

        Returns:
            This container instance
        """
        self._username = username
        self._password = password
        self.with_env("COUCHDB_USER", username)
        self.with_env("COUCHDB_PASSWORD", password)
        return self

    def get_url(self) -> str:
        """
        Get the CouchDB HTTP API URL with authentication.

        Returns:
            HTTP URL in format: http://username:password@host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"http://{self._username}:{self._password}@{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed CouchDB port number on the host.

        Returns:
            Host port number mapped to the CouchDB port
        """
        return self.get_mapped_port(self._port)

    def get_username(self) -> str:
        """
        Get the CouchDB username.

        Returns:
            CouchDB username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the CouchDB password.

        Returns:
            CouchDB password
        """
        return self._password
