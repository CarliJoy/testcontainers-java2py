"""
Container enums and simple types.

This module contains enums and simple types used by container classes.
"""

from __future__ import annotations

from enum import Enum


class BindMode(Enum):
    """Possible modes for binding storage volumes."""
    
    READ_ONLY = "ro"
    READ_WRITE = "rw"
    
    def __str__(self) -> str:
        """Return the string representation for Docker."""
        return self.value


class SelinuxContext(Enum):
    """Possible contexts for use with SELinux."""
    
    SHARED = "z"
    SINGLE = "Z"
    NONE = ""
    
    def __str__(self) -> str:
        """Return the string representation for Docker."""
        return self.value


class InternetProtocol(Enum):
    """The IP protocols supported by Docker."""
    
    TCP = "tcp"
    UDP = "udp"
    
    def to_docker_notation(self) -> str:
        """
        Convert to Docker notation.
        
        Returns:
            Protocol name in lowercase (e.g., 'tcp', 'udp')
        """
        return self.value
    
    @classmethod
    def from_docker_notation(cls, protocol: str) -> InternetProtocol:
        """
        Create from Docker notation.
        
        Args:
            protocol: Protocol string (case-insensitive)
            
        Returns:
            InternetProtocol enum value
            
        Raises:
            ValueError: If protocol is not recognized
        """
        protocol_upper = protocol.upper()
        for member in cls:
            if member.name == protocol_upper:
                return member
        raise ValueError(f"Unknown protocol: {protocol}")
    
    def __str__(self) -> str:
        """Return the string representation for Docker."""
        return self.value
