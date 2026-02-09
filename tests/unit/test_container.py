"""Tests for container protocol and types."""

from __future__ import annotations

import pytest

from testcontainers.core.container import ExecResult


class TestExecResult:
    """Tests for ExecResult dataclass."""

    def test_create_exec_result(self):
        """Test creating an ExecResult."""
        result = ExecResult(
            exit_code=0,
            stdout="Hello, World!",
            stderr=""
        )
        
        assert result.exit_code == 0
        assert result.stdout == "Hello, World!"
        assert result.stderr == ""

    def test_exec_result_with_error(self):
        """Test ExecResult with error output."""
        result = ExecResult(
            exit_code=1,
            stdout="",
            stderr="Error occurred"
        )
        
        assert result.exit_code == 1
        assert result.stdout == ""
        assert result.stderr == "Error occurred"

    def test_exec_result_equality(self):
        """Test ExecResult equality."""
        result1 = ExecResult(0, "output", "")
        result2 = ExecResult(0, "output", "")
        result3 = ExecResult(1, "output", "")
        
        assert result1 == result2
        assert result1 != result3
