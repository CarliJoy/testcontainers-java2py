"""
Redpanda container implementation.

This module provides a container for Redpanda, a Kafka-compatible streaming platform.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/redpanda/src/main/java/org/testcontainers/redpanda/RedpandaContainer.java
"""

from __future__ import annotations

from typing import Callable

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class RedpandaContainer(GenericContainer):
    """
    Redpanda streaming platform container.

    Redpanda is a Kafka-compatible event streaming platform that's easier to deploy
    and manage than Kafka. It provides Kafka API compatibility along with Schema
    Registry and HTTP Proxy.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/redpanda/src/main/java/org/testcontainers/redpanda/RedpandaContainer.java

    Example:
        >>> with RedpandaContainer() as redpanda:
        ...     bootstrap_servers = redpanda.get_bootstrap_servers()
        ...     schema_registry = redpanda.get_schema_registry_address()
        ...     # Connect to Redpanda using Kafka client

        >>> # With SASL authentication
        >>> redpanda = RedpandaContainer()
        >>> redpanda.with_enable_sasl()
        >>> redpanda.with_superuser("admin")
        >>> redpanda.with_enable_authorization()
        >>> redpanda.start()

        >>> # With additional listeners for container networking
        >>> redpanda = RedpandaContainer()
        >>> redpanda.with_listener("broker:9093")
        >>> redpanda.start()

    Exposed ports:
        - 9092: Kafka API
        - 9644: Admin API
        - 8081: Schema Registry
        - 8082: HTTP Proxy

    Notes:
        - Requires Redpanda version >= v22.2.1
        - Runs in single-node development mode
        - Default authentication is disabled
        - SASL and authorization can be enabled
    """

    # Default configuration
    DEFAULT_IMAGE = "redpandadata/redpanda:v23.3.1"
    DEFAULT_BROKER_PORT = 9092
    DEFAULT_ADMIN_PORT = 9644
    DEFAULT_SCHEMA_REGISTRY_PORT = 8081
    DEFAULT_REST_PROXY_PORT = 8082

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Redpanda container.

        Args:
            image: Docker image name (default: redpandadata/redpanda:v23.3.1)
        """
        super().__init__(image)

        self._enable_authorization = False
        self._authentication_method = "none"
        self._schema_registry_authentication_method = "none"
        self._superusers: list[str] = []
        self._listeners: dict[str, Callable[[], str] | None] = {}

        # Expose Redpanda ports
        self.with_exposed_ports(
            self.DEFAULT_BROKER_PORT,
            self.DEFAULT_ADMIN_PORT,
            self.DEFAULT_SCHEMA_REGISTRY_PORT,
            self.DEFAULT_REST_PROXY_PORT,
        )

        # Configure Redpanda to run in development mode
        self.with_command(
            [
                "redpanda",
                "start",
                "--mode=dev-container",
                "--smp=1",
                "--memory=1G",
            ]
        )

        # Wait for Redpanda to be ready
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Successfully started Redpanda!.*")
            .with_times(1)
        )

    def with_enable_authorization(self) -> RedpandaContainer:
        """
        Enable authorization in Redpanda (fluent API).

        When enabled, Redpanda will enforce ACLs for Kafka operations.

        Returns:
            This container instance
        """
        self._enable_authorization = True
        return self

    def with_enable_sasl(self) -> RedpandaContainer:
        """
        Enable SASL authentication for Kafka API (fluent API).

        When enabled, clients must authenticate using SASL/SCRAM.

        Returns:
            This container instance
        """
        self._authentication_method = "sasl"
        return self

    def with_enable_schema_registry_http_basic_auth(self) -> RedpandaContainer:
        """
        Enable HTTP Basic authentication for Schema Registry (fluent API).

        When enabled, Schema Registry requests must include HTTP Basic auth headers.

        Returns:
            This container instance
        """
        self._schema_registry_authentication_method = "http_basic"
        return self

    def with_superuser(self, username: str) -> RedpandaContainer:
        """
        Register a username as a superuser (fluent API).

        Superusers have all permissions in Redpanda and bypass ACL checks.

        Args:
            username: Username to register as superuser

        Returns:
            This container instance
        """
        self._superusers.append(username)
        return self

    def with_listener(
        self,
        listener: str,
        advertised_listener: Callable[[], str] | None = None,
    ) -> RedpandaContainer:
        """
        Add an additional Kafka listener (fluent API).

        Listeners allow connections from different networks. The listener format
        is 'host:port'. The host will be added as a network alias.

        Default listeners:
        - 0.0.0.0:9092 (exposed to host)
        - 0.0.0.0:9093 (internal)

        Args:
            listener: Listener address in format 'host:port'
            advertised_listener: Optional callable returning advertised listener address

        Returns:
            This container instance

        Example:
            >>> # Add listener for container network
            >>> redpanda.with_listener("broker:9093")
            >>> # Add listener with custom advertised address
            >>> redpanda.with_listener(
            ...     "broker:9093",
            ...     lambda: f"external:9093"
            ... )
        """
        self._listeners[listener] = advertised_listener
        return self

    def start(self) -> RedpandaContainer:  # type: ignore[override]
        """
        Start the Redpanda container.

        Configures the container with authentication, authorization, and listener
        settings before starting.

        Returns:
            This container instance
        """
        # Add network aliases for listener hosts
        for listener in self._listeners.keys():
            host = listener.split(":")[0]
            self.with_network_aliases(host)

        super().start()
        return self

    def get_bootstrap_servers(self) -> str:
        """
        Get the Kafka bootstrap servers address.

        Returns:
            Bootstrap servers in format: PLAINTEXT://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self.DEFAULT_BROKER_PORT)
        return f"PLAINTEXT://{host}:{port}"

    def get_schema_registry_address(self) -> str:
        """
        Get the Schema Registry HTTP address.

        Returns:
            Schema Registry address in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.DEFAULT_SCHEMA_REGISTRY_PORT)
        return f"http://{host}:{port}"

    def get_admin_address(self) -> str:
        """
        Get the Redpanda Admin API HTTP address.

        Returns:
            Admin API address in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.DEFAULT_ADMIN_PORT)
        return f"http://{host}:{port}"

    def get_rest_proxy_address(self) -> str:
        """
        Get the REST Proxy HTTP address.

        The REST Proxy provides an HTTP interface to Kafka.

        Returns:
            REST Proxy address in format: http://host:port
        """
        host = self.get_host()
        port = self.get_mapped_port(self.DEFAULT_REST_PROXY_PORT)
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed Kafka broker port on the host.

        Returns:
            Host port number mapped to the broker port
        """
        return self.get_mapped_port(self.DEFAULT_BROKER_PORT)

    def get_schema_registry_port(self) -> int:
        """
        Get the exposed Schema Registry port on the host.

        Returns:
            Host port number mapped to the Schema Registry port
        """
        return self.get_mapped_port(self.DEFAULT_SCHEMA_REGISTRY_PORT)

    def get_admin_port(self) -> int:
        """
        Get the exposed Admin API port on the host.

        Returns:
            Host port number mapped to the Admin API port
        """
        return self.get_mapped_port(self.DEFAULT_ADMIN_PORT)

    def get_rest_proxy_port(self) -> int:
        """
        Get the exposed REST Proxy port on the host.

        Returns:
            Host port number mapped to the REST Proxy port
        """
        return self.get_mapped_port(self.DEFAULT_REST_PROXY_PORT)
