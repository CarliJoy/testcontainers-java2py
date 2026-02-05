"""
Neo4j container implementation.

This module provides a container for Neo4j graph databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/neo4j/src/main/java/org/testcontainers/containers/Neo4jContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class Neo4jContainer(GenericContainer):
    """
    Neo4j graph database container.

    This container starts a Neo4j graph database instance with authentication.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/neo4j/src/main/java/org/testcontainers/containers/Neo4jContainer.java

    Example:
        >>> with Neo4jContainer() as neo4j:
        ...     bolt_url = neo4j.get_bolt_url()
        ...     http_url = neo4j.get_http_url()
        ...     # Connect to Neo4j

        >>> # Custom configuration
        >>> neo4j = Neo4jContainer("neo4j:5")
        >>> neo4j.with_authentication("neo4j", "mypassword")
        >>> neo4j.start()
        >>> bolt_url = neo4j.get_bolt_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "neo4j:5"
    DEFAULT_HTTP_PORT = 7474
    DEFAULT_BOLT_PORT = 7687
    DEFAULT_USERNAME = "neo4j"
    DEFAULT_PASSWORD = "test"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Neo4j container.

        Args:
            image: Docker image name (default: neo4j:5)
        """
        super().__init__(image)

        self._http_port = self.DEFAULT_HTTP_PORT
        self._bolt_port = self.DEFAULT_BOLT_PORT
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD
        self._auth_disabled = False

        # Expose Neo4j ports
        self.with_exposed_ports(self._http_port, self._bolt_port)

        # Set default authentication
        self.with_env("NEO4J_AUTH", f"{self._username}/{self._password}")

        # Wait for Neo4j to be ready
        # Neo4j logs "Remote interface available" or "Started" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*(Remote interface available|Started).*")
        )

    def with_authentication(
        self,
        username: str,
        password: str,
    ) -> Neo4jContainer:
        """
        Enable Neo4j authentication with custom credentials (fluent API).

        Args:
            username: Neo4j username
            password: Neo4j password

        Returns:
            This container instance
        """
        self._username = username
        self._password = password
        self._auth_disabled = False
        self.with_env("NEO4J_AUTH", f"{username}/{password}")
        return self

    def without_authentication(self) -> Neo4jContainer:
        """
        Disable Neo4j authentication (fluent API).

        Returns:
            This container instance
        """
        self._auth_disabled = True
        self.with_env("NEO4J_AUTH", "none")
        return self

    def get_bolt_url(self) -> str:
        """
        Get the Neo4j Bolt protocol connection URL.

        Returns:
            Bolt URL in format: bolt://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._bolt_port)
        return f"bolt://{host}:{port}"

    def get_http_url(self) -> str:
        """
        Get the Neo4j HTTP API URL.

        Returns:
            HTTP URL in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._http_port)
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Bolt port number on the host.

        Returns:
            Host port number mapped to the Bolt port
        """
        return self.get_mapped_port(self._bolt_port)

    def get_http_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self._http_port)

    def get_username(self) -> str:
        """
        Get the Neo4j username.

        Returns:
            Neo4j username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the Neo4j password.

        Returns:
            Neo4j password
        """
        return self._password

    def is_auth_disabled(self) -> bool:
        """
        Check if authentication is disabled.

        Returns:
            True if authentication is disabled, False otherwise
        """
        return self._auth_disabled
