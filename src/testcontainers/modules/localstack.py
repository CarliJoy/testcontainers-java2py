"""
LocalStack AWS cloud emulation container wrapper.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/localstack/src/main/java/org/testcontainers/localstack/LocalStackContainer.java
"""

from __future__ import annotations

import re

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy


class LocalStackContainer(GenericContainer):
    """
    Wrapper for LocalStack AWS service emulation (version 0.11.2).

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/localstack/src/main/java/org/testcontainers/localstack/LocalStackContainer.java
    """

    PORT = 4566
    DEFAULT_IMAGE = "localstack/localstack:0.11.2"
    DEFAULT_REGION = "us-east-1"
    DEFAULT_ACCESS_KEY_ID = "test"
    DEFAULT_SECRET_ACCESS_KEY = "test"
    STARTER_SCRIPT = "/tmp/localstack_boot.sh"

    def __init__(self, image: str = DEFAULT_IMAGE):
        super().__init__(image)

        # Extract version from image tag
        version = self._extract_version(image)

        # Determine mode based on version
        self._legacy_mode = self._should_run_in_legacy_mode(version)
        self._services_env_var_required = self._is_services_env_var_required(version)
        self._is_version_2 = self._is_version_2(version)

        # Service enablement
        self._enabled_services = []

        # CRITICAL: Bind Docker socket for Lambda/ECS/Docker-in-Docker support
        # This matches Java implementation line 61
        docker_socket = "/var/run/docker.sock"
        self.with_bind(docker_socket, docker_socket)

        # Configure starter script mechanism (Java lines 63-69)
        # This ensures LocalStack starts with proper configuration
        self.with_command(
            "sh",
            "-c",
            f"while [ ! -f {self.STARTER_SCRIPT} ]; do sleep 0.1; done; {self.STARTER_SCRIPT}"
        )

        # Expose port
        self.with_exposed_ports(self.PORT)

        # Wait for startup message
        self.waiting_for(LogMessageWaitStrategy().with_regex(r".*Ready\.\n"))

    def _extract_version(self, image: str) -> str:
        """Extract version tag from image name."""
        if ":" in image:
            return image.split(":")[-1]
        return "0.11.2"

    def _should_run_in_legacy_mode(self, version: str) -> bool:
        """Check if version requires legacy mode (< 0.11)."""
        if version == "latest" or version.startswith("latest-") or version.endswith("-latest"):
            return False

        if self._is_semantic_version(version):
            return self._compare_version(version, "0.11") < 0

        return True

    def _is_services_env_var_required(self, version: str) -> bool:
        """Check if version requires SERVICES env var (< 0.13)."""
        if version == "latest":
            return False

        if self._is_semantic_version(version):
            return self._compare_version(version, "0.13") < 0

        return True

    def _is_version_2(self, version: str) -> bool:
        """Check if version is 2.x or later."""
        if version == "latest":
            return True

        if self._is_semantic_version(version):
            return self._compare_version(version, "2.0.0") >= 0

        return False

    def _is_semantic_version(self, version: str) -> bool:
        """Check if version string is semantic."""
        return bool(re.match(r'^\d+\.\d+', version))

    def _compare_version(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        def normalize(v):
            parts = re.match(r'^(\d+)\.(\d+)(?:\.(\d+))?', v)
            if parts:
                return [int(parts.group(1)), int(parts.group(2)), int(parts.group(3) or 0)]
            return [0, 0, 0]

        v1_parts = normalize(v1)
        v2_parts = normalize(v2)

        for i in range(3):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        return 0

    def with_services(self, *service_names: str) -> LocalStackContainer:
        """Specify which AWS services to activate."""
        self._enabled_services.extend(service_names)
        return self

    def _configure(self) -> None:
        super()._configure()

        # Validate services if required
        if self._services_env_var_required and not self._enabled_services:
            raise ValueError("services list must not be empty")

        # Apply service list if specified
        if self._enabled_services:
            service_str = ",".join(self._enabled_services)
            self.with_env("SERVICES", service_str)
            if self._services_env_var_required:
                self.with_env("EAGER_SERVICE_LOADING", "1")

        # Set hostname environment variable based on version
        if self._is_version_2:
            self._resolve_hostname("LOCALSTACK_HOST")
        else:
            self._resolve_hostname("HOSTNAME_EXTERNAL")

        # Expose ports
        self._expose_ports()

    def _resolve_hostname(self, env_var: str) -> None:
        """Set hostname environment variable if not already set."""
        if env_var not in self.env:
            self.with_env(env_var, self.get_host())

    def _expose_ports(self) -> None:
        """Expose appropriate ports based on mode."""
        if self._legacy_mode:
            # Legacy mode exposes individual service ports (not implemented here)
            self.with_exposed_ports(self.PORT)
        else:
            self.with_exposed_ports(self.PORT)

    def get_endpoint(self) -> str:
        """Build edge service endpoint URL."""
        host = self.get_host()
        port = self.get_mapped_port(self.PORT)
        return f"http://{host}:{port}"

    def get_access_key(self) -> str:
        """Retrieve AWS access key."""
        return self.env.get("AWS_ACCESS_KEY_ID", self.DEFAULT_ACCESS_KEY_ID)

    def get_secret_key(self) -> str:
        """Retrieve AWS secret key."""
        return self.env.get("AWS_SECRET_ACCESS_KEY", self.DEFAULT_SECRET_ACCESS_KEY)

    def get_region(self) -> str:
        """Retrieve AWS region."""
        return self.env.get("DEFAULT_REGION", self.DEFAULT_REGION)
