"""
LocalStack container implementation.

This module provides a container for LocalStack AWS cloud stack simulation.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/localstack/src/main/java/org/testcontainers/containers/localstack/LocalStackContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class LocalStackContainer(GenericContainer):
    """
    LocalStack container for AWS cloud stack simulation.

    This container starts a LocalStack instance that provides a fully functional
    local AWS cloud stack for development and testing.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/localstack/src/main/java/org/testcontainers/containers/localstack/LocalStackContainer.java

    Example:
        >>> with LocalStackContainer() as localstack:
        ...     url = localstack.get_url()
        ...     # Connect to LocalStack services

        >>> # With specific services
        >>> localstack = LocalStackContainer("localstack/localstack:2.0")
        >>> localstack.with_services(["s3", "dynamodb", "sqs"])
        >>> localstack.start()
        >>> url = localstack.get_url()
    """

    # Default configuration
    DEFAULT_IMAGE = "localstack/localstack:latest"
    DEFAULT_EDGE_PORT = 4566

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a LocalStack container.

        Args:
            image: Docker image name (default: localstack/localstack:latest)
        """
        super().__init__(image)

        self._edge_port = self.DEFAULT_EDGE_PORT
        self._services: list[str] = []

        # Expose edge service port
        self.with_exposed_ports(self._edge_port)

        # Wait for LocalStack to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/_localstack/health")
            .for_status_code(200)
        )

    def with_services(self, services: list[str]) -> LocalStackContainer:
        """
        Set the AWS services to enable (fluent API).

        If not specified, all services are enabled by default.

        Args:
            services: List of AWS service names (e.g., ["s3", "dynamodb", "sqs"])

        Returns:
            This container instance
        """
        self._services = services
        return self

    def start(self) -> LocalStackContainer:  # type: ignore[override]
        """
        Start the LocalStack container with any configured options.

        Returns:
            This container instance
        """
        # Set SERVICES environment variable if specific services are configured
        if self._services:
            services_str = ",".join(self._services)
            self.with_env("SERVICES", services_str)

        super().start()
        return self

    def get_url(self) -> str:
        """
        Get the LocalStack edge service URL.

        This URL provides access to all AWS services through a single endpoint.

        Returns:
            URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._edge_port)
        return f"http://{host}:{port}"

    def get_port(self) -> int:
        """
        Get the exposed edge service port number on the host.

        Returns:
            Host port number mapped to the edge service port
        """
        return self.get_mapped_port(self._edge_port)
