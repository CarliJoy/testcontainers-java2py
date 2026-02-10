"""Tests for new service modules: Consul, LDAP, Grafana LGTM, and Azure Azurite."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Import modules directly to avoid issues with __init__.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from testcontainers.modules.consul import ConsulContainer
from testcontainers.modules.ldap import LLdapContainer
from testcontainers.modules.grafana import LgtmStackContainer
from testcontainers.modules.azure import AzuriteContainer


# Consul Tests

class TestConsulContainer:
    """Tests for ConsulContainer."""

    def test_consul_init_defaults(self):
        """Test Consul container initialization with defaults."""
        consul = ConsulContainer()

        assert consul._http_port == 8500
        assert consul._grpc_port == 8502
        assert 8500 in consul._exposed_ports
        assert 8502 in consul._exposed_ports
        assert consul._env["CONSUL_ADDR"] == "http://0.0.0.0:8500"
        assert consul._init_commands == []

    def test_consul_with_consul_command(self):
        """Test adding Consul commands."""
        consul = ConsulContainer()
        result = consul.with_consul_command("kv put config/test value1")

        assert result is consul
        assert "kv put config/test value1" in consul._init_commands

    def test_consul_with_multiple_commands(self):
        """Test adding multiple Consul commands."""
        consul = ConsulContainer()
        consul.with_consul_command("kv put config/test1 value1", "kv put config/test2 value2")

        assert len(consul._init_commands) == 2
        assert "kv put config/test1 value1" in consul._init_commands
        assert "kv put config/test2 value2" in consul._init_commands

    def test_consul_get_http_port(self, monkeypatch):
        """Test getting HTTP port."""
        call_tracker = {"called_with": None}
        
        def mock_get_mapped_port(self, port):
            call_tracker["called_with"] = port
            return 32768
        
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        consul = ConsulContainer()
        port = consul.get_http_port()

        assert port == 32768
        assert call_tracker["called_with"] == 8500

    def test_consul_get_grpc_port(self, monkeypatch):
        """Test getting gRPC port."""
        call_tracker = {"called_with": None}
        
        def mock_get_mapped_port(self, port):
            call_tracker["called_with"] = port
            return 32769
        
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        consul = ConsulContainer()
        port = consul.get_grpc_port()

        assert port == 32769
        assert call_tracker["called_with"] == 8502


# LDAP Tests

class TestLLdapContainer:
    """Tests for LLdapContainer."""

    def test_lldap_init_defaults(self):
        """Test LDAP container initialization with defaults."""
        ldap = LLdapContainer()

        assert ldap._ldap_port == 3890
        assert ldap._ldaps_port == 6360
        assert ldap._ui_port == 17170
        assert 3890 in ldap._exposed_ports
        assert 17170 in ldap._exposed_ports

    def test_lldap_with_base_dn(self):
        """Test setting base DN."""
        ldap = LLdapContainer()
        result = ldap.with_base_dn("dc=mycompany,dc=com")

        assert result is ldap
        assert ldap._env["LLDAP_LDAP_BASE_DN"] == "dc=mycompany,dc=com"

    def test_lldap_with_user_pass(self):
        """Test setting user password."""
        ldap = LLdapContainer()
        result = ldap.with_user_pass("secret123")

        assert result is ldap
        assert ldap._env["LLDAP_LDAP_USER_PASS"] == "secret123"

    def test_lldap_get_ldap_url_without_tls(self, monkeypatch):
        """Test getting LDAP URL without TLS."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32770)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        ldap = LLdapContainer()
        url = ldap.get_ldap_url()

        assert url == "ldap://localhost:32770"

    def test_lldap_get_ldap_url_with_tls(self, monkeypatch):
        """Test getting LDAP URL with TLS."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32771)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        ldap = LLdapContainer()
        ldap.with_env("LLDAP_LDAPS_OPTIONS__ENABLED", "true")
        url = ldap.get_ldap_url()

        assert url == "ldaps://localhost:32771"

    def test_lldap_get_base_dn_default(self):
        """Test getting default base DN."""
        ldap = LLdapContainer()
        base_dn = ldap.get_base_dn()

        assert base_dn == "dc=example,dc=com"

    def test_lldap_get_base_dn_custom(self):
        """Test getting custom base DN."""
        ldap = LLdapContainer()
        ldap.with_base_dn("dc=test,dc=org")
        base_dn = ldap.get_base_dn()

        assert base_dn == "dc=test,dc=org"

    def test_lldap_get_user(self):
        """Test getting user DN."""
        ldap = LLdapContainer()
        ldap.with_base_dn("dc=test,dc=org")
        user = ldap.get_user()

        assert user == "cn=admin,ou=people,dc=test,dc=org"

    def test_lldap_get_password_default(self):
        """Test getting default password."""
        ldap = LLdapContainer()
        password = ldap.get_password()

        assert password == "password"

    def test_lldap_get_password_custom(self):
        """Test getting custom password."""
        ldap = LLdapContainer()
        ldap.with_user_pass("mysecret")
        password = ldap.get_password()

        assert password == "mysecret"


# Grafana LGTM Tests

class TestLgtmStackContainer:
    """Tests for LgtmStackContainer."""

    def test_lgtm_init_defaults(self):
        """Test LGTM container initialization with defaults."""
        lgtm = LgtmStackContainer()

        assert lgtm._grafana_port == 3000
        assert lgtm._tempo_port == 3200
        assert lgtm._loki_port == 3100
        assert lgtm._otlp_grpc_port == 4317
        assert lgtm._otlp_http_port == 4318
        assert lgtm._prometheus_port == 9090
        assert 3000 in lgtm._exposed_ports
        assert 3200 in lgtm._exposed_ports
        assert 3100 in lgtm._exposed_ports
        assert 4317 in lgtm._exposed_ports
        assert 4318 in lgtm._exposed_ports
        assert 9090 in lgtm._exposed_ports

    def test_lgtm_get_grafana_http_url(self, monkeypatch):
        """Test getting Grafana HTTP URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32772)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_grafana_http_url()

        assert url == "http://localhost:32772"

    def test_lgtm_get_otlp_grpc_url(self, monkeypatch):
        """Test getting OTLP gRPC URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32773)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_otlp_grpc_url()

        assert url == "http://localhost:32773"

    def test_lgtm_get_otlp_http_url(self, monkeypatch):
        """Test getting OTLP HTTP URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32774)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_otlp_http_url()

        assert url == "http://localhost:32774"

    def test_lgtm_get_tempo_url(self, monkeypatch):
        """Test getting Tempo URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32775)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_tempo_url()

        assert url == "http://localhost:32775"

    def test_lgtm_get_loki_url(self, monkeypatch):
        """Test getting Loki URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32776)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_loki_url()

        assert url == "http://localhost:32776"

    def test_lgtm_get_prometheus_http_url(self, monkeypatch):
        """Test getting Prometheus HTTP URL."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(return_value=32777)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        lgtm = LgtmStackContainer()
        url = lgtm.get_prometheus_http_url()

        assert url == "http://localhost:32777"


# Azure Azurite Tests

class TestAzuriteContainer:
    """Tests for AzuriteContainer."""

    def test_azurite_init_defaults(self):
        """Test Azurite container initialization with defaults."""
        azurite = AzuriteContainer()

        assert azurite._blob_port == 10000
        assert azurite._queue_port == 10001
        assert azurite._table_port == 10002
        assert 10000 in azurite._exposed_ports
        assert 10001 in azurite._exposed_ports
        assert 10002 in azurite._exposed_ports
        assert azurite._cert_file is None
        assert azurite._key_file is None
        assert azurite._pwd is None

    def test_azurite_with_ssl_pfx(self):
        """Test configuring SSL with PFX certificate."""
        azurite = AzuriteContainer()
        result = azurite.with_ssl_pfx("/path/to/cert.pfx", "password123")

        assert result is azurite
        assert azurite._cert_file == "/path/to/cert.pfx"
        assert azurite._pwd == "password123"
        assert azurite._cert_extension == ".pfx"

    def test_azurite_with_ssl_pem(self):
        """Test configuring SSL with PEM certificate."""
        azurite = AzuriteContainer()
        result = azurite.with_ssl_pem("/path/to/cert.pem", "/path/to/key.pem")

        assert result is azurite
        assert azurite._cert_file == "/path/to/cert.pem"
        assert azurite._key_file == "/path/to/key.pem"
        assert azurite._cert_extension == ".pem"

    def test_azurite_get_connection_string_default(self, monkeypatch):
        """Test getting connection string with default credentials."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(side_effect=lambda port: {
            10000: 32778,
            10001: 32779,
            10002: 32780,
        }[port])
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        azurite = AzuriteContainer()
        conn_str = azurite.get_connection_string()

        assert "devstoreaccount1" in conn_str
        assert "http://localhost:32778" in conn_str
        assert "http://localhost:32779" in conn_str
        assert "http://localhost:32780" in conn_str

    def test_azurite_get_connection_string_custom_credentials(self, monkeypatch):
        """Test getting connection string with custom credentials."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(side_effect=lambda port: {
            10000: 32778,
            10001: 32779,
            10002: 32780,
        }[port])
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        azurite = AzuriteContainer()
        conn_str = azurite.get_connection_string("myaccount", "mykey")

        assert "myaccount" in conn_str
        assert "mykey" in conn_str

    def test_azurite_get_connection_string_with_ssl(self, monkeypatch):
        """Test getting connection string with SSL enabled."""
        mock_get_host = MagicMock(return_value="localhost")
        mock_get_mapped_port = MagicMock(side_effect=lambda port: {
            10000: 32778,
            10001: 32779,
            10002: 32780,
        }[port])
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_host", mock_get_host)
        monkeypatch.setattr("testcontainers.core.generic_container.GenericContainer.get_mapped_port", mock_get_mapped_port)

        azurite = AzuriteContainer()
        azurite.with_ssl_pfx("/path/to/cert.pfx", "password")
        conn_str = azurite.get_connection_string()

        assert "https://" in conn_str
        assert "http://" not in conn_str

    def test_azurite_command_line_without_ssl(self):
        """Test command line generation without SSL."""
        azurite = AzuriteContainer()
        cmd = azurite._get_command_line()

        assert "azurite" in cmd
        assert "--blobHost 0.0.0.0" in cmd
        assert "--queueHost 0.0.0.0" in cmd
        assert "--tableHost 0.0.0.0" in cmd
        assert "--cert" not in cmd

    def test_azurite_command_line_with_pfx_ssl(self):
        """Test command line generation with PFX SSL."""
        azurite = AzuriteContainer()
        azurite.with_ssl_pfx("/path/to/cert.pfx", "password123")
        cmd = azurite._get_command_line()

        assert "--cert /cert.pfx" in cmd
        assert "--pwd password123" in cmd
        assert "--key" not in cmd

    def test_azurite_command_line_with_pem_ssl(self):
        """Test command line generation with PEM SSL."""
        azurite = AzuriteContainer()
        azurite.with_ssl_pem("/path/to/cert.pem", "/path/to/key.pem")
        cmd = azurite._get_command_line()

        assert "--cert /cert.pem" in cmd
        assert "--key /key.pem" in cmd
        assert "--pwd" not in cmd
