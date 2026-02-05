"""
Log message-based wait strategy.

This module provides a wait strategy that waits for a specific log message
or pattern to appear in the container logs.
"""

from __future__ import annotations

import re
import time
from datetime import timedelta

from testcontainers.waiting.wait_strategy import AbstractWaitStrategy


class LogMessageWaitStrategy(AbstractWaitStrategy):
    """
    Wait strategy that waits for a specific message in container logs.
    
    This strategy monitors container logs and waits until a message matching
    the specified regular expression appears a specified number of times.
    """
    
    def __init__(self):
        """Initialize the log message wait strategy."""
        super().__init__()
        self._regex: str | None = None
        self._times: int = 1
    
    def with_regex(self, regex: str) -> LogMessageWaitStrategy:
        """
        Set the regular expression to match in logs.
        
        Args:
            regex: Regular expression pattern to match
            
        Returns:
            This wait strategy for method chaining
        """
        self._regex = regex
        return self
    
    def with_times(self, times: int) -> LogMessageWaitStrategy:
        """
        Set the number of times the message should appear.
        
        Args:
            times: Number of times to find the message
            
        Returns:
            This wait strategy for method chaining
        """
        self._times = times
        return self
    
    def _wait_until_ready(self) -> None:
        """
        Wait until the log message appears the required number of times.
        
        Raises:
            TimeoutError: If the message doesn't appear within the timeout
            ValueError: If no regex pattern is set
        """
        if self._wait_strategy_target is None:
            raise RuntimeError("Wait strategy target not set")
        
        if self._regex is None:
            raise ValueError("Regex pattern must be set")
        
        # Compile the regex pattern with DOTALL flag (matches across newlines)
        pattern = re.compile(self._regex, re.DOTALL)
        
        timeout_seconds = self._startup_timeout.total_seconds()
        start_time = time.time()
        match_count = 0
        last_log_length = 0
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Get the latest logs
                logs = self._wait_strategy_target.get_logs()
                
                # Only search in new log content
                new_logs = logs[last_log_length:]
                last_log_length = len(logs)
                
                # Count matches in new log content
                matches = pattern.findall(new_logs)
                match_count += len(matches)
                
                # Check if we've found enough matches
                if match_count >= self._times:
                    return
                
            except Exception:
                # Container might not be fully started yet
                pass
            
            # Sleep before checking again
            time.sleep(0.5)
        
        raise TimeoutError(
            f"Timed out waiting for log output matching '{self._regex}' "
            f"(found {match_count}/{self._times} times) after {timeout_seconds} seconds"
        )
