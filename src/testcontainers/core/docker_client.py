"""
Docker client factory and wrapper for Testcontainers.

This module provides a singleton Docker client factory that manages Docker client
connections and configurations. It's converted from the Java testcontainers library.
"""

from __future__ import annotations

import logging
import os
import platform
import threading
import uuid
from typing import Optional, Dict, Any

import docker
from docker import DockerClient
from docker.errors import DockerException

logger = logging.getLogger(__name__)


class DockerClientWrapper:
    """
    Simple wrapper around Docker client.
    
    Equivalent to Java's DelegatingDockerClient - provides a simple delegation pattern.
    """

    def __init__(self, client: DockerClient):
        """
        Initialize wrapper with a Docker client.
        
        Args:
            client: The Docker client instance to wrap
        """
        self._client = client

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to wrapped client."""
        return getattr(self._client, name)

    def close(self) -> None:
        """
        Close the Docker client connection.
        
        Note: For the global client, this should raise an error as in Java.
        """
        raise RuntimeError("You should never close the global DockerClient!")

    @property
    def client(self) -> DockerClient:
        """Get the underlying Docker client."""
        return self._client


class LazyDockerClient:
    """
    Lazy-loading Docker client that only initializes when first accessed.
    
    Equivalent to Java's lazyClient() method in DockerClientFactory.
    """

    def __init__(self, factory: DockerClientFactory):
        """
        Initialize lazy client with factory reference.
        
        Args:
            factory: The DockerClientFactory instance to use
        """
        self._factory = factory
        self._client: Optional[DockerClient] = None

    def __getattr__(self, name: str) -> Any:
        """Lazy load and delegate to actual client."""
        if self._client is None:
            self._client = self._factory.client()
        return getattr(self._client, name)

    def __str__(self) -> str:
        return "LazyDockerClient"


class DockerClientFactory:
    """
    Singleton factory for creating and caching Docker clients.
    
    This class provides initialized Docker clients. The correct client configuration
    is determined on first use and cached thereafter.
    
    Converted from Java's DockerClientFactory class.
    """

    # Class-level constants
    TESTCONTAINERS_LABEL = "org.testcontainers"
    TESTCONTAINERS_SESSION_ID_LABEL = f"{TESTCONTAINERS_LABEL}.sessionId"
    TESTCONTAINERS_LANG_LABEL = f"{TESTCONTAINERS_LABEL}.lang"
    TESTCONTAINERS_VERSION_LABEL = f"{TESTCONTAINERS_LABEL}.version"
    
    SESSION_ID = str(uuid.uuid4())
    TESTCONTAINERS_VERSION = "0.1.0"  # Should be read from package version
    
    # Singleton instance
    _instance: Optional[DockerClientFactory] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize Docker client factory (private - use instance() method)."""
        self._client: Optional[DockerClient] = None
        self._cached_client_failure: Optional[Exception] = None
        self._docker_host_ip_address: Optional[str] = None
        self._active_api_version: Optional[str] = None

    @classmethod
    def instance(cls) -> DockerClientFactory:
        """
        Get singleton instance of DockerClientFactory.
        
        Returns:
            The singleton DockerClientFactory instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def lazy_client(cls) -> LazyDockerClient:
        """
        Create a lazy-loading Docker client.
        
        The client will only be initialized when first accessed.
        
        Returns:
            A LazyDockerClient instance
        """
        return LazyDockerClient(cls.instance())

    def is_docker_available(self) -> bool:
        """
        Check if Docker is accessible and client can be created.
        
        Returns:
            True if Docker is available, False otherwise
        """
        try:
            self.client()
            return True
        except Exception:
            return False

    def client(self) -> DockerClient:
        """
        Get or create the Docker client.
        
        This method caches the client for subsequent calls.
        
        Returns:
            A Docker client instance
            
        Raises:
            DockerException: If Docker is not available or client creation fails
        """
        # Fail fast if checks have failed previously
        if self._cached_client_failure is not None:
            logger.debug("There is a cached client failure - throwing", exc_info=self._cached_client_failure)
            raise self._cached_client_failure

        if self._client is not None:
            return self._client

        try:
            # Try to create client from environment
            self._client = self._create_docker_client()
            
            # Get Docker info for logging
            info = self._client.info()
            version = self._client.version()
            
            self._active_api_version = version.get('ApiVersion', 'unknown')
            
            # Log Docker connection info
            server_version = info.get('ServerVersion', 'unknown')
            os_type = info.get('OperatingSystem', 'unknown')
            mem_total = info.get('MemTotal', 0) // (1024 * 1024)  # Convert to MB
            
            logger.info("Testcontainers version: %s", self.TESTCONTAINERS_VERSION)
            logger.info(
                "Connected to docker:\n"
                "  Server Version: %s\n"
                "  API Version: %s\n"
                "  Operating System: %s\n"
                "  Total Memory: %d MB",
                server_version,
                self._active_api_version,
                os_type,
                mem_total
            )
            
            # Determine Docker host IP
            self._docker_host_ip_address = self._determine_docker_host_ip()
            logger.info("Docker host IP address is %s", self._docker_host_ip_address)
            
            return self._client
            
        except Exception as e:
            self._cached_client_failure = e
            logger.error("Failed to create Docker client", exc_info=e)
            raise

    def _create_docker_client(self) -> DockerClient:
        """
        Create a Docker client using environment configuration.
        
        Returns:
            A configured Docker client
            
        Raises:
            DockerException: If client creation fails
        """
        try:
            # Try to create from environment (DOCKER_HOST, etc.)
            client = docker.from_env()
            
            # Test the connection
            client.ping()
            
            return client
        except DockerException as e:
            logger.error("Failed to create Docker client from environment: %s", e)
            raise

    def _determine_docker_host_ip(self) -> str:
        """
        Determine the Docker host IP address.
        
        Returns:
            The Docker host IP address
        """
        # Check if running in Docker
        if os.path.exists('/.dockerenv'):
            # Running inside Docker, try to get gateway
            try:
                import socket
                # Try to connect to Docker gateway to get local IP
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    # Doesn't actually connect, just determines route
                    s.connect(('10.0.0.0', 80))
                    return s.getsockname()[0]
            except Exception:
                pass
        
        # Check DOCKER_HOST environment variable
        docker_host = os.environ.get('DOCKER_HOST', '')
        if docker_host.startswith('tcp://'):
            # Extract host from tcp://host:port
            host = docker_host.replace('tcp://', '').split(':')[0]
            return host
        
        # Default to localhost
        return 'localhost'

    def docker_host_ip_address(self) -> str:
        """
        Get the Docker host IP address.
        
        Returns:
            The Docker host IP address
        """
        if self._docker_host_ip_address is None:
            # Ensure client is initialized
            self.client()
        return self._docker_host_ip_address or 'localhost'

    @classmethod
    def marker_labels(cls) -> Dict[str, str]:
        """
        Get default marker labels for Testcontainers.
        
        These labels are added to containers to identify them as Testcontainers.
        
        Returns:
            Dictionary of label key-value pairs
        """
        return {
            cls.TESTCONTAINERS_LABEL: "true",
            cls.TESTCONTAINERS_LANG_LABEL: "python",
            cls.TESTCONTAINERS_VERSION_LABEL: cls.TESTCONTAINERS_VERSION,
        }

    def get_active_api_version(self) -> Optional[str]:
        """
        Get the active Docker API version.
        
        Returns:
            The Docker API version string, or None if not yet determined
        """
        return self._active_api_version

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance (mainly for testing).
        
        Warning: This should only be used in tests.
        """
        with cls._lock:
            if cls._instance is not None and cls._instance._client is not None:
                try:
                    # Don't actually close the client as it might be shared
                    pass
                except Exception:
                    pass
            cls._instance = None
