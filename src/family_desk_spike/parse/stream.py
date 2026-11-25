"""Pure parsers for Alpaca WebSocket frames (stock quotes and news).

A frame is a JSON array of messages, each with a `T` type field.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from family_desk_spike.models import MAX_TEXT, NewsItem, Quote, StreamControl, SubscriptionAck
from family_desk_spike.parse.alpaca_rest import news_item_from_obj

Message = Quote | NewsItem | StreamControl | SubscriptionAck


@dataclass(frozen=True)
class ParsedFrame:
    messages: list[Message] = field(default_factory=list)
    ignored: int = 0  # known-but-unused types (trades, bars, ...)
    malformed: int = 0


def quote_from_obj(obj: dict[str, Any]) -> Quote:
    return Quote.model_validate(
        {
            "symbol": obj.get("S"),
            "bid_price": obj.get("bp"),
            "bid_size": obj.get("bs"),
            "ask_price": obj.get("ap"),
            "ask_size": obj.get("as"),
            "timestamp": obj.get("t"),
            "bid_exchange": obj.get("bx"),
            "ask_exchange": obj.get("ax"),
            "conditions": tuple(obj.get("c") or ()),
            "tape": obj.get("z"),
        }
    )


def _tuple(obj: dict[str, Any], key: str) -> tuple[str, ...]:
    return tuple(str(s) for s in (obj.get(key) or ()))


def _one(
    obj: dict[str, Any], stream: str
) -> Quote | NewsItem | StreamControl | SubscriptionAck | None:
    kind = obj.get("T")
    if kind == "q":
        return quote_from_obj(obj)
    if kind == "n":
        return news_item_from_obj(obj)
    if kind in ("success", "error"):
        code = obj.get("code")
        return StreamControl(
            kind=kind,
            msg=str(obj.get("msg", ""))[:MAX_TEXT],
            code=int(code) if code is not None else None,
        )
    if kind == "subscription":
        return SubscriptionAck(
            stream=stream,
            quotes=_tuple(obj, "quotes"),
            trades=_tuple(obj, "trades"),
            bars=_tuple(obj, "bars"),
            news=_tuple(obj, "news"),
        )
    return None


def parse_frame(raw: str | bytes, stream: str) -> ParsedFrame:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ParsedFrame(malformed=1)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return ParsedFrame(malformed=1)
    out: list[Message] = []
    ignored = malformed = 0
    for obj in data:
        if not isinstance(obj, dict):
            malformed += 1
            continue
        try:
            msg = _one(obj, stream)
        except (ValidationError, ValueError, TypeError):
            malformed += 1
            continue
        if msg is None:
            ignored += 1
        else:
            out.append(msg)
    return ParsedFrame(messages=out, ignored=ignored, malformed=malformed)
