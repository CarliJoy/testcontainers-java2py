"""
MariaDB SQL database container wrapper.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/mariadb/src/main/java/org/testcontainers/mariadb/MariaDBContainer.java
"""

from __future__ import annotations
from testcontainers.modules.jdbc import JdbcDatabaseContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class MariaDBContainer(JdbcDatabaseContainer):
    """
    Wrapper for MariaDB 10.3.6 with MySQL-compatible protocol.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/mariadb/src/main/java/org/testcontainers/mariadb/MariaDBContainer.java
    """

    # Constants matching Java
    DEFAULT_IMAGE = "mariadb:10.3.6"
    MARIADB_PORT = 3306
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
        super().__init__(image=image, port=self.MARIADB_PORT, username=username, password=password, dbname=dbname)
        
        # Set startup attempts like Java (line 87 in Java source)
        self._startup_attempts = 3
        
        # Configure environment variables
        self._configure()

    def _configure(self) -> None:
        """Configure environment variables for MariaDB initialization."""
        # Database setup
        self.with_env("MYSQL_DATABASE", self._dbname)
        
        # Handle non-root users (Java logic from lines 68-72)
        # Note: Username comparison is case-sensitive (MySQL/MariaDB are case-sensitive for usernames)
        is_root_user = self._username == self.MYSQL_ROOT_USER
        if not is_root_user:
            self.with_env("MYSQL_USER", self._username)
        
        # Password configuration logic (Java logic from lines 73-83)
        has_password = bool(self._password)
        if has_password:
            self.with_env("MYSQL_PASSWORD", self._password)
            self.with_env("MYSQL_ROOT_PASSWORD", self._password)
        elif is_root_user:
            self.with_env("MYSQL_ALLOW_EMPTY_PASSWORD", "yes")
        else:
            raise ValueError("Empty password can be used only with the root user")
        
        # Add wait strategy matching Java/MySQL behavior (moved inside _configure for consistency)
        # MariaDB uses the same "ready for connections" message as MySQL
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*ready for connections.*")
            .with_times(2)  # MariaDB logs this twice during startup
        )

    def get_driver_class_name(self) -> str:
        """Get the JDBC driver class name for MariaDB."""
        return "org.mariadb.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        """
        Get the JDBC connection URL for MariaDB.

        Returns:
            JDBC connection URL in format: jdbc:mariadb://host:port/database[?params]
        """
        additional_params = self._construct_url_parameters("?", "&")
        return f"jdbc:mariadb://{self.get_host()}:{self.get_port()}/{self._dbname}{additional_params}"

    def get_test_query_string(self) -> str:
        """Get the test query string for MariaDB."""
        return "SELECT 1"

    def with_config_override(self, config_path: str) -> "MariaDBContainer":
        """
        Map a custom MariaDB configuration file into the container.

        This matches the Java withConfigurationOverride() method (lines 121-124).
        The configuration file will be mounted at /etc/mysql/conf.d/.

        Args:
            config_path: Path to custom my.cnf file

        Returns:
            This container instance

        Example:
            >>> mariadb = MariaDBContainer()
            >>> mariadb.with_config_override("./custom-my.cnf")
        """
        self.with_copy_file_to_container(config_path, "/etc/mysql/conf.d/custom.cnf")
        return self
