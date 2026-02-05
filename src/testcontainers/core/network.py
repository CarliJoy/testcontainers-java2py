"""
Docker network management for Testcontainers.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/Network.java
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from docker.models.networks import Network as DockerNetwork

from testcontainers.core.docker_client import DockerClientFactory

logger = logging.getLogger(__name__)


@runtime_checkable
class Network(Protocol):
    """
    Protocol for network management in Testcontainers.
    
    Networks allow containers to communicate with each other.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/Network.java
    """

    def get_id(self) -> str:
        """Get the network ID, creating the network if needed."""
        ...

    def close(self) -> None:
        """Close and remove the network."""
        ...

    def __enter__(self) -> Network:
        """Context manager entry."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        ...


class NetworkImpl:
    """
    Implementation of Network interface.
    
    Creates and manages Docker networks for inter-container communication.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/Network.java
    """

    def __init__(
        self,
        name: Optional[str] = None,
        driver: Optional[str] = None,
        enable_ipv6: Optional[bool] = None,
        labels: Optional[dict[str, str]] = None,
    ):
        """
        Initialize a new network.
        
        Args:
            name: Network name (auto-generated if not provided)
            driver: Network driver (e.g., 'bridge', 'overlay')
            enable_ipv6: Enable IPv6 networking
            labels: Additional labels for the network
        """
        self._name = name or f"testcontainers-{uuid.uuid4()}"
        self._driver = driver
        self._enable_ipv6 = enable_ipv6
        self._labels = labels or {}
        self._id: Optional[str] = None
        self._initialized = False
        self._network: Optional[DockerNetwork] = None

    def get_id(self) -> str:
        """
        Get the network ID, lazily creating the network if needed.
        
        Returns:
            The Docker network ID
        """
        if not self._initialized:
            self._create()
            self._initialized = True
        return self._id

    def _create(self) -> None:
        """Create the Docker network."""
        client = DockerClientFactory.instance().client()
        
        # Prepare network configuration
        network_config = {
            "name": self._name,
            "check_duplicate": True,
            "labels": self._get_labels(),
        }
        
        if self._driver:
            network_config["driver"] = self._driver
        
        if self._enable_ipv6 is not None:
            network_config["enable_ipv6"] = self._enable_ipv6
        
        logger.info(f"Creating network: {self._name}")
        self._network = client.networks.create(**network_config)
        self._id = self._network.id
        logger.info(f"Created network {self._name} with ID: {self._id}")

    def _get_labels(self) -> dict[str, str]:
        """Get labels including Testcontainers markers."""
        labels = dict(self._labels)
        # Add Testcontainers marker labels
        labels.update(DockerClientFactory.marker_labels())
        return labels

    def close(self) -> None:
        """Remove the Docker network."""
        if self._initialized and self._network:
            try:
                logger.info(f"Removing network: {self._name}")
                self._network.remove()
                logger.info(f"Removed network: {self._name}")
            except Exception as e:
                logger.warning(f"Failed to remove network {self._name}: {e}")
            finally:
                self._initialized = False
                self._id = None
                self._network = None

    def __enter__(self) -> NetworkImpl:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    @property
    def name(self) -> str:
        """Get the network name."""
        return self._name

    @property
    def id(self) -> str:
        """Get the network ID (alias for get_id)."""
        return self.get_id()


class SharedNetwork(NetworkImpl):
    """
    A shared network that cannot be closed by users.
    
    This is useful for sharing a network across multiple test runs.
    Only the ResourceReaper can close this network.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/Network.java
    """

    def close(self) -> None:
        """Override close to prevent users from closing the shared network."""
        # Do not allow users to close SHARED network
        pass


# Singleton shared network instance
SHARED = SharedNetwork(name="testcontainers-shared")


def new_network(
    name: Optional[str] = None,
    driver: Optional[str] = None,
    enable_ipv6: Optional[bool] = None,
    labels: Optional[dict[str, str]] = None,
) -> NetworkImpl:
    """
    Create a new network with the given configuration.
    
    Args:
        name: Network name (auto-generated if not provided)
        driver: Network driver (e.g., 'bridge', 'overlay')
        enable_ipv6: Enable IPv6 networking
        labels: Additional labels for the network
        
    Returns:
        A new NetworkImpl instance
        
    Example:
        >>> with new_network() as network:
        ...     container1 = GenericContainer("redis").with_network(network)
        ...     container2 = GenericContainer("app").with_network(network)
        ...     # Containers can communicate using container names
    """
    return NetworkImpl(name=name, driver=driver, enable_ipv6=enable_ipv6, labels=labels)
