"""
Redis container implementation.

This module provides a container for Redis in-memory data store.
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class RedisContainer(GenericContainer):
    """
    Redis container.

    This container starts a Redis instance with optional password authentication.

    Example:
        >>> with RedisContainer() as redis:
        ...     url = redis.get_connection_url()
        ...     # Connect to Redis

        >>> # With password
        >>> redis = RedisContainer("redis:7")
        >>> redis.with_password("mypassword")
        >>> redis.start()
        >>> url = redis.get_connection_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "redis:7"
    DEFAULT_PORT = 6379

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Redis container.

        Args:
            image: Docker image name (default: redis:7)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._password: str | None = None

        # Expose Redis port
        self.with_exposed_ports(self._port)

        # Wait for Redis to be ready
        # Redis logs "Ready to accept connections" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Ready to accept connections.*")
        )

    def with_password(self, password: str) -> RedisContainer:
        """
        Set Redis password authentication (fluent API).

        Args:
            password: Redis password

        Returns:
            This container instance
        """
        self._password = password
        return self

    def start(self) -> RedisContainer:  # type: ignore[override]
        """
        Start the Redis container with any configured options.

        Returns:
            This container instance
        """
        # If password is set, add it to command as array to avoid shell injection
        if self._password:
            self.with_command(["redis-server", "--requirepass", self._password])

        super().start()
        return self

    def get_connection_url(self) -> str:
        """
        Get the Redis connection URL.

        Returns:
            Connection URL in format:
            - Without password: redis://host:port
            - With password: redis://:password@host:port
        """
        host = self.get_host()
        port = self.get_port()

        if self._password:
            return f"redis://:{self._password}@{host}:{port}"
        else:
            return f"redis://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Redis port number on the host.

        Returns:
            Host port number mapped to the Redis port
        """
        return self.get_mapped_port(self._port)

    def get_password(self) -> str | None:
        """
        Get the Redis password if authentication is enabled.

        Returns:
            Redis password or None
        """
        return self._password
