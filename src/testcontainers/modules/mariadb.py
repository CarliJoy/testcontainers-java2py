"""MariaDB SQL database container wrapper."""

from __future__ import annotations
from testcontainers.modules.jdbc import JdbcDatabaseContainer


class MariaDBContainer(JdbcDatabaseContainer):
    """Wrapper for MariaDB 10.3.6 with MySQL-compatible protocol."""

    def __init__(
        self,
        image: str = "mariadb:10.3.6",
        username: str = "test",
        password: str = "test",
        dbname: str = "test",
    ):
        super().__init__(image=image, port=3306, username=username, password=password, dbname=dbname)

    def _configure(self) -> None:
        # Database setup
        self.with_env("MYSQL_DATABASE", self._dbname)
        
        # Handle non-root users
        is_root_user = self._username == "root"
        if not is_root_user:
            self.with_env("MYSQL_USER", self._username)
        
        # Password configuration logic
        has_password = bool(self._password)
        if has_password:
            self.with_env("MYSQL_PASSWORD", self._password)
            self.with_env("MYSQL_ROOT_PASSWORD", self._password)
        elif is_root_user:
            self.with_env("MYSQL_ALLOW_EMPTY_PASSWORD", "yes")
        else:
            raise ValueError("Only root can have empty password")

    def get_driver_class_name(self) -> str:
        return "org.mariadb.jdbc.Driver"

    def get_jdbc_url(self) -> str:
        return f"jdbc:mariadb://{self.get_host()}:{self.get_port()}/{self._dbname}"

    def get_test_query_string(self) -> str:
        return "SELECT 1"
