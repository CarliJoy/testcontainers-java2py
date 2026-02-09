"""Tests for container types (enums)."""

from __future__ import annotations

import pytest

from testcontainers.core.container_types import BindMode, SelinuxContext, InternetProtocol


class TestBindMode:
    """Tests for BindMode enum."""

    def test_read_only_value(self):
        """Test READ_ONLY has correct value."""
        assert BindMode.READ_ONLY.value == "ro"
        assert str(BindMode.READ_ONLY) == "ro"

    def test_read_write_value(self):
        """Test READ_WRITE has correct value."""
        assert BindMode.READ_WRITE.value == "rw"
        assert str(BindMode.READ_WRITE) == "rw"


class TestSelinuxContext:
    """Tests for SelinuxContext enum."""

    def test_shared_value(self):
        """Test SHARED has correct value."""
        assert SelinuxContext.SHARED.value == "z"
        assert str(SelinuxContext.SHARED) == "z"

    def test_single_value(self):
        """Test SINGLE has correct value."""
        assert SelinuxContext.SINGLE.value == "Z"
        assert str(SelinuxContext.SINGLE) == "Z"

    def test_none_value(self):
        """Test NONE has correct value."""
        assert SelinuxContext.NONE.value == ""
        assert str(SelinuxContext.NONE) == ""


class TestInternetProtocol:
    """Tests for InternetProtocol enum."""

    def test_tcp_value(self):
        """Test TCP has correct value."""
        assert InternetProtocol.TCP.value == "tcp"
        assert str(InternetProtocol.TCP) == "tcp"

    def test_udp_value(self):
        """Test UDP has correct value."""
        assert InternetProtocol.UDP.value == "udp"
        assert str(InternetProtocol.UDP) == "udp"

    def test_to_docker_notation(self):
        """Test conversion to Docker notation."""
        assert InternetProtocol.TCP.to_docker_notation() == "tcp"
        assert InternetProtocol.UDP.to_docker_notation() == "udp"

    def test_from_docker_notation_lowercase(self):
        """Test creation from lowercase Docker notation."""
        assert InternetProtocol.from_docker_notation("tcp") == InternetProtocol.TCP
        assert InternetProtocol.from_docker_notation("udp") == InternetProtocol.UDP

    def test_from_docker_notation_uppercase(self):
        """Test creation from uppercase Docker notation."""
        assert InternetProtocol.from_docker_notation("TCP") == InternetProtocol.TCP
        assert InternetProtocol.from_docker_notation("UDP") == InternetProtocol.UDP

    def test_from_docker_notation_mixed_case(self):
        """Test creation from mixed case Docker notation."""
        assert InternetProtocol.from_docker_notation("Tcp") == InternetProtocol.TCP
        assert InternetProtocol.from_docker_notation("uDp") == InternetProtocol.UDP

    def test_from_docker_notation_invalid(self):
        """Test that invalid protocol raises ValueError."""
        with pytest.raises(ValueError, match="Unknown protocol: icmp"):
            InternetProtocol.from_docker_notation("icmp")
