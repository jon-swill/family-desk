"""Startup REST news GET (D14): recent watchlist news, metadata only (P-02 positive case)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta

from family_desk_spike.applog import utc_iso
from family_desk_spike.broker.alpaca_readonly import alpaca_headers, ensure_ok
from family_desk_spike.config import Settings
from family_desk_spike.models import NewsItem
from family_desk_spike.net.readonly_http import ReadOnlyHttp
from family_desk_spike.parse.alpaca_rest import parse_news_page

NEWS_PATH = "/v1beta1/news"


def news_params(
    symbols: Sequence[str], now: datetime, lookback_hours: int, limit: int
) -> dict[str, str]:
    return {
        "symbols": ",".join(symbols),
        "start": utc_iso(now - timedelta(hours=lookback_hours)),
        "limit": str(limit),
        "sort": "desc",
        "include_content": "false",
    }


def watchlist_matches(items: Sequence[NewsItem], symbols: Sequence[str]) -> list[NewsItem]:
    wanted = set(symbols)
    return [n for n in items if wanted.intersection(n.symbols)]


async def fetch_recent_news(
    http: ReadOnlyHttp,
    *,
    data_base_url: str,
    settings: Settings,
    symbols: Sequence[str],
    now: datetime,
    lookback_hours: int,
    limit: int,
) -> list[NewsItem]:
    """One page only (small limit): this is a liveness proof, not a history download."""
    resp = await http.get(
        data_base_url.rstrip("/") + NEWS_PATH,
        params=news_params(symbols, now, lookback_hours, limit),
        headers=alpaca_headers(settings),
    )
    items, _ = parse_news_page(ensure_ok(resp, NEWS_PATH))
    return items


async def fetch_news_window(
    http: ReadOnlyHttp,
    *,
    data_base_url: str,
    settings: Settings,
    symbols: Sequence[str],
    start: datetime,
    end: datetime,
    limit: int = 50,
) -> tuple[list[NewsItem], bool]:
    """One page of watchlist news in [start, end]. Returns (items, truncated)."""
    resp = await http.get(
        data_base_url.rstrip("/") + NEWS_PATH,
        params={
            "symbols": ",".join(symbols),
            "start": utc_iso(start),
            "end": utc_iso(end),
            "limit": str(limit),
            "sort": "desc",
            "include_content": "false",
        },
        headers=alpaca_headers(settings),
    )
    items, token = parse_news_page(ensure_ok(resp, NEWS_PATH))
    return items, token is not None
