"""
MongoDB container implementation.

This module provides a container for MongoDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mongodb/src/main/java/org/testcontainers/containers/MongoDBContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MongoDBContainer(GenericContainer):
    """
    MongoDB database container.

    This container starts a MongoDB database instance with optional authentication.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mongodb/src/main/java/org/testcontainers/containers/MongoDBContainer.java

    Example:
        >>> with MongoDBContainer() as mongo:
        ...     connection_string = mongo.get_connection_string()
        ...     # Connect to MongoDB

        >>> # With authentication
        >>> mongo = MongoDBContainer("mongo:7")
        >>> mongo.with_authentication("admin", "myuser", "mypass")
        >>> mongo.start()
        >>> connection_string = mongo.get_connection_string()
    """

    # Default configuration
    DEFAULT_IMAGE = "mongo:7"
    DEFAULT_PORT = 27017

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a MongoDB container.

        Args:
            image: Docker image name (default: mongo:7)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._username: str | None = None
        self._password: str | None = None
        self._auth_database: str | None = None

        # Expose MongoDB port
        self.with_exposed_ports(self._port)

        # Wait for MongoDB to be ready
        # MongoDB logs "Waiting for connections" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Waiting for connections.*")
        )

    def with_authentication(
        self,
        auth_database: str,
        username: str,
        password: str,
    ) -> MongoDBContainer:
        """
        Enable MongoDB authentication (fluent API).

        Args:
            auth_database: Authentication database (usually "admin")
            username: MongoDB username
            password: MongoDB password

        Returns:
            This container instance
        """
        self._auth_database = auth_database
        self._username = username
        self._password = password

        # Set environment variables for MongoDB authentication
        self.with_env("MONGO_INITDB_ROOT_USERNAME", username)
        self.with_env("MONGO_INITDB_ROOT_PASSWORD", password)
        self.with_env("MONGO_INITDB_DATABASE", auth_database)

        return self

    def get_connection_string(self) -> str:
        """
        Get the MongoDB connection string.

        Returns:
            Connection string in format:
            - Without auth: mongodb://host:port
            - With auth: mongodb://user:pass@host:port/?authSource=authDb
        """
        host = self.get_host()
        port = self.get_port()

        if self._username and self._password and self._auth_database:
            return (
                f"mongodb://{self._username}:{self._password}@"
                f"{host}:{port}/?authSource={self._auth_database}"
            )
        else:
            return f"mongodb://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed MongoDB port number on the host.

        Returns:
            Host port number mapped to the MongoDB port
        """
        return self.get_mapped_port(self._port)

    def get_username(self) -> str | None:
        """
        Get the MongoDB username if authentication is enabled.

        Returns:
            MongoDB username or None
        """
        return self._username

    def get_password(self) -> str | None:
        """
        Get the MongoDB password if authentication is enabled.

        Returns:
            MongoDB password or None
        """
        return self._password

    def get_auth_database(self) -> str | None:
        """
        Get the MongoDB authentication database if authentication is enabled.

        Returns:
            Authentication database or None
        """
        return self._auth_database
