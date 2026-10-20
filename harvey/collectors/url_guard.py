"""Conservative outbound URL guard for the profile collector.

This is application-layer defence in depth, NOT a DNS pinning firewall.
Host networking must independently deny access to private/metadata ranges.
"""
from __future__ import annotations
import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

def checked_host(url: str) -> str:
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Malformed URL") from exc
    if parsed.scheme not in ("http", "https") or not host:
        raise ValueError("Only absolute HTTP(S) URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Embedded credentials forbidden")
    if port not in (None, 80, 443):
        raise ValueError("Nonstandard port forbidden")
    host = host.rstrip(".").lower()
    if not host or host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("Local hostname forbidden")
    if "%" in host:
        raise ValueError("Scoped address forbidden")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return host
    if not addr.is_global:
        raise ValueError("Non-global address forbidden")
    return host

async def check_public_url(url: str) -> None:
    host = checked_host(url)
    loop = asyncio.get_running_loop()
    try:
        records = await loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("DNS resolution failed") from exc
    addresses = [entry[4][0] for entry in records]
    if not addresses or any(not ipaddress.ip_address(addr).is_global for addr in addresses):
        raise ValueError("DNS resolved to non-public address")
