"""Tests for ClickHouse, CockroachDB, and Selenium container modules."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from testcontainers.modules.clickhouse import ClickHouseContainer
from testcontainers.modules.cockroachdb import CockroachDBContainer
from testcontainers.modules.selenium import BrowserWebDriverContainer, BrowserType


# ClickHouse Tests

class TestClickHouseContainer:
    """Tests for ClickHouseContainer."""

    def test_clickhouse_init_defaults(self):
        """Test ClickHouse container initialization with defaults."""
        clickhouse = ClickHouseContainer()

        assert clickhouse._username == "test"
        assert clickhouse._password == "test"
        assert clickhouse._dbname == "default"
        assert clickhouse._port == 8123
        assert 8123 in clickhouse._exposed_ports
        assert 9000 in clickhouse._exposed_ports

    def test_clickhouse_init_custom(self):
        """Test ClickHouse container initialization with custom values."""
        clickhouse = ClickHouseContainer(
            image="clickhouse/clickhouse-server:23.3",
            username="myuser",
            password="mypass",
            dbname="mydb",
        )

        assert clickhouse._username == "myuser"
        assert clickhouse._password == "mypass"
        assert clickhouse._dbname == "mydb"

    def test_clickhouse_with_username(self):
        """Test setting username with fluent API."""
        clickhouse = ClickHouseContainer()
        result = clickhouse.with_username("newuser")

        assert result is clickhouse
        assert clickhouse._username == "newuser"

    def test_clickhouse_with_password(self):
        """Test setting password with fluent API."""
        clickhouse = ClickHouseContainer()
        result = clickhouse.with_password("newpass")

        assert result is clickhouse
        assert clickhouse._password == "newpass"

    def test_clickhouse_with_database_name(self):
        """Test setting database name with fluent API."""
        clickhouse = ClickHouseContainer()
        result = clickhouse.with_database_name("newdb")

        assert result is clickhouse
        assert clickhouse._dbname == "newdb"

    def test_clickhouse_environment_variables(self):
        """Test ClickHouse environment variables are set correctly."""
        clickhouse = ClickHouseContainer(
            username="testuser", password="testpass", dbname="testdb"
        )

        assert clickhouse._env["CLICKHOUSE_USER"] == "testuser"
        assert clickhouse._env["CLICKHOUSE_PASSWORD"] == "testpass"
        assert clickhouse._env["CLICKHOUSE_DB"] == "testdb"

    def test_clickhouse_get_driver_class_name(self):
        """Test getting JDBC driver class name."""
        clickhouse = ClickHouseContainer()
        assert clickhouse.get_driver_class_name() == "com.clickhouse.jdbc.Driver"

    def test_clickhouse_get_jdbc_url(self, monkeypatch):
        """Test getting JDBC URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32768)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        clickhouse = ClickHouseContainer(dbname="testdb")
        url = clickhouse.get_jdbc_url()

        assert url == "jdbc:clickhouse://localhost:32768/testdb"

    def test_clickhouse_get_http_url(self, monkeypatch):
        """Test getting HTTP URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32768)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        clickhouse = ClickHouseContainer()
        url = clickhouse.get_http_url()

        assert url == "http://localhost:32768"

    def test_clickhouse_get_connection_string(self, monkeypatch):
        """Test getting connection string."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32768)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        clickhouse = ClickHouseContainer(
            username="user", password="pass", dbname="testdb"
        )
        conn_str = clickhouse.get_connection_string()

        assert conn_str == "clickhouse://user:pass@localhost:32768/testdb"


# CockroachDB Tests

class TestCockroachDBContainer:
    """Tests for CockroachDBContainer."""

    def test_cockroachdb_init_defaults(self):
        """Test CockroachDB container initialization with defaults."""
        cockroach = CockroachDBContainer()

        assert cockroach._username == "root"
        assert cockroach._password == ""
        assert cockroach._dbname == "postgres"
        assert cockroach._port == 26257
        assert 26257 in cockroach._exposed_ports
        assert 8080 in cockroach._exposed_ports

    def test_cockroachdb_init_custom(self):
        """Test CockroachDB container initialization with custom values."""
        cockroach = CockroachDBContainer(
            image="cockroachdb/cockroach:v23.1.0",
            username="myuser",
            password="mypass",
            dbname="mydb",
        )

        assert cockroach._username == "myuser"
        assert cockroach._password == "mypass"
        assert cockroach._dbname == "mydb"

    def test_cockroachdb_version_support_check_supported(self):
        """Test version check for versions >= 22.1.0."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v23.1.0")
        assert cockroach._supports_env_vars is True

    def test_cockroachdb_version_support_check_not_supported(self):
        """Test version check for versions < 22.1.0."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v19.2.11")
        assert cockroach._supports_env_vars is False

    def test_cockroachdb_version_support_check_latest(self):
        """Test version check for latest tag."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:latest")
        assert cockroach._supports_env_vars is True

    def test_cockroachdb_with_username_supported_version(self):
        """Test setting username with supported version."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v23.1.0")
        result = cockroach.with_username("newuser")

        assert result is cockroach
        assert cockroach._username == "newuser"
        assert cockroach._env["COCKROACH_USER"] == "newuser"

    def test_cockroachdb_with_username_unsupported_version(self):
        """Test setting username with unsupported version raises error."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v19.2.11")

        with pytest.raises(RuntimeError, match="not supported in versions below 22.1.0"):
            cockroach.with_username("newuser")

    def test_cockroachdb_with_password_supported_version(self):
        """Test setting password with supported version."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v23.1.0")
        result = cockroach.with_password("newpass")

        assert result is cockroach
        assert cockroach._password == "newpass"
        assert cockroach._env["COCKROACH_PASSWORD"] == "newpass"

    def test_cockroachdb_with_password_unsupported_version(self):
        """Test setting password with unsupported version raises error."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v19.2.11")

        with pytest.raises(RuntimeError, match="not supported in versions below 22.1.0"):
            cockroach.with_password("newpass")

    def test_cockroachdb_with_database_name_supported_version(self):
        """Test setting database name with supported version."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v23.1.0")
        result = cockroach.with_database_name("newdb")

        assert result is cockroach
        assert cockroach._dbname == "newdb"
        assert cockroach._env["COCKROACH_DATABASE"] == "newdb"

    def test_cockroachdb_with_database_name_unsupported_version(self):
        """Test setting database name with unsupported version raises error."""
        cockroach = CockroachDBContainer(image="cockroachdb/cockroach:v19.2.11")

        with pytest.raises(RuntimeError, match="not supported in versions below 22.1.0"):
            cockroach.with_database_name("newdb")

    def test_cockroachdb_environment_variables(self):
        """Test CockroachDB environment variables are set correctly."""
        cockroach = CockroachDBContainer(
            image="cockroachdb/cockroach:v23.1.0",
            username="testuser",
            password="testpass",
            dbname="testdb",
        )

        assert cockroach._env["COCKROACH_USER"] == "testuser"
        assert cockroach._env["COCKROACH_PASSWORD"] == "testpass"
        assert cockroach._env["COCKROACH_DATABASE"] == "testdb"

    def test_cockroachdb_get_driver_class_name(self):
        """Test getting JDBC driver class name (PostgreSQL compatible)."""
        cockroach = CockroachDBContainer()
        assert cockroach.get_driver_class_name() == "org.postgresql.Driver"

    def test_cockroachdb_get_jdbc_url(self, monkeypatch):
        """Test getting JDBC URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32770)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        cockroach = CockroachDBContainer(dbname="testdb")
        url = cockroach.get_jdbc_url()

        assert url == "jdbc:postgresql://localhost:32770/testdb"

    def test_cockroachdb_get_connection_string_with_password(self, monkeypatch):
        """Test getting connection string with password."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32770)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        cockroach = CockroachDBContainer(
            username="root", password="mypass", dbname="testdb"
        )
        conn_str = cockroach.get_connection_string()

        assert conn_str == "postgresql://root:mypass@localhost:32770/testdb"

    def test_cockroachdb_get_connection_string_without_password(self, monkeypatch):
        """Test getting connection string without password."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32770)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        cockroach = CockroachDBContainer(username="root", password="", dbname="testdb")
        conn_str = cockroach.get_connection_string()

        assert conn_str == "postgresql://root@localhost:32770/testdb"


# Selenium Tests

class TestBrowserWebDriverContainer:
    """Tests for BrowserWebDriverContainer."""

    def test_selenium_init_defaults(self):
        """Test Selenium container initialization with defaults (Chrome)."""
        selenium = BrowserWebDriverContainer()

        assert selenium._selenium_port == 4444
        assert selenium._vnc_port == 5900
        assert 4444 in selenium._exposed_ports
        assert 5900 in selenium._exposed_ports
        assert selenium._env["TZ"] == "Etc/UTC"
        assert selenium._env["no_proxy"] == "localhost"

    def test_selenium_init_chrome(self):
        """Test Selenium container with Chrome browser."""
        selenium = BrowserWebDriverContainer(browser=BrowserType.CHROME)

        # Check that the image name contains chrome
        image_name = str(selenium._image._image_name)
        assert "chrome" in image_name.lower()

    def test_selenium_init_firefox(self):
        """Test Selenium container with Firefox browser."""
        selenium = BrowserWebDriverContainer(browser=BrowserType.FIREFOX)

        # Check that the image name contains firefox
        image_name = str(selenium._image._image_name)
        assert "firefox" in image_name.lower()

    def test_selenium_init_edge(self):
        """Test Selenium container with Edge browser."""
        selenium = BrowserWebDriverContainer(browser=BrowserType.EDGE)

        # Check that the image name contains edge
        image_name = str(selenium._image._image_name)
        assert "edge" in image_name.lower()

    def test_selenium_init_custom_image(self):
        """Test Selenium container with custom image."""
        custom_image = "selenium/standalone-chrome:4.15.0"
        selenium = BrowserWebDriverContainer(image=custom_image)

        # Check that the image matches
        image_name = str(selenium._image._image_name)
        assert image_name == custom_image

    def test_selenium_custom_image_overrides_browser(self):
        """Test that custom image overrides browser parameter."""
        custom_image = "selenium/standalone-firefox:4.15.0"
        selenium = BrowserWebDriverContainer(
            browser=BrowserType.CHROME, image=custom_image
        )

        # Check that firefox image is used (not chrome)
        image_name = str(selenium._image._image_name)
        assert image_name == custom_image

    def test_selenium_invalid_browser_type(self):
        """Test that invalid browser type raises error."""
        with pytest.raises(ValueError, match="Unsupported browser type"):
            BrowserWebDriverContainer(browser="invalid")  # type: ignore

    def test_selenium_get_selenium_url(self, monkeypatch):
        """Test getting Selenium WebDriver URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32772)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        selenium = BrowserWebDriverContainer()
        selenium._container = MagicMock()  # Set _container to simulate started container
        url = selenium.get_selenium_url()

        assert url == "http://localhost:32772/wd/hub"

    def test_selenium_get_selenium_url_not_started(self):
        """Test getting Selenium URL when container not started raises error."""
        selenium = BrowserWebDriverContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            selenium.get_selenium_url()

    def test_selenium_get_selenium_address(self, monkeypatch):
        """Test getting Selenium address (alias for get_selenium_url)."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32772)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        selenium = BrowserWebDriverContainer()
        selenium._container = MagicMock()  # Set _container to simulate started container
        url = selenium.get_selenium_address()

        assert url == "http://localhost:32772/wd/hub"

    def test_selenium_get_vnc_address(self, monkeypatch):
        """Test getting VNC address."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(side_effect=lambda port: 32773 if port == 5900 else 32772)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        selenium = BrowserWebDriverContainer()
        selenium._container = MagicMock()  # Set _container to simulate started container
        url = selenium.get_vnc_address()

        assert url == "vnc://vnc:secret@localhost:32773"

    def test_selenium_get_vnc_address_not_started(self):
        """Test getting VNC address when container not started raises error."""
        selenium = BrowserWebDriverContainer()

        with pytest.raises(RuntimeError, match="Container not started"):
            selenium.get_vnc_address()

    def test_selenium_get_selenium_port(self, monkeypatch):
        """Test getting Selenium port."""
        mock_get_mapped_port = MagicMock(return_value=32772)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        selenium = BrowserWebDriverContainer()
        port = selenium.get_selenium_port()

        assert port == 32772
        mock_get_mapped_port.assert_called_once_with(4444)

    def test_selenium_get_vnc_port(self, monkeypatch):
        """Test getting VNC port."""
        mock_get_mapped_port = MagicMock(return_value=32773)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        selenium = BrowserWebDriverContainer()
        port = selenium.get_vnc_port()

        assert port == 32773
        mock_get_mapped_port.assert_called_once_with(5900)

    def test_selenium_shared_memory_size(self):
        """Test that shared memory size is set to 2GB."""
        selenium = BrowserWebDriverContainer()

        # 2GB in bytes
        expected_shm_size = 2 * 1024 * 1024 * 1024
        assert selenium._shm_size == expected_shm_size
