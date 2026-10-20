"""Security regressions for outbound profile URLs."""
from unittest.mock import AsyncMock, patch
import socket

import pytest

from harvey.collectors.url_guard import checked_host, check_public_url


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://10.0.0.1/", "http://169.254.169.254/",
    "http://[::1]/", "https://localhost/", "https://foo.local/",
    "file:///etc/passwd", "http://example.com:8080/",
    "http://user:pass@example.com/",
])
def test_reject_non_public_urls(url):
    with pytest.raises(ValueError):
        checked_host(url)


def test_allow_public_https():
    assert checked_host("https://example.com/") == "example.com"


@pytest.mark.asyncio
async def test_reject_dns_private_result():
    loop = __import__("asyncio").get_running_loop()
    record = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.10", 0))
    with patch.object(loop, "getaddrinfo", new_callable=AsyncMock, return_value=[record]):
        with pytest.raises(ValueError, match="non-public"):
            await check_public_url("https://example.com/")


@pytest.mark.asyncio
async def test_allow_dns_public_result():
    loop = __import__("asyncio").get_running_loop()
    record = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", 0))
    with patch.object(loop, "getaddrinfo", new_callable=AsyncMock, return_value=[record]):
        await check_public_url("https://example.com/")
