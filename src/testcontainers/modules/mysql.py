"""
MySQL container implementation.

This module provides a container for MySQL databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java
"""

from __future__ import annotations

from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MySQLContainer(JdbcDatabaseContainer):
    """
    MySQL database container.

    This container starts a MySQL database instance with configurable
    credentials, database name, and configuration options.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mysql/src/main/java/org/testcontainers/containers/MySQLContainer.java

    Example:
        >>> with MySQLContainer() as mysql:
        ...     url = mysql.get_jdbc_url()
        ...     host = mysql.get_host()
        ...     port = mysql.get_port()
        ...     # Connect to MySQL

        >>> # Custom configuration
        >>> mysql = MySQLContainer("mysql:8.0")
        >>> mysql.with_username("myuser")
        >>> mysql.with_password("mypass")
        >>> mysql.with_database_name("mydb")
        >>> mysql.with_config_option("max_connections", "200")
        >>> mysql.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "mysql:8"
    MYSQL_PORT = 3306
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWORD = "test"
    DEFAULT_DATABASE = "test"
    MYSQL_ROOT_USER = "root"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        dbname: str = DEFAULT_DATABASE,
    ):
        """
        Initialize a MySQL container.

        Args:
            image: Docker image name (default: mysql:8)
            username: Database username (default: test)
            password: Database password (default: test)
            dbname: Database name (default: test)
        """
        super().__init__(
            image=image,
            port=self.MYSQL_PORT,
            username=username,
            password=password,
            dbname=dbname,
        )

        # Explicitly add exposed port like Java does
        self.with_exposed_ports(self.MYSQL_PORT)

        # Configure environment variables using Java's conditional logic
        self.with_env("MYSQL_DATABASE", self._dbname)
        
        # Only set MYSQL_USER if username is not root (Java logic)
        if self._username.lower() != self.MYSQL_ROOT_USER.lower():
            self.with_env("MYSQL_USER", self._username)
        
        # Handle password: empty password only allowed for root
        if self._password:
            self.with_env("MYSQL_PASSWORD", self._password)
            self.with_env("MYSQL_ROOT_PASSWORD", self._password)
        elif self._username.lower() == self.MYSQL_ROOT_USER.lower():
            self.with_env("MYSQL_ALLOW_EMPTY_PASSWORD", "yes")
        else:
            raise ValueError("Empty password can be used only with the root user")

        # Set startup attempts like Java (line 98 in Java source)
        self._startup_attempts = 3

        # Wait for MySQL to be ready
        # MySQL logs "ready for connections" when it's ready to accept connections
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*ready for connections.*")
            .with_times(2)  # MySQL logs this twice during startup (once for each phase)
        )



    def get_driver_class_name(self) -> str:
        """
        Get the JDBC driver class name for MySQL.

        Returns:
            MySQL JDBC driver class name
        """
        return "com.mysql.cj.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for MySQL.

        Automatically adds useSSL=false and allowPublicKeyRetrieval=true
        parameters if not already present, matching Java implementation.

        Returns:
            JDBC connection URL in format: jdbc:mysql://host:port/database[?params]
        """
        host = self.get_host()
        port = self.get_port()
        
        # Build base URL with any configured URL parameters
        additional_params = self._construct_url_parameters("?", "&")
        url = f"jdbc:mysql://{host}:{port}/{self._dbname}{additional_params}"
        
        # Add default SSL settings like Java (lines 118-131 in Java source)
        # This matches constructUrlForConnection() behavior
        if "useSSL=" not in url:
            separator = "&" if "?" in url else "?"
            url = url + separator + "useSSL=false"
        
        if "allowPublicKeyRetrieval=" not in url:
            url = url + "&allowPublicKeyRetrieval=true"
        
        return url

    def get_connection_string(self) -> str:
        """
        Get the MySQL connection string (Python native format).

        Returns:
            Connection string in format: mysql://user:pass@host:port/database
        """
        host = self.get_host()
        port = self.get_port()
        return f"mysql://{self._username}:{self._password}@{host}:{port}/{self._dbname}"

    def with_config_override(self, config_path: str) -> "MySQLContainer":
        """
        Map a custom MySQL configuration file into the container.

        This matches the Java withConfigurationOverride() method (lines 153-156).
        The configuration file will be mounted at /etc/mysql/conf.d/.

        Args:
            config_path: Path to custom my.cnf file

        Returns:
            This container instance

        Example:
            >>> mysql = MySQLContainer()
            >>> mysql.with_config_override("./custom-my.cnf")
        """
        self.with_copy_file_to_container(config_path, "/etc/mysql/conf.d/custom.cnf")
        return self
