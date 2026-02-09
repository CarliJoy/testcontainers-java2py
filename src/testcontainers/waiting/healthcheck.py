"""
Docker healthcheck-based wait strategy.

This module provides a wait strategy that leverages Docker's built-in
healthcheck mechanism.
"""

from __future__ import annotations

import time
from datetime import timedelta

from testcontainers.waiting.wait_strategy import AbstractWaitStrategy


class DockerHealthcheckWaitStrategy(AbstractWaitStrategy):
    """
    Wait strategy leveraging Docker's built-in healthcheck mechanism.
    
    This strategy polls the container's health status and waits until
    it reports as healthy.
    
    See: https://docs.docker.com/engine/reference/builder/#healthcheck
    
    
    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/DockerHealthcheckWaitStrategy.java
    """
    
    def _wait_until_ready(self) -> None:
        """
        Wait until the container reports healthy status.
        
        Raises:
            TimeoutError: If the container doesn't become healthy within the timeout
            RuntimeError: If the container has no healthcheck configured
        """
        if self._wait_strategy_target is None:
            raise RuntimeError("Wait strategy target not set")
        
        timeout_seconds = self._startup_timeout.total_seconds()
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                if self._wait_strategy_target.is_healthy():
                    return
            except RuntimeError:
                # Container might not have healthcheck configured
                raise
            
            # Sleep before checking again (1 second intervals)
            time.sleep(1)
        
        raise TimeoutError(
            f"Timed out waiting for container to become healthy after "
            f"{timeout_seconds} seconds"
        )
