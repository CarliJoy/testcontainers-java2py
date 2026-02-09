"""
Selenium browser container implementation.

This module provides containers for Selenium standalone browsers (Chrome, Firefox, Edge).

Java source:
https://github.com/testcontainers/testcontainers-java/blob/main/modules/selenium/src/main/java/org/testcontainers/containers/BrowserWebDriverContainer.java
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from testcontainers.core.generic_container import GenericContainer
from testcontainers.waiting.log import LogMessageWaitStrategy
from testcontainers.waiting.port import HostPortWaitStrategy
from testcontainers.waiting.wait_all import WaitAllStrategy


class BrowserType(str, Enum):
    """Browser types supported by Selenium containers."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


class BrowserWebDriverContainer(GenericContainer):
    """
    Selenium browser WebDriver container.

    This container starts a Selenium standalone browser instance (Chrome, Firefox,
    or Edge) with VNC support for debugging. The container exposes the Selenium
    WebDriver endpoint for remote control.

    Java source:
    https://github.com/testcontainers/testcontainers-java/blob/main/modules/selenium/src/main/java/org/testcontainers/containers/BrowserWebDriverContainer.java

    Example:
        >>> with BrowserWebDriverContainer() as selenium:
        ...     url = selenium.get_selenium_url()
        ...     # Connect with RemoteWebDriver(url, options)

        >>> # Specific browser
        >>> selenium = BrowserWebDriverContainer(BrowserType.FIREFOX)
        >>> selenium.start()
        >>> url = selenium.get_selenium_url()

        >>> # Custom image
        >>> selenium = BrowserWebDriverContainer(image="selenium/standalone-chrome:4.16.0")
        >>> selenium.start()

    Note:
        - Default browser is Chrome
        - Selenium 4+ images include VNC server on port 5900
        - The container uses 2GB of shared memory (/dev/shm) by default
    """

    # Default configuration
    DEFAULT_CHROME_IMAGE = "selenium/standalone-chrome:4.16.0"
    DEFAULT_FIREFOX_IMAGE = "selenium/standalone-firefox:4.16.0"
    DEFAULT_EDGE_IMAGE = "selenium/standalone-edge:4.16.0"
    DEFAULT_SELENIUM_PORT = 4444
    DEFAULT_VNC_PORT = 5900
    DEFAULT_VNC_PASSWORD = "secret"

    def __init__(
        self,
        browser: Optional[BrowserType] = None,
        image: Optional[str] = None,
    ):
        """
        Initialize a Selenium browser container.

        Args:
            browser: Browser type (CHROME, FIREFOX, or EDGE). Default is CHROME.
                     Ignored if custom image is provided.
            image: Custom Docker image name. If provided, overrides browser parameter.

        Note:
            Either browser or image should be provided, not both. If both are provided,
            image takes precedence.
        """
        # Determine the image to use
        if image:
            container_image = image
        else:
            # Default to Chrome if no browser specified
            if browser is None:
                browser = BrowserType.CHROME

            if browser == BrowserType.CHROME:
                container_image = self.DEFAULT_CHROME_IMAGE
            elif browser == BrowserType.FIREFOX:
                container_image = self.DEFAULT_FIREFOX_IMAGE
            elif browser == BrowserType.EDGE:
                container_image = self.DEFAULT_EDGE_IMAGE
            else:
                raise ValueError(f"Unsupported browser type: {browser}")

        super().__init__(container_image)

        self._selenium_port = self.DEFAULT_SELENIUM_PORT
        self._vnc_port = self.DEFAULT_VNC_PORT

        # Expose Selenium and VNC ports
        self.with_exposed_ports(self._selenium_port, self._vnc_port)

        # Set timezone (use UTC by default)
        self.with_env("TZ", "Etc/UTC")

        # Set no_proxy to localhost to avoid issues
        self.with_env("no_proxy", "localhost")

        # Set shared memory size to 2GB for browser stability
        # Browsers need adequate shared memory for rendering
        self._shm_size = 2 * 1024 * 1024 * 1024  # 2GB in bytes

        # Wait for Selenium to be ready
        # Selenium logs specific messages when ready, and port should be accessible
        log_wait = (
            LogMessageWaitStrategy()
            .with_regex(
                r".*(RemoteWebDriver instances should connect to|"
                r"Selenium Server is up and running|"
                r"Started Selenium Standalone).*"
            )
            .with_startup_timeout(60)
        )

        port_wait = HostPortWaitStrategy().with_startup_timeout(60)

        self.waiting_for(
            WaitAllStrategy()
            .with_strategy(log_wait)
            .with_strategy(port_wait)
            .with_startup_timeout(60)
        )

        # Set startup attempts to 3 for better reliability
        self._startup_attempts = 3

    def get_selenium_url(self) -> str:
        """
        Get the Selenium WebDriver URL.

        This URL is used to connect RemoteWebDriver clients to the browser.

        Returns:
            Selenium WebDriver URL in format: http://host:port/wd/hub

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._selenium_port)
        return f"http://{host}:{port}/wd/hub"

    def get_selenium_address(self) -> str:
        """
        Get the Selenium WebDriver address (alias for get_selenium_url).

        Returns:
            Selenium WebDriver URL
        """
        return self.get_selenium_url()

    def get_vnc_address(self) -> str:
        """
        Get the VNC connection address for viewing the browser session.

        Returns:
            VNC address in format: vnc://vnc:secret@host:port

        Raises:
            RuntimeError: If container is not started
        """
        if not self._container:
            raise RuntimeError("Container not started")

        host = self.get_host()
        port = self.get_mapped_port(self._vnc_port)
        return f"vnc://vnc:{self.DEFAULT_VNC_PASSWORD}@{host}:{port}"

    def get_selenium_port(self) -> int:
        """
        Get the exposed Selenium port number on the host.

        Returns:
            Host port number mapped to the Selenium port
        """
        return self.get_mapped_port(self._selenium_port)

    def get_vnc_port(self) -> int:
        """
        Get the exposed VNC port number on the host.

        Returns:
            Host port number mapped to the VNC port
        """
        return self.get_mapped_port(self._vnc_port)
