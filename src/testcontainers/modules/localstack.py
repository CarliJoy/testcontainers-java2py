"""LocalStack AWS cloud emulation container wrapper."""

from __future__ import annotations
from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class LocalStackContainer(GenericContainer):
    """Wrapper for LocalStack AWS service emulation (version 0.11.2)."""

    def __init__(self, image: str = "localstack/localstack:0.11.2"):
        super().__init__(image)
        
        # Edge service port (unified endpoint)
        self._edge_port = 4566
        
        # Service enablement
        self._enabled_services = []
        
        # AWS config defaults
        self._region = "us-east-1"
        self._access_key = "test"
        self._secret_key = "test"
        
        self.with_exposed_ports(self._edge_port)
        
        # Wait for startup message
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*Ready\.\n"))

    def with_services(self, *service_names: str) -> LocalStackContainer:
        """Specify which AWS services to activate."""
        self._enabled_services.extend(service_names)
        return self

    def _configure(self) -> None:
        # Apply service list if specified
        if self._enabled_services:
            service_str = ",".join(self._enabled_services)
            self.with_env("SERVICES", service_str)

    def get_url(self) -> str:
        """Build edge service endpoint URL."""
        return f"http://{self.get_host()}:{self.get_mapped_port(self._edge_port)}"

    def get_port(self) -> int:
        """Retrieve mapped edge port."""
        return self.get_mapped_port(self._edge_port)
    
    def get_region(self) -> str:
        """Retrieve AWS region."""
        return self._region
    
    def get_access_key(self) -> str:
        """Retrieve AWS access key."""
        return self._access_key
    
    def get_secret_key(self) -> str:
        """Retrieve AWS secret key."""
        return self._secret_key
