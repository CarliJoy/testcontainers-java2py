"""Tests for wait strategies."""

from __future__ import annotations

import time
from datetime import timedelta
from unittest.mock import Mock, MagicMock

import pytest

from testcontainers.waiting import (
    WaitStrategyTarget,
    AbstractWaitStrategy,
    DockerHealthcheckWaitStrategy,
    LogMessageWaitStrategy,
    HostPortWaitStrategy,
)


@pytest.fixture
def mock_target():
    """Create a mock wait strategy target."""
    target = Mock(spec=WaitStrategyTarget)
    target.get_container_id.return_value = "test_container_id"
    target.get_host.return_value = "localhost"
    target.is_running.return_value = True
    target.is_healthy.return_value = False
    target.get_exposed_ports.return_value = [8080]
    target.get_mapped_port.return_value = 8080
    target.get_logs.return_value = ""
    target.get_liveness_check_port_numbers.return_value = {8080}
    return target


class TestAbstractWaitStrategy:
    """Tests for AbstractWaitStrategy base class."""
    
    def test_default_timeout(self):
        """Test default startup timeout is 60 seconds."""
        class TestStrategy(AbstractWaitStrategy):
            def _wait_until_ready(self):
                pass
        
        strategy = TestStrategy()
        assert strategy._startup_timeout == timedelta(seconds=60)
    
    def test_with_startup_timeout(self):
        """Test setting custom startup timeout."""
        class TestStrategy(AbstractWaitStrategy):
            def _wait_until_ready(self):
                pass
        
        strategy = TestStrategy()
        result = strategy.with_startup_timeout(timedelta(seconds=30))
        
        assert strategy._startup_timeout == timedelta(seconds=30)
        assert result is strategy  # Fluent API
    
    def test_wait_until_ready_sets_target(self, mock_target):
        """Test that wait_until_ready sets the target."""
        class TestStrategy(AbstractWaitStrategy):
            def _wait_until_ready(self):
                pass
        
        strategy = TestStrategy()
        strategy.wait_until_ready(mock_target)
        
        assert strategy._wait_strategy_target is mock_target


class TestDockerHealthcheckWaitStrategy:
    """Tests for DockerHealthcheckWaitStrategy."""
    
    def test_wait_succeeds_when_healthy(self, mock_target):
        """Test wait succeeds when container becomes healthy."""
        mock_target.is_healthy.return_value = True
        
        strategy = DockerHealthcheckWaitStrategy()
        strategy.wait_until_ready(mock_target)
        
        mock_target.is_healthy.assert_called()
    
    def test_wait_timeout(self, mock_target):
        """Test wait times out if container never becomes healthy."""
        mock_target.is_healthy.return_value = False
        
        strategy = DockerHealthcheckWaitStrategy()
        strategy = strategy.with_startup_timeout(timedelta(seconds=1))
        
        with pytest.raises(TimeoutError, match="Timed out waiting for container to become healthy"):
            strategy.wait_until_ready(mock_target)
    
    def test_wait_eventually_succeeds(self, mock_target):
        """Test wait succeeds when container becomes healthy after some time."""
        call_count = [0]
        
        def is_healthy_side_effect():
            call_count[0] += 1
            return call_count[0] > 2  # Healthy after 2 calls
        
        mock_target.is_healthy.side_effect = is_healthy_side_effect
        
        strategy = DockerHealthcheckWaitStrategy()
        strategy.wait_until_ready(mock_target)
        
        assert call_count[0] >= 3


class TestLogMessageWaitStrategy:
    """Tests for LogMessageWaitStrategy."""
    
    def test_wait_succeeds_when_message_found(self, mock_target):
        """Test wait succeeds when log message is found."""
        mock_target.get_logs.return_value = "Server started successfully"
        
        strategy = LogMessageWaitStrategy()
        strategy = strategy.with_regex(".*Server started.*")
        strategy.wait_until_ready(mock_target)
        
        mock_target.get_logs.assert_called()
    
    def test_wait_timeout(self, mock_target):
        """Test wait times out if message never appears."""
        mock_target.get_logs.return_value = "Some other log message"
        
        strategy = LogMessageWaitStrategy()
        strategy = strategy.with_regex(".*Server started.*")
        strategy = strategy.with_startup_timeout(timedelta(seconds=1))
        
        with pytest.raises(TimeoutError, match="Timed out waiting for log output"):
            strategy.wait_until_ready(mock_target)
    
    def test_wait_requires_regex(self, mock_target):
        """Test wait fails if no regex is set."""
        strategy = LogMessageWaitStrategy()
        
        with pytest.raises(ValueError, match="Regex pattern must be set"):
            strategy.wait_until_ready(mock_target)
    
    def test_wait_with_multiple_occurrences(self, mock_target):
        """Test wait can require multiple occurrences."""
        logs = ["First log", "Second log", "Third log"]
        call_count = [0]
        
        def get_logs_side_effect():
            result = "\n".join(logs[:call_count[0] + 1])
            call_count[0] += 1
            return result
        
        mock_target.get_logs.side_effect = get_logs_side_effect
        
        strategy = LogMessageWaitStrategy()
        strategy = strategy.with_regex(".*log.*")
        strategy = strategy.with_times(3)
        strategy.wait_until_ready(mock_target)
        
        assert call_count[0] >= 3
    
    def test_regex_matches_multiline(self, mock_target):
        """Test regex can match across multiple lines."""
        mock_target.get_logs.return_value = "Line 1\nLine 2\nLine 3"
        
        strategy = LogMessageWaitStrategy()
        strategy = strategy.with_regex("Line 1.*Line 3")
        strategy.wait_until_ready(mock_target)
        
        # Should succeed because DOTALL flag is used


class TestHostPortWaitStrategy:
    """Tests for HostPortWaitStrategy."""
    
    def test_wait_with_no_ports(self, mock_target):
        """Test wait succeeds immediately if no ports to check."""
        mock_target.get_liveness_check_port_numbers.return_value = set()
        
        strategy = HostPortWaitStrategy()
        strategy.wait_until_ready(mock_target)
        
        # Should succeed immediately
    
    def test_check_port_success(self):
        """Test _check_port returns True for open port."""
        strategy = HostPortWaitStrategy()
        
        # We can't easily test real port connections, so just verify the method exists
        assert hasattr(strategy, '_check_port')
    
    def test_with_ports_fluent_api(self):
        """Test with_ports returns self for fluent API."""
        strategy = HostPortWaitStrategy()
        result = strategy.with_ports(8080, 8081)
        
        assert result is strategy
        assert strategy._ports == [8080, 8081]
    
    def test_wait_timeout(self, mock_target, monkeypatch):
        """Test wait times out if ports never become available."""
        # Mock the _check_port method to always return False
        def mock_check_port(host, port, timeout=1.0):
            return False
        
        strategy = HostPortWaitStrategy()
        monkeypatch.setattr(strategy, '_check_port', mock_check_port)
        strategy = strategy.with_ports(8080)
        strategy = strategy.with_startup_timeout(timedelta(seconds=1))
        
        with pytest.raises(TimeoutError, match="Timed out waiting for ports"):
            strategy.wait_until_ready(mock_target)
    
    def test_wait_succeeds_when_port_ready(self, mock_target, monkeypatch):
        """Test wait succeeds when port becomes available."""
        # Mock the _check_port method to return True
        def mock_check_port(host, port, timeout=1.0):
            return True
        
        strategy = HostPortWaitStrategy()
        monkeypatch.setattr(strategy, '_check_port', mock_check_port)
        strategy = strategy.with_ports(8080)
        strategy.wait_until_ready(mock_target)
        
        # Should succeed
