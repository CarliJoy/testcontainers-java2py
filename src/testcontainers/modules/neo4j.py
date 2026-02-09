"""
Neo4j graph database container wrapper.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/neo4j/src/main/java/org/testcontainers/neo4j/Neo4jContainer.java
"""

from __future__ import annotations
from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy
from testcontainers.waiting.http import HttpWaitStrategy
from testcontainers.waiting.wait_all import WaitAllStrategy


class Neo4jContainer(GenericContainer):
    """
    Wrapper providing Neo4j 4.4 graph database with configurable auth and plugins.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/neo4j/src/main/java/org/testcontainers/neo4j/Neo4jContainer.java
    """

    def __init__(self, image: str = "neo4j:4.4"):
        super().__init__(image)
        
        # Store configuration state
        self._config = {
            "ports": {"bolt": 7687, "http": 7474, "https": 7473},
            "auth": {"enabled": True, "secret": "password"},
            "extensions": set(),
        }
        
        # Open network ports
        ports_to_expose = [
            self._config["ports"]["bolt"],
            self._config["ports"]["http"],
            self._config["ports"]["https"],
        ]
        self.with_exposed_ports(*ports_to_expose)
        
        # Build combined readiness check
        bolt_pattern = f".*Bolt enabled on .*:{self._config['ports']['bolt']}\\.\n"
        log_wait = LogMessageWaitStrategy().with_regex(bolt_pattern)
        http_wait = HttpWaitStrategy().for_port(self._config["ports"]["http"]).for_status_code(200)
        combined = WaitAllStrategy()
        combined.with_strategy(log_wait)
        combined.with_strategy(http_wait)
        self.waiting_for(combined)

    def _configure(self) -> None:
        # Handle authentication configuration
        if self._config["auth"]["enabled"] and self._config["auth"]["secret"]:
            auth_string = f"neo4j/{self._config['auth']['secret']}"
        else:
            auth_string = "none"
        self.with_env("NEO4J_AUTH", auth_string)
        
        # Handle extension plugins
        if self._config["extensions"]:
            plugin_names = list(self._config["extensions"])
            formatted_list = "[" + ",".join(f'"{name}"' for name in plugin_names) + "]"
            self.with_env("NEO4JLABS_PLUGINS", formatted_list)

    def with_admin_password(self, secret: str | None) -> Neo4jContainer:
        """Configure admin credentials (None disables authentication)."""
        if secret:
            self._config["auth"]["enabled"] = True
            self._config["auth"]["secret"] = secret
        else:
            self._config["auth"]["enabled"] = False
            self._config["auth"]["secret"] = None
        return self

    def without_authentication(self) -> Neo4jContainer:
        """Disable authentication mechanism."""
        self._config["auth"]["enabled"] = False
        self._config["auth"]["secret"] = None
        return self

    def with_labs_plugins(self, *names: str) -> Neo4jContainer:
        """Register Neo4j Labs extensions (like APOC, GDS)."""
        self._config["extensions"].update(names)
        return self

    def with_neo4j_config(self, setting_name: str, setting_value: str) -> Neo4jContainer:
        """Apply Neo4j configuration parameter (auto-converts to env format)."""
        # Transform config key to environment variable name
        env_var = "NEO4J_" + setting_name.replace("_", "__").replace(".", "_")
        self.with_env(env_var, setting_value)
        return self

    def get_bolt_url(self) -> str:
        """Build Bolt protocol connection URI."""
        h = self.get_host()
        p = self.get_mapped_port(self._config["ports"]["bolt"])
        return f"bolt://{h}:{p}"

    def get_http_url(self) -> str:
        """Build HTTP API endpoint URI."""
        h = self.get_host()
        p = self.get_mapped_port(self._config["ports"]["http"])
        return f"http://{h}:{p}"

    def get_https_url(self) -> str:
        """Build HTTPS API endpoint URI."""
        h = self.get_host()
        p = self.get_mapped_port(self._config["ports"]["https"])
        return f"https://{h}:{p}"

    def get_admin_password(self) -> str | None:
        """Retrieve configured admin secret."""
        return self._config["auth"]["secret"] if self._config["auth"]["enabled"] else None
