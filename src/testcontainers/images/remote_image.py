"""
Remote Docker image handling.

This module provides functionality for pulling Docker images from registries.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Optional

from docker import DockerClient
from docker.errors import ImageNotFound, APIError

from testcontainers.core.docker_client import DockerClientFactory
from testcontainers.images.image_pull_policy import ImagePullPolicy
from testcontainers.images.pull_policy import PullPolicy
from testcontainers.images.substitutor import get_image_name_substitutor

logger = logging.getLogger(__name__)


class RemoteDockerImage:
    """
    Represents a Docker image that may need to be pulled from a registry.
    
    This class handles the logic for determining whether to pull an image
    and performing the pull operation.
    """
    
    def __init__(
        self,
        image_name: str,
        pull_policy: Optional[ImagePullPolicy] = None,
        docker_client: Optional[DockerClient] = None,
    ):
        """
        Initialize a remote Docker image.
        
        Args:
            image_name: The Docker image name (e.g., "nginx:latest")
            pull_policy: Policy for determining when to pull (defaults to DefaultPullPolicy)
            docker_client: Docker client to use (defaults to lazy client)
        """
        # Apply image name substitution
        substitutor = get_image_name_substitutor()
        self._image_name = substitutor.substitute(image_name)
        
        if self._image_name != image_name:
            logger.info(f"Image name substituted: {image_name} -> {self._image_name}")
        
        self._pull_policy = pull_policy or PullPolicy.default_policy()
        self._docker_client = docker_client or DockerClientFactory.lazy_client()
        self._resolved_image_name: Optional[str] = None
    
    @property
    def image_name(self) -> str:
        """Get the image name."""
        return self._image_name
    
    def with_pull_policy(self, pull_policy: ImagePullPolicy) -> RemoteDockerImage:
        """
        Set the pull policy (fluent API).
        
        Args:
            pull_policy: The pull policy to use
            
        Returns:
            This RemoteDockerImage instance
        """
        self._pull_policy = pull_policy
        return self
    
    def resolve(self, pull_timeout: timedelta = timedelta(seconds=300)) -> str:
        """
        Resolve the image, pulling if necessary.
        
        Args:
            pull_timeout: Maximum time to wait for image pull
            
        Returns:
            The canonical image name
            
        Raises:
            TimeoutError: If pull takes longer than timeout
            Exception: If pull fails
        """
        if self._resolved_image_name is not None:
            return self._resolved_image_name
        
        # Check if we should pull
        if not self._pull_policy.should_pull(self._image_name):
            self._resolved_image_name = self._image_name
            return self._resolved_image_name
        
        # Pull the image
        logger.info(
            f"Pulling docker image: {self._image_name}. "
            f"Please be patient; this may take some time but only needs to be done once."
        )
        
        start_time = time.time()
        timeout_seconds = pull_timeout.total_seconds()
        
        try:
            # Attempt to pull the image
            self._pull_image(timeout_seconds)
            
            elapsed = time.time() - start_time
            logger.info(f"Image {self._image_name} pull took {elapsed:.2f} seconds")
            
            self._resolved_image_name = self._image_name
            return self._resolved_image_name
            
        except Exception as e:
            logger.error(
                f"Failed to pull image: {self._image_name}. "
                f"Please check output of `docker pull {self._image_name}`",
                exc_info=e
            )
            raise
    
    def _pull_image(self, timeout_seconds: float) -> None:
        """
        Pull the image with retry logic.
        
        Args:
            timeout_seconds: Maximum time to wait
            
        Raises:
            TimeoutError: If pull takes longer than timeout
            Exception: If pull fails
        """
        start_time = time.time()
        retry_delay = 0.05  # Start with 50ms
        max_retry_delay = 30.0  # Max 30 seconds between retries
        
        last_exception = None
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Parse image name and tag
                if ':' in self._image_name:
                    repository, tag = self._image_name.rsplit(':', 1)
                else:
                    repository = self._image_name
                    tag = 'latest'
                
                # Pull the image
                self._docker_client.images.pull(repository, tag=tag)
                return  # Success!
                
            except (APIError, ImageNotFound) as e:
                last_exception = e
                
                # Log retry
                remaining = timeout_seconds - (time.time() - start_time)
                logger.warning(
                    f"Retrying pull for image: {self._image_name} "
                    f"({remaining:.0f}s remaining)"
                )
                
                # Wait before retry with exponential backoff
                time.sleep(min(retry_delay, remaining))
                retry_delay = min(retry_delay * 2, max_retry_delay)
        
        # Timeout
        raise TimeoutError(
            f"Timed out pulling image: {self._image_name} after {timeout_seconds}s"
        ) from last_exception
    
    def __str__(self) -> str:
        """String representation."""
        if self._resolved_image_name:
            return self._resolved_image_name
        return f"<resolving: {self._image_name}>"
    
    def __repr__(self) -> str:
        """Repr representation."""
        return f"RemoteDockerImage({self._image_name!r})"
