"""Tests for advanced wait strategies."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, MagicMock, patch
import time

from testcontainers.waiting import (
    HttpWaitStrategy,
    ShellStrategy,
    WaitAllStrategy,
    WaitAllMode,
)
from testcontainers.core.container import ExecResult


@pytest.fixture
def mock_target():
    """Create a mock wait strategy target."""
    target = Mock()
    target.get_host.return_value = "localhost"
    target.get_exposed_port.return_value = 8080
    target.get_container_info.return_value = {"Name": "test_container"}
    return target


class TestHttpWaitStrategy:
    """Tests for HttpWaitStrategy."""

    def test_default_configuration(self, mock_target):
        """Test default HTTP wait strategy configuration."""
        strategy = HttpWaitStrategy()
        assert strategy._path == "/"
        assert strategy._method == "GET"
        assert strategy._tls_enabled is False

    def test_fluent_api(self):
        """Test fluent API configuration."""
        strategy = (
            HttpWaitStrategy()
            .for_path("/health")
            .for_port(8080)
            .for_status_code(200)
            .with_method("POST")
            .using_tls()
            .allow_insecure()
            .with_basic_credentials("user", "pass")
            .with_header("X-Test", "value")
            .with_read_timeout(5.0)
        )
        
        assert strategy._path == "/health"
        assert strategy._liveness_port == 8080
        assert 200 in strategy._status_codes
        assert strategy._method == "POST"
        assert strategy._tls_enabled is True
        assert strategy._allow_insecure is True
        assert strategy._username == "user"
        assert strategy._password == "pass"
        assert strategy._headers["X-Test"] == "value"
        assert strategy._read_timeout == 5.0

    def test_build_liveness_uri_http(self):
        """Test building HTTP URI."""
        strategy = HttpWaitStrategy().for_path("/api/health")
        mock_target = Mock()
        mock_target.get_host.return_value = "localhost"
        strategy._wait_strategy_target = mock_target
        
        uri = strategy._build_liveness_uri(8080)
        assert uri == "http://localhost:8080/api/health"

    def test_build_liveness_uri_https(self):
        """Test building HTTPS URI."""
        strategy = HttpWaitStrategy().using_tls().for_path("/secure")
        mock_target = Mock()
        mock_target.get_host.return_value = "example.com"
        strategy._wait_strategy_target = mock_target
        
        uri = strategy._build_liveness_uri(443)
        assert uri == "https://example.com/secure"

    def test_build_liveness_uri_default_ports(self):
        """Test that default ports are omitted."""
        strategy = HttpWaitStrategy()
        mock_target = Mock()
        mock_target.get_host.return_value = "localhost"
        strategy._wait_strategy_target = mock_target
        
        # HTTP port 80 should be omitted
        uri = strategy._build_liveness_uri(80)
        assert uri == "http://localhost/"
        
        # HTTPS port 443 should be omitted
        strategy_https = HttpWaitStrategy().using_tls()
        strategy_https._wait_strategy_target = mock_target
        uri = strategy_https._build_liveness_uri(443)
        assert uri == "https://localhost/"

    def test_check_status_code_default(self):
        """Test default status code check (200)."""
        strategy = HttpWaitStrategy()
        assert strategy._check_status_code(200) is True
        assert strategy._check_status_code(404) is False

    def test_check_status_code_specific(self):
        """Test specific status code check."""
        strategy = HttpWaitStrategy().for_status_code(201).for_status_code(202)
        assert strategy._check_status_code(201) is True
        assert strategy._check_status_code(202) is True
        assert strategy._check_status_code(200) is False

    def test_check_status_code_predicate(self):
        """Test status code predicate."""
        strategy = HttpWaitStrategy().for_status_code_matching(lambda c: c < 300)
        assert strategy._check_status_code(200) is True
        assert strategy._check_status_code(299) is True
        assert strategy._check_status_code(404) is False

    def test_read_timeout_validation(self):
        """Test read timeout validation."""
        strategy = HttpWaitStrategy()
        
        # Valid timeout
        strategy.with_read_timeout(5.0)
        assert strategy._read_timeout == 5.0
        
        # Invalid timeout
        with pytest.raises(ValueError, match="at least 1 millisecond"):
            strategy.with_read_timeout(0.0)


class TestShellStrategy:
    """Tests for ShellStrategy."""

    def test_with_command(self):
        """Test setting shell command."""
        strategy = ShellStrategy().with_command("test -f /ready")
        assert strategy._command == "test -f /ready"

    def test_requires_command(self, mock_target):
        """Test that command is required."""
        strategy = ShellStrategy().with_startup_timeout(1.0)
        strategy._wait_strategy_target = mock_target
        
        with pytest.raises(ValueError, match="Command must be set"):
            strategy._wait_until_ready()

    def test_wait_succeeds_when_command_succeeds(self, mock_target):
        """Test waiting succeeds when command succeeds."""
        strategy = ShellStrategy().with_command("echo ready").with_startup_timeout(5.0)
        strategy._wait_strategy_target = mock_target
        
        # Mock successful command execution
        mock_target.exec_in_container.return_value = ExecResult(0, b"ready\n", b"")
        
        # Should not raise
        strategy._wait_until_ready()
        
        # Verify command was called
        mock_target.exec_in_container.assert_called_with(
            "/bin/sh", "-c", "echo ready"
        )

    def test_wait_timeout_when_command_fails(self, mock_target):
        """Test timeout when command keeps failing."""
        strategy = ShellStrategy().with_command("false").with_startup_timeout(1.0)
        strategy._wait_strategy_target = mock_target
        
        # Mock failing command execution
        mock_target.exec_in_container.return_value = ExecResult(1, b"", b"error")
        
        with pytest.raises(TimeoutError, match="Timed out"):
            strategy._wait_until_ready()


class TestWaitAllStrategy:
    """Tests for WaitAllStrategy."""

    def test_default_mode(self):
        """Test default mode is WITH_OUTER_TIMEOUT."""
        strategy = WaitAllStrategy()
        assert strategy._mode == WaitAllMode.WITH_OUTER_TIMEOUT

    def test_with_strategy(self, mock_target):
        """Test adding strategies."""
        strategy = WaitAllStrategy()
        
        strategy1 = Mock()
        strategy2 = Mock()
        
        strategy.with_strategy(strategy1).with_strategy(strategy2)
        
        assert len(strategy._strategies) == 2
        assert strategy1 in strategy._strategies
        assert strategy2 in strategy._strategies

    def test_with_outer_timeout_mode(self, mock_target):
        """Test WITH_OUTER_TIMEOUT mode applies timeout to strategies."""
        strategy = WaitAllStrategy(WaitAllMode.WITH_OUTER_TIMEOUT)
        strategy.with_startup_timeout(10.0)
        
        strategy1 = Mock()
        strategy1.with_startup_timeout = Mock(return_value=strategy1)
        
        strategy.with_strategy(strategy1)
        
        # Should have applied timeout to strategy
        strategy1.with_startup_timeout.assert_called_with(10.0)

    def test_with_individual_timeouts_mode(self):
        """Test WITH_INDIVIDUAL_TIMEOUTS_ONLY mode."""
        strategy = WaitAllStrategy(WaitAllMode.WITH_INDIVIDUAL_TIMEOUTS_ONLY)
        
        # Should raise when trying to set timeout
        with pytest.raises(ValueError, match="not supported"):
            strategy.with_startup_timeout(10.0)

    def test_wait_until_ready_calls_all_strategies(self, mock_target):
        """Test that all strategies are called."""
        strategy = WaitAllStrategy()
        
        strategy1 = Mock()
        strategy2 = Mock()
        strategy1.wait_until_ready = Mock()
        strategy2.wait_until_ready = Mock()
        
        strategy.with_strategy(strategy1).with_strategy(strategy2)
        strategy.wait_until_ready(mock_target)
        
        strategy1.wait_until_ready.assert_called_once_with(mock_target)
        strategy2.wait_until_ready.assert_called_once_with(mock_target)

    def test_wait_all_respects_order(self, mock_target):
        """Test that strategies are waited for in order."""
        strategy = WaitAllStrategy()
        
        call_order = []
        
        def make_wait(name):
            def wait(target):
                call_order.append(name)
            return wait
        
        strategy1 = Mock()
        strategy1.wait_until_ready = make_wait("strategy1")
        
        strategy2 = Mock()
        strategy2.wait_until_ready = make_wait("strategy2")
        
        strategy.with_strategy(strategy1).with_strategy(strategy2)
        strategy.wait_until_ready(mock_target)
        
        assert call_order == ["strategy1", "strategy2"]
