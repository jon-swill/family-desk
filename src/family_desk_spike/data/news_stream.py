"""Alpaca News stream (D14): subscribe the watchlist, dedupe by news id, keep metadata
only (id, headline, symbols, url, source, timestamps). Headline text is inert data: it is
never parsed for meaning, evaluated, templated or sent anywhere (inv. 6). A quiet
stream logs a `heartbeat` so silence is visible, not assumed (P-02).

A heartbeat proves only that the socket is open, not that the subscription delivers.
So the stream is also cross-checked against REST: watchlist items that REST has and the
stream never delivered are logged as a `news.stall`, not as silence."""

from __future__ import annotations

import asyncio
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from family_desk_spike.applog import AppLog, utc_iso
from family_desk_spike.broker.alpaca_readonly import ApiError
from family_desk_spike.config import Settings, StreamsConfig
from family_desk_spike.core.clock import Clock
from family_desk_spike.data.news_rest import fetch_news_window
from family_desk_spike.data.stream_client import Connector, Sleep, StreamSession, symbols_list
from family_desk_spike.models import NewsItem
from family_desk_spike.net.readonly_http import ReadOnlyHttp
from family_desk_spike.parse.alpaca_rest import ParseError
from family_desk_spike.parse.stream import Message

STREAM = "news"
# Owner decision 2026-11-25: subscribe to all news ("*", Alpaca's documented example) so
# every item proves the stream delivers (P-02 known positive, like EDGAR's pre-filter
# count); our code filters to the watchlist. Off-watchlist items are counted, never logged.
SUBSCRIBE_ALL = ["*"]


def news_payload(n: NewsItem) -> dict[str, object]:
    return {
        "id": n.id,
        "headline": n.headline,
        "symbols": list(n.symbols),
        "url": n.url,
        "source": n.source,
        "created_at": utc_iso(n.created_at),
        "updated_at": utc_iso(n.updated_at) if n.updated_at else None,
    }


@dataclass
class NewsDeduper:
    seen: set[int] = field(default_factory=set)
    duplicates: int = 0

    def first_time(self, news_id: int) -> bool:
        if news_id in self.seen:
            self.duplicates += 1
            return False
        self.seen.add(news_id)
        return True


STALL_VERDICTS = frozenset({"stall", "partial"})


@dataclass(frozen=True)
class CrossCheck:
    """REST watchlist items created in [window_start, cutoff] vs what the stream delivered."""

    window_start: datetime
    cutoff: datetime
    rest_watchlist: int
    delivered: int
    missed_ids: tuple[int, ...]
    pending: int  # REST watchlist items newer than the cutoff, not yet delivered
    verdict: str  # ok | stall | partial | no_positive_case


def cross_check(
    rest_items: Iterable[NewsItem],
    stream_ids: set[int],
    symbols: Sequence[str],
    window_start: datetime,
    cutoff: datetime,
) -> CrossCheck:
    """Pure. `stall`: REST has judged items and the stream delivered none of them.
    `partial`: some missed. `no_positive_case`: nothing to compare, so the stream's
    silence is still unproven (P-02), not "ok"."""
    wanted = set(symbols)
    tagged = {
        n.id: n
        for n in rest_items
        if wanted.intersection(n.symbols) and n.created_at >= window_start
    }
    judged = [n for n in tagged.values() if n.created_at <= cutoff]
    missed = tuple(sorted(n.id for n in judged if n.id not in stream_ids))
    pending = sum(1 for n in tagged.values() if n.created_at > cutoff and n.id not in stream_ids)
    delivered = len(judged) - len(missed)
    if not judged:
        verdict = "no_positive_case"
    elif not missed:
        verdict = "ok"
    elif delivered == 0:
        verdict = "stall"
    else:
        verdict = "partial"
    return CrossCheck(window_start, cutoff, len(judged), delivered, missed, pending, verdict)


@dataclass
class NewsMonitor:
    symbols: tuple[str, ...]
    log: AppLog
    clock: Clock
    heartbeat_after: float
    started_mono: float
    dedupe: NewsDeduper = field(default_factory=NewsDeduper)
    stream_items: int = 0  # unique items of any symbol: the liveness count
    watchlist_items: int = 0
    heartbeats: int = 0
    stream_ids: set[int] = field(default_factory=set)  # every id the stream delivered
    verdicts: Counter[str] = field(default_factory=Counter)
    missed: set[int] = field(default_factory=set)
    _last_activity: float = field(init=False)

    def __post_init__(self) -> None:
        self._last_activity = self.started_mono

    def seed(self, ids: Sequence[int]) -> None:
        """Mark REST-fetched ids as seen so the stream doesn't double count them."""
        self.dedupe.seen.update(ids)

    def on_message(self, msg: Message) -> None:
        if not isinstance(msg, NewsItem):
            return
        self._last_activity = self.clock.monotonic()
        self.stream_ids.add(msg.id)
        if not self.dedupe.first_time(msg.id):
            return
        self.stream_items += 1
        if not set(self.symbols).intersection(msg.symbols):
            return  # counted for liveness only; no metadata kept (C-7: store only what we use)
        self.watchlist_items += 1
        self.log.append("news.stream", news_payload(msg), source_ts=utc_iso(msg.created_at))

    def on_tick(self) -> None:
        now = self.clock.monotonic()
        if now - self._last_activity >= self.heartbeat_after:
            self.heartbeats += 1
            self._last_activity = now
            self.log.append(
                f"{STREAM}.heartbeat",
                {"detail": "no news in window; connection alive", "window_s": self.heartbeat_after},
            )

    def record_cross_check(self, result: CrossCheck, *, final: bool) -> None:
        self.verdicts[result.verdict] += 1
        self.missed.update(result.missed_ids)
        self.log.append(
            f"{STREAM}.cross_check",
            {
                "window_start": utc_iso(result.window_start),
                "cutoff": utc_iso(result.cutoff),
                "rest_watchlist": result.rest_watchlist,
                "delivered": result.delivered,
                "missed": len(result.missed_ids),
                "pending": result.pending,
                "verdict": result.verdict,
                "final": final,
            },
        )
        if result.verdict in STALL_VERDICTS:
            self.log.append(
                f"{STREAM}.stall",
                {
                    "detail": "REST has watchlist news the stream never delivered; "
                    "heartbeats only prove the socket is open",
                    "verdict": result.verdict,
                    "missed_ids": list(result.missed_ids[:50]),
                },
            )

    def record_cross_check_error(self, kind: str) -> None:
        self.verdicts["error"] += 1
        self.log.append(f"{STREAM}.cross_check", {"verdict": "error", "detail": kind})

    def summary(self) -> dict[str, object]:
        return {
            "stream_items": self.stream_items,
            "stream_watchlist_items": self.watchlist_items,
            "delivery_proven": self.stream_items > 0,
            "duplicates_dropped": self.dedupe.duplicates,
            "heartbeats": self.heartbeats,
            "cross_check": {
                "verdicts": dict(sorted(self.verdicts.items())),
                "missed_total": len(self.missed),
                "stalled": bool(self.verdicts["stall"] or self.verdicts["partial"]),
            },
        }


async def run_news_cross_check(
    monitor: NewsMonitor,
    http: ReadOnlyHttp,
    *,
    data_base_url: str,
    settings: Settings,
    window_start: datetime,
    grace_seconds: float,
    final: bool,
) -> CrossCheck | None:
    """One REST cross-check of the stream. Errors are logged, never raised."""
    now = monitor.clock()
    try:
        items, _ = await fetch_news_window(
            http,
            data_base_url=data_base_url,
            settings=settings,
            symbols=monitor.symbols,
            start=window_start,
            end=now,
        )
    except (ApiError, OSError, ParseError) as exc:
        monitor.record_cross_check_error(type(exc).__name__)
        return None
    cutoff = now - timedelta(seconds=grace_seconds)
    result = cross_check(items, monitor.stream_ids, monitor.symbols, window_start, cutoff)
    monitor.record_cross_check(result, final=final)
    return result


def build_news_session(
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
) -> tuple[StreamSession, NewsMonitor]:
    monitor = NewsMonitor(
        symbols=tuple(symbols_list(symbols)),
        log=log,
        clock=clock,
        heartbeat_after=streams.stale_after_seconds,
        started_mono=clock.monotonic(),
    )
    session = StreamSession(
        name=STREAM,
        url=url,
        connector=connector,
        settings=settings,
        subscribe={"news": list(SUBSCRIBE_ALL)},
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
