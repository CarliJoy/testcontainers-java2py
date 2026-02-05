"""
Container protocol and related types.

This module defines the Container protocol which specifies the interface
that all container classes must implement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic, Optional, List, Dict, Any

from testcontainers.core.container_types import BindMode, SelinuxContext


# Type variable for self-referencing containers
SELF = TypeVar('SELF', bound='Container')


@dataclass
class ExecResult:
    """
    Results from a docker exec command.
    
    Attributes:
        exit_code: The exit code of the command
        stdout: Standard output from the command
        stderr: Standard error from the command
    """
    exit_code: int
    stdout: str
    stderr: str


class Container(Protocol[SELF]):
    """
    Protocol defining the container API.
    
    This protocol specifies the interface that all container implementations
    must provide. It includes methods for configuration, lifecycle management,
    and state querying.
    """
    
    def self(self) -> SELF:
        """
        Return a reference to this container instance.
        
        This is useful for fluent API patterns where methods return self
        for method chaining.
        
        Returns:
            Reference to this container instance
        """
        ...
    
    def set_command(self, *command: str) -> None:
        """
        Set the command that should be run in the container.
        
        Args:
            *command: Command parts to run in the container
        """
        ...
    
    def add_env(self, key: str, value: str) -> None:
        """
        Add an environment variable to be passed to the container.
        
        Args:
            key: Environment variable key
            value: Environment variable value
        """
        ...
    
    def add_exposed_port(self, port: int) -> None:
        """
        Add an exposed port.
        
        Args:
            port: TCP port to expose
        """
        ...
    
    def add_exposed_ports(self, *ports: int) -> None:
        """
        Add multiple exposed ports.
        
        Args:
            *ports: TCP ports to expose
        """
        ...
    
    # Fluent API methods that return self
    
    def with_command(self, *command: str) -> SELF:
        """
        Set the command (fluent API).
        
        Args:
            *command: Command parts to run
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    def with_env(self, key: str, value: str) -> SELF:
        """
        Add environment variable (fluent API).
        
        Args:
            key: Environment variable key
            value: Environment variable value
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    def with_exposed_ports(self, *ports: int) -> SELF:
        """
        Add exposed ports (fluent API).
        
        Args:
            *ports: TCP ports to expose
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    def with_label(self, key: str, value: str) -> SELF:
        """
        Add a label to the container (fluent API).
        
        Args:
            key: Label key
            value: Label value
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    def with_network(self, network: Any) -> SELF:
        """
        Set the network for the container (fluent API).
        
        Args:
            network: Network to use
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    def with_network_aliases(self, *aliases: str) -> SELF:
        """
        Set network aliases for the container (fluent API).
        
        Args:
            *aliases: Network aliases
            
        Returns:
            This container instance for method chaining
        """
        ...
    
    # Lifecycle methods
    
    def start(self) -> None:
        """Start the container."""
        ...
    
    def stop(self) -> None:
        """Stop the container."""
        ...
    
    # Execution methods
    
    def exec(self, command: str | List[str]) -> ExecResult:
        """
        Execute a command in the running container.
        
        Args:
            command: Command to execute
            
        Returns:
            ExecResult with exit code and output
        """
        ...
