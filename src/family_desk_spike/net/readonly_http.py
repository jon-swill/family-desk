"""The one outbound HTTP client (D12, G-7). GET only, (host, path) allowlist, checked
before anything is sent. Every Alpaca and SEC request goes through `ReadOnlyHttp`.

The transport interface has only `get`, so another verb cannot be expressed at all;
`fetch(method, ...)` exists so tests can prove any other verb is refused before send.
Redirects are never followed (a redirect could leave the allowlist).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urlsplit

import httpx

ALPACA_PAPER_TRADING_HOST = "paper-api.alpaca.markets"
ALPACA_DATA_HOST = "data.alpaca.markets"
SEC_HOST = "www.sec.gov"

ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        (ALPACA_PAPER_TRADING_HOST, "/v2/account"),
        (ALPACA_PAPER_TRADING_HOST, "/v2/positions"),
        (ALPACA_PAPER_TRADING_HOST, "/v2/clock"),
        (ALPACA_DATA_HOST, "/v1beta1/news"),
        (SEC_HOST, "/cgi-bin/browse-edgar"),
        (SEC_HOST, "/files/company_tickers.json"),
    }
)

ALLOWED_METHOD = "GET"
MAX_BODY_BYTES = 20 * 1024 * 1024
# Strict shape, checked before parsing, so urllib and httpx cannot read a URL differently
# (no backslash, "@", "%", whitespace, query or fragment characters).
SAFE_URL = re.compile(r"^https://[A-Za-z0-9.-]+(?::443)?/[A-Za-z0-9/._-]*$")


class RefusedRequestError(PermissionError):
    """Raised before any byte is sent."""


class TransportFailureError(ConnectionError):
    """Network-level failure (timeout, refused, reset, protocol). An OSError, so every
    caller's network-error path handles it. Carries only the error type, never the URL."""


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes
    headers: Mapping[str, str] = field(default_factory=dict)


class GetTransport(Protocol):
    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str],
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResponse: ...


def check_request(
    method: str, url: str, allowlist: frozenset[tuple[str, str]] = ALLOWLIST
) -> tuple[str, str]:
    """Pure policy check. Returns (host, path) or raises RefusedRequestError."""
    if method != ALLOWED_METHOD:
        raise RefusedRequestError(f"method {method!r} refused: only GET is allowed")
    if not SAFE_URL.fullmatch(url):
        raise RefusedRequestError("URL has characters outside the strict allowlist shape")
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise RefusedRequestError("only https is allowed")
    if parts.username is not None or parts.password is not None:
        raise RefusedRequestError("credentials in URL refused")
    try:
        port = parts.port
    except ValueError as exc:
        raise RefusedRequestError("invalid port") from exc
    if port not in (None, 443):
        raise RefusedRequestError("non-default port refused")
    if parts.query or parts.fragment:
        raise RefusedRequestError("pass query parameters via params, not in the URL")
    host = (parts.hostname or "").lower()
    path = parts.path
    if (host, path) not in allowlist:
        raise RefusedRequestError(f"({host}, {path}) is not on the allowlist")
    return host, path


@dataclass
class ReadOnlyHttp:
    transport: GetTransport
    allowlist: frozenset[tuple[str, str]] = ALLOWLIST
    timeout: float = 15.0
    sent: int = 0
    refused: int = 0

    async def fetch(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        try:
            check_request(method, url, self.allowlist)
        except RefusedRequestError:
            self.refused += 1
            raise
        self.sent += 1
        return await self.transport.get(
            url, params=dict(params or {}), headers=dict(headers or {}), timeout_s=self.timeout
        )

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        return await self.fetch(ALLOWED_METHOD, url, params=params, headers=headers)


@dataclass
class HttpxTransport:
    """Real transport (I/O edge). No redirects, bounded body size."""

    client: httpx.AsyncClient = field(
        default_factory=lambda: httpx.AsyncClient(follow_redirects=False, http2=False)
    )

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str],
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResponse:
        try:
            resp = await self.client.get(
                url, params=dict(params), headers=dict(headers), timeout=timeout_s
            )
        except httpx.TransportError as exc:
            # httpx errors are not OSError; callers back off on OSError (R-23). Without
            # this, one SEC timeout killed the EDGAR poller (failure-check, 2026-11-25).
            raise TransportFailureError(type(exc).__name__) from exc
        body = resp.content[:MAX_BODY_BYTES]
        return HttpResponse(status=resp.status_code, body=body, headers=dict(resp.headers))

    async def aclose(self) -> None:
        await self.client.aclose()
