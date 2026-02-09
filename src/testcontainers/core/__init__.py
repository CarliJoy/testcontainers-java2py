"""Core testcontainers functionality."""

from testcontainers.core.docker_client import DockerClientFactory, DockerClientWrapper
from testcontainers.core.container_types import BindMode, SelinuxContext, InternetProtocol
from testcontainers.core.container import Container, ExecResult
from testcontainers.core.container_state import ContainerState
from testcontainers.core.network import Network, NetworkImpl, new_network, SHARED

__all__ = [
    "DockerClientFactory",
    "DockerClientWrapper",
    "BindMode",
    "SelinuxContext", 
    "InternetProtocol",
    "Container",
    "ExecResult",
    "ContainerState",
    "Network",
    "NetworkImpl",
    "new_network",
    "SHARED",
]

# Import GenericContainer and SocatContainer after other modules to avoid circular imports
def __getattr__(name):
    if name == "GenericContainer":
        from testcontainers.core.generic_container import GenericContainer
        return GenericContainer
    if name == "SocatContainer":
        from testcontainers.core.socat_container import SocatContainer
        return SocatContainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
