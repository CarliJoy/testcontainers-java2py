"""Core testcontainers functionality."""

from testcontainers.core.docker_client import DockerClientFactory, DockerClientWrapper
from testcontainers.core.container_types import BindMode, SelinuxContext, InternetProtocol
from testcontainers.core.container import Container, ExecResult
from testcontainers.core.container_state import ContainerState

__all__ = [
    "DockerClientFactory",
    "DockerClientWrapper",
    "BindMode",
    "SelinuxContext", 
    "InternetProtocol",
    "Container",
    "ExecResult",
    "ContainerState",
]

# Import GenericContainer after other modules to avoid circular imports
def __getattr__(name):
    if name == "GenericContainer":
        from testcontainers.core.generic_container import GenericContainer
        return GenericContainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
