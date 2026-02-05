"""Composite wait strategy that waits for multiple strategies.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/WaitAllStrategy.java
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import TYPE_CHECKING

from .wait_strategy import WaitStrategy, WaitStrategyTarget

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class WaitAllMode(Enum):
    """Mode for WaitAllStrategy timeout handling.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/WaitAllStrategy.java
    """
    
    # Outer timeout applied to each strategy
    WITH_OUTER_TIMEOUT = "WITH_OUTER_TIMEOUT"
    
    # Each strategy uses its own timeout, no outer limit
    WITH_INDIVIDUAL_TIMEOUTS_ONLY = "WITH_INDIVIDUAL_TIMEOUTS_ONLY"
    
    # Strategies use their timeout, but outer timeout kills all
    WITH_MAXIMUM_OUTER_TIMEOUT = "WITH_MAXIMUM_OUTER_TIMEOUT"


class WaitAllStrategy(WaitStrategy):
    """Wait strategy that waits for multiple strategies to complete.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/WaitAllStrategy.java
    """

    def __init__(self, mode: WaitAllMode = WaitAllMode.WITH_OUTER_TIMEOUT) -> None:
        """Initialize the composite wait strategy.
        
        Args:
            mode: Timeout handling mode
        """
        self._mode = mode
        self._strategies: list[WaitStrategy] = []
        self._timeout = 30.0  # seconds

    def with_strategy(self, strategy: WaitStrategy) -> WaitAllStrategy:
        """Add a strategy to wait for.
        
        Args:
            strategy: Strategy to add
            
        Returns:
            This strategy for method chaining
        """
        # Apply outer timeout if mode requires it
        if self._mode == WaitAllMode.WITH_OUTER_TIMEOUT:
            strategy.with_startup_timeout(self._timeout)
        
        self._strategies.append(strategy)
        return self

    def with_startup_timeout(self, timeout: float) -> WaitAllStrategy:
        """Set the startup timeout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            This strategy for method chaining
        """
        if self._mode == WaitAllMode.WITH_INDIVIDUAL_TIMEOUTS_ONLY:
            raise ValueError(
                f"Changing startup timeout is not supported with mode "
                f"{WaitAllMode.WITH_INDIVIDUAL_TIMEOUTS_ONLY}"
            )
        
        self._timeout = timeout
        
        # Apply to all existing strategies
        for strategy in self._strategies:
            strategy.with_startup_timeout(self._timeout)
        
        return self

    def wait_until_ready(self, target: WaitStrategyTarget) -> None:
        """Wait for all strategies to be ready.
        
        Args:
            target: The container to wait for
        """
        if self._mode == WaitAllMode.WITH_INDIVIDUAL_TIMEOUTS_ONLY:
            self._wait_until_nested_strategies_are_ready(target)
        else:
            # Apply outer timeout
            start_time = time.time()
            
            try:
                self._wait_until_nested_strategies_are_ready(target)
            except Exception as e:
                elapsed = time.time() - start_time
                if elapsed >= self._timeout:
                    raise TimeoutError(
                        f"Timed out after {elapsed:.1f}s waiting for all strategies "
                        f"(timeout: {self._timeout}s)"
                    ) from e
                raise
            
            elapsed = time.time() - start_time
            if self._mode == WaitAllMode.WITH_MAXIMUM_OUTER_TIMEOUT and elapsed >= self._timeout:
                raise TimeoutError(
                    f"Timed out after {elapsed:.1f}s waiting for all strategies "
                    f"(timeout: {self._timeout}s)"
                )

    def _wait_until_nested_strategies_are_ready(
        self, target: WaitStrategyTarget
    ) -> None:
        """Wait for all nested strategies."""
        for i, strategy in enumerate(self._strategies):
            logger.debug("Waiting for strategy %d of %d", i + 1, len(self._strategies))
            strategy.wait_until_ready(target)
