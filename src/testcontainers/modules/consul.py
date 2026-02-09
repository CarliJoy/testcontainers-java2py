"""
Consul container implementation.

This module provides a container for HashiCorp Consul service discovery.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/consul/src/main/java/org/testcontainers/consul/ConsulContainer.java
"""

from __future__ import annotations

import logging

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy

logger = logging.getLogger(__name__)


class ConsulContainer(GenericContainer):
    """
    HashiCorp Consul service discovery container.

    This container starts a Consul agent in development mode with HTTP and gRPC APIs.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/consul/src/main/java/org/testcontainers/consul/ConsulContainer.java

    Example:
        >>> with ConsulContainer() as consul:
        ...     http_port = consul.get_http_port()
        ...     # Connect to Consul

        >>> # With custom commands
        >>> consul = ConsulContainer("hashicorp/consul:1.15")
        >>> consul.with_consul_command("kv put config/testing1 value123")
        >>> consul.start()

    Supported images:
        - hashicorp/consul
        - consul
    """

    # Default configuration
    DEFAULT_IMAGE = "hashicorp/consul:latest"
    CONSUL_HTTP_PORT = 8500
    CONSUL_GRPC_PORT = 8502

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Consul container.

        Args:
            image: Docker image name (default: hashicorp/consul:latest)
        """
        super().__init__(image)

        self._http_port = self.CONSUL_HTTP_PORT
        self._grpc_port = self.CONSUL_GRPC_PORT
        self._init_commands: list[str] = []

        # Expose Consul ports
        self.with_exposed_ports(self._http_port, self._grpc_port)

        # Set environment variables
        self.with_env("CONSUL_ADDR", f"http://0.0.0.0:{self._http_port}")

        # Set command for dev mode
        self.with_command(["agent", "-dev", "-client", "0.0.0.0"])

        # Add IPC_LOCK capability
        def add_ipc_lock_capability(create_kwargs):
            if "host_config" not in create_kwargs:
                create_kwargs["host_config"] = {}
            if "cap_add" not in create_kwargs["host_config"]:
                create_kwargs["host_config"]["cap_add"] = []
            create_kwargs["host_config"]["cap_add"].append("IPC_LOCK")
            return create_kwargs

        self.with_create_container_modifier(add_ipc_lock_capability)

        # Wait for Consul to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/v1/status/leader")
            .for_port(self._http_port)
            .for_status_code(200)
        )

    def start(self) -> ConsulContainer:
        """
        Start the container and run init commands.

        Returns:
            This container instance
        """
        super().start()
        self._run_consul_commands()
        return self

    def _run_consul_commands(self) -> None:
        """Run consul commands after container is started."""
        if not self._init_commands:
            return

        commands = " && ".join([f"consul {cmd}" for cmd in self._init_commands])
        try:
            result = self.exec(["/bin/sh", "-c", commands])
            if result.exit_code != 0:
                logger.error(
                    "Failed to execute init commands %s. Exit code %s. Stdout: %s",
                    self._init_commands,
                    result.exit_code,
                    result.stdout
                )
        except Exception as e:
            logger.error(
                "Failed to execute init commands %s. Exception: %s",
                self._init_commands,
                str(e)
            )

    def with_consul_command(self, *commands: str) -> ConsulContainer:
        """
        Run consul commands using the consul CLI.

        Useful for registering K/V pairs like:
            .with_consul_command("kv put config/testing1 value123")
            .with_consul_command("kv put config/testing2 value456")
        or configuring ACLs:
            .with_consul_command("acl policy create -name test -rules @policy.hcl")

        Args:
            commands: The commands to send to the consul cli

        Returns:
            This container instance
        """
        self._init_commands.extend(commands)
        return self

    def get_http_port(self) -> int:
        """
        Get the exposed Consul HTTP port number on the host.

        Returns:
            Host port number mapped to the Consul HTTP port
        """
        return self.get_mapped_port(self._http_port)

    def get_grpc_port(self) -> int:
        """
        Get the exposed Consul gRPC port number on the host.

        Returns:
            Host port number mapped to the Consul gRPC port
        """
        return self.get_mapped_port(self._grpc_port)
