"""
Google Cloud emulator containers implementation.

This module provides containers for various Google Cloud service emulators.

Java source:
https://github.com/testcontainers/testcontainers-java/tree/main/modules/gcloud/src/main/java/org/testcontainers/containers
"""

from __future__ import annotations

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.http import HttpWaitStrategy
from testcontainers.waiting.log import LogMessageWaitStrategy


class BigtableEmulatorContainer(GenericContainer):
    """
    Google Cloud Bigtable emulator container.

    This container starts a Bigtable emulator using the Google Cloud SDK.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/BigtableEmulatorContainer.java

    Example:
        >>> with BigtableEmulatorContainer() as bigtable:
        ...     endpoint = bigtable.get_emulator_endpoint()
        ...     port = bigtable.get_emulator_port()
        ...     # Connect to Bigtable emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "gcr.io/google.com/cloudsdktool/google-cloud-cli"
    PORT = 9000

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Bigtable emulator container.

        Args:
            image: Docker image name (default: gcr.io/google.com/cloudsdktool/google-cloud-cli)
        """
        super().__init__(image)

        self.with_exposed_ports(self.PORT)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*running.*$")
        )
        self.with_command("/bin/sh", "-c", "gcloud beta emulators bigtable start --host-port 0.0.0.0:9000")

    def get_emulator_endpoint(self) -> str:
        """
        Get the emulator endpoint.

        Returns:
            Host:port pair for the emulator endpoint
        """
        return f"{self.get_host()}:{self.get_emulator_port()}"

    def get_emulator_port(self) -> int:
        """
        Get the exposed emulator port number on the host.

        Returns:
            Host port number mapped to the emulator port
        """
        return self.get_mapped_port(self.PORT)


class PubSubEmulatorContainer(GenericContainer):
    """
    Google Cloud Pub/Sub emulator container.

    This container starts a Pub/Sub emulator using the Google Cloud SDK.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/PubSubEmulatorContainer.java

    Example:
        >>> with PubSubEmulatorContainer() as pubsub:
        ...     endpoint = pubsub.get_emulator_endpoint()
        ...     # Connect to Pub/Sub emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "gcr.io/google.com/cloudsdktool/google-cloud-cli"
    PORT = 8085

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Pub/Sub emulator container.

        Args:
            image: Docker image name (default: gcr.io/google.com/cloudsdktool/google-cloud-cli)
        """
        super().__init__(image)

        self.with_exposed_ports(self.PORT)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*started.*$")
        )
        self.with_command("/bin/sh", "-c", "gcloud beta emulators pubsub start --host-port 0.0.0.0:8085")

    def get_emulator_endpoint(self) -> str:
        """
        Get the emulator endpoint.

        Returns:
            Host:port pair for the emulator endpoint
        """
        return f"{self.get_host()}:{self.get_mapped_port(self.PORT)}"


class DatastoreEmulatorContainer(GenericContainer):
    """
    Google Cloud Datastore emulator container.

    This container starts a Datastore emulator using the Google Cloud SDK.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/DatastoreEmulatorContainer.java

    Example:
        >>> with DatastoreEmulatorContainer() as datastore:
        ...     endpoint = datastore.get_emulator_endpoint()
        ...     project_id = datastore.get_project_id()
        ...     # Connect to Datastore emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "gcr.io/google.com/cloudsdktool/google-cloud-cli"
    HTTP_PORT = 8081
    PROJECT_ID = "test-project"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Datastore emulator container.

        Args:
            image: Docker image name (default: gcr.io/google.com/cloudsdktool/google-cloud-cli)
        """
        super().__init__(image)

        self._flags: str | None = None

        self.with_exposed_ports(self.HTTP_PORT)
        self.waiting_for(
            HttpWaitStrategy()
            .with_path("/")
            .with_status_code(200)
        )

    def with_flags(self, flags: str) -> DatastoreEmulatorContainer:
        """
        Set additional flags for the Datastore emulator (fluent API).

        Args:
            flags: Additional command-line flags

        Returns:
            This container instance
        """
        self._flags = flags
        return self

    def start(self) -> DatastoreEmulatorContainer:  # type: ignore[override]
        """
        Start the Datastore emulator container with any configured options.

        Returns:
            This container instance
        """
        command = f"gcloud beta emulators datastore start --project {self.PROJECT_ID} --host-port 0.0.0.0:{self.HTTP_PORT}"
        if self._flags:
            command += f" {self._flags}"

        self.with_command("/bin/sh", "-c", command)
        super().start()
        return self

    def get_emulator_endpoint(self) -> str:
        """
        Get the emulator endpoint.

        Returns:
            Host:port pair for the emulator endpoint
        """
        return f"{self.get_host()}:{self.get_mapped_port(self.HTTP_PORT)}"

    def get_project_id(self) -> str:
        """
        Get the project ID used by the emulator.

        Returns:
            Project ID
        """
        return self.PROJECT_ID


class FirestoreEmulatorContainer(GenericContainer):
    """
    Google Cloud Firestore emulator container.

    This container starts a Firestore emulator using the Google Cloud SDK.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/FirestoreEmulatorContainer.java

    Example:
        >>> with FirestoreEmulatorContainer() as firestore:
        ...     endpoint = firestore.get_emulator_endpoint()
        ...     # Connect to Firestore emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "gcr.io/google.com/cloudsdktool/google-cloud-cli"
    PORT = 8080

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Firestore emulator container.

        Args:
            image: Docker image name (default: gcr.io/google.com/cloudsdktool/google-cloud-cli)
        """
        super().__init__(image)

        self._flags: str | None = None

        self.with_exposed_ports(self.PORT)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*running.*$")
        )

    def with_flags(self, flags: str) -> FirestoreEmulatorContainer:
        """
        Set additional flags for the Firestore emulator (fluent API).

        Args:
            flags: Additional command-line flags

        Returns:
            This container instance
        """
        self._flags = flags
        return self

    def start(self) -> FirestoreEmulatorContainer:  # type: ignore[override]
        """
        Start the Firestore emulator container with any configured options.

        Returns:
            This container instance
        """
        command = f"gcloud beta emulators firestore start --host-port 0.0.0.0:{self.PORT}"
        if self._flags:
            command += f" {self._flags}"

        self.with_command("/bin/sh", "-c", command)
        super().start()
        return self

    def get_emulator_endpoint(self) -> str:
        """
        Get the emulator endpoint.

        Returns:
            Host:port pair for the emulator endpoint
        """
        return f"{self.get_host()}:{self.get_mapped_port(self.PORT)}"


class SpannerEmulatorContainer(GenericContainer):
    """
    Google Cloud Spanner emulator container.

    This container starts a Spanner emulator.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/SpannerEmulatorContainer.java

    Example:
        >>> with SpannerEmulatorContainer() as spanner:
        ...     grpc_endpoint = spanner.get_emulator_grpc_endpoint()
        ...     http_endpoint = spanner.get_emulator_http_endpoint()
        ...     # Connect to Spanner emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "gcr.io/cloud-spanner-emulator/emulator"
    GRPC_PORT = 9010
    HTTP_PORT = 9020

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a Spanner emulator container.

        Args:
            image: Docker image name (default: gcr.io/cloud-spanner-emulator/emulator)
        """
        super().__init__(image)

        self.with_exposed_ports(self.GRPC_PORT, self.HTTP_PORT)
        self.waiting_for(
            LogMessageWaitStrategy()
            .with_regex(r".*Cloud Spanner emulator running\..*")
        )

    def get_emulator_grpc_endpoint(self) -> str:
        """
        Get the gRPC emulator endpoint.

        Returns:
            Host:port pair for the gRPC endpoint
        """
        return f"{self.get_host()}:{self.get_mapped_port(self.GRPC_PORT)}"

    def get_emulator_http_endpoint(self) -> str:
        """
        Get the HTTP REST emulator endpoint.

        Returns:
            Host:port pair for the HTTP endpoint
        """
        return f"{self.get_host()}:{self.get_mapped_port(self.HTTP_PORT)}"


class BigQueryEmulatorContainer(GenericContainer):
    """
    Google Cloud BigQuery emulator container.

    This container starts a BigQuery emulator.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/BigQueryEmulatorContainer.java

    Example:
        >>> with BigQueryEmulatorContainer() as bigquery:
        ...     http_endpoint = bigquery.get_emulator_http_endpoint()
        ...     grpc_port = bigquery.get_emulator_grpc_port()
        ...     project_id = bigquery.get_project_id()
        ...     # Connect to BigQuery emulator
    """

    # Default configuration
    DEFAULT_IMAGE = "ghcr.io/goccy/bigquery-emulator"
    HTTP_PORT = 9050
    GRPC_PORT = 9060
    PROJECT_ID = "test-project"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a BigQuery emulator container.

        Args:
            image: Docker image name (default: ghcr.io/goccy/bigquery-emulator)
        """
        super().__init__(image)

        self.with_exposed_ports(self.HTTP_PORT, self.GRPC_PORT)
        self.with_command("--project", self.PROJECT_ID)

    def get_emulator_http_endpoint(self) -> str:
        """
        Get the HTTP emulator endpoint.

        Returns:
            HTTP URL for the emulator endpoint
        """
        return f"http://{self.get_host()}:{self.get_mapped_port(self.HTTP_PORT)}"

    def get_emulator_grpc_port(self) -> int:
        """
        Get the gRPC emulator port.

        Returns:
            Host port number mapped to the gRPC port
        """
        return self.get_mapped_port(self.GRPC_PORT)

    def get_project_id(self) -> str:
        """
        Get the project ID used by the emulator.

        Returns:
            Project ID
        """
        return self.PROJECT_ID
