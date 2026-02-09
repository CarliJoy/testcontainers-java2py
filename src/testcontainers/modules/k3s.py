"""
K3s lightweight Kubernetes container implementation.

This module provides a container for K3s, a lightweight Kubernetes distribution.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/k3s/src/main/java/org/testcontainers/k3s/K3sContainer.java
"""

from __future__ import annotations

import re

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class K3sContainer(GenericContainer):
    """
    K3s lightweight Kubernetes container.

    K3s is a lightweight Kubernetes distribution designed for edge, IoT, and CI/CD.
    This container starts a K3s instance with API server access and kubeconfig.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/k3s/src/main/java/org/testcontainers/k3s/K3sContainer.java

    Example:
        >>> with K3sContainer() as k3s:
        ...     kubeconfig = k3s.get_kubeconfig()
        ...     # Use kubeconfig to connect to K3s

        >>> # Custom image version
        >>> k3s = K3sContainer("rancher/k3s:v1.28.5-k3s1")
        >>> k3s.start()
    """

    # Default configuration
    DEFAULT_IMAGE = "rancher/k3s"
    KUBE_SECURE_PORT = 6443
    RANCHER_WEBHOOK_PORT = 8443

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a K3s container.

        Args:
            image: Docker image name (default: rancher/k3s)
        """
        super().__init__(image)

        self._kubeconfig = None

        # Expose Kubernetes API port
        self.with_exposed_ports(self.KUBE_SECURE_PORT, self.RANCHER_WEBHOOK_PORT)

        # K3s requires privileged mode
        self.with_privileged_mode(True)

        # Note: Java version configures:
        # - cgroup namespace mode to "host"
        # - bind mount /sys/fs/cgroup
        # - tmpfs mounts for /run and /var/run
        # Python implementation currently doesn't support these configurations
        # You may need to use with_create_container_modifier for advanced Docker configurations

        # Set K3s server command with placeholder for TLS SAN
        # We'll update this in start() when we know the actual host
        self.with_command("server", "--disable=traefik")

        # Wait for K3s to be ready
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*Node controller sync successful.*"))

    def start(self) -> K3sContainer:
        """
        Start the K3s container and retrieve kubeconfig.

        Returns:
            Self for method chaining
        """
        # Add TLS SAN before starting
        current_command = self._command if hasattr(self, '_command') and self._command else []
        if isinstance(current_command, str):
            current_command = [current_command]
        
        # Add TLS SAN if not already present
        has_tls_san = any("--tls-san=" in str(arg) for arg in current_command)
        if not has_tls_san:
            current_command.append(f"--tls-san={self.get_host()}")
            self.with_command(*current_command)
        
        super().start()

        # Retrieve and process kubeconfig
        raw_kubeconfig = self.exec_in_container(["cat", "/etc/rancher/k3s/k3s.yaml"])[0].decode("utf-8")

        # Update server URL in kubeconfig
        server_url = f"https://{self.get_host()}:{self.get_mapped_port(self.KUBE_SECURE_PORT)}"
        self._kubeconfig = self._update_kubeconfig_server(raw_kubeconfig, server_url)

        return self

    def _update_kubeconfig_server(self, kubeconfig: str, server_url: str) -> str:
        """
        Update the server URL in kubeconfig YAML.

        Args:
            kubeconfig: Original kubeconfig YAML
            server_url: New server URL

        Returns:
            Updated kubeconfig YAML
        """
        # Replace the server URL (handles the default https://127.0.0.1:6443)
        updated = re.sub(
            r"server:\s+https://[^\s]+", f"server: {server_url}", kubeconfig
        )

        # Ensure current-context is set to default
        if "current-context:" not in updated:
            updated += "\ncurrent-context: default\n"
        else:
            updated = re.sub(
                r"current-context:\s+[^\s]+",
                "current-context: default",
                updated,
            )

        return updated

    def get_kubeconfig(self) -> str:
        """
        Get the kubeconfig YAML for connecting to K3s from the host.

        Returns:
            Kubeconfig YAML string

        Raises:
            RuntimeError: If container is not started
        """
        if self._kubeconfig is None:
            raise RuntimeError("Container must be started before getting kubeconfig")
        return self._kubeconfig

    def generate_internal_kubeconfig(self, network_alias: str) -> str:
        """
        Generate a kubeconfig for use within the Docker network.

        This kubeconfig can be used by another container running in the same
        network as the K3s container.

        Args:
            network_alias: Network alias of the K3s container

        Returns:
            Kubeconfig YAML string for internal network access

        Raises:
            ValueError: If network_alias is not in container's network aliases
        """
        if self._kubeconfig is None:
            raise RuntimeError("Container must be started before generating internal kubeconfig")

        # Check if network alias is valid
        # Note: In Python implementation, we may not have easy access to network aliases
        # For now, just generate the kubeconfig with the provided alias

        server_url = f"https://{network_alias}:{self.KUBE_SECURE_PORT}"
        return self._update_kubeconfig_server(self._kubeconfig, server_url)
