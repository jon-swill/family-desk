"""Pure parsers for Alpaca REST payloads (account, positions, clock, news)."""

from __future__ import annotations

import json
from typing import Any

from family_desk_spike.models import (
    MAX_SYMBOLS,
    MAX_TEXT,
    Account,
    MarketClock,
    NewsItem,
    Position,
)


class ParseError(ValueError):
    pass


def _json(body: bytes) -> Any:
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ParseError(f"invalid JSON: {type(exc).__name__}") from exc


def parse_account(body: bytes) -> Account:
    data = _json(body)
    if not isinstance(data, dict):
        raise ParseError("account: expected an object")
    return Account.model_validate(data)


def parse_positions(body: bytes) -> list[Position]:
    data = _json(body)
    if not isinstance(data, list):
        raise ParseError("positions: expected a list")
    return [Position.model_validate(p) for p in data]


def parse_clock(body: bytes) -> MarketClock:
    data = _json(body)
    if not isinstance(data, dict):
        raise ParseError("clock: expected an object")
    return MarketClock.model_validate(data)


def news_item_from_obj(obj: dict[str, Any]) -> NewsItem:
    """Metadata only: summary, content, author and images are dropped here."""
    return NewsItem.model_validate(
        {
            "id": obj.get("id"),
            "headline": str(obj.get("headline", ""))[:MAX_TEXT],
            "symbols": tuple(str(s) for s in (obj.get("symbols") or [])[:MAX_SYMBOLS]),
            "url": obj.get("url") or None,
            "source": obj.get("source"),
            "created_at": obj.get("created_at"),
            "updated_at": obj.get("updated_at") or None,
        }
    )


def parse_news_page(body: bytes) -> tuple[list[NewsItem], str | None]:
    data = _json(body)
    if not isinstance(data, dict) or not isinstance(data.get("news"), list):
        raise ParseError("news: expected an object with a 'news' list")
    items = [news_item_from_obj(n) for n in data["news"] if isinstance(n, dict)]
    token = data.get("next_page_token")
    return items, (str(token) if token else None)
