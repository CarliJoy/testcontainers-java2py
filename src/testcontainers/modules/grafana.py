"""
Grafana LGTM Stack container implementation.

This module provides a container for Grafana LGTM (Loki, Grafana, Tempo, Mimir) observability stack.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/grafana/src/main/java/org/testcontainers/grafana/LgtmStackContainer.java
"""

from __future__ import annotations

import logging

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy

logger = logging.getLogger(__name__)


class LgtmStackContainer(GenericContainer):
    """
    Grafana LGTM (Loki, Grafana, Tempo, Mimir) observability stack container.

    This container starts the full Grafana LGTM stack with OpenTelemetry collector,
    providing metrics, logs, and traces collection and visualization.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/grafana/src/main/java/org/testcontainers/grafana/LgtmStackContainer.java

    Example:
        >>> with LgtmStackContainer() as lgtm:
        ...     grafana_url = lgtm.get_grafana_http_url()
        ...     otlp_grpc_url = lgtm.get_otlp_grpc_url()
        ...     # Connect to LGTM stack

        >>> # Custom image
        >>> lgtm = LgtmStackContainer("grafana/otel-lgtm:0.4.0")
        >>> lgtm.start()
        >>> prometheus_url = lgtm.get_prometheus_http_url()

    Supported image:
        - grafana/otel-lgtm
    """

    # Default configuration
    DEFAULT_IMAGE = "grafana/otel-lgtm:latest"
    GRAFANA_PORT = 3000
    OTLP_GRPC_PORT = 4317
    OTLP_HTTP_PORT = 4318
    LOKI_PORT = 3100
    TEMPO_PORT = 3200
    PROMETHEUS_PORT = 9090

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Grafana LGTM Stack container.

        Args:
            image: Docker image name (default: grafana/otel-lgtm:latest)
        """
        super().__init__(image)

        self._grafana_port = self.GRAFANA_PORT
        self._tempo_port = self.TEMPO_PORT
        self._loki_port = self.LOKI_PORT
        self._otlp_grpc_port = self.OTLP_GRPC_PORT
        self._otlp_http_port = self.OTLP_HTTP_PORT
        self._prometheus_port = self.PROMETHEUS_PORT

        # Expose all ports
        self.with_exposed_ports(
            self._grafana_port,
            self._tempo_port,
            self._loki_port,
            self._otlp_grpc_port,
            self._otlp_http_port,
            self._prometheus_port
        )

        # Wait for LGTM stack to be ready
        self.waiting_for(
            LogMessageWaitStrategy(
                ".*The OpenTelemetry collector and the Grafana LGTM stack are up and running.*\\s",
                count=1
            )
        )

    def start(self) -> LgtmStackContainer:
        """
        Start the container and log access information.

        Returns:
            This container instance
        """
        super().start()
        logger.info("Access to the Grafana dashboard: %s", self.get_grafana_http_url())
        return self

    def get_otlp_grpc_url(self) -> str:
        """
        Get the OpenTelemetry gRPC endpoint URL.

        Returns:
            OTLP gRPC URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._otlp_grpc_port)}"

    def get_tempo_url(self) -> str:
        """
        Get the Tempo traces endpoint URL.

        Returns:
            Tempo URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._tempo_port)}"

    def get_loki_url(self) -> str:
        """
        Get the Loki logs endpoint URL.

        Returns:
            Loki URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._loki_port)}"

    def get_otlp_http_url(self) -> str:
        """
        Get the OpenTelemetry HTTP endpoint URL.

        Returns:
            OTLP HTTP URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._otlp_http_port)}"

    def get_prometheus_http_url(self) -> str:
        """
        Get the Prometheus metrics endpoint URL.

        Returns:
            Prometheus URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._prometheus_port)}"

    def get_grafana_http_url(self) -> str:
        """
        Get the Grafana dashboard URL.

        Returns:
            Grafana URL in format: http://host:port
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self._grafana_port)}"
