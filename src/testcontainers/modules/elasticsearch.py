"""
Elasticsearch container implementation.

This module provides a container for Elasticsearch search and analytics engine.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/elasticsearch/src/main/java/org/testcontainers/elasticsearch/ElasticsearchContainer.java
"""

from __future__ import annotations

from typing import Optional
from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


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
    DEFAULT_IMAGE = "docker.elastic.co/elasticsearch/elasticsearch:7.9.2"
    ELASTICSEARCH_DEFAULT_PORT = 9200
    ELASTICSEARCH_DEFAULT_TCP_PORT = 9300
    ELASTICSEARCH_DEFAULT_PASSWORD = "changeme"
    DEFAULT_CERT_PATH = "/usr/share/elasticsearch/config/certs/http_ca.crt"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an Elasticsearch container.

        Args:
            image: Docker image name
        """
        super().__init__(image)

        self._http_port = self.ELASTICSEARCH_DEFAULT_PORT
        self._transport_port = self.ELASTICSEARCH_DEFAULT_TCP_PORT
        self._password: str | None = None
        self._cert_path: str = ""
        
        # Check if version 8+
        self._is_at_least_major_version_8 = self._check_version_8(image)

        # Expose Elasticsearch ports
        self.with_exposed_ports(self._http_port, self._transport_port)

        # Default environment variables for single-node cluster
        self.with_env("discovery.type", "single-node")
        
        # Disable disk threshold checks
        self.with_env("cluster.routing.allocation.disk.threshold_enabled", "false")
        
        # Wait strategy matching Java regex
        regex = r".*(\"message\":\s?\"started[\s?|\"].*|] started\n$)"
        self.waiting_for(LogMessageWaitStrategy().with_regex(regex))
        
        # If version 8+, enable security by default
        if self._is_at_least_major_version_8:
            self.with_password(self.ELASTICSEARCH_DEFAULT_PASSWORD)
            self.with_cert_path(self.DEFAULT_CERT_PATH)

    def _check_version_8(self, image: str) -> bool:
        """Check if the image version is 8.0.0 or higher."""
        try:
            # Extract version from image name
            if ':' in image:
                version_str = image.split(':')[-1]
                # Parse major version
                if version_str and version_str[0].isdigit():
                    major_version = int(version_str.split('.')[0])
                    return major_version >= 8
        except (ValueError, IndexError):
            pass
        return False

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
        self.with_env("ELASTIC_PASSWORD", password)
        
        # Enable security for versions < 8 (version 8+ has it enabled by default)
        if not self._is_at_least_major_version_8:
            self.with_env("xpack.security.enabled", "true")
        
        return self

    def with_cert_path(self, cert_path: str) -> ElasticsearchContainer:
        """
        Configure a CA cert path.

        Args:
            cert_path: Path to the CA certificate within the Docker container

        Returns:
            This container instance
        """
        self._cert_path = cert_path
        return self

    def ca_cert_as_bytes(self) -> Optional[bytes]:
        """
        Extract the CA certificate from the container.

        Returns:
            Bytes of the CA certificate or None if not found
        """
        if not self._cert_path:
            return None
        
        if not self._container:
            return None
        
        try:
            # Copy file from container
            import tarfile
            import io
            
            bits, _ = self._docker_client.api.get_archive(
                self._container.id, self._cert_path
            )
            
            # Extract file from tar
            tar_stream = io.BytesIO(b''.join(bits))
            with tarfile.open(fileobj=tar_stream) as tar:
                members = tar.getmembers()
                if members:
                    extracted = tar.extractfile(members[0])
                    if extracted:
                        return extracted.read()
        except Exception:
            # Certificate not found or error occurred
            pass
        
        return None

    def start(self) -> ElasticsearchContainer:  # type: ignore[override]
        """
        Start the Elasticsearch container with configured options.

        Returns:
            This container instance
        """
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
        if not self._container:
            raise RuntimeError("Container not started")
        
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
        
        Note:
            Deprecated in Elasticsearch 8.0+
        """
        return self.get_mapped_port(self._transport_port)
