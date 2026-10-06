from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse
import httpx
from .registry import PermissionLevel, ToolDefinition, ToolRegistry

BLOCKED_HOSTS = [
    "169.254.169.254",
    "metadata.google.internal",
    "100.100.100.200",
]


def _is_ssrf_safe(url: str, allowed_domains: Optional[str] = None) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    if not hostname:
        return False

    for blocked in BLOCKED_HOSTS:
        if hostname == blocked or hostname.endswith("." + blocked):
            return False

    if allowed_domains and allowed_domains != "*":
        domains = [d.strip().lower() for d in allowed_domains.split(",")]
        if hostname.lower() not in domains:
            return False

    return True


async def http_request(url: str) -> str:
    if not _is_ssrf_safe(url):
        return "SSRF Error: Access to restricted URL denied."
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(url)
        return f"HTTP {res.status_code}\n{res.text[:2000]}"


def register_http_db_tools(registry: ToolRegistry) -> None:
    registry.register(ToolDefinition("http_request", "SSRF protected HTTP GET request.", {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}, {}, PermissionLevel.SAFE_WRITE, func=http_request))
