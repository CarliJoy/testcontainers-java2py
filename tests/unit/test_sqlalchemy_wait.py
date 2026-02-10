"""Tests for SqlAlchemy wait strategy."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, Mock

import pytest
from testcontainers.waiting.sqlalchemy import SqlAlchemyWaitStrategy


class MockTarget:
    """Mock wait strategy target for testing."""
    
    def __init__(self):
        self._running = True
        self._connection_string = "postgresql://test:test@localhost:5432/test"
    
    def is_running(self) -> bool:
        return self._running
    
    def get_connection_string(self) -> str:
        return self._connection_string


class TestSqlAlchemyWaitStrategy:
    """Tests for SqlAlchemyWaitStrategy."""
    
    def test_init_defaults(self):
        """Test SqlAlchemyWaitStrategy initialization with defaults."""
        strategy = SqlAlchemyWaitStrategy()
        
        assert strategy._test_query == "SELECT 1"
        assert strategy._connection_url_provider is None
        assert strategy._sleep_time == 0.1
    
    def test_with_query(self):
        """Test setting custom test query."""
        strategy = SqlAlchemyWaitStrategy()
        result = strategy.with_query("SELECT version()")
        
        assert result is strategy
        assert strategy._test_query == "SELECT version()"
    
    def test_with_connection_url_provider(self):
        """Test setting custom connection URL provider."""
        strategy = SqlAlchemyWaitStrategy()
        provider = lambda target: "postgresql://custom:url@localhost:5432/db"
        result = strategy.with_connection_url_provider(provider)
        
        assert result is strategy
        assert strategy._connection_url_provider is provider
    
    def test_with_startup_timeout(self):
        """Test setting startup timeout."""
        strategy = SqlAlchemyWaitStrategy()
        result = strategy.with_startup_timeout(timedelta(seconds=30))
        
        assert result is strategy
        assert strategy._startup_timeout == timedelta(seconds=30)
    
    def test_wait_until_ready_no_sqlalchemy(self, monkeypatch):
        """Test error when SqlAlchemy is not installed."""
        strategy = SqlAlchemyWaitStrategy()
        target = MockTarget()
        
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", None)
        import builtins
        original_import = builtins.__import__
        def mock_import(name, *args, **kwargs):
            if name == "sqlalchemy":
                raise ImportError("No module named 'sqlalchemy'")
            return original_import(name, *args, **kwargs)
        monkeypatch.setattr("builtins.__import__", mock_import)
        
        with pytest.raises(ImportError, match="SqlAlchemy is required"):
            strategy.wait_until_ready(target)
    
    def test_wait_until_ready_no_target(self, monkeypatch):
        """Test error when target is not set."""
        strategy = SqlAlchemyWaitStrategy()
        
        # Don't set target
        strategy._wait_strategy_target = None
        
        # Mock sys.modules to simulate sqlalchemy being available
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", MagicMock())
        with pytest.raises(RuntimeError, match="Wait strategy target not set"):
            strategy._wait_until_ready()
    
    def test_wait_until_ready_success(self, monkeypatch):
        """Test successful connection and query execution."""
        strategy = SqlAlchemyWaitStrategy()
        target = MockTarget()
        
        # Mock sqlalchemy module
        mock_sqlalchemy = MagicMock()
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        mock_sqlalchemy.create_engine.return_value = mock_engine
        mock_sqlalchemy.text = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_connection.execute.return_value = mock_result
        
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", mock_sqlalchemy)
        strategy.wait_until_ready(target)
        
        # Verify connection was attempted
        mock_sqlalchemy.create_engine.assert_called_once()
        mock_engine.connect.assert_called_once()
        mock_connection.execute.assert_called_once()
        mock_result.fetchone.assert_called_once()
        mock_engine.dispose.assert_called_once()
    
    def test_wait_until_ready_timeout(self, monkeypatch):
        """Test timeout when database never becomes ready."""
        strategy = SqlAlchemyWaitStrategy()
        strategy._startup_timeout = timedelta(milliseconds=100)
        target = MockTarget()
        
        # Mock sqlalchemy to always fail
        mock_sqlalchemy = MagicMock()
        mock_sqlalchemy.create_engine.side_effect = Exception("Connection refused")
        
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", mock_sqlalchemy)
        with pytest.raises(TimeoutError, match="Container is started but database connection failed"):
            strategy.wait_until_ready(target)
    
    def test_wait_until_ready_container_not_running(self, monkeypatch):
        """Test waiting for container to start running."""
        strategy = SqlAlchemyWaitStrategy()
        strategy._startup_timeout = timedelta(seconds=2)
        strategy._sleep_time = 0.001  # Reduce sleep time for test
        target = MockTarget()
        
        # Start with container not running
        target._running = False
        
        # Track calls to is_running
        is_running_calls = [0]
        original_is_running = target.is_running
        def is_running_side_effect():
            is_running_calls[0] += 1
            # After 3 checks, make container running
            if is_running_calls[0] >= 3:
                target._running = True
            return target._running
        
        target.is_running = is_running_side_effect
        
        # Mock successful connection once container is running
        mock_sqlalchemy = MagicMock()
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        mock_sqlalchemy.create_engine.return_value = mock_engine
        mock_sqlalchemy.text = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_connection.execute.return_value = mock_result
        
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", mock_sqlalchemy)
        strategy.wait_until_ready(target)
        
        # Verify container eventually became running
        assert target._running is True
    
    def test_wait_until_ready_custom_provider(self, monkeypatch):
        """Test using custom connection URL provider."""
        strategy = SqlAlchemyWaitStrategy()
        custom_url = "mysql://custom:pass@localhost:3306/db"
        strategy.with_connection_url_provider(lambda target: custom_url)
        
        target = MockTarget()
        
        # Mock sqlalchemy
        mock_sqlalchemy = MagicMock()
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        mock_sqlalchemy.create_engine.return_value = mock_engine
        mock_sqlalchemy.text = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_connection.execute.return_value = mock_result
        
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", mock_sqlalchemy)
        strategy.wait_until_ready(target)
        
        # Verify custom URL was used
        call_args = mock_sqlalchemy.create_engine.call_args
        assert call_args[0][0] == custom_url
    
    def test_wait_until_ready_no_connection_string_method(self, monkeypatch):
        """Test error when target doesn't have get_connection_string method."""
        strategy = SqlAlchemyWaitStrategy()
        
        # Create target without get_connection_string method
        target = type('Target', (), {
            'is_running': lambda self: True,
        })()
        
        mock_sqlalchemy = MagicMock()
        monkeypatch.setitem(__import__('sys').modules, "sqlalchemy", mock_sqlalchemy)
        strategy._wait_strategy_target = target
        with pytest.raises(RuntimeError, match="Target must have get_connection_string"):
            strategy._wait_until_ready()
