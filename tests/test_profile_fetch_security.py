"""HTTP redirect/response bounds tests for the profile fetcher."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from harvey.collectors.profile import ProfileCollector


@pytest.mark.asyncio
async def test_redirect_to_private_address_never_fetched():
    calls = []
    async def handler(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={"location": "http://127.0.0.1/admin"})
    collector = ProfileCollector(state=None)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=False) as client:
        collector._client = client
        with patch("harvey.collectors.profile.check_public_url", new_callable=AsyncMock) as guard:
            async def check(url):
                if url.startswith("http://127.0.0.1"):
                    raise ValueError("private address blocked")
            guard.side_effect = check
            assert await collector._get("https://example.com/") == ""
    assert calls == ["https://example.com/"]


@pytest.mark.asyncio
async def test_oversized_response_rejected():
    async def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"},
                              content=b"x" * 2_000_001)
    collector = ProfileCollector(state=None)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector._client = client
        with patch("harvey.collectors.profile.check_public_url", new_callable=AsyncMock):
            assert await collector._get("https://example.com/") == ""
