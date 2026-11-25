"""IEX quote stream (D13): subscribe the watchlist's quotes, log every quote, track
per-symbol staleness (stall = connected but silent), update rate, spread and clock skew."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field

from family_desk_spike.applog import AppLog, utc_iso
from family_desk_spike.config import Settings, StreamsConfig
from family_desk_spike.core.clock import Clock
from family_desk_spike.core.staleness import SeriesStats, StalenessTracker, summarize
from family_desk_spike.data.stream_client import Connector, Sleep, StreamSession, symbols_list
from family_desk_spike.models import Quote
from family_desk_spike.parse.stream import Message

STREAM = "iex"


def quote_payload(q: Quote) -> dict[str, object]:
    return {
        "S": q.symbol,
        "bp": str(q.bid_price),
        "bs": str(q.bid_size),
        "ap": str(q.ask_price),
        "as": str(q.ask_size),
        "bx": q.bid_exchange,
        "ax": q.ask_exchange,
        "c": list(q.conditions),
        "z": q.tape,
    }


@dataclass
class QuoteMonitor:
    symbols: tuple[str, ...]
    log: AppLog
    clock: Clock
    stale_after: float
    started_mono: float
    stats: dict[str, SeriesStats] = field(default_factory=dict)
    tracker: StalenessTracker = field(init=False)
    unexpected_symbols: int = 0

    def __post_init__(self) -> None:
        self.tracker = StalenessTracker(self.stale_after, self.started_mono, self.symbols)

    def on_message(self, msg: Message) -> None:
        if not isinstance(msg, Quote):
            return
        if msg.symbol not in self.symbols:
            self.unexpected_symbols += 1
        received = self.clock()
        skew_ms = (received - msg.timestamp).total_seconds() * 1000
        spread = msg.spread_bps
        self.stats.setdefault(msg.symbol, SeriesStats()).add(
            float(spread) if spread is not None else None, skew_ms
        )
        self.log.append("quote", quote_payload(msg), source_ts=utc_iso(msg.timestamp))
        for key, state, gap in self.tracker.observe(msg.symbol, self.clock.monotonic()):
            self._staleness_event(key, state, gap)

    def on_tick(self) -> None:
        for key, state, gap in self.tracker.check(self.clock.monotonic()):
            self._staleness_event(key, state, gap)

    def _staleness_event(self, key: str, state: str, gap: float) -> None:
        self.log.append(
            f"{STREAM}.staleness",
            {"symbol": key, "state": state, "gap_s": round(gap, 3), "at": utc_iso(self.clock())},
        )

    def summary(self) -> dict[str, object]:
        now = self.clock.monotonic()
        duration = now - self.started_mono
        return {
            "per_symbol": summarize(self.stats, self.symbols, duration),
            "stale_events": dict(self.tracker.stale_events),
            "max_gap_s": {k: round(v, 3) for k, v in self.tracker.max_gaps(now).items()},
            "unexpected_symbols": self.unexpected_symbols,
        }


def build_quote_session(
    *,
    url: str,
    connector: Connector,
    settings: Settings,
    symbols: Sequence[str],
    log: AppLog,
    clock: Clock,
    streams: StreamsConfig,
    stop: asyncio.Event,
    sleep: Sleep | None = None,
) -> tuple[StreamSession, QuoteMonitor]:
    monitor = QuoteMonitor(
        symbols=tuple(symbols_list(symbols)),
        log=log,
        clock=clock,
        stale_after=streams.stale_after_seconds,
        started_mono=clock.monotonic(),
    )
    session = StreamSession(
        name=STREAM,
        url=url,
        connector=connector,
        settings=settings,
        subscribe={"quotes": list(monitor.symbols)},
        log=log,
        clock=clock,
        on_message=monitor.on_message,
        on_tick=monitor.on_tick,
        stop=stop,
        backoff_initial=streams.backoff_initial_seconds,
        backoff_max=streams.backoff_max_seconds,
        connection_limit_backoff=streams.connection_limit_backoff_seconds,
        sleep=sleep,
    )
    return session, monitor
