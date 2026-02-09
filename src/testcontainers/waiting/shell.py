"""Shell command wait strategy implementation.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/ShellStrategy.java
"""

from __future__ import annotations

import logging
import time

from .wait_strategy import AbstractWaitStrategy

logger = logging.getLogger(__name__)


class ShellStrategy(AbstractWaitStrategy):
    """Wait strategy that waits for a shell command to exit successfully.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/ShellStrategy.java
    """

    def __init__(self) -> None:
        super().__init__()
        self._command: str | None = None

    def with_command(self, command: str) -> ShellStrategy:
        """Set the shell command to execute.
        
        Args:
            command: Shell command to execute in the container
            
        Returns:
            This strategy for method chaining
        """
        self._command = command
        return self

    def _wait_until_ready(self) -> None:
        """Implementation of the wait logic."""
        if not self._command:
            raise ValueError("Command must be set before waiting")
        
        container_name = self._wait_strategy_target.get_container_info()["Name"]
        
        logger.info(
            "%s: Waiting for %d seconds for command to succeed: %s",
            container_name,
            self._startup_timeout,
            self._command,
        )
        
        start_time = time.time()
        while True:
            try:
                # Execute command in container
                result = self._wait_strategy_target.exec_in_container(
                    "/bin/sh", "-c", self._command
                )
                
                if result.exit_code == 0:
                    logger.info(
                        "%s: Command succeeded: %s", container_name, self._command
                    )
                    return
                
                # Command failed, check timeout
                if time.time() - start_time >= self._startup_timeout:
                    raise TimeoutError(
                        f"Timed out waiting for container to execute "
                        f"`{self._command}` successfully. "
                        f"Last exit code: {result.exit_code}"
                    )
                
                time.sleep(0.5)
                
            except Exception as e:
                if time.time() - start_time >= self._startup_timeout:
                    raise TimeoutError(
                        f"Timed out waiting for container to execute "
                        f"`{self._command}` successfully."
                    ) from e
                time.sleep(0.5)
