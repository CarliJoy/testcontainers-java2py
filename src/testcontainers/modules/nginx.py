"""
Nginx HTTP server container wrapper.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/nginx/src/main/java/org/testcontainers/nginx/NginxContainer.java
"""

from __future__ import annotations
from testcontainers.core.generic_container import GenericContainer
from testcontainers.core.container_types import BindMode


class NginxContainer(GenericContainer):
    """
    Wrapper for Nginx 1.9.4 web server with foreground execution.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/nginx/src/main/java/org/testcontainers/nginx/NginxContainer.java
    """

    def __init__(self, image: str = "nginx:1.9.4"):
        super().__init__(image)
        self._http_listen_port = 80
        self.with_exposed_ports(self._http_listen_port)
        self.with_command(["nginx", "-g", "daemon off;"])

    def get_base_url(self, protocol: str, port_number: int) -> str:
        """Construct endpoint URL using protocol and port."""
        return f"{protocol}://{self.get_host()}:{self.get_mapped_port(port_number)}"

    def with_custom_content(self, host_path: str) -> NginxContainer:
        """Bind mount directory as static content root."""
        self.with_volume_mapping(host_path, "/usr/share/nginx/html", BindMode.READ_ONLY)
        return self


NGINXContainer = NginxContainer
