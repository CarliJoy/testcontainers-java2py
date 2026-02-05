"""
Elasticsearch container implementation.

This module provides a container for Elasticsearch search and analytics engine.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/elasticsearch/src/main/java/org/testcontainers/elasticsearch/ElasticsearchContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class ElasticsearchContainer(GenericContainer):
    """
    Elasticsearch search and analytics engine container.

    This container starts an Elasticsearch instance with configurable
    authentication and security settings.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/elasticsearch/src/main/java/org/testcontainers/elasticsearch/ElasticsearchContainer.java

    Example:
        >>> with ElasticsearchContainer() as es:
        ...     http_url = es.get_http_url()
        ...     # Connect to Elasticsearch

        >>> # With password authentication
        >>> es = ElasticsearchContainer("elasticsearch:8.11.0")
        >>> es.with_password("mypassword")
        >>> es.start()
        >>> http_url = es.get_http_url()

    Security considerations:
        - Default configuration disables security for simplicity
        - For production use, enable xpack.security and use strong passwords
        - Consider using HTTPS/TLS for production deployments
        - Default user is 'elastic' when security is enabled
    """

    # Default configuration
    DEFAULT_IMAGE = "elasticsearch:8.11.0"
    DEFAULT_HTTP_PORT = 9200
    DEFAULT_TRANSPORT_PORT = 9300

    # Default credentials
    DEFAULT_USERNAME = "elastic"
    DEFAULT_PASSWORD = "changeme"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an Elasticsearch container.

        Args:
            image: Docker image name (default: elasticsearch:8.11.0)
        """
        super().__init__(image)

        self._http_port = self.DEFAULT_HTTP_PORT
        self._transport_port = self.DEFAULT_TRANSPORT_PORT
        self._password: str | None = None

        # Expose Elasticsearch ports
        self.with_exposed_ports(self._http_port, self._transport_port)

        # Default environment variables for single-node cluster
        self.with_env("discovery.type", "single-node")
        
        # Disable security by default for easier testing
        # Users should enable it with with_password() for production
        self.with_env("xpack.security.enabled", "false")
        
        # Set reasonable memory limits for testing
        self.with_env("ES_JAVA_OPTS", "-Xms512m -Xmx512m")

        # Wait for Elasticsearch to be ready
        # Check the cluster health endpoint
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/_cluster/health")
            .for_port(self._http_port)
            .for_status_code(200)
        )

    def with_password(self, password: str) -> ElasticsearchContainer:
        """
        Set the password for the 'elastic' user and enable security (fluent API).

        When a password is set, xpack security is automatically enabled.

        Args:
            password: Password for the elastic user

        Returns:
            This container instance

        Security note:
            Setting a password enables xpack.security.enabled=true
        """
        self._password = password
        return self

    def start(self) -> ElasticsearchContainer:  # type: ignore[override]
        """
        Start the Elasticsearch container with configured options.

        If a password was set, security features are enabled.

        Returns:
            This container instance
        """
        # Enable security if password is set
        if self._password:
            self.with_env("xpack.security.enabled", "true")
            self.with_env("ELASTIC_PASSWORD", self._password)
            
            # Update wait strategy to use authentication
            self.waiting_for(
                HttpWaitStrategy()
                .for_path("/_cluster/health")
                .for_port(self._http_port)
                .for_status_code(200)
                .with_basic_credentials(self.DEFAULT_USERNAME, self._password)
            )

        super().start()
        return self

    def get_http_url(self) -> str:
        """
        Get the Elasticsearch HTTP URL.

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

    def get_http_host_address(self) -> str:
        """
        Get the Elasticsearch HTTP host address (host:port).

        Returns:
            HTTP host address in format: host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self._http_port)
        return f"{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed HTTP port number on the host.

        Returns:
            Host port number mapped to the HTTP port
        """
        return self.get_mapped_port(self._http_port)

    def get_transport_port(self) -> int:
        """
        Get the exposed transport port number on the host.

        The transport port is used for internal cluster communication.

        Returns:
            Host port number mapped to the transport port
        """
        return self.get_mapped_port(self._transport_port)

    def get_username(self) -> str:
        """
        Get the Elasticsearch username.

        Returns:
            Username (always 'elastic')
        """
        return self.DEFAULT_USERNAME

    def get_password(self) -> str | None:
        """
        Get the Elasticsearch password if authentication is enabled.

        Returns:
            Password or None if security is disabled
        """
        return self._password
