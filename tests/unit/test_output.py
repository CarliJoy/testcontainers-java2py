"""Tests for container output handling."""

from __future__ import annotations

import logging
import pytest
from unittest.mock import Mock

from testcontainers.output import (
    OutputFrame,
    OutputType,
    Slf4jLogConsumer,
    PrintLogConsumer,
)


class TestOutputFrame:
    """Tests for OutputFrame."""

    def test_create_stdout_frame(self):
        """Test creating STDOUT frame."""
        data = b"Hello World\n"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        assert frame.type == OutputType.STDOUT
        assert frame.bytes == data

    def test_create_stderr_frame(self):
        """Test creating STDERR frame."""
        data = b"Error message\n"
        frame = OutputFrame(OutputType.STDERR, data)
        
        assert frame.type == OutputType.STDERR
        assert frame.bytes == data

    def test_create_end_frame(self):
        """Test END sentinel frame."""
        frame = OutputFrame.END
        
        assert frame.type == OutputType.END
        assert frame.bytes is None

    def test_get_utf8_string(self):
        """Test getting UTF-8 string with line ending."""
        data = b"Test message\n"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        result = frame.get_utf8_string()
        assert result == "Test message\n"

    def test_get_utf8_string_without_line_ending_lf(self):
        """Test removing LF line ending."""
        data = b"Test message\n"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        result = frame.get_utf8_string_without_line_ending()
        assert result == "Test message"

    def test_get_utf8_string_without_line_ending_crlf(self):
        """Test removing CRLF line ending."""
        data = b"Test message\r\n"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        result = frame.get_utf8_string_without_line_ending()
        assert result == "Test message"

    def test_get_utf8_string_without_line_ending_cr(self):
        """Test removing CR line ending."""
        data = b"Test message\r"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        result = frame.get_utf8_string_without_line_ending()
        assert result == "Test message"

    def test_get_utf8_string_without_line_ending_no_ending(self):
        """Test when there's no line ending."""
        data = b"Test message"
        frame = OutputFrame(OutputType.STDOUT, data)
        
        result = frame.get_utf8_string_without_line_ending()
        assert result == "Test message"

    def test_get_utf8_string_empty(self):
        """Test with empty data."""
        frame = OutputFrame(OutputType.STDOUT, b"")
        
        assert frame.get_utf8_string() == ""
        assert frame.get_utf8_string_without_line_ending() == ""

    def test_get_utf8_string_none(self):
        """Test with None data."""
        frame = OutputFrame(OutputType.END, None)
        
        assert frame.get_utf8_string() == ""
        assert frame.get_utf8_string_without_line_ending() == ""

    def test_repr(self):
        """Test string representation."""
        frame = OutputFrame(OutputType.STDOUT, b"test\n")
        repr_str = repr(frame)
        
        assert "OutputType.STDOUT" in repr_str
        assert "test" in repr_str


class TestSlf4jLogConsumer:
    """Tests for Slf4jLogConsumer."""

    def test_create_with_logger(self):
        """Test creating consumer with logger."""
        logger = logging.getLogger("test")
        consumer = Slf4jLogConsumer(logger)
        
        assert consumer._logger == logger
        assert consumer._separate_output_streams is False

    def test_with_prefix(self):
        """Test adding prefix."""
        logger = logging.getLogger("test")
        consumer = Slf4jLogConsumer(logger).with_prefix("container")
        
        assert consumer._prefix == "[container] "

    def test_with_extra(self):
        """Test adding extra context."""
        logger = logging.getLogger("test")
        consumer = Slf4jLogConsumer(logger).with_extra("container_id", "abc123")
        
        assert consumer._extra["container_id"] == "abc123"

    def test_with_separate_output_streams(self):
        """Test enabling separate output streams."""
        logger = logging.getLogger("test")
        consumer = Slf4jLogConsumer(logger).with_separate_output_streams()
        
        assert consumer._separate_output_streams is True

    def test_accept_stdout_combined(self, caplog):
        """Test accepting STDOUT with combined streams."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger)
        
        frame = OutputFrame(OutputType.STDOUT, b"Test message\n")
        
        with caplog.at_level(logging.INFO):
            consumer.accept(frame)
        
        assert "STDOUT: Test message" in caplog.text

    def test_accept_stderr_combined(self, caplog):
        """Test accepting STDERR with combined streams."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger)
        
        frame = OutputFrame(OutputType.STDERR, b"Error message\n")
        
        with caplog.at_level(logging.INFO):
            consumer.accept(frame)
        
        assert "STDERR: Error message" in caplog.text

    def test_accept_stdout_separate(self, caplog):
        """Test accepting STDOUT with separate streams."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger, separate_output_streams=True)
        
        frame = OutputFrame(OutputType.STDOUT, b"Test message\n")
        
        with caplog.at_level(logging.INFO):
            consumer.accept(frame)
        
        assert "Test message" in caplog.text
        # Should not contain stream type
        assert "STDOUT" not in caplog.text

    def test_accept_stderr_separate(self, caplog):
        """Test accepting STDERR with separate streams."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger, separate_output_streams=True)
        
        frame = OutputFrame(OutputType.STDERR, b"Error message\n")
        
        with caplog.at_level(logging.ERROR):
            consumer.accept(frame)
        
        assert "Error message" in caplog.text

    def test_accept_with_prefix(self, caplog):
        """Test accepting with prefix."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger).with_prefix("my-container")
        
        frame = OutputFrame(OutputType.STDOUT, b"Test\n")
        
        with caplog.at_level(logging.INFO):
            consumer.accept(frame)
        
        assert "[my-container]" in caplog.text

    def test_accept_end_frame(self, caplog):
        """Test accepting END frame (should be ignored)."""
        logger = logging.getLogger("test.consumer")
        consumer = Slf4jLogConsumer(logger)
        
        with caplog.at_level(logging.INFO):
            consumer.accept(OutputFrame.END)
        
        # Should not log anything
        assert len(caplog.records) == 0


class TestPrintLogConsumer:
    """Tests for PrintLogConsumer."""

    def test_create_without_prefix(self):
        """Test creating consumer without prefix."""
        consumer = PrintLogConsumer()
        assert consumer._prefix == ""

    def test_create_with_prefix(self):
        """Test creating consumer with prefix."""
        consumer = PrintLogConsumer(prefix="container")
        assert consumer._prefix == "[container] "

    def test_accept_stdout(self, capsys):
        """Test accepting STDOUT."""
        consumer = PrintLogConsumer()
        frame = OutputFrame(OutputType.STDOUT, b"Test output\n")
        
        consumer.accept(frame)
        
        captured = capsys.readouterr()
        assert "Test output" in captured.out

    def test_accept_with_prefix(self, capsys):
        """Test accepting with prefix."""
        consumer = PrintLogConsumer(prefix="my-container")
        frame = OutputFrame(OutputType.STDOUT, b"Test\n")
        
        consumer.accept(frame)
        
        captured = capsys.readouterr()
        assert "[my-container]" in captured.out
        assert "Test" in captured.out

    def test_accept_end_frame(self, capsys):
        """Test accepting END frame (should be ignored)."""
        consumer = PrintLogConsumer()
        consumer.accept(OutputFrame.END)
        
        captured = capsys.readouterr()
        assert captured.out == ""
