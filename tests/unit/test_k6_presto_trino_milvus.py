"""Tests for K6, Presto, Trino, and Milvus container modules."""

from __future__ import annotations

from testcontainers.modules.k6 import K6Container
from testcontainers.modules.presto import PrestoContainer
from testcontainers.modules.trino import TrinoContainer
from testcontainers.modules.milvus import MilvusContainer


# K6 Tests


class TestK6Container:
    """Tests for K6Container."""

    def test_k6_init_defaults(self):
        """Test K6 container initialization with defaults."""
        k6 = K6Container()

        assert k6._test_script is None
        assert k6._cmd_options == []
        assert k6._script_vars == {}

    def test_k6_init_custom_image(self):
        """Test K6 container initialization with custom image."""
        k6 = K6Container("grafana/k6:latest")

        assert "grafana/k6" in str(k6._image)

    def test_k6_with_test_script(self):
        """Test setting test script with fluent API."""
        k6 = K6Container()
        result = k6.with_test_script("/path/to/test.js")

        assert result is k6
        assert k6._test_script == "/home/k6/test.js"

    def test_k6_with_cmd_options(self):
        """Test setting command options with fluent API."""
        k6 = K6Container()
        result = k6.with_cmd_options("--vus", "10", "--duration", "30s")

        assert result is k6
        assert k6._cmd_options == ["--vus", "10", "--duration", "30s"]

    def test_k6_with_script_var(self):
        """Test setting script variables with fluent API."""
        k6 = K6Container()
        result = k6.with_script_var("MY_VAR", "value")

        assert result is k6
        assert k6._script_vars == {"MY_VAR": "value"}

    def test_k6_multiple_script_vars(self):
        """Test setting multiple script variables."""
        k6 = K6Container()
        k6.with_script_var("VAR1", "value1")
        k6.with_script_var("VAR2", "value2")

        assert k6._script_vars == {"VAR1": "value1", "VAR2": "value2"}


# Presto Tests


class TestPrestoContainer:
    """Tests for PrestoContainer."""

    def test_presto_init_defaults(self):
        """Test Presto container initialization with defaults."""
        presto = PrestoContainer()

        assert presto._username == "test"
        assert presto._password == ""
        assert presto._port == 8080
        assert 8080 in presto._exposed_ports

    def test_presto_init_custom_image(self):
        """Test Presto container initialization with custom image."""
        presto = PrestoContainer("ghcr.io/trinodb/presto:400")

        assert "ghcr.io/trinodb/presto" in str(presto._image)

    def test_presto_with_username(self):
        """Test setting username with fluent API."""
        presto = PrestoContainer()
        result = presto.with_username("admin")

        assert result is presto
        assert presto._username == "admin"

    def test_presto_with_database_name(self):
        """Test setting database name with fluent API."""
        presto = PrestoContainer()
        result = presto.with_database_name("mycatalog")

        assert result is presto
        assert presto._catalog == "mycatalog"
        assert presto._dbname == "mycatalog"

    def test_presto_get_driver_class_name(self):
        """Test getting JDBC driver class name."""
        presto = PrestoContainer()

        assert presto.get_driver_class_name() == "io.prestosql.jdbc.PrestoDriver"

    def test_presto_get_password(self):
        """Test getting password (should be empty)."""
        presto = PrestoContainer()

        assert presto.get_password() == ""

    def test_presto_get_test_query_string(self):
        """Test getting test query string."""
        presto = PrestoContainer()

        assert presto.get_test_query_string() == "SELECT count(*) FROM tpch.tiny.nation"


# Trino Tests


class TestTrinoContainer:
    """Tests for TrinoContainer."""

    def test_trino_init_defaults(self):
        """Test Trino container initialization with defaults."""
        trino = TrinoContainer()

        assert trino._username == "test"
        assert trino._password == ""
        assert trino._port == 8080
        assert 8080 in trino._exposed_ports

    def test_trino_init_custom_image(self):
        """Test Trino container initialization with custom image."""
        trino = TrinoContainer("trinodb/trino:400")

        assert "trinodb/trino" in str(trino._image)

    def test_trino_with_username(self):
        """Test setting username with fluent API."""
        trino = TrinoContainer()
        result = trino.with_username("admin")

        assert result is trino
        assert trino._username == "admin"

    def test_trino_with_database_name(self):
        """Test setting database name with fluent API."""
        trino = TrinoContainer()
        result = trino.with_database_name("mycatalog")

        assert result is trino
        assert trino._catalog == "mycatalog"
        assert trino._dbname == "mycatalog"

    def test_trino_get_driver_class_name(self):
        """Test getting JDBC driver class name."""
        trino = TrinoContainer()

        assert trino.get_driver_class_name() == "io.trino.jdbc.TrinoDriver"

    def test_trino_get_password(self):
        """Test getting password (should be empty)."""
        trino = TrinoContainer()

        assert trino.get_password() == ""

    def test_trino_get_test_query_string(self):
        """Test getting test query string."""
        trino = TrinoContainer()

        assert trino.get_test_query_string() == "SELECT count(*) FROM tpch.tiny.nation"


# Milvus Tests


class TestMilvusContainer:
    """Tests for MilvusContainer."""

    def test_milvus_init_defaults(self):
        """Test Milvus container initialization with defaults."""
        milvus = MilvusContainer()

        assert milvus._etcd_endpoint is None
        assert 9091 in milvus._exposed_ports
        assert 19530 in milvus._exposed_ports

    def test_milvus_init_custom_image(self):
        """Test Milvus container initialization with custom image."""
        milvus = MilvusContainer("milvusdb/milvus:v2.3.0")

        assert "milvusdb/milvus" in str(milvus._image)

    def test_milvus_with_etcd_endpoint(self):
        """Test setting etcd endpoint with fluent API."""
        milvus = MilvusContainer()
        result = milvus.with_etcd_endpoint("etcd:2379")

        assert result is milvus
        assert milvus._etcd_endpoint == "etcd:2379"
