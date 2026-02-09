"""
Memcached container implementation.

This module provides a container for Memcached in-memory caching system.
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.port import HostPortWaitStrategy


class MemcachedContainer(GenericContainer):
    """
    Memcached in-memory caching container.

    This container starts a Memcached instance for high-performance
    distributed memory object caching.

    Example:
        >>> with MemcachedContainer() as memcached:
        ...     url = memcached.get_connection_url()
        ...     # Connect to Memcached

        >>> # With custom image
        >>> memcached = MemcachedContainer("memcached:1.6-alpine")
        >>> memcached.start()
        >>> url = memcached.get_connection_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "memcached:latest"
    DEFAULT_PORT = 11211

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Memcached container.

        Args:
            image: Docker image name (default: memcached:latest)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT

        # Expose Memcached port
        self.with_exposed_ports(self._port)

        # Wait for Memcached to be ready (port-based)
        self.waiting_for(HostPortWaitStrategy())

    def get_connection_url(self) -> str:
        """
        Get the Memcached connection URL.

        Returns:
            Connection URL in format: host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Memcached port number on the host.

        Returns:
            Host port number mapped to the Memcached port
        """
        return self.get_mapped_port(self._port)
