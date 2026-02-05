"""Tests for database container modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.modules.mongodb import MongoDBContainer
from testcontainers.modules.mysql import MySQLContainer
from testcontainers.modules.postgres import PostgreSQLContainer
from testcontainers.modules.redis import RedisContainer
from testcontainers.waiting.log import LogMessageWaitStrategy

# Fixtures

@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client."""
    client = MagicMock()
    client.containers = MagicMock()
    return client


@pytest.fixture
def mock_container():
    """Create a mock Docker container."""
    container = MagicMock()
    container.id = "test-container-id"
    container.attrs = {
        "NetworkSettings": {
            "Ports": {
                "5432/tcp": [{"HostPort": "32768"}],
                "3306/tcp": [{"HostPort": "32769"}],
                "27017/tcp": [{"HostPort": "32770"}],
                "6379/tcp": [{"HostPort": "32771"}],
            }
        }
    }
    container.status = "running"
    return container


# PostgreSQL Tests

class TestPostgreSQLContainer:
    """Tests for PostgreSQLContainer."""

    def test_postgres_init_defaults(self):
        """Test PostgreSQL container initialization with defaults."""
        postgres = PostgreSQLContainer()

        assert postgres._username == "test"
        assert postgres._password == "test"
        assert postgres._dbname == "test"
        assert postgres._port == 5432
        assert 5432 in postgres._exposed_ports

    def test_postgres_init_custom(self):
        """Test PostgreSQL container initialization with custom values."""
        postgres = PostgreSQLContainer(
            image="postgres:15",
            username="myuser",
            password="mypass",
            dbname="mydb"
        )

        assert postgres._username == "myuser"
        assert postgres._password == "mypass"
        assert postgres._dbname == "mydb"

    def test_postgres_with_username(self):
        """Test setting username with fluent API."""
        postgres = PostgreSQLContainer()
        result = postgres.with_username("newuser")

        assert result is postgres
        assert postgres._username == "newuser"

    def test_postgres_with_password(self):
        """Test setting password with fluent API."""
        postgres = PostgreSQLContainer()
        result = postgres.with_password("newpass")

        assert result is postgres
        assert postgres._password == "newpass"

    def test_postgres_with_database_name(self):
        """Test setting database name with fluent API."""
        postgres = PostgreSQLContainer()
        result = postgres.with_database_name("newdb")

        assert result is postgres
        assert postgres._dbname == "newdb"

    def test_postgres_environment_variables(self):
        """Test PostgreSQL environment variables are set correctly."""
        postgres = PostgreSQLContainer(
            username="testuser",
            password="testpass",
            dbname="testdb"
        )

        assert postgres._env["POSTGRES_USER"] == "testuser"
        assert postgres._env["POSTGRES_PASSWORD"] == "testpass"
        assert postgres._env["POSTGRES_DB"] == "testdb"

    def test_postgres_get_driver_class_name(self):
        """Test PostgreSQL driver class name."""
        postgres = PostgreSQLContainer()

        assert postgres.get_driver_class_name() == "org.postgresql.Driver"

    def test_postgres_get_jdbc_url(self):
        """Test PostgreSQL JDBC URL generation."""
        postgres = PostgreSQLContainer()
        postgres._container = MagicMock()

        with patch.object(postgres, 'get_host', return_value='localhost'):
            with patch.object(postgres, 'get_mapped_port', return_value=5432):
                url = postgres.get_jdbc_url()

        assert url == "jdbc:postgresql://localhost:5432/test"

    def test_postgres_get_connection_string(self):
        """Test PostgreSQL Python connection string."""
        postgres = PostgreSQLContainer()
        postgres._container = MagicMock()

        with patch.object(postgres, 'get_host', return_value='localhost'):
            with patch.object(postgres, 'get_mapped_port', return_value=5432):
                url = postgres.get_connection_string()

        assert url == "postgresql://test:test@localhost:5432/test"

    def test_postgres_wait_strategy(self):
        """Test PostgreSQL wait strategy is configured."""
        postgres = PostgreSQLContainer()

        assert isinstance(postgres._wait_strategy, LogMessageWaitStrategy)
        assert postgres._wait_strategy._times == 2


# MySQL Tests

class TestMySQLContainer:
    """Tests for MySQLContainer."""

    def test_mysql_init_defaults(self):
        """Test MySQL container initialization with defaults."""
        mysql = MySQLContainer()

        assert mysql._username == "test"
        assert mysql._password == "test"
        assert mysql._dbname == "test"
        assert mysql._port == 3306
        assert 3306 in mysql._exposed_ports

    def test_mysql_init_custom(self):
        """Test MySQL container initialization with custom values."""
        mysql = MySQLContainer(
            image="mysql:8.0",
            username="myuser",
            password="mypass",
            dbname="mydb"
        )

        assert mysql._username == "myuser"
        assert mysql._password == "mypass"
        assert mysql._dbname == "mydb"

    def test_mysql_with_username(self):
        """Test setting username with fluent API."""
        mysql = MySQLContainer()
        result = mysql.with_username("newuser")

        assert result is mysql
        assert mysql._username == "newuser"

    def test_mysql_with_config_option(self):
        """Test setting MySQL config option."""
        mysql = MySQLContainer()
        result = mysql.with_config_option("max_connections", "200")

        assert result is mysql
        assert mysql._config_options["max_connections"] == "200"

    def test_mysql_multiple_config_options(self):
        """Test setting multiple MySQL config options."""
        mysql = MySQLContainer()
        mysql.with_config_option("max_connections", "200")
        mysql.with_config_option("innodb_buffer_pool_size", "256M")

        assert mysql._config_options["max_connections"] == "200"
        assert mysql._config_options["innodb_buffer_pool_size"] == "256M"

    def test_mysql_environment_variables(self):
        """Test MySQL environment variables are set correctly."""
        mysql = MySQLContainer(
            username="testuser",
            password="testpass",
            dbname="testdb"
        )

        assert mysql._env["MYSQL_USER"] == "testuser"
        assert mysql._env["MYSQL_PASSWORD"] == "testpass"
        assert mysql._env["MYSQL_DATABASE"] == "testdb"
        assert mysql._env["MYSQL_ROOT_PASSWORD"] == "testpass"

    def test_mysql_get_driver_class_name(self):
        """Test MySQL driver class name."""
        mysql = MySQLContainer()

        assert mysql.get_driver_class_name() == "com.mysql.cj.jdbc.Driver"

    def test_mysql_get_jdbc_url(self):
        """Test MySQL JDBC URL generation."""
        mysql = MySQLContainer()
        mysql._container = MagicMock()

        with patch.object(mysql, 'get_host', return_value='localhost'):
            with patch.object(mysql, 'get_mapped_port', return_value=3306):
                url = mysql.get_jdbc_url()

        assert url == "jdbc:mysql://localhost:3306/test"

    def test_mysql_get_connection_string(self):
        """Test MySQL Python connection string."""
        mysql = MySQLContainer()
        mysql._container = MagicMock()

        with patch.object(mysql, 'get_host', return_value='localhost'):
            with patch.object(mysql, 'get_mapped_port', return_value=3306):
                url = mysql.get_connection_string()

        assert url == "mysql://test:test@localhost:3306/test"

    def test_mysql_wait_strategy(self):
        """Test MySQL wait strategy is configured."""
        mysql = MySQLContainer()

        assert isinstance(mysql._wait_strategy, LogMessageWaitStrategy)
        assert mysql._wait_strategy._times == 2


# MongoDB Tests

class TestMongoDBContainer:
    """Tests for MongoDBContainer."""

    def test_mongodb_init_defaults(self):
        """Test MongoDB container initialization with defaults."""
        mongo = MongoDBContainer()

        assert mongo._port == 27017
        assert 27017 in mongo._exposed_ports
        assert mongo._username is None
        assert mongo._password is None
        assert mongo._auth_database is None

    def test_mongodb_init_custom_image(self):
        """Test MongoDB container with custom image."""
        mongo = MongoDBContainer(image="mongo:6")

        assert mongo._image.image_name == "mongo:6"

    def test_mongodb_with_authentication(self):
        """Test MongoDB authentication configuration."""
        mongo = MongoDBContainer()
        result = mongo.with_authentication("admin", "myuser", "mypass")

        assert result is mongo
        assert mongo._auth_database == "admin"
        assert mongo._username == "myuser"
        assert mongo._password == "mypass"

    def test_mongodb_authentication_env_vars(self):
        """Test MongoDB authentication environment variables."""
        mongo = MongoDBContainer()
        mongo.with_authentication("admin", "testuser", "testpass")

        assert mongo._env["MONGO_INITDB_ROOT_USERNAME"] == "testuser"
        assert mongo._env["MONGO_INITDB_ROOT_PASSWORD"] == "testpass"
        assert mongo._env["MONGO_INITDB_DATABASE"] == "admin"

    def test_mongodb_get_connection_string_no_auth(self):
        """Test MongoDB connection string without authentication."""
        mongo = MongoDBContainer()
        mongo._container = MagicMock()

        with patch.object(mongo, 'get_host', return_value='localhost'):
            with patch.object(mongo, 'get_mapped_port', return_value=27017):
                url = mongo.get_connection_string()

        assert url == "mongodb://localhost:27017"

    def test_mongodb_get_connection_string_with_auth(self):
        """Test MongoDB connection string with authentication."""
        mongo = MongoDBContainer()
        mongo.with_authentication("admin", "testuser", "testpass")
        mongo._container = MagicMock()

        with patch.object(mongo, 'get_host', return_value='localhost'):
            with patch.object(mongo, 'get_mapped_port', return_value=27017):
                url = mongo.get_connection_string()

        assert url == "mongodb://testuser:testpass@localhost:27017/?authSource=admin"

    def test_mongodb_get_username(self):
        """Test getting MongoDB username."""
        mongo = MongoDBContainer()
        mongo.with_authentication("admin", "testuser", "testpass")

        assert mongo.get_username() == "testuser"

    def test_mongodb_get_password(self):
        """Test getting MongoDB password."""
        mongo = MongoDBContainer()
        mongo.with_authentication("admin", "testuser", "testpass")

        assert mongo.get_password() == "testpass"

    def test_mongodb_get_auth_database(self):
        """Test getting MongoDB auth database."""
        mongo = MongoDBContainer()
        mongo.with_authentication("admin", "testuser", "testpass")

        assert mongo.get_auth_database() == "admin"

    def test_mongodb_wait_strategy(self):
        """Test MongoDB wait strategy is configured."""
        mongo = MongoDBContainer()

        assert isinstance(mongo._wait_strategy, LogMessageWaitStrategy)


# Redis Tests

class TestRedisContainer:
    """Tests for RedisContainer."""

    def test_redis_init_defaults(self):
        """Test Redis container initialization with defaults."""
        redis = RedisContainer()

        assert redis._port == 6379
        assert 6379 in redis._exposed_ports
        assert redis._password is None

    def test_redis_init_custom_image(self):
        """Test Redis container with custom image."""
        redis = RedisContainer(image="redis:6")

        assert redis._image.image_name == "redis:6"

    def test_redis_with_password(self):
        """Test Redis password configuration."""
        redis = RedisContainer()
        result = redis.with_password("mypassword")

        assert result is redis
        assert redis._password == "mypassword"

    def test_redis_get_connection_url_no_password(self):
        """Test Redis connection URL without password."""
        redis = RedisContainer()
        redis._container = MagicMock()

        with patch.object(redis, 'get_host', return_value='localhost'):
            with patch.object(redis, 'get_mapped_port', return_value=6379):
                url = redis.get_connection_url()

        assert url == "redis://localhost:6379"

    def test_redis_get_connection_url_with_password(self):
        """Test Redis connection URL with password."""
        redis = RedisContainer()
        redis.with_password("mypassword")
        redis._container = MagicMock()

        with patch.object(redis, 'get_host', return_value='localhost'):
            with patch.object(redis, 'get_mapped_port', return_value=6379):
                url = redis.get_connection_url()

        assert url == "redis://:mypassword@localhost:6379"

    def test_redis_get_password(self):
        """Test getting Redis password."""
        redis = RedisContainer()
        redis.with_password("testpass")

        assert redis.get_password() == "testpass"

    def test_redis_get_password_none(self):
        """Test getting Redis password when not set."""
        redis = RedisContainer()

        assert redis.get_password() is None

    def test_redis_wait_strategy(self):
        """Test Redis wait strategy is configured."""
        redis = RedisContainer()

        assert isinstance(redis._wait_strategy, LogMessageWaitStrategy)


# JDBC Base Class Tests

class TestJdbcDatabaseContainer:
    """Tests for JdbcDatabaseContainer base class."""

    def test_jdbc_init(self):
        """Test JDBC container initialization."""
        # Create a concrete implementation for testing
        class TestJdbcContainer(JdbcDatabaseContainer):
            def get_driver_class_name(self) -> str:
                return "test.Driver"

            def get_jdbc_url(self) -> str:
                return "jdbc:test://localhost:5432/test"

        container = TestJdbcContainer("test:latest", port=5432)

        assert container._port == 5432
        assert container._username == "test"
        assert container._password == "test"
        assert container._dbname == "test"

    def test_jdbc_fluent_api(self):
        """Test JDBC fluent API methods."""
        class TestJdbcContainer(JdbcDatabaseContainer):
            def get_driver_class_name(self) -> str:
                return "test.Driver"

            def get_jdbc_url(self) -> str:
                return "jdbc:test://localhost:5432/test"

        container = TestJdbcContainer("test:latest")

        result = container.with_username("user")
        assert result is container
        assert container.get_username() == "user"

        result = container.with_password("pass")
        assert result is container
        assert container.get_password() == "pass"

        result = container.with_database_name("db")
        assert result is container
        assert container.get_database_name() == "db"

    def test_jdbc_get_connection_url(self):
        """Test JDBC get_connection_url delegates to get_jdbc_url."""
        class TestJdbcContainer(JdbcDatabaseContainer):
            def get_driver_class_name(self) -> str:
                return "test.Driver"

            def get_jdbc_url(self) -> str:
                return "jdbc:test://localhost:5432/test"

        container = TestJdbcContainer("test:latest")

        assert container.get_connection_url() == container.get_jdbc_url()

    def test_jdbc_get_port(self):
        """Test JDBC get_port returns mapped port."""
        class TestJdbcContainer(JdbcDatabaseContainer):
            def get_driver_class_name(self) -> str:
                return "test.Driver"

            def get_jdbc_url(self) -> str:
                return "jdbc:test://localhost:5432/test"

        container = TestJdbcContainer("test:latest", port=5432)
        container._container = MagicMock()

        with patch.object(container, 'get_mapped_port', return_value=32768):
            port = container.get_port()

        assert port == 32768

    def test_jdbc_getters(self):
        """Test JDBC getter methods."""
        class TestJdbcContainer(JdbcDatabaseContainer):
            def get_driver_class_name(self) -> str:
                return "test.Driver"

            def get_jdbc_url(self) -> str:
                return "jdbc:test://localhost:5432/test"

        container = TestJdbcContainer(
            "test:latest",
            username="myuser",
            password="mypass",
            dbname="mydb"
        )

        assert container.get_username() == "myuser"
        assert container.get_password() == "mypass"
        assert container.get_database_name() == "mydb"

    def test_jdbc_abstract_methods(self):
        """Test JDBC abstract methods must be implemented."""
        # This should raise TypeError because abstract methods are not implemented
        with pytest.raises(TypeError):
            JdbcDatabaseContainer("test:latest")
