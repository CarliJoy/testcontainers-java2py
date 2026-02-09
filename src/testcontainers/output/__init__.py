"""Container output handling.

This module provides classes for capturing and processing container output.
"""

from .output_frame import OutputFrame, OutputType
from .log_consumer import LogConsumer, Slf4jLogConsumer, PrintLogConsumer

__all__ = [
    "OutputFrame",
    "OutputType",
    "LogConsumer",
    "Slf4jLogConsumer",
    "PrintLogConsumer",
]