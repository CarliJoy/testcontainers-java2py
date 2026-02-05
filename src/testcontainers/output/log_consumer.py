"""Log consumers for container output.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/Slf4jLogConsumer.java
"""

from __future__ import annotations

import logging
from typing import Protocol, Optional

from .output_frame import OutputFrame, OutputType


class LogConsumer(Protocol):
    """Protocol for consuming container output.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/BaseConsumer.java
    """
    
    def accept(self, frame: OutputFrame) -> None:
        """Accept and process an output frame.
        
        Args:
            frame: The output frame to process
        """
        ...


class Slf4jLogConsumer:
    """A consumer that logs output to a Python logger (equivalent to SLF4J).
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/Slf4jLogConsumer.java
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        separate_output_streams: bool = False
    ) -> None:
        """Initialize the log consumer.
        
        Args:
            logger: Python logger to use
            separate_output_streams: If True, log STDOUT to info and STDERR to error
        """
        self._logger = logger
        self._separate_output_streams = separate_output_streams
        self._prefix = ""
        self._extra: dict[str, str] = {}

    def with_prefix(self, prefix: str) -> Slf4jLogConsumer:
        """Add a prefix to log messages.
        
        Args:
            prefix: Prefix string
            
        Returns:
            This consumer for method chaining
        """
        self._prefix = f"[{prefix}] "
        return self

    def with_extra(self, key: str, value: str) -> Slf4jLogConsumer:
        """Add extra context to log messages.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            This consumer for method chaining
        """
        self._extra[key] = value
        return self

    def with_separate_output_streams(self) -> Slf4jLogConsumer:
        """Enable separate output stream logging.
        
        Returns:
            This consumer for method chaining
        """
        self._separate_output_streams = True
        return self

    def accept(self, frame: OutputFrame) -> None:
        """Accept and log an output frame.
        
        Args:
            frame: The output frame to log
        """
        output_type = frame.type
        message = frame.get_utf8_string_without_line_ending()
        
        if output_type == OutputType.END:
            return
        
        # Build log message
        if self._separate_output_streams:
            if output_type == OutputType.STDOUT:
                self._logger.info(
                    f"{self._prefix}{message}",
                    extra=self._extra
                )
            elif output_type == OutputType.STDERR:
                self._logger.error(
                    f"{self._prefix}{message}",
                    extra=self._extra
                )
        else:
            self._logger.info(
                f"{self._prefix}{output_type.value}: {message}",
                extra=self._extra
            )


class PrintLogConsumer:
    """A simple consumer that prints output to stdout/stderr.
    
    This is a Python-specific implementation for convenience.
    """
    
    def __init__(self, prefix: Optional[str] = None) -> None:
        """Initialize the print consumer.
        
        Args:
            prefix: Optional prefix for output
        """
        self._prefix = f"[{prefix}] " if prefix else ""

    def accept(self, frame: OutputFrame) -> None:
        """Accept and print an output frame.
        
        Args:
            frame: The output frame to print
        """
        if frame.type == OutputType.END:
            return
        
        message = frame.get_utf8_string_without_line_ending()
        print(f"{self._prefix}{message}")
