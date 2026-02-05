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
    DEFAULT_IMAGE = "rabbitmq:3.7.25-management-alpine"
    DEFAULT_AMQP_PORT = 5672
    DEFAULT_AMQPS_PORT = 5671
    DEFAULT_HTTP_PORT = 15672
    DEFAULT_HTTPS_PORT = 15671

    # Default credentials
    DEFAULT_USERNAME = "guest"
    DEFAULT_PASSWORD = "guest"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a RabbitMQ container.

        Args:
            image: Docker image name (default: rabbitmq:3.7.25-management-alpine)
        """
        super().__init__(image)

        self._amqp_port = self.DEFAULT_AMQP_PORT
        self._amqps_port = self.DEFAULT_AMQPS_PORT
        self._http_port = self.DEFAULT_HTTP_PORT
        self._https_port = self.DEFAULT_HTTPS_PORT
        self._admin_username = self.DEFAULT_USERNAME
        self._admin_password = self.DEFAULT_PASSWORD

        # Expose RabbitMQ ports (all 4 ports like Java)
        self.with_exposed_ports(
            self._amqp_port,
            self._amqps_port,
            self._http_port,
            self._https_port
        )

        # Wait for RabbitMQ to be ready
        # RabbitMQ logs "Server startup complete" when ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Server startup complete.*")
        )

    def start(self) -> RabbitMQContainer:  # type: ignore[override]
        """
        Start the RabbitMQ container with configured options.

        Returns:
            This container instance
        """
        # Configure environment variables
        if self._admin_username is not None:
            self.with_env("RABBITMQ_DEFAULT_USER", self._admin_username)
        if self._admin_password is not None:
            self.with_env("RABBITMQ_DEFAULT_PASS", self._admin_password)
        
        super().start()
        return self

    def with_admin_user(self, username: str) -> RabbitMQContainer:
        """
        Set the admin username (fluent API).

        Args:
            username: RabbitMQ admin username

        Returns:
            This container instance
        """
        self._admin_username = username
        return self

    def with_admin_password(self, password: str) -> RabbitMQContainer:
        """
        Set the admin password (fluent API).

        Args:
            password: RabbitMQ admin password

        Returns:
            This container instance

        Security note:
            Use strong passwords for production deployments
        """
        self._admin_password = password
        return self

    def with_ssl(
        self,
        key_file: str,
        cert_file: str,
        ca_file: str,
        verify: str = "verify_none",
        fail_if_no_cert: bool = False,
        verification_depth: int | None = None,
    ) -> RabbitMQContainer:
        """
        Configure SSL/TLS for RabbitMQ.

        Args:
            key_file: Path to the private key file
            cert_file: Path to the certificate file
            ca_file: Path to the CA certificate file
            verify: SSL verification mode ("verify_none" or "verify_peer")
            fail_if_no_cert: Whether to fail if no peer certificate is provided
            verification_depth: Maximum certificate chain depth

        Returns:
            This container instance
        """
        self.with_env("RABBITMQ_SSL_CACERTFILE", "/etc/rabbitmq/ca_cert.pem")
        self.with_env("RABBITMQ_SSL_CERTFILE", "/etc/rabbitmq/rabbitmq_cert.pem")
        self.with_env("RABBITMQ_SSL_KEYFILE", "/etc/rabbitmq/rabbitmq_key.pem")
        self.with_env("RABBITMQ_SSL_VERIFY", verify)
        self.with_env("RABBITMQ_SSL_FAIL_IF_NO_PEER_CERT", str(fail_if_no_cert).lower())
        
        if verification_depth is not None:
            self.with_env("RABBITMQ_SSL_DEPTH", str(verification_depth))
        
        # Copy certificate files to container
        self.with_copy_file_to_container(cert_file, "/etc/rabbitmq/rabbitmq_cert.pem")
        self.with_copy_file_to_container(ca_file, "/etc/rabbitmq/ca_cert.pem")
        self.with_copy_file_to_container(key_file, "/etc/rabbitmq/rabbitmq_key.pem")
        
        return self

    def get_admin_username(self) -> str:
        """Get the admin username."""
        return self._admin_username

    def get_admin_password(self) -> str:
        """Get the admin password."""
        return self._admin_password

    def get_amqp_port(self) -> int:
        """Get the AMQP port (5672)."""
        return self.get_mapped_port(self._amqp_port)

    def get_amqps_port(self) -> int:
        """Get the AMQPS port (5671)."""
        return self.get_mapped_port(self._amqps_port)

    def get_http_port(self) -> int:
        """Get the HTTP management port (15672)."""
        return self.get_mapped_port(self._http_port)

    def get_https_port(self) -> int:
        """Get the HTTPS management port (15671)."""
        return self.get_mapped_port(self._https_port)

    def get_amqp_url(self) -> str:
        """
        Get the AMQP connection URL.

        Returns:
            AMQP URL in format: amqp://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_amqp_port()
        return f"amqp://{host}:{port}"

    def get_amqps_url(self) -> str:
        """
        Get the AMQPS connection URL.

        Returns:
            AMQPS URL in format: amqps://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_amqps_port()
        return f"amqps://{host}:{port}"

    def get_http_url(self) -> str:
        """
        Get the RabbitMQ Management HTTP API URL.

        Returns:
            HTTP URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_http_port()
        return f"http://{host}:{port}"

    def get_https_url(self) -> str:
        """
        Get the RabbitMQ Management HTTPS API URL.

        Returns:
            HTTPS URL in format: https://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_https_port()
        return f"https://{host}:{port}"
