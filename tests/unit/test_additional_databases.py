"""Tests for additional database container modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from testcontainers.modules.cassandra import CassandraContainer
from testcontainers.modules.couchdb import CouchDBContainer
from testcontainers.modules.influxdb import InfluxDBContainer
from testcontainers.modules.mariadb import MariaDBContainer
from testcontainers.modules.neo4j import Neo4jContainer
from testcontainers.waiting.log import LogMessageWaitStrategy

# MariaDB Tests


class TestMariaDBContainer:
    """Tests for MariaDBContainer."""

    def test_mariadb_init_defaults(self):
        """Test MariaDB container initialization with defaults."""
        mariadb = MariaDBContainer()

        assert mariadb._username == "test"
        assert mariadb._password == "test"
        assert mariadb._dbname == "test"
        assert mariadb._port == 3306
        assert 3306 in mariadb._exposed_ports

    def test_mariadb_init_custom(self):
        """Test MariaDB container initialization with custom values."""
        mariadb = MariaDBContainer(
            image="mariadb:10",
            username="myuser",
            password="mypass",
            dbname="mydb"
        )

        assert mariadb._username == "myuser"
        assert mariadb._password == "mypass"
        assert mariadb._dbname == "mydb"

    def test_mariadb_with_username(self):
        """Test setting username with fluent API."""
        mariadb = MariaDBContainer()
        result = mariadb.with_username("newuser")

        assert result is mariadb
        assert mariadb._username == "newuser"

    def test_mariadb_with_password(self):
        """Test setting password with fluent API."""
        mariadb = MariaDBContainer()
        result = mariadb.with_password("newpass")

        assert result is mariadb
        assert mariadb._password == "newpass"

    def test_mariadb_with_database_name(self):
        """Test setting database name with fluent API."""
        mariadb = MariaDBContainer()
        result = mariadb.with_database_name("newdb")

        assert result is mariadb
        assert mariadb._dbname == "newdb"

    def test_mariadb_environment_variables(self):
        """Test MariaDB environment variables are set correctly after configure."""
        mariadb = MariaDBContainer(
            username="testuser",
            password="testpass",
            dbname="testdb"
        )
        mariadb._configure()

        assert mariadb._env.get("MYSQL_USER") == "testuser"
        assert mariadb._env.get("MYSQL_PASSWORD") == "testpass"
        assert mariadb._env.get("MYSQL_DATABASE") == "testdb"
        assert mariadb._env.get("MYSQL_ROOT_PASSWORD") == "testpass"

    def test_mariadb_get_driver_class_name(self):
        """Test MariaDB driver class name."""
        mariadb = MariaDBContainer()

        assert mariadb.get_driver_class_name() == "org.mariadb.jdbc.Driver"

    def test_mariadb_get_jdbc_url(self):
        """Test MariaDB JDBC URL generation."""
        mariadb = MariaDBContainer()
        mariadb._container = MagicMock()

        with patch.object(mariadb, 'get_host', return_value='localhost'):
            with patch.object(mariadb, 'get_mapped_port', return_value=3306):
                url = mariadb.get_jdbc_url()

        assert url == "jdbc:mariadb://localhost:3306/test"

    def test_mariadb_get_connection_string(self):
        """Test MariaDB test query string."""
        mariadb = MariaDBContainer()

        assert mariadb.get_test_query_string() == "SELECT 1"

    def test_mariadb_wait_strategy(self):
        """Test MariaDB wait strategy is inherited from parent."""
        mariadb = MariaDBContainer()

        assert mariadb._wait_strategy is not None


# Cassandra Tests


class TestCassandraContainer:
    """Tests for CassandraContainer."""

    def test_cassandra_init_defaults(self):
        """Test Cassandra container initialization with defaults."""
        cassandra = CassandraContainer()

        assert cassandra._cql_port == 9042
        assert 9042 in cassandra._exposed_ports
        assert cassandra._datacenter_name == "datacenter1"
        assert cassandra._cluster_label == "test-cluster"

    def test_cassandra_init_custom_image(self):
        """Test Cassandra container with custom image."""
        cassandra = CassandraContainer(image="cassandra:4")

        assert cassandra._image.image_name == "cassandra:4"

    def test_cassandra_with_datacenter(self):
        """Test setting datacenter with fluent API."""
        cassandra = CassandraContainer()
        result = cassandra.with_datacenter("dc1")

        assert result is cassandra
        assert cassandra._datacenter_name == "dc1"

    def test_cassandra_with_cluster_name(self):
        """Test setting cluster name with fluent API."""
        cassandra = CassandraContainer()
        result = cassandra.with_cluster_name("my-cluster")

        assert result is cassandra
        assert cassandra._cluster_label == "my-cluster"

    def test_cassandra_environment_variables(self):
        """Test Cassandra environment variables are set correctly."""
        cassandra = CassandraContainer()
        cassandra.with_datacenter("dc1")
        cassandra.with_cluster_name("my-cluster")

        assert cassandra._env["CASSANDRA_DC"] == "dc1"
        assert cassandra._env["CASSANDRA_CLUSTER_NAME"] == "my-cluster"

    def test_cassandra_get_contact_points(self):
        """Test Cassandra contact points generation."""
        cassandra = CassandraContainer()
        cassandra._container = MagicMock()

        with patch.object(cassandra, 'get_host', return_value='localhost'):
            with patch.object(cassandra, 'get_mapped_port', return_value=9042):
                contact_points = cassandra.get_contact_points()

        assert contact_points == "localhost:9042"

    def test_cassandra_get_datacenter(self):
        """Test getting Cassandra datacenter."""
        cassandra = CassandraContainer()
        cassandra.with_datacenter("dc1")

        assert cassandra.get_datacenter() == "dc1"

    def test_cassandra_get_cluster_name(self):
        """Test getting Cassandra cluster name."""
        cassandra = CassandraContainer()
        cassandra.with_cluster_name("my-cluster")

        assert cassandra.get_cluster_name() == "my-cluster"

    def test_cassandra_wait_strategy(self):
        """Test Cassandra wait strategy is configured."""
        cassandra = CassandraContainer()

        assert isinstance(cassandra._wait_strategy, LogMessageWaitStrategy)


# Neo4j Tests


class TestNeo4jContainer:
    """Tests for Neo4jContainer."""

    def test_neo4j_init_defaults(self):
        """Test Neo4j container initialization with defaults."""
        neo4j = Neo4jContainer()

        assert neo4j._config["ports"]["http"] == 7474
        assert neo4j._config["ports"]["bolt"] == 7687
        assert neo4j._config["ports"]["https"] == 7473
        assert 7474 in neo4j._exposed_ports
        assert 7687 in neo4j._exposed_ports
        assert 7473 in neo4j._exposed_ports
        assert neo4j._config["auth"]["enabled"] is True
        assert neo4j._config["auth"]["secret"] == "password"

    def test_neo4j_init_custom_image(self):
        """Test Neo4j container with custom image."""
        neo4j = Neo4jContainer(image="neo4j:4")

        assert neo4j._image.image_name == "neo4j:4"

    def test_neo4j_with_authentication(self):
        """Test Neo4j password configuration."""
        neo4j = Neo4jContainer()
        result = neo4j.with_admin_password("mypassword")

        assert result is neo4j
        assert neo4j._config["auth"]["secret"] == "mypassword"
        assert neo4j._config["auth"]["enabled"] is True

    def test_neo4j_without_authentication(self):
        """Test Neo4j without authentication."""
        neo4j = Neo4jContainer()
        result = neo4j.without_authentication()

        assert result is neo4j
        assert neo4j._config["auth"]["enabled"] is False

    def test_neo4j_authentication_env_vars(self):
        """Test Neo4j authentication environment variables."""
        neo4j = Neo4jContainer()
        neo4j.with_admin_password("testpass")
        neo4j._configure()

        assert neo4j._env["NEO4J_AUTH"] == "neo4j/testpass"

    def test_neo4j_no_auth_env_vars(self):
        """Test Neo4j no auth environment variables."""
        neo4j = Neo4jContainer()
        neo4j.without_authentication()
        neo4j._configure()

        assert neo4j._env["NEO4J_AUTH"] == "none"

    def test_neo4j_get_bolt_url(self):
        """Test Neo4j Bolt URL generation."""
        neo4j = Neo4jContainer()
        neo4j._container = MagicMock()

        with patch.object(neo4j, 'get_host', return_value='localhost'):
            with patch.object(neo4j, 'get_mapped_port', return_value=7687):
                url = neo4j.get_bolt_url()

        assert url == "bolt://localhost:7687"

    def test_neo4j_get_http_url(self):
        """Test Neo4j HTTP URL generation."""
        neo4j = Neo4jContainer()
        neo4j._container = MagicMock()

        with patch.object(neo4j, 'get_host', return_value='localhost'):
            with patch.object(neo4j, 'get_mapped_port', return_value=7474):
                url = neo4j.get_http_url()

        assert url == "http://localhost:7474"

    def test_neo4j_get_password(self):
        """Test getting Neo4j password."""
        neo4j = Neo4jContainer()
        neo4j.with_admin_password("testpass")

        assert neo4j.get_admin_password() == "testpass"

    def test_neo4j_is_auth_disabled(self):
        """Test checking if Neo4j auth is disabled."""
        neo4j = Neo4jContainer()
        neo4j.without_authentication()

        assert neo4j.get_admin_password() is None

    def test_neo4j_wait_strategy(self):
        """Test Neo4j wait strategy is configured."""
        neo4j = Neo4jContainer()

        from testcontainers.waiting.wait_all import WaitAllStrategy
        assert isinstance(neo4j._wait_strategy, WaitAllStrategy)


# InfluxDB Tests


class TestInfluxDBContainer:
    """Tests for InfluxDBContainer."""

    def test_influxdb_init_defaults(self):
        """Test InfluxDB container initialization with defaults."""
        influxdb = InfluxDBContainer()

        assert influxdb._port == 8086
        assert 8086 in influxdb._exposed_ports
        assert influxdb._username == "admin"
        assert influxdb._password == "password"
        assert influxdb._org == "test-org"
        assert influxdb._bucket == "test-bucket"
        assert influxdb._admin_token == "test-token"

    def test_influxdb_init_custom_image(self):
        """Test InfluxDB container with custom image."""
        influxdb = InfluxDBContainer(image="influxdb:2.6")

        assert influxdb._image.image_name == "influxdb:2.6"

    def test_influxdb_with_authentication(self):
        """Test InfluxDB authentication configuration."""
        influxdb = InfluxDBContainer()
        result = influxdb.with_authentication(
            "myuser",
            "mypass",
            "myorg",
            "mybucket",
            "mytoken"
        )

        assert result is influxdb
        assert influxdb._username == "myuser"
        assert influxdb._password == "mypass"
        assert influxdb._org == "myorg"
        assert influxdb._bucket == "mybucket"
        assert influxdb._admin_token == "mytoken"

    def test_influxdb_with_authentication_no_token(self):
        """Test InfluxDB authentication without custom token."""
        influxdb = InfluxDBContainer()
        default_token = influxdb._admin_token
        result = influxdb.with_authentication(
            "myuser",
            "mypass",
            "myorg",
            "mybucket"
        )

        assert result is influxdb
        assert influxdb._admin_token == default_token

    def test_influxdb_environment_variables(self):
        """Test InfluxDB environment variables are set correctly."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket", "testtoken")

        assert influxdb._env["DOCKER_INFLUXDB_INIT_MODE"] == "setup"
        assert influxdb._env["DOCKER_INFLUXDB_INIT_USERNAME"] == "testuser"
        assert influxdb._env["DOCKER_INFLUXDB_INIT_PASSWORD"] == "testpass"
        assert influxdb._env["DOCKER_INFLUXDB_INIT_ORG"] == "testorg"
        assert influxdb._env["DOCKER_INFLUXDB_INIT_BUCKET"] == "testbucket"
        assert influxdb._env["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"] == "testtoken"

    def test_influxdb_get_url(self):
        """Test InfluxDB URL generation."""
        influxdb = InfluxDBContainer()
        influxdb._container = MagicMock()

        with patch.object(influxdb, 'get_host', return_value='localhost'):
            with patch.object(influxdb, 'get_mapped_port', return_value=8086):
                url = influxdb.get_url()

        assert url == "http://localhost:8086"

    def test_influxdb_get_username(self):
        """Test getting InfluxDB username."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket")

        assert influxdb.get_username() == "testuser"

    def test_influxdb_get_password(self):
        """Test getting InfluxDB password."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket")

        assert influxdb.get_password() == "testpass"

    def test_influxdb_get_org(self):
        """Test getting InfluxDB org."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket")

        assert influxdb.get_org() == "testorg"

    def test_influxdb_get_bucket(self):
        """Test getting InfluxDB bucket."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket")

        assert influxdb.get_bucket() == "testbucket"

    def test_influxdb_get_admin_token(self):
        """Test getting InfluxDB admin token."""
        influxdb = InfluxDBContainer()
        influxdb.with_authentication("testuser", "testpass", "testorg", "testbucket", "testtoken")

        assert influxdb.get_admin_token() == "testtoken"

    def test_influxdb_wait_strategy(self):
        """Test InfluxDB wait strategy is configured."""
        influxdb = InfluxDBContainer()

        assert isinstance(influxdb._wait_strategy, LogMessageWaitStrategy)


# CouchDB Tests


class TestCouchDBContainer:
    """Tests for CouchDBContainer."""

    def test_couchdb_init_defaults(self):
        """Test CouchDB container initialization with defaults."""
        couchdb = CouchDBContainer()

        assert couchdb._port == 5984
        assert 5984 in couchdb._exposed_ports
        assert couchdb._username == "admin"
        assert couchdb._password == "password"

    def test_couchdb_init_custom_image(self):
        """Test CouchDB container with custom image."""
        couchdb = CouchDBContainer(image="couchdb:2")

        assert couchdb._image.image_name == "couchdb:2"

    def test_couchdb_with_authentication(self):
        """Test CouchDB authentication configuration."""
        couchdb = CouchDBContainer()
        result = couchdb.with_authentication("myuser", "mypass")

        assert result is couchdb
        assert couchdb._username == "myuser"
        assert couchdb._password == "mypass"

    def test_couchdb_environment_variables(self):
        """Test CouchDB environment variables are set correctly."""
        couchdb = CouchDBContainer()
        couchdb.with_authentication("testuser", "testpass")

        assert couchdb._env["COUCHDB_USER"] == "testuser"
        assert couchdb._env["COUCHDB_PASSWORD"] == "testpass"

    def test_couchdb_get_url(self):
        """Test CouchDB URL generation."""
        couchdb = CouchDBContainer()
        couchdb._container = MagicMock()

        with patch.object(couchdb, 'get_host', return_value='localhost'):
            with patch.object(couchdb, 'get_mapped_port', return_value=5984):
                url = couchdb.get_url()

        assert url == "http://admin:password@localhost:5984"

    def test_couchdb_get_url_custom_credentials(self):
        """Test CouchDB URL generation with custom credentials."""
        couchdb = CouchDBContainer()
        couchdb.with_authentication("myuser", "mypass")
        couchdb._container = MagicMock()

        with patch.object(couchdb, 'get_host', return_value='localhost'):
            with patch.object(couchdb, 'get_mapped_port', return_value=5984):
                url = couchdb.get_url()

        assert url == "http://myuser:mypass@localhost:5984"

    def test_couchdb_get_username(self):
        """Test getting CouchDB username."""
        couchdb = CouchDBContainer()
        couchdb.with_authentication("testuser", "testpass")

        assert couchdb.get_username() == "testuser"

    def test_couchdb_get_password(self):
        """Test getting CouchDB password."""
        couchdb = CouchDBContainer()
        couchdb.with_authentication("testuser", "testpass")

        assert couchdb.get_password() == "testpass"

    def test_couchdb_wait_strategy(self):
        """Test CouchDB wait strategy is configured."""
        couchdb = CouchDBContainer()

        assert isinstance(couchdb._wait_strategy, LogMessageWaitStrategy)
