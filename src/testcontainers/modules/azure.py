"""
Azure Azurite container implementation.

This module provides a container for Azure Azurite storage emulator.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/azure/src/main/java/org/testcontainers/azure/AzuriteContainer.java
"""

from __future__ import annotations

import logging
from typing import Optional

from testcontainers.core.generic_container import GenericContainer

logger = logging.getLogger(__name__)


class AzuriteContainer(GenericContainer):
    """
    Azure Azurite storage emulator container.

    This container starts an Azurite emulator for Azure Blob, Queue, and Table storage.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/azure/src/main/java/org/testcontainers/azure/AzuriteContainer.java

    Example:
        >>> with AzuriteContainer() as azurite:
        ...     connection_string = azurite.get_connection_string()
        ...     # Connect to Azurite

        >>> # With SSL certificate
        >>> from testcontainers.core.file import MountableFile
        >>> azurite = AzuriteContainer("mcr.microsoft.com/azure-storage/azurite:latest")
        >>> azurite.with_ssl(MountableFile("/path/to/cert.pfx"), "password")
        >>> azurite.start()

    Supported image:
        - mcr.microsoft.com/azure-storage/azurite
    """

    # Default configuration
    DEFAULT_IMAGE = "mcr.microsoft.com/azure-storage/azurite:latest"
    DEFAULT_BLOB_PORT = 10000
    DEFAULT_QUEUE_PORT = 10001
    DEFAULT_TABLE_PORT = 10002

    # Well-known account credentials
    WELL_KNOWN_ACCOUNT_NAME = "devstoreaccount1"
    WELL_KNOWN_ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

    CONNECTION_STRING_FORMAT = (
        "DefaultEndpointsProtocol={protocol};AccountName={account_name};AccountKey={account_key};"
        "BlobEndpoint={protocol}://{host}:{blob_port}/{account_name};"
        "QueueEndpoint={protocol}://{host}:{queue_port}/{account_name};"
        "TableEndpoint={protocol}://{host}:{table_port}/{account_name};"
    )

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an Azurite container.

        Args:
            image: Docker image name (default: mcr.microsoft.com/azure-storage/azurite:latest)
        """
        super().__init__(image)

        self._blob_port = self.DEFAULT_BLOB_PORT
        self._queue_port = self.DEFAULT_QUEUE_PORT
        self._table_port = self.DEFAULT_TABLE_PORT

        self._cert_file: Optional[str] = None
        self._cert_extension: Optional[str] = None
        self._key_file: Optional[str] = None
        self._pwd: Optional[str] = None

        # Expose Azurite ports
        self.with_exposed_ports(self._blob_port, self._queue_port, self._table_port)

    def _configure(self) -> None:
        """Configure the container before starting."""
        # Build command line
        command = self._get_command_line()
        self.with_command(command)

        # Copy certificate files if configured
        if self._cert_file:
            logger.info("Using path for cert file: '%s'", self._cert_file)
            self.with_copy_file_to_container(self._cert_file, f"/cert{self._cert_extension}")
            if self._key_file:
                logger.info("Using path for key file: '%s'", self._key_file)
                self.with_copy_file_to_container(self._key_file, "/key.pem")

    def start(self) -> AzuriteContainer:
        """
        Start the container after configuration.

        Returns:
            This container instance
        """
        self._configure()
        super().start()
        return self

    def with_ssl_pfx(self, pfx_cert: str, password: str) -> AzuriteContainer:
        """
        Configure SSL with a PFX certificate and password.

        Args:
            pfx_cert: Path to the PFX certificate file
            password: Password securing the certificate

        Returns:
            This container instance
        """
        self._cert_file = pfx_cert
        self._pwd = password
        self._cert_extension = ".pfx"
        return self

    def with_ssl_pem(self, pem_cert: str, pem_key: str) -> AzuriteContainer:
        """
        Configure SSL with PEM certificate and key files.

        Args:
            pem_cert: Path to the PEM certificate file
            pem_key: Path to the PEM key file

        Returns:
            This container instance
        """
        self._cert_file = pem_cert
        self._key_file = pem_key
        self._cert_extension = ".pem"
        return self

    def get_connection_string(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None
    ) -> str:
        """
        Get the connection string for Azurite.

        Args:
            account_name: Account name (defaults to well-known account)
            account_key: Account key (defaults to well-known key)

        Returns:
            Azure storage connection string
        """
        if account_name is None:
            account_name = self.WELL_KNOWN_ACCOUNT_NAME
        if account_key is None:
            account_key = self.WELL_KNOWN_ACCOUNT_KEY

        protocol = "https" if self._cert_file else "http"

        return self.CONNECTION_STRING_FORMAT.format(
            protocol=protocol,
            account_name=account_name,
            account_key=account_key,
            host=self.get_host(),
            blob_port=self.get_mapped_port(self._blob_port),
            queue_port=self.get_mapped_port(self._queue_port),
            table_port=self.get_mapped_port(self._table_port)
        )

    def _get_command_line(self) -> str:
        """
        Build the Azurite command line.

        Returns:
            Command line string
        """
        args = ["azurite"]
        args.append("--blobHost")
        args.append("0.0.0.0")
        args.append("--queueHost")
        args.append("0.0.0.0")
        args.append("--tableHost")
        args.append("0.0.0.0")

        if self._cert_file:
            args.append("--cert")
            args.append(f"/cert{self._cert_extension}")
            if self._pwd:
                args.append("--pwd")
                args.append(self._pwd)
            else:
                args.append("--key")
                args.append("/key.pem")

        cmd = " ".join(args)
        logger.debug("Using command line: '%s'", cmd)
        return cmd
