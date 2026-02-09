"""
Vault container implementation.

This module provides a container for HashiCorp Vault secrets management.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/vault/src/main/java/org/testcontainers/containers/VaultContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy


class VaultContainer(GenericContainer):
    """
    HashiCorp Vault secrets management container.

    This container starts a Vault server in development mode with configurable
    root token for secrets management and encryption.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/vault/src/main/java/org/testcontainers/containers/VaultContainer.java

    Example:
        >>> with VaultContainer() as vault:
        ...     url = vault.get_url()
        ...     token = vault.get_token()
        ...     # Connect to Vault

        >>> # With custom root token
        >>> vault = VaultContainer("hashicorp/vault:1.15")
        >>> vault.with_root_token("mytoken")
        >>> vault.start()
        >>> url = vault.get_url()

    Security considerations:
        - Development mode is NOT secure for production
        - Root token provides full access to Vault
        - Use proper Vault setup for production deployments
    """

    # Default configuration
    DEFAULT_IMAGE = "hashicorp/vault:latest"
    DEFAULT_PORT = 8200

    # Default root token
    DEFAULT_ROOT_TOKEN = "root-token"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Vault container.

        Args:
            image: Docker image name (default: hashicorp/vault:latest)
        """
        super().__init__(image)

        self._port = self.DEFAULT_PORT
        self._root_token = self.DEFAULT_ROOT_TOKEN

        # Expose Vault port
        self.with_exposed_ports(self._port)

        # Set command for dev mode
        self.with_command(["vault", "server", "-dev"])

        # Set environment variables
        self.with_env("VAULT_DEV_ROOT_TOKEN_ID", self._root_token)
        self.with_env("VAULT_DEV_LISTEN_ADDRESS", f"0.0.0.0:{self._port}")

        # Disable mlock in dev mode (alternative to IPC_LOCK capability)
        self.with_env("SKIP_SETCAP", "true")

        # Wait for Vault to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/v1/sys/health")
            .for_status_code_matching(lambda code: code in [200, 429, 472, 473])
        )

    def with_root_token(self, token: str) -> VaultContainer:
        """
        Set the Vault root token (fluent API).

        Args:
            token: Root token for Vault authentication

        Returns:
            This container instance

        Security note:
            Store tokens securely and rotate regularly
        """
        self._root_token = token
        self.with_env("VAULT_DEV_ROOT_TOKEN_ID", token)
        return self

    def get_url(self) -> str:
        """
        Get the Vault API URL.

        Returns:
            API URL in format: http://host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._port)
        return f"http://{host}:{port}"

    def get_token(self) -> str:
        """
        Get the Vault root token.

        Returns:
            Root token for authentication
        """
        return self._root_token

    def get_port(self) -> int:
        """
        Get the exposed Vault port number on the host.

        Returns:
            Host port number mapped to the Vault port
        """
        return self.get_mapped_port(self._port)
