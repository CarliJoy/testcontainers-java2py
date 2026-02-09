"""HTTP wait strategy implementation.

Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/HttpWaitStrategy.java
"""

from __future__ import annotations

import base64
import logging
import ssl
import time
import urllib.request
import urllib.error
from typing import Callable, Optional
from urllib.parse import urljoin

from .wait_strategy import AbstractWaitStrategy, WaitStrategyTarget

logger = logging.getLogger(__name__)


class HttpWaitStrategy(AbstractWaitStrategy):
    """Wait strategy that waits for an HTTP(S) endpoint to return a specific status code.
    
    Java source: https://github.com/testcontainers/testcontainers-java/blob/main/core/src/main/java/org/testcontainers/containers/wait/strategy/HttpWaitStrategy.java
    """

    def __init__(self) -> None:
        super().__init__()
        self._path = "/"
        self._method = "GET"
        self._status_codes: set[int] = set()
        self._tls_enabled = False
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._headers: dict[str, str] = {}
        self._response_predicate: Optional[Callable[[str], bool]] = None
        self._status_code_predicate: Optional[Callable[[int], bool]] = None
        self._liveness_port: Optional[int] = None
        self._read_timeout = 1.0  # seconds
        self._allow_insecure = False

    def for_status_code(self, status_code: int) -> HttpWaitStrategy:
        """Wait for the given status code.
        
        Args:
            status_code: The expected HTTP status code
            
        Returns:
            This strategy for method chaining
        """
        self._status_codes.add(status_code)
        return self

    def for_status_code_matching(
        self, predicate: Callable[[int], bool]
    ) -> HttpWaitStrategy:
        """Wait for status code to pass the given predicate.
        
        Args:
            predicate: Function that tests the status code
            
        Returns:
            This strategy for method chaining
        """
        self._status_code_predicate = predicate
        return self

    def for_path(self, path: str) -> HttpWaitStrategy:
        """Set the path to check.
        
        Args:
            path: The URL path to check
            
        Returns:
            This strategy for method chaining
        """
        self._path = path
        return self

    def for_port(self, port: int) -> HttpWaitStrategy:
        """Wait for the given port.
        
        Args:
            port: The port number to check
            
        Returns:
            This strategy for method chaining
        """
        self._liveness_port = port
        return self

    def using_tls(self) -> HttpWaitStrategy:
        """Use HTTPS instead of HTTP.
        
        Returns:
            This strategy for method chaining
        """
        self._tls_enabled = True
        return self

    def with_method(self, method: str) -> HttpWaitStrategy:
        """Set the HTTP method to use (GET by default).
        
        Args:
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            This strategy for method chaining
        """
        self._method = method
        return self

    def allow_insecure(self) -> HttpWaitStrategy:
        """Allow untrusted (self-signed) SSL certificates.
        
        Returns:
            This strategy for method chaining
        """
        self._allow_insecure = True
        return self

    def with_basic_credentials(
        self, username: str, password: str
    ) -> HttpWaitStrategy:
        """Authenticate with HTTP Basic Authorization.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            This strategy for method chaining
        """
        self._username = username
        self._password = password
        return self

    def with_header(self, name: str, value: str) -> HttpWaitStrategy:
        """Add a custom HTTP header.
        
        Args:
            name: Header name
            value: Header value
            
        Returns:
            This strategy for method chaining
        """
        self._headers[name] = value
        return self

    def with_headers(self, headers: dict[str, str]) -> HttpWaitStrategy:
        """Add multiple custom HTTP headers.
        
        Args:
            headers: Dictionary of header name/value pairs
            
        Returns:
            This strategy for method chaining
        """
        self._headers.update(headers)
        return self

    def with_read_timeout(self, timeout: float) -> HttpWaitStrategy:
        """Set the HTTP connection read timeout.
        
        Args:
            timeout: Timeout in seconds (minimum 0.001)
            
        Returns:
            This strategy for method chaining
        """
        if timeout < 0.001:
            raise ValueError("timeout must be at least 1 millisecond")
        self._read_timeout = timeout
        return self

    def for_response_predicate(
        self, predicate: Callable[[str], bool]
    ) -> HttpWaitStrategy:
        """Wait for response body to pass the given predicate.
        
        Args:
            predicate: Function that tests the response body
            
        Returns:
            This strategy for method chaining
        """
        self._response_predicate = predicate
        return self

    def _wait_until_ready(self) -> None:
        """Implementation of the wait logic."""
        container_name = self._wait_strategy_target.get_container_info()["Name"]

        # Determine which port to use
        if self._liveness_port is not None:
            liveness_check_port = self._wait_strategy_target.get_exposed_port(
                self._liveness_port
            )
        else:
            ports = self._get_liveness_check_ports()
            if not ports:
                logger.warning(
                    "%s: No exposed ports or mapped ports - cannot wait for status",
                    container_name,
                )
                return
            liveness_check_port = list(ports)[0]

        if liveness_check_port is None or liveness_check_port == -1:
            return

        # Build the URI
        uri = self._build_liveness_uri(liveness_check_port)
        
        logger.info(
            "%s: Waiting for %d seconds for URL: %s",
            container_name,
            self._startup_timeout,
            uri,
        )

        # Try to connect
        start_time = time.time()
        while True:
            try:
                self._check_url(uri)
                logger.info("%s: URL %s is accessible", container_name, uri)
                return
            except Exception as e:
                if time.time() - start_time >= self._startup_timeout:
                    raise TimeoutError(
                        f"Timed out waiting for URL to be accessible "
                        f"({uri} should return HTTP {self._status_codes or 200})"
                    ) from e
                time.sleep(0.5)

    def _build_liveness_uri(self, port: int) -> str:
        """Build the URI to check."""
        scheme = "https" if self._tls_enabled else "http"
        host = self._wait_strategy_target.get_host()
        
        # Don't include default ports
        if (self._tls_enabled and port == 443) or (not self._tls_enabled and port == 80):
            port_suffix = ""
        else:
            port_suffix = f":{port}"
        
        return f"{scheme}://{host}{port_suffix}{self._path}"

    def _check_url(self, url: str) -> None:
        """Check if the URL is accessible and matches criteria."""
        # Create request
        request = urllib.request.Request(url, method=self._method)
        
        # Add basic auth if configured
        if self._username:
            credentials = f"{self._username}:{self._password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            request.add_header("Authorization", f"Basic {encoded}")
        
        # Add custom headers
        for name, value in self._headers.items():
            request.add_header(name, value)
        
        # Create SSL context if needed
        context = None
        if self._tls_enabled and self._allow_insecure:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        # Make request
        try:
            with urllib.request.urlopen(
                request, timeout=self._read_timeout, context=context
            ) as response:
                status_code = response.status
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status_code = e.code
            body = e.read().decode("utf-8") if e.fp else ""
        
        # Check status code
        if not self._check_status_code(status_code):
            raise RuntimeError(f"HTTP response code was: {status_code}")
        
        # Check response body if predicate is set
        if self._response_predicate and not self._response_predicate(body):
            raise RuntimeError(f"Response did not match predicate: {body}")

    def _check_status_code(self, status_code: int) -> bool:
        """Check if status code matches criteria."""
        # Default: expect 200 OK
        if not self._status_codes and self._status_code_predicate is None:
            return status_code == 200
        
        # Check specific status codes
        if self._status_codes and status_code in self._status_codes:
            return True
        
        # Check predicate
        if self._status_code_predicate and self._status_code_predicate(status_code):
            return True
        
        return False
