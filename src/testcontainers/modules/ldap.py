"""
LLDAP container implementation.

This module provides a container for LLDAP (Light LDAP) authentication service.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/ldap/src/main/java/org/testcontainers/ldap/LLdapContainer.java
"""

from __future__ import annotations

import logging

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy

logger = logging.getLogger(__name__)


class LLdapContainer(GenericContainer):
    """
    LLDAP (Light LDAP) authentication service container.

    This container starts an LLDAP server with LDAP protocol and web UI.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/ldap/src/main/java/org/testcontainers/ldap/LLdapContainer.java

    Example:
        >>> with LLdapContainer() as ldap:
        ...     ldap_url = ldap.get_ldap_url()
        ...     user = ldap.get_user()
        ...     password = ldap.get_password()
        ...     # Connect to LDAP

        >>> # With custom configuration
        >>> ldap = LLdapContainer("lldap/lldap:latest")
        >>> ldap.with_base_dn("dc=mycompany,dc=com")
        >>> ldap.with_user_pass("secret123")
        >>> ldap.start()

    Supported image:
        - lldap/lldap
    """

    # Default configuration
    DEFAULT_IMAGE = "lldap/lldap:latest"
    LDAP_PORT = 3890
    LDAPS_PORT = 6360
    UI_PORT = 17170

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a LLDAP container.

        Args:
            image: Docker image name (default: lldap/lldap:latest)
        """
        super().__init__(image)

        self._ldap_port = self.LDAP_PORT
        self._ldaps_port = self.LDAPS_PORT
        self._ui_port = self.UI_PORT

        # Expose LDAP and UI ports
        self.with_exposed_ports(self._ldap_port, self._ui_port)

        # Wait for LLDAP to be ready
        self.waiting_for(
            HttpWaitStrategy()
            .for_path("/health")
            .for_port(self._ui_port)
            .for_status_code(200)
        )

    def start(self) -> LLdapContainer:
        """
        Start the container and log UI information.

        Returns:
            This container instance
        """
        super().start()
        logger.info(
            "LLDAP container is ready! UI available at http://%s:%s",
            self.get_host(),
            self.get_mapped_port(self._ui_port)
        )
        return self

    def with_base_dn(self, base_dn: str) -> LLdapContainer:
        """
        Set the LDAP base DN.

        Args:
            base_dn: Base DN for LDAP (e.g., "dc=example,dc=com")

        Returns:
            This container instance
        """
        self.with_env("LLDAP_LDAP_BASE_DN", base_dn)
        return self

    def with_user_pass(self, user_pass: str) -> LLdapContainer:
        """
        Set the admin user password.

        Args:
            user_pass: Password for admin user

        Returns:
            This container instance
        """
        self.with_env("LLDAP_LDAP_USER_PASS", user_pass)
        return self

    def get_ldap_port(self) -> int:
        """
        Get the exposed LDAP port number on the host.

        Returns:
            Host port number mapped to the LDAP port (LDAP or LDAPS)
        """
        ldaps_enabled = self._env.get("LLDAP_LDAPS_OPTIONS__ENABLED", "false") == "true"
        port = self._ldaps_port if ldaps_enabled else self._ldap_port
        return self.get_mapped_port(port)

    def get_ldap_url(self) -> str:
        """
        Get the LDAP connection URL.

        Returns:
            LDAP URL in format: ldap://host:port or ldaps://host:port
        """
        ldaps_enabled = self._env.get("LLDAP_LDAPS_OPTIONS__ENABLED", "false") == "true"
        protocol = "ldaps" if ldaps_enabled else "ldap"
        return f"{protocol}://{self.get_host()}:{self.get_ldap_port()}"

    def get_base_dn(self) -> str:
        """
        Get the LDAP base DN.

        Returns:
            Base DN (defaults to "dc=example,dc=com" if not set)
        """
        return self._env.get("LLDAP_LDAP_BASE_DN", "dc=example,dc=com")

    def get_user(self) -> str:
        """
        Get the admin user DN.

        Returns:
            Admin user DN in format: cn=admin,ou=people,<base_dn>
        """
        return f"cn=admin,ou=people,{self.get_base_dn()}"

    def get_password(self) -> str:
        """
        Get the admin user password.

        Returns:
            Admin password (defaults to "password" if not set)
        """
        return self._env.get("LLDAP_LDAP_USER_PASS", "password")
