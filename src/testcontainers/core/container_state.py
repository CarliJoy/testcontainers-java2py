"""
Container state protocol.

This module defines the ContainerState protocol which provides methods
for querying the state of a running container.
"""

from __future__ import annotations

from typing import Protocol, Optional, List, Dict, Any


class ContainerState(Protocol):
    """
    Protocol for querying container state.
    
    This protocol provides methods to check the state of a container,
    get port mappings, and retrieve container information.
    """
    
    STATE_HEALTHY = "healthy"
    
    def get_container_id(self) -> Optional[str]:
        """
        Get the container ID.
        
        Returns:
            Container ID, or None if container not yet created
        """
        ...
    
    def get_host(self) -> str:
        """
        Get the host that this container may be reached on.
        
        This may not be the local machine (e.g., when using Docker Machine).
        
        Returns:
            Host address (IP or hostname)
        """
        ...
    
    def is_running(self) -> bool:
        """
        Check if the container is currently running.
        
        Returns:
            True if container is running, False otherwise
        """
        ...
    
    def is_created(self) -> bool:
        """
        Check if the container has been created.
        
        Returns:
            True if container is created (may or may not be running)
        """
        ...
    
    def is_healthy(self) -> bool:
        """
        Check if the container has health state 'healthy'.
        
        Returns:
            True if container is healthy
            
        Raises:
            RuntimeError: If container image has no healthcheck
        """
        ...
    
    def get_exposed_ports(self) -> List[int]:
        """
        Get the list of ports exposed by this container.
        
        Returns:
            List of exposed port numbers
        """
        ...
    
    def get_mapped_port(self, port: int) -> int:
        """
        Get the actual mapped port for a given exposed port.
        
        Should be used in conjunction with get_host().
        
        Args:
            port: The exposed port number
            
        Returns:
            The host port that the exposed port is mapped to
            
        Raises:
            ValueError: If the port is not exposed
        """
        ...
    
    def get_first_mapped_port(self) -> int:
        """
        Get the actual mapped port for the first exposed port.
        
        Should be used in conjunction with get_host().
        
        Returns:
            The host port that the first exposed port is mapped to
            
        Raises:
            RuntimeError: If there are no exposed ports
        """
        ...
    
    def get_logs(self) -> str:
        """
        Get the container logs as a string.
        
        Returns:
            Container logs (stdout and stderr combined)
        """
        ...
    
    def get_container_info(self) -> Dict[str, Any]:
        """
        Get cached container information.
        
        Returns:
            Container inspection data
        """
        ...
    
    def get_current_container_info(self) -> Dict[str, Any]:
        """
        Inspect the container and return up-to-date information.
        
        This performs a fresh inspection of the container.
        
        Returns:
            Current container inspection data
        """
        ...
    
    def copy_file_from_container(self, container_path: str, local_path: str) -> None:
        """
        Copy a file or directory from the container to the host.
        
        Args:
            container_path: Path in the container
            local_path: Destination path on the host
        """
        ...
    
    def copy_file_to_container(self, local_path: str, container_path: str) -> None:
        """
        Copy a file or directory from the host to the container.
        
        Args:
            local_path: Source path on the host
            container_path: Destination path in the container
        """
        ...
