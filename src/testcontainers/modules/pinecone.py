"""
Pinecone Local container module.

Pinecone is a vector database for AI applications.

Example:
    
    .. code-block:: python

        from testcontainers.modules.pinecone import PineconeLocalContainer

        with PineconeLocalContainer() as pinecone:
            endpoint = pinecone.get_endpoint()
            # Use the endpoint to connect to Pinecone

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/modules/pinecone/src/main/java/org/testcontainers/pinecone/PineconeLocalContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer


class PineconeLocalContainer(GenericContainer):
    """
    Pinecone Local container.

    Example:

        .. code-block:: python

            from testcontainers.modules.pinecone import PineconeLocalContainer

            with PineconeLocalContainer() as pinecone:
                endpoint = pinecone.get_endpoint()
    """

    def __init__(self, image: str = "ghcr.io/pinecone-io/pinecone-local:latest", **kwargs) -> None:
        super().__init__(image=image, **kwargs)
        self.port = 5080
        self.with_exposed_ports(self.port)
        self.with_env("PORT", str(self.port))

    def get_endpoint(self) -> str:
        """
        Get the HTTP endpoint for Pinecone Local.

        Returns:
            str: HTTP endpoint URL
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"
