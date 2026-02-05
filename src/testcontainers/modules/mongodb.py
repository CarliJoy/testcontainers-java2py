"""
MongoDB container implementation.

This module provides a container for MongoDB databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mongodb/src/main/java/org/testcontainers/containers/MongoDBContainer.java
"""

from __future__ import annotations

import time

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MongoDBContainer(GenericContainer):
    """
    MongoDB database container.

    This container starts a MongoDB database instance as a single-node replica set,
    matching the Java implementation behavior.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mongodb/src/main/java/org/testcontainers/containers/MongoDBContainer.java

    Example:
        >>> with MongoDBContainer() as mongo:
        ...     connection_string = mongo.get_connection_string()
        ...     replica_set_url = mongo.get_replica_set_url()
        ...     # Connect to MongoDB

        >>> # Custom image
        >>> mongo = MongoDBContainer("mongo:7")
        >>> mongo.start()
        >>> connection_string = mongo.get_connection_string()
    """

    # Default configuration
    DEFAULT_IMAGE = "mongo:4.0.10"
    MONGODB_PORT = 27017
    MONGODB_DATABASE_NAME_DEFAULT = "test"
    REPLICA_SET_NAME = "docker-rs"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a MongoDB container.

        Args:
            image: Docker image name (default: mongo:4.0.10)
        """
        super().__init__(image)

        self._port = self.MONGODB_PORT

        # Expose MongoDB port
        self.with_exposed_ports(self._port)

        # Start with replica set enabled (Java default behavior)
        self.with_command(["--replSet", self.REPLICA_SET_NAME])

        # Wait for MongoDB to be ready
        # MongoDB logs "waiting for connections" when ready (case-insensitive)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r"(?i).*waiting for connections.*")
            .with_times(1)
        )

    def start(self) -> MongoDBContainer:  # type: ignore[override]
        """
        Start the MongoDB container and initialize the replica set.

        Returns:
            This container instance
        """
        super().start()
        
        # Initialize replica set after container starts (matching Java behavior)
        self._init_replica_set()
        
        return self

    def _init_replica_set(self) -> None:
        """
        Initialize a single-node replica set.
        
        This matches the Java implementation's initReplicaSet() method.
        """
        # Check if replica set is already initialized
        if self._is_replica_set_initialized():
            return

        # Initialize replica set
        exit_code, output = self.exec(
            [
                "sh",
                "-c",
                'mongosh --eval "rs.initiate();" || mongo --eval "rs.initiate();"'
            ]
        )
        
        if exit_code != 0:
            raise RuntimeError(f"Failed to initialize replica set: {output}")

        # Wait for replica set to be ready (matching Java's AWAIT_INIT_REPLICA_SET_ATTEMPTS)
        max_attempts = 60
        for attempt in range(max_attempts):
            exit_code, _ = self.exec(
                [
                    "sh",
                    "-c",
                    'mongosh --eval "if(db.runCommand({isMaster:1}).ismaster==false) quit(1);" || '
                    'mongo --eval "if(db.runCommand({isMaster:1}).ismaster==false) quit(1);"'
                ]
            )
            
            if exit_code == 0:
                return
                
            time.sleep(0.1)

        raise RuntimeError(f"Replica set not initialized after {max_attempts} attempts")

    def _is_replica_set_initialized(self) -> bool:
        """
        Check if the replica set is already initialized.
        
        Returns:
            True if replica set is initialized, False otherwise
        """
        exit_code, _ = self.exec(
            [
                "sh",
                "-c",
                'mongosh --eval "if(db.adminCommand({replSetGetStatus:1})[\'myState\']!=1) quit(900);" || '
                'mongo --eval "if(db.adminCommand({replSetGetStatus:1})[\'myState\']!=1) quit(900);"'
            ]
        )
        return exit_code == 0

    def get_connection_string(self) -> str:
        """
        Get the MongoDB connection string.

        Returns:
            Connection string in format: mongodb://host:port
        """
        host = self.get_host()
        port = self.get_port()
        return f"mongodb://{host}:{port}"

    def get_replica_set_url(self, database: str = MONGODB_DATABASE_NAME_DEFAULT) -> str:
        """
        Get the replica set URL for a database.
        
        This matches the Java implementation's getReplicaSetUrl() method.

        Args:
            database: Database name (default: test)

        Returns:
            Replica set URL in format: mongodb://host:port/database
        """
        if not self.is_running():
            raise RuntimeError("MongoDBContainer should be started first")
        
        return f"{self.get_connection_string()}/{database}"

    def get_port(self) -> int:
        """
        Get the exposed MongoDB port number on the host.

        Returns:
            Host port number mapped to the MongoDB port
        """
        return self.get_mapped_port(self._port)
