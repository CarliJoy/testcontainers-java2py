"""
Base wait strategy interface and implementations.

This module provides the WaitStrategy protocol and base implementation for
waiting until containers are ready.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Protocol, Set

from testcontainers.core.container_state import ContainerState


class WaitStrategyTarget(Protocol):
    """
    Protocol for container targets that wait strategies can operate on.
    
    This extends ContainerState with additional methods needed for waiting.
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/WaitStrategy.java
    """
    
    def get_container_id(self) -> str:
        """Get the container ID."""
        ...
    
    def get_host(self) -> str:
        """Get the container host."""
        ...
    
    def is_running(self) -> bool:
        """Check if container is running."""
        ...
    
    def is_healthy(self) -> bool:
        """Check if container is healthy."""
        ...
    
    def get_exposed_ports(self) -> list[int]:
        """Get exposed ports."""
        ...
    
    def get_mapped_port(self, port: int) -> int:
        """Get mapped port."""
        ...
    
    def get_logs(self) -> str:
        """Get container logs."""
        ...
    
    def get_liveness_check_port_numbers(self) -> Set[int]:
        """
        Get the ports on which to check if the container is ready.
        
        Returns:
            Set of port numbers to check for liveness
        """
        exposed = set(self.get_exposed_ports())
        mapped = {self.get_mapped_port(port) for port in exposed}
        return mapped


class WaitStrategy(Protocol):
    """
    Protocol for wait strategies.
    
    A wait strategy determines when a container is considered ready to use.
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/WaitStrategy.java
    """
    
    def wait_until_ready(self, wait_strategy_target: WaitStrategyTarget) -> None:
        """
        Wait until the container is ready.
        
        Args:
            wait_strategy_target: The container to wait for
            
        Raises:
            TimeoutError: If the container doesn't become ready within the timeout
        """
        ...
    
    def with_startup_timeout(self, startup_timeout: timedelta) -> WaitStrategy:
        """
        Set the startup timeout.
        
        Args:
            startup_timeout: Maximum time to wait for container
            
        Returns:
            This wait strategy for method chaining
        """
        ...


class AbstractWaitStrategy(ABC):
    """
    Abstract base class for wait strategies.
    
    Provides common functionality for concrete wait strategy implementations.
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/AbstractWaitStrategy.java
    """
    
    def __init__(self):
        """Initialize the wait strategy."""
        self._wait_strategy_target: WaitStrategyTarget | None = None
        self._startup_timeout = timedelta(seconds=60)
    
    def wait_until_ready(self, wait_strategy_target: WaitStrategyTarget) -> None:
        """
        Wait until the target has started.
        
        Args:
            wait_strategy_target: The target of the wait strategy
        """
        self._wait_strategy_target = wait_strategy_target
        self._wait_until_ready()
    
    @abstractmethod
    def _wait_until_ready(self) -> None:
        """
        Wait until the target has started.
        
        This method should be implemented by subclasses.
        """
        pass
    
    def with_startup_timeout(self, startup_timeout: timedelta) -> AbstractWaitStrategy:
        """
        Set the duration of waiting time until container treated as started.
        
        Args:
            startup_timeout: Timeout duration
            
        Returns:
            This wait strategy for method chaining
        """
        self._startup_timeout = startup_timeout
        return self
    
    def _get_liveness_check_ports(self) -> Set[int]:
        """
        Get the ports on which to check if the container is ready.
        
        Returns:
            Set of port numbers
        """
        if self._wait_strategy_target is None:
            return set()
        return self._wait_strategy_target.get_liveness_check_port_numbers()
