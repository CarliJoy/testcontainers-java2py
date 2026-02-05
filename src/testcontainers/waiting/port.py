"""
Host port-based wait strategy.

This module provides a wait strategy that waits until specified ports
are accepting connections on the container host.
"""

from __future__ import annotations

import socket
import time
from datetime import timedelta
from typing import Optional

from testcontainers.waiting.wait_strategy import AbstractWaitStrategy


class HostPortWaitStrategy(AbstractWaitStrategy):
    """
    Wait strategy that waits until ports are accepting connections.
    
    This strategy attempts to establish socket connections to the specified
    ports on the container host. If no ports are specified, it checks all
    exposed ports.
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/HostPortWaitStrategy.java
    """
    
    def __init__(self):
        """Initialize the host port wait strategy."""
        super().__init__()
        self._ports: list[int] | None = None
    
    def with_ports(self, *ports: int) -> HostPortWaitStrategy:
        """
        Set specific ports to wait for.
        
        If not set, all exposed ports will be checked.
        
        Args:
            *ports: Port numbers to wait for
            
        Returns:
            This wait strategy for method chaining
        """
        self._ports = list(ports)
        return self
    
    def _wait_until_ready(self) -> None:
        """
        Wait until all specified ports are accepting connections.
        
        Raises:
            TimeoutError: If ports don't become available within the timeout
        """
        if self._wait_strategy_target is None:
            raise RuntimeError("Wait strategy target not set")
        
        # Determine which ports to check
        if self._ports is None or len(self._ports) == 0:
            # Use all liveness check ports
            ports_to_check = list(self._get_liveness_check_ports())
            if not ports_to_check:
                # No ports to check, consider ready
                return
        else:
            # Map container ports to host ports
            ports_to_check = [
                self._wait_strategy_target.get_mapped_port(port)
                for port in self._ports
            ]
        
        host = self._wait_strategy_target.get_host()
        timeout_seconds = self._startup_timeout.total_seconds()
        start_time = time.time()
        
        # Keep checking until all ports are available or timeout
        while time.time() - start_time < timeout_seconds:
            all_ports_ready = True
            
            for port in ports_to_check:
                if not self._check_port(host, port):
                    all_ports_ready = False
                    break
            
            if all_ports_ready:
                return
            
            # Sleep before trying again
            time.sleep(0.5)
        
        raise TimeoutError(
            f"Timed out waiting for ports {ports_to_check} to be ready on "
            f"{host} after {timeout_seconds} seconds"
        )
    
    def _check_port(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """
        Check if a port is accepting connections.
        
        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds
            
        Returns:
            True if the port is accepting connections, False otherwise
        """
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.error, socket.timeout, OSError):
            return False
