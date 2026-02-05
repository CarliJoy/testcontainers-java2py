"""
NGINX container implementation.

This module provides a container for NGINX web server.
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class NGINXContainer(GenericContainer):
    """
    NGINX web server container.

    This container starts an NGINX web server instance with configurable
    ports and custom configuration support.

    Example:
        >>> with NGINXContainer() as nginx:
        ...     url = nginx.get_url()
        ...     # Access NGINX server

        >>> # With custom configuration
        >>> nginx = NGINXContainer("nginx:alpine")
        >>> nginx.with_custom_config("/path/to/nginx.conf")
        >>> nginx.start()
        >>> url = nginx.get_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "nginx:latest"
    DEFAULT_HTTP_PORT = 80
    DEFAULT_HTTPS_PORT = 443

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an NGINX container.

        Args:
            image: Docker image name (default: nginx:latest)
        """
        super().__init__(image)

        self._http_port = self.DEFAULT_HTTP_PORT
        self._https_port = self.DEFAULT_HTTPS_PORT
        self._custom_config_path: str | None = None

        # Expose HTTP port by default
        self.with_exposed_ports(self._http_port)

        # Wait for NGINX to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/")
            .for_status_code_matching(lambda code: code < 500)
        )

    def with_custom_config(self, config_path: str) -> NGINXContainer:
        """
        Mount a custom NGINX configuration file (fluent API).

        Args:
            config_path: Path to custom nginx.conf file on host

        Returns:
            This container instance
        """
        self._custom_config_path = config_path
        return self

    def with_https(self) -> NGINXContainer:
        """
        Enable HTTPS port exposure (fluent API).

        Returns:
            This container instance
        """
        self.with_exposed_ports(self._https_port)
        return self

    def start(self) -> NGINXContainer:  # type: ignore[override]
        """
        Start the NGINX container with any configured options.

        Returns:
            This container instance
        """
        # Mount custom config if provided
        if self._custom_config_path:
            self.with_volume_mapping(
                self._custom_config_path,
                "/etc/nginx/nginx.conf",
                "ro"
            )

        super().start()
        return self

    def get_url(self) -> str:
        """
        Get the HTTP URL for the NGINX server.

        Returns:
            HTTP URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._http_port)
        return f"http://{host}:{port}"

    def get_https_url(self) -> str:
        """
        Get the HTTPS URL for the NGINX server.

        Returns:
            HTTPS URL in format: https://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._https_port)
        return f"https://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self._http_port)
