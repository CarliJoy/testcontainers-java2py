"""
Couchbase database container implementation.

This module provides a container for Couchbase NoSQL databases.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchbase/src/main/java/org/testcontainers/couchbase/CouchbaseContainer.java
"""

from __future__ import annotations

from enum import Enum
from typing import Set

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy
from testcontainers.waiting.strategy import WaitingStrategy


class CouchbaseService(Enum):
    """
    Couchbase services that can be enabled.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchbase/src/main/java/org/testcontainers/couchbase/CouchbaseService.java
    """

    KV = ("kv", 256)
    QUERY = ("n1ql", 0)
    SEARCH = ("fts", 256)
    INDEX = ("index", 256)
    ANALYTICS = ("cbas", 1024)
    EVENTING = ("eventing", 256)

    def __init__(self, identifier: str, minimum_quota_mb: int):
        self._identifier = identifier
        self._minimum_quota_mb = minimum_quota_mb

    @property
    def identifier(self) -> str:
        """Get the internal service identifier."""
        return self._identifier

    @property
    def minimum_quota_mb(self) -> int:
        """Get the minimum quota for the service in MB."""
        return self._minimum_quota_mb

    def has_quota(self) -> bool:
        """Check if the service has a quota that needs to be applied."""
        return self._minimum_quota_mb > 0


class BucketDefinition:
    """
    Configuration for a Couchbase bucket.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchbase/src/main/java/org/testcontainers/couchbase/BucketDefinition.java
    """

    def __init__(self, name: str):
        """
        Initialize a bucket definition.

        Args:
            name: The name of the bucket
        """
        self.name = name
        self.flush_enabled = False
        self.query_primary_index = True
        self.quota = 100
        self.num_replicas = 0

    def with_replicas(self, num_replicas: int) -> BucketDefinition:
        """
        Configure the number of replicas (defaults to 0).

        Args:
            num_replicas: Number of replicas (0-3)

        Returns:
            This bucket definition for method chaining
        """
        if num_replicas < 0 or num_replicas > 3:
            raise ValueError("The number of replicas must be between 0 and 3 (inclusive)")
        self.num_replicas = num_replicas
        return self

    def with_flush_enabled(self, flush_enabled: bool) -> BucketDefinition:
        """
        Enable or disable flush for this bucket.

        Args:
            flush_enabled: If True, the bucket can be flushed

        Returns:
            This bucket definition for method chaining
        """
        self.flush_enabled = flush_enabled
        return self

    def with_quota(self, quota: int) -> BucketDefinition:
        """
        Set a custom bucket quota (100MiB by default).

        Args:
            quota: The quota in mebibytes (MiB)

        Returns:
            This bucket definition for method chaining
        """
        if quota < 100:
            raise ValueError("Bucket quota cannot be less than 100MiB!")
        self.quota = quota
        return self

    def with_primary_index(self, create: bool) -> BucketDefinition:
        """
        Enable or disable creating a primary index.

        Args:
            create: If False, a primary index will not be created

        Returns:
            This bucket definition for method chaining
        """
        self.query_primary_index = create
        return self


class CouchbaseContainer(GenericContainer):
    """
    Couchbase NoSQL database container.

    This container starts a Couchbase database instance with configurable
    services, credentials, and buckets.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/couchbase/src/main/java/org/testcontainers/couchbase/CouchbaseContainer.java

    Supported image: couchbase/server

    Exposed ports (depending on enabled services):
    - Console: 8091, 18091 (SSL)
    - Key-Value: 11210, 11207 (SSL)
    - View: 8092, 18092 (SSL)
    - Query: 8093, 18093 (SSL)
    - Search: 8094, 18094 (SSL)
    - Analytics: 8095, 18095 (SSL)
    - Eventing: 8096, 18096 (SSL)

    Note: The container setup is complex and involves HTTP API calls to configure
    the cluster. This Python implementation provides the basic container setup
    but does not include all the advanced configuration logic from the Java version.

    Example:
        >>> with CouchbaseContainer() as couchbase:
        ...     conn_str = couchbase.get_connection_string()
        ...     username = couchbase.get_username()
        ...     password = couchbase.get_password()
        ...     # Connect to Couchbase

        >>> # Custom configuration
        >>> from testcontainers.modules.couchbase import CouchbaseService
        >>> couchbase = CouchbaseContainer("couchbase/server:latest")
        >>> couchbase.with_credentials("admin", "password123")
        >>> couchbase.with_enabled_services(
        ...     CouchbaseService.KV,
        ...     CouchbaseService.QUERY,
        ...     CouchbaseService.INDEX
        ... )
        >>> couchbase.start()
    """

    DEFAULT_IMAGE = "couchbase/server"
    MGMT_PORT = 8091
    MGMT_SSL_PORT = 18091
    VIEW_PORT = 8092
    VIEW_SSL_PORT = 18092
    QUERY_PORT = 8093
    QUERY_SSL_PORT = 18093
    SEARCH_PORT = 8094
    SEARCH_SSL_PORT = 18094
    ANALYTICS_PORT = 8095
    ANALYTICS_SSL_PORT = 18095
    EVENTING_PORT = 8096
    EVENTING_SSL_PORT = 18096
    KV_PORT = 11210
    KV_SSL_PORT = 11207

    DEFAULT_USERNAME = "Administrator"
    DEFAULT_PASSWORD = "password"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Couchbase container.

        Args:
            image: Docker image name (default: couchbase/server)
        """
        super().__init__(image)

        self._username = self.DEFAULT_USERNAME
        self._password = self.DEFAULT_PASSWORD
        self._enabled_services: Set[CouchbaseService] = {
            CouchbaseService.KV,
            CouchbaseService.QUERY,
            CouchbaseService.SEARCH,
            CouchbaseService.INDEX,
        }
        self._buckets: list[BucketDefinition] = []
        self._custom_service_quotas: dict[CouchbaseService, int] = {}

        self._configure_ports()
        self._configure_wait_strategy()

    def _configure_ports(self) -> None:
        """Configure exposed ports based on enabled services."""
        # Management ports are always exposed
        self.with_exposed_ports(self.MGMT_PORT, self.MGMT_SSL_PORT)

        # Add ports for enabled services
        if CouchbaseService.KV in self._enabled_services:
            self.with_exposed_ports(self.KV_PORT, self.KV_SSL_PORT)
            self.with_exposed_ports(self.VIEW_PORT, self.VIEW_SSL_PORT)

        if CouchbaseService.QUERY in self._enabled_services:
            self.with_exposed_ports(self.QUERY_PORT, self.QUERY_SSL_PORT)

        if CouchbaseService.SEARCH in self._enabled_services:
            self.with_exposed_ports(self.SEARCH_PORT, self.SEARCH_SSL_PORT)

        if CouchbaseService.ANALYTICS in self._enabled_services:
            self.with_exposed_ports(self.ANALYTICS_PORT, self.ANALYTICS_SSL_PORT)

        if CouchbaseService.EVENTING in self._enabled_services:
            self.with_exposed_ports(self.EVENTING_PORT, self.EVENTING_SSL_PORT)

    def _configure_wait_strategy(self) -> None:
        """Configure wait strategy to check cluster health."""
        # Wait for management API to be ready
        wait_strategy = HttpWaitStrategy().for_path("/pools").for_port(self.MGMT_PORT).for_status_code(200)

        self.waiting_for(wait_strategy)

    def with_credentials(self, username: str, password: str) -> CouchbaseContainer:
        """
        Set custom username and password for the admin user.

        Args:
            username: The admin username
            password: The admin password

        Returns:
            This container instance for method chaining
        """
        self._username = username
        self._password = password
        return self

    def with_bucket(self, bucket_definition: BucketDefinition) -> CouchbaseContainer:
        """
        Add a bucket to be created on container startup.

        Args:
            bucket_definition: The bucket configuration

        Returns:
            This container instance for method chaining
        """
        self._buckets.append(bucket_definition)
        return self

    def with_enabled_services(self, *services: CouchbaseService) -> CouchbaseContainer:
        """
        Configure which services to enable.

        Args:
            services: Services to enable

        Returns:
            This container instance for method chaining
        """
        self._enabled_services = set(services)
        self._configure_ports()
        self._configure_wait_strategy()
        return self

    def with_service_quota(self, service: CouchbaseService, quota_mb: int) -> CouchbaseContainer:
        """
        Configure a custom memory quota for a service.

        Args:
            service: The service to configure
            quota_mb: The memory quota in MB

        Returns:
            This container instance for method chaining
        """
        if not service.has_quota():
            raise ValueError(f"The provided service ({service}) has no quota to configure")
        if quota_mb < service.minimum_quota_mb:
            raise ValueError(
                f"The custom quota ({quota_mb}) must not be smaller than "
                f"the minimum quota for the service ({service.minimum_quota_mb})"
            )
        self._custom_service_quotas[service] = quota_mb
        return self

    def get_username(self) -> str:
        """
        Get the configured username.

        Returns:
            The username
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the configured password.

        Returns:
            The password
        """
        return self._password

    def get_bootstrap_carrier_direct_port(self) -> int:
        """
        Get the mapped Key-Value port.

        Returns:
            Mapped KV port number
        """
        return self.get_mapped_port(self.KV_PORT)

    def get_bootstrap_http_direct_port(self) -> int:
        """
        Get the mapped management port.

        Returns:
            Mapped management port number
        """
        return self.get_mapped_port(self.MGMT_PORT)

    def get_connection_string(self) -> str:
        """
        Get the Couchbase connection string.

        Returns:
            Connection string in format: couchbase://host:port
        """
        return f"couchbase://{self.get_host()}:{self.get_bootstrap_carrier_direct_port()}"
