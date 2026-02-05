"""Output frame for container logs.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/OutputFrame.java
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class OutputType(Enum):
    """Type of output stream.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/OutputFrame.java
    """
    
    STDOUT = "STDOUT"
    STDERR = "STDERR"
    END = "END"


class OutputFrame:
    """Holds exactly one complete line of container output.
    
    Lines are split on newline characters (LF, CR LF).
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/output/OutputFrame.java
    """
    
    # Sentinel frame indicating end of output
    END: OutputFrame
    
    def __init__(self, output_type: OutputType, data: Optional[bytes]) -> None:
        """Initialize an output frame.
        
        Args:
            output_type: Type of output (STDOUT, STDERR, END)
            data: Raw bytes of the output line
        """
        self._type = output_type
        self._bytes = data

    @property
    def type(self) -> OutputType:
        """Get the output type."""
        return self._type

    @property
    def bytes(self) -> Optional[bytes]:
        """Get the raw bytes."""
        return self._bytes

    def get_utf8_string(self) -> str:
        """Get the output as a UTF-8 string, including line ending."""
        if self._bytes is None:
            return ""
        return self._bytes.decode("utf-8", errors="replace")

    def get_utf8_string_without_line_ending(self) -> str:
        """Get the output as a UTF-8 string, excluding line ending."""
        if self._bytes is None:
            return ""
        
        # Determine line ending length
        length = len(self._bytes)
        line_ending_length = self._determine_line_ending_length(self._bytes)
        
        # Decode without line ending
        return self._bytes[:length - line_ending_length].decode("utf-8", errors="replace")

    @staticmethod
    def _determine_line_ending_length(data: bytes) -> int:
        """Determine the length of the line ending."""
        if not data:
            return 0
        
        # Check last character
        if data[-1] == ord('\r'):
            return 1
        elif data[-1] == ord('\n'):
            # Check for CRLF
            if len(data) > 1 and data[-2] == ord('\r'):
                return 2
            return 1
        
        return 0

    def __repr__(self) -> str:
        """String representation of the frame."""
        return f"OutputFrame(type={self._type}, data={self.get_utf8_string()!r})"


# Create the END sentinel
OutputFrame.END = OutputFrame(OutputType.END, None)
