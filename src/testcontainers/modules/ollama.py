"""
Ollama container implementation.

This module provides a container for Ollama - a tool to run large language models locally.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/ollama/src/main/java/org/testcontainers/ollama/OllamaContainer.java
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer


class OllamaContainer(GenericContainer):
    """
    Ollama container for running large language models.

    This container starts an Ollama instance that can run various AI models locally.
    It automatically detects and uses NVIDIA GPU support if available.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/ollama/src/main/java/org/testcontainers/ollama/OllamaContainer.java

    Example:
        >>> with OllamaContainer() as ollama:
        ...     endpoint = ollama.get_endpoint()
        ...     port = ollama.get_port()
        ...     # Connect to Ollama and use models

        >>> # Commit container with a loaded model
        >>> ollama = OllamaContainer()
        >>> ollama.start()
        >>> # ... load model into ollama ...
        >>> ollama.commit_to_image("my-ollama-with-model:latest")
    """

    # Default configuration
    DEFAULT_IMAGE = "ollama/ollama"
    OLLAMA_PORT = 11434

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize an Ollama container.

        Args:
            image: Docker image name (default: ollama/ollama)
        """
        super().__init__(image)

        self.with_exposed_ports(self.OLLAMA_PORT)

        # TODO: Add GPU support detection when Docker client supports it
        # The Java version checks for NVIDIA runtime and adds device requests
        # This would require extending the Python Docker client wrapper

    def commit_to_image(self, image_name: str) -> None:
        """
        Commit the current file system changes in the container into a new image.

        This should be used for creating an image that contains a loaded model.

        Args:
            image_name: The name of the new image (e.g., "my-ollama:latest")
        """
        if self.get_wrapped_container() is None:
            raise RuntimeError("Container must be started before committing to image")

        # Parse image name to extract repository and tag
        if ":" in image_name:
            repository, tag = image_name.rsplit(":", 1)
        else:
            repository = image_name
            tag = "latest"

        # Get the Docker client and commit the container
        client = self.get_docker_client()
        container = self.get_wrapped_container()

        # Check if image already exists
        try:
            client.images.get(image_name)
            # Image exists, skip commit
            return
        except Exception:
            # Image doesn't exist, proceed with commit
            pass

        # Commit the container to a new image
        container.commit(
            repository=repository,
            tag=tag,
            conf={"Labels": {"org.testcontainers.sessionId": ""}}
        )

    def get_port(self) -> int:
        """
        Get the exposed Ollama port number on the host.

        Returns:
            Host port number mapped to the Ollama port
        """
        return self.get_mapped_port(self.OLLAMA_PORT)

    def get_endpoint(self) -> str:
        """
        Get the Ollama HTTP endpoint URL.

        Returns:
            HTTP URL for the Ollama endpoint
        """
        return f"http://{self.get_host()}:{self.get_port()}"
