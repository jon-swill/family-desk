"""Typed models (D11). External data is parsed into these at the boundary.

Account deliberately has no account number or id field: they are never parsed or stored.
Text fields from outside (headlines, company names) are size-capped data, never instructions.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

MAX_TEXT = 1000
MAX_URL = 2048
MAX_SYMBOLS = 50


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")


class Account(_Model):
    """GET /v2/account. Alpaca's schema marks only `id` and `status` required
    (https://docs.alpaca.markets/reference/getaccount-1, read 2026-11-25).

    Required here: the fields the runner reads to judge the account, so a missing one
    fails closed. Optional: fields no code path depends on. Types are still validated
    when a field is present. Absent or unknown fields become a schema-drift event
    (`parse.alpaca_rest.SchemaDrift`), never a silent default.
    """

    status: str
    currency: str
    trading_blocked: bool
    account_blocked: bool
    equity: Decimal | None = None
    cash: Decimal | None = None
    buying_power: Decimal | None = None
    # Not in Alpaca's current Account schema; PDT is being retired (FINRA intraday margin
    # rule). Kept optional so the log still shows it if an older payload carries it.
    pattern_day_trader: bool | None = None


class Position(_Model):
    symbol: str
    qty: Decimal
    side: str
    avg_entry_price: Decimal
    market_value: Decimal | None = None
    asset_class: str | None = None


class MarketClock(_Model):
    timestamp: AwareDatetime
    is_open: bool
    next_open: AwareDatetime
    next_close: AwareDatetime


class Quote(_Model):
    symbol: str
    bid_price: Decimal
    bid_size: Decimal
    ask_price: Decimal
    ask_size: Decimal
    timestamp: AwareDatetime
    bid_exchange: str | None = None
    ask_exchange: str | None = None
    conditions: tuple[str, ...] = ()
    tape: str | None = None

    @property
    def spread(self) -> Decimal | None:
        if self.bid_price <= 0 or self.ask_price <= 0 or self.ask_price < self.bid_price:
            return None
        return self.ask_price - self.bid_price

    @property
    def spread_bps(self) -> Decimal | None:
        s = self.spread
        if s is None:
            return None
        mid = (self.ask_price + self.bid_price) / 2
        return s / mid * Decimal(10000)


class NewsItem(_Model):
    """Metadata only (inv. 6, C-7): no summary or content is kept."""

    id: int
    headline: str = Field(max_length=MAX_TEXT)
    symbols: tuple[str, ...] = Field(max_length=MAX_SYMBOLS)
    url: str | None = Field(default=None, max_length=MAX_URL)
    source: str | None = None
    created_at: AwareDatetime
    updated_at: AwareDatetime | None = None


class Filing8K(_Model):
    accession_number: str
    cik: str = Field(pattern=r"^\d{10}$")
    company_name: str = Field(max_length=MAX_TEXT)
    form_type: str
    updated: AwareDatetime
    link: str | None = Field(default=None, max_length=MAX_URL)


class SubscriptionAck(_Model):
    stream: str
    quotes: tuple[str, ...] = ()
    trades: tuple[str, ...] = ()
    bars: tuple[str, ...] = ()
    news: tuple[str, ...] = ()


class StreamControl(_Model):
    """`success` / `error` control messages from an Alpaca stream."""

    kind: Literal["success", "error"]
    msg: str = Field(max_length=MAX_TEXT)
    code: int | None = None


class StreamEvent(_Model):
    """Something the spike itself observed about a stream (logged, never silent)."""

    stream: str
    event: Literal[
        "connecting",
        "connected",
        "authenticated",
        "subscribed",
        "disconnected",
        "reconnect_scheduled",
        "error",
        "stale",
        "fresh",
        "heartbeat",
    ]
    detail: str = ""
    at: datetime
