"""Alpaca paper, read-only: account, positions, clock. All requests via ReadOnlyHttp."""

from __future__ import annotations

from dataclasses import dataclass

from family_desk_spike.config import Settings
from family_desk_spike.models import Account, MarketClock, Position
from family_desk_spike.net.readonly_http import HttpResponse, ReadOnlyHttp
from family_desk_spike.parse.alpaca_rest import parse_account, parse_clock, parse_positions


class ApiError(RuntimeError):
    """Non-2xx response. Carries status and path only, never headers or body."""

    def __init__(self, status: int, path: str) -> None:
        super().__init__(f"HTTP {status} on {path}")
        self.status = status
        self.path = path


def alpaca_headers(settings: Settings) -> dict[str, str]:
    return {
        "APCA-API-KEY-ID": settings.api_key_id.get_secret_value(),
        "APCA-API-SECRET-KEY": settings.api_secret_key.get_secret_value(),
        "Accept": "application/json",
    }


def ensure_ok(resp: HttpResponse, path: str) -> bytes:
    if not 200 <= resp.status < 300:
        raise ApiError(resp.status, path)
    return resp.body


@dataclass
class AlpacaReadOnly:
    http: ReadOnlyHttp
    trading_base_url: str
    settings: Settings

    def __repr__(self) -> str:
        return f"AlpacaReadOnly(trading_base_url={self.trading_base_url!r})"

    async def _get(self, path: str) -> bytes:
        url = self.trading_base_url.rstrip("/") + path
        resp = await self.http.get(url, headers=alpaca_headers(self.settings))
        return ensure_ok(resp, path)

    async def get_account(self) -> Account:
        return parse_account(await self._get("/v2/account"))

    async def get_positions(self) -> list[Position]:
        return parse_positions(await self._get("/v2/positions"))

    async def get_clock(self) -> MarketClock:
        return parse_clock(await self._get("/v2/clock"))
