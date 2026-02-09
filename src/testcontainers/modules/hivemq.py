"""
HiveMQ MQTT broker container implementation.

This module provides a container for HiveMQ MQTT broker.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/hivemq/src/main/java/org/testcontainers/hivemq/HiveMQContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class HiveMQContainer(GenericContainer):
    """
    HiveMQ MQTT broker container.

    This container starts a HiveMQ MQTT broker instance with support for
    both Community Edition and Enterprise Edition images.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/hivemq/src/main/java/org/testcontainers/hivemq/HiveMQContainer.java

    Example:
        >>> with HiveMQContainer("hivemq/hivemq-ce:latest") as hivemq:
        ...     mqtt_port = hivemq.get_mqtt_port()
        ...     host = hivemq.get_host()
        ...     # Connect to HiveMQ MQTT broker

        >>> # Enable Control Center
        >>> hivemq = HiveMQContainer("hivemq/hivemq4:latest")
        >>> hivemq.with_control_center()
        >>> hivemq.start()
    """

    # Default images
    DEFAULT_EE_IMAGE = "hivemq/hivemq4"
    DEFAULT_CE_IMAGE = "hivemq/hivemq-ce"

    # Port constants
    MQTT_PORT = 1883
    CONTROL_CENTER_PORT = 8080
    DEBUGGING_PORT = 9000

    def __init__(self, image: str = DEFAULT_CE_IMAGE):
        """
        Initialize a HiveMQ container.

        Args:
            image: Docker image name (default: hivemq/hivemq-ce)
        """
        super().__init__(image)

        # Expose MQTT port
        self.with_exposed_ports(self.MQTT_PORT)

        # Note: Java version uses tmpfs mounts for /opt/hivemq/log, /opt/hivemq/data,
        # and for EE images: /opt/hivemq/audit, /opt/hivemq/backup
        # Python implementation currently doesn't support tmpfs configuration

        # Wait for HiveMQ to be ready
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*Started HiveMQ in.*"))

    def with_control_center(self) -> HiveMQContainer:
        """
        Enable the HiveMQ Control Center.

        Note: Control Center is a HiveMQ 4 Enterprise feature.
        Must be called before the container is started.

        Returns:
            Self for method chaining
        """
        self.with_exposed_ports(self.CONTROL_CENTER_PORT)
        return self

    def with_debugging(self) -> HiveMQContainer:
        """
        Enable remote debugging.

        Must be called before the container is started.

        Returns:
            Self for method chaining
        """
        self.with_exposed_ports(self.DEBUGGING_PORT)
        self.with_env(
            "JAVA_OPTS",
            f"-agentlib:jdwp=transport=dt_socket,address=0.0.0.0:{self.DEBUGGING_PORT},server=y,suspend=y",
        )
        return self

    def get_mqtt_port(self) -> int:
        """
        Get the mapped MQTT port.

        Returns:
            The host port mapped to the MQTT port (1883)
        """
        return self.get_mapped_port(self.MQTT_PORT)

    def get_control_center_port(self) -> int:
        """
        Get the mapped Control Center port.

        Returns:
            The host port mapped to the Control Center port (8080)
        """
        return self.get_mapped_port(self.CONTROL_CENTER_PORT)
