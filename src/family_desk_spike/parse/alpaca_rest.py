"""Pure parsers for Alpaca REST payloads (account, positions, clock, news)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

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


# Fields of the Account object in Alpaca's Trading API schema for GET /v2/account
# (https://docs.alpaca.markets/reference/getaccount-1, page updated 2026-05-27, read
# 2026-11-25). A key outside this set and outside our model is reported as unknown.
ACCOUNT_DOCUMENTED_FIELDS = frozenset(
    {
        "account_blocked", "account_number", "accrued_fees", "balance_asof",
        "buying_power", "cash", "created_at", "crypto_status", "currency", "equity", "id",
        "initial_margin", "intraday_adjustments", "last_equity", "last_maintenance_margin",
        "long_market_value", "maintenance_margin", "multiplier",
        "non_marginable_buying_power", "options_approved_level", "options_buying_power",
        "options_trading_level", "pending_reg_taf_fees", "pending_transfer_in",
        "pending_transfer_out", "portfolio_value", "regt_buying_power",
        "short_market_value", "shorting_enabled", "sma", "status",
        "trade_suspended_by_user", "trading_blocked", "transfers_blocked",
    }
)  # fmt: skip
MAX_DRIFT_NAMES = 50
_FIELD_NAME = re.compile(r"^[A-Za-z0-9_]{1,64}$")


@dataclass(frozen=True)
class SchemaDrift:
    """Field names only, never values (an unknown field could hold anything)."""

    entity: str
    missing_required: tuple[str, ...] = ()
    missing_optional: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()
    unknown_invalid_names: int = 0  # keys too long or with odd characters: counted only

    @property
    def empty(self) -> bool:
        return not (
            self.missing_required
            or self.missing_optional
            or self.unknown
            or self.unknown_invalid_names
        )

    def payload(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "missing_required": list(self.missing_required),
            "missing_optional": list(self.missing_optional),
            "unknown": list(self.unknown),
            "unknown_invalid_names": self.unknown_invalid_names,
        }


class SchemaDriftError(ParseError):
    """A field the code depends on is missing. Carries the drift so it can be logged."""

    def __init__(self, drift: SchemaDrift) -> None:
        super().__init__(f"{drift.entity}: missing required {', '.join(drift.missing_required)}")
        self.drift = drift


def schema_drift(
    entity: str, data: dict[str, Any], model: type[BaseModel], documented: frozenset[str]
) -> SchemaDrift:
    fields = model.model_fields
    required = sorted(n for n, f in fields.items() if f.is_required() and n not in data)
    optional = sorted(n for n, f in fields.items() if not f.is_required() and n not in data)
    extra = [k for k in data if k not in documented and k not in fields]
    valid = sorted(k for k in extra if _FIELD_NAME.match(k))
    return SchemaDrift(
        entity=entity,
        missing_required=tuple(required),
        missing_optional=tuple(optional),
        unknown=tuple(valid[:MAX_DRIFT_NAMES]),
        unknown_invalid_names=len(extra) - len(valid),
    )


def _validation_summary(exc: ValidationError) -> str:
    """Locations and error types only: pydantic's own message echoes input values."""
    parts = [f"{'.'.join(str(p) for p in e['loc'])}:{e['type']}" for e in exc.errors()]
    return "; ".join(parts[:10])


def _json(body: bytes) -> Any:
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ParseError(f"invalid JSON: {type(exc).__name__}") from exc


def parse_account(body: bytes) -> tuple[Account, SchemaDrift]:
    """Fails closed on a missing required field or a wrong type; reports other drift."""
    data = _json(body)
    if not isinstance(data, dict):
        raise ParseError("account: expected an object")
    drift = schema_drift("account", data, Account, ACCOUNT_DOCUMENTED_FIELDS)
    if drift.missing_required:
        raise SchemaDriftError(drift)
    try:
        account = Account.model_validate(data)
    except ValidationError as exc:
        raise ParseError(f"account: {_validation_summary(exc)}") from None
    return account, drift


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
