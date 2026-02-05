"""
RabbitMQ container implementation.

This module provides a container for RabbitMQ message broker.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/rabbitmq/src/main/java/org/testcontainers/containers/RabbitMQContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class RabbitMQContainer(GenericContainer):
    """
    RabbitMQ message broker container.

    This container starts a RabbitMQ instance with the management plugin enabled.
    The management plugin provides a web-based UI and HTTP API.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/rabbitmq/src/main/java/org/testcontainers/containers/RabbitMQContainer.java

    Example:
        >>> with RabbitMQContainer() as rabbitmq:
        ...     amqp_url = rabbitmq.get_amqp_url()
        ...     http_url = rabbitmq.get_http_url()
        ...     # Connect to RabbitMQ

        >>> # With custom vhost
        >>> rabbitmq = RabbitMQContainer("rabbitmq:3-management")
        >>> rabbitmq.with_vhost("myvhost")
        >>> rabbitmq.start()
        >>> amqp_url = rabbitmq.get_amqp_url()

    Security considerations:
        - Default credentials are guest/guest
        - Change credentials for production use
        - Consider using TLS/SSL for production deployments
        - Management UI is exposed on port 15672
    """

    # Default configuration
    DEFAULT_IMAGE = "rabbitmq:3-management"
    DEFAULT_AMQP_PORT = 5672
    DEFAULT_HTTPS_PORT = 5671
    DEFAULT_MANAGEMENT_PORT = 15672

    # Default credentials
    DEFAULT_USERNAME = "guest"
    DEFAULT_PASSWORD = "guest"
    DEFAULT_VHOST = "/"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a RabbitMQ container.

        Args:
            image: Docker image name (default: rabbitmq:3-management)
        """
        super().__init__(image)

        self._amqp_port = self.DEFAULT_AMQP_PORT
        self._management_port = self.DEFAULT_MANAGEMENT_PORT
        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD
        self._vhost = self.DEFAULT_VHOST

        # Expose RabbitMQ ports
        self.with_exposed_ports(self._amqp_port, self._management_port)

        # Set default environment variables
        self.with_env("RABBITMQ_DEFAULT_USER", self._username)
        self.with_env("RABBITMQ_DEFAULT_PASS", self._password)
        self.with_env("RABBITMQ_DEFAULT_VHOST", self._vhost)

        # Wait for RabbitMQ to be ready
        # RabbitMQ logs "Server startup complete" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Server startup complete.*")
        )

    def with_vhost(self, vhost: str) -> RabbitMQContainer:
        """
        Set the RabbitMQ virtual host (fluent API).

        Virtual hosts provide logical grouping and separation of resources.

        Args:
            vhost: Virtual host name (e.g., "/", "myvhost")

        Returns:
            This container instance
        """
        self._vhost = vhost
        self.with_env("RABBITMQ_DEFAULT_VHOST", vhost)
        return self

    def with_username(self, username: str) -> RabbitMQContainer:
        """
        Set the RabbitMQ username (fluent API).

        Args:
            username: RabbitMQ username

        Returns:
            This container instance
        """
        self._username = username
        self.with_env("RABBITMQ_DEFAULT_USER", username)
        return self

    def with_password(self, password: str) -> RabbitMQContainer:
        """
        Set the RabbitMQ password (fluent API).

        Args:
            password: RabbitMQ password

        Returns:
            This container instance

        Security note:
            Use strong passwords for production deployments
        """
        self._password = password
        self.with_env("RABBITMQ_DEFAULT_PASS", password)
        return self

    def with_credentials(
        self, username: str, password: str
    ) -> RabbitMQContainer:
        """
        Set both username and password (fluent API).

        Args:
            username: RabbitMQ username
            password: RabbitMQ password

        Returns:
            This container instance
        """
        self.with_username(username)
        self.with_password(password)
        return self

    def get_amqp_url(self) -> str:
        """
        Get the AMQP connection URL.

        This URL is used by AMQP clients to connect to RabbitMQ.

        Returns:
            AMQP URL in format: amqp://user:pass@host:port/vhost

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._amqp_port)
        
        # URL encode vhost (replace / with %2F)
        vhost = self._vhost
        if vhost == "/":
            vhost = ""
        elif vhost.startswith("/"):
            vhost = vhost[1:]

        return f"amqp://{self._username}:{self._password}@{host}:{port}/{vhost}"

    def get_http_url(self) -> str:
        """
        Get the RabbitMQ Management HTTP API URL.

        This URL provides access to the management REST API and web UI.

        Returns:
            HTTP URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._management_port)
        return f"http://{host}:{port}"

    def get_admin_url(self) -> str:
        """
        Get the RabbitMQ Management UI URL.

        Alias for get_http_url() for compatibility.

        Returns:
            HTTP URL for the management UI
        """
        return self.get_http_url()

    def get_amqp_port(self) -> int:
        """
        Get the exposed AMQP port number on the host.

        Returns:
            Host port number mapped to the AMQP port
        """
        return self.get_mapped_port(self._amqp_port)

    def get_management_port(self) -> int:
        """
        Get the exposed management port number on the host.

        Returns:
            Host port number mapped to the management port
        """
        return self.get_mapped_port(self._management_port)

    def get_port(self) -> int:
        """
        Get the exposed AMQP port number on the host.

        Alias for get_amqp_port().

        Returns:
            Host port number mapped to the AMQP port
        """
        return self.get_amqp_port()

    def get_username(self) -> str:
        """
        Get the RabbitMQ username.

        Returns:
            RabbitMQ username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the RabbitMQ password.

        Returns:
            RabbitMQ password
        """
        return self._password

    def get_vhost(self) -> str:
        """
        Get the RabbitMQ virtual host.

        Returns:
            Virtual host name
        """
        return self._vhost
