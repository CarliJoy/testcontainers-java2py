"""
K6 container implementation.

This module provides a container for K6 load testing tool.

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/k6/src/main/java/org/testcontainers/k6/K6Container.java
"""

from __future__ import annotations

import os
from typing import Any

from testcontainers.core.generic_container import GenericContainer


class K6Container(GenericContainer):
    """
    K6 load testing container.

    This container runs K6 load tests using test scripts provided by the user.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/k6/src/main/java/org/testcontainers/k6/K6Container.java

    Example:
        >>> with K6Container() as k6:
        ...     k6.with_test_script("./load-test.js")
        ...     k6.with_cmd_options("--vus", "10", "--duration", "30s")
        ...     k6.start()

        >>> # With script variables
        >>> k6 = K6Container()
        >>> k6.with_test_script("./test.js")
        >>> k6.with_script_var("MY_HOSTNAME", "example.com")
        >>> k6.with_cmd_options("--out", "json=results.json")
        >>> k6.start()

    Supported image:
        - grafana/k6
    """

    DEFAULT_IMAGE = "grafana/k6"

    def __init__(self, image: str = DEFAULT_IMAGE):
        """
        Initialize a K6 container.

        Args:
            image: Docker image name (default: grafana/k6)
        """
        super().__init__(image)

        self._test_script: str | None = None
        self._cmd_options: list[str] = []
        self._script_vars: dict[str, str] = {}

    def with_test_script(self, test_script: str) -> K6Container:
        """
        Specify the test script to be executed within the container.

        Args:
            test_script: Path to the test script file to be copied into the container

        Returns:
            This container instance
        """
        script_name = os.path.basename(test_script)
        self._test_script = f"/home/k6/{script_name}"
        self.with_volume_mapping(test_script, self._test_script)
        return self

    def with_cmd_options(self, *options: str) -> K6Container:
        """
        Specify additional command line options for the k6 command.

        Args:
            *options: Command line options

        Returns:
            This container instance
        """
        self._cmd_options.extend(options)
        return self

    def with_script_var(self, key: str, value: str) -> K6Container:
        """
        Add a key-value pair for access within test scripts as an environment variable.

        Args:
            key: Unique identifier for the variable
            value: Value of the variable

        Returns:
            This container instance
        """
        self._script_vars[key] = value
        return self

    def _configure(self) -> None:
        """
        Configure the container command before starting.

        This is called automatically during container startup.
        """
        command_parts = ["run"]
        command_parts.extend(self._cmd_options)

        for key, value in self._script_vars.items():
            command_parts.append("--env")
            command_parts.append(f"{key}={value}")

        if self._test_script:
            command_parts.append(self._test_script)

        self.with_command(command_parts)

    def start(self) -> K6Container:  # type: ignore[override]
        """
        Start the K6 container.

        Returns:
            This container instance
        """
        self._configure()
        super().start()
        return self
