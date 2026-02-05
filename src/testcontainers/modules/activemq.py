"""
Apache ActiveMQ container implementation.

This module provides a container for Apache ActiveMQ Classic message broker.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/activemq/src/main/java/org/testcontainers/containers/ActiveMQContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class ActiveMQContainer(GenericContainer):
    """
    Apache ActiveMQ Classic message broker container.

    This container starts an ActiveMQ instance with OpenWire protocol and web console.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/activemq/src/main/java/org/testcontainers/containers/ActiveMQContainer.java

    Example:
        >>> with ActiveMQContainer() as activemq:
        ...     broker_url = activemq.get_broker_url()
        ...     console_url = activemq.get_web_console_url()
        ...     # Connect to ActiveMQ

        >>> # With custom credentials
        >>> activemq = ActiveMQContainer()
        >>> activemq.with_credentials("myuser", "mypassword")
        >>> activemq.start()
        >>> broker_url = activemq.get_broker_url()

    Security considerations:
        - Default credentials are admin/admin
        - Change credentials for production use
        - Consider using TLS/SSL for production deployments
        - Web console is accessible on port 8161
    """

    # Default configuration
    DEFAULT_IMAGE = "apache/activemq-classic:latest"
    DEFAULT_OPENWIRE_PORT = 61616
    DEFAULT_WEB_CONSOLE_PORT = 8161

    # Default credentials
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "admin"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an ActiveMQ container.

        Args:
            image: Docker image name (default: apache/activemq-classic:latest)
        """
        super().__init__(image)

        self._openwire_port = self.DEFAULT_OPENWIRE_PORT
        self._web_console_port = self.DEFAULT_WEB_CONSOLE_PORT
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD

        # Expose ActiveMQ ports
        self.with_exposed_ports(self._openwire_port, self._web_console_port)

        # Wait for ActiveMQ web console to be ready
        # The admin page requires authentication, so we expect 401 unauthorized
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/admin")
            .for_port(self._web_console_port)
            .for_status_code_matching(lambda code: code in [200, 401])
        )

    def with_credentials(
        self, username: str, password: str
    ) -> ActiveMQContainer:
        """
        Set both username and password (fluent API).

        Args:
            username: ActiveMQ username
            password: ActiveMQ password

        Returns:
            This container instance

        Security note:
            Use strong passwords for production deployments
        """
        self._username = username
        self._password = password
        return self

    def get_broker_url(self) -> str:
        """
        Get the ActiveMQ broker URL for OpenWire protocol.

        This URL is used by JMS clients to connect to ActiveMQ.

        Returns:
            Broker URL in format: tcp://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._openwire_port)
        return f"tcp://{host}:{port}"

    def get_web_console_url(self) -> str:
        """
        Get the ActiveMQ web console URL.

        The web console provides management UI and REST API.

        Returns:
            Web console URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._web_console_port)
        return f"http://{host}:{port}"

    def get_openwire_port(self) -> int:
        """
        Get the exposed OpenWire port number on the host.

        Returns:
            Host port number mapped to the OpenWire port
        """
        return self.get_mapped_port(self._openwire_port)

    def get_web_console_port(self) -> int:
        """
        Get the exposed web console port number on the host.

        Returns:
            Host port number mapped to the web console port
        """
        return self.get_mapped_port(self._web_console_port)

    def get_port(self) -> int:
        """
        Get the exposed OpenWire port number on the host.

        Alias for get_openwire_port().

        Returns:
            Host port number mapped to the OpenWire port
        """
        return self.get_openwire_port()

    def get_username(self) -> str:
        """
        Get the ActiveMQ username.

        Returns:
            ActiveMQ username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the ActiveMQ password.

        Returns:
            ActiveMQ password
        """
        return self._password
