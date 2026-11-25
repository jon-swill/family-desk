"""Alpaca News stream (D14): subscribe the watchlist, dedupe by news id, keep metadata
only (id, headline, symbols, url, source, timestamps). Headline text is inert data: it is
never parsed for meaning, evaluated, templated or sent anywhere (inv. 6). A quiet
stream logs a `heartbeat` so silence is visible, not assumed (P-02)."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field

from family_desk_spike.applog import AppLog, utc_iso
from family_desk_spike.config import Settings, StreamsConfig
from family_desk_spike.core.clock import Clock
from family_desk_spike.data.stream_client import Connector, Sleep, StreamSession, symbols_list
from family_desk_spike.models import NewsItem
from family_desk_spike.parse.stream import Message

STREAM = "news"


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


@dataclass
class NewsMonitor:
    symbols: tuple[str, ...]
    log: AppLog
    clock: Clock
    heartbeat_after: float
    started_mono: float
    dedupe: NewsDeduper = field(default_factory=NewsDeduper)
    stream_items: int = 0
    watchlist_items: int = 0
    heartbeats: int = 0
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
        if not self.dedupe.first_time(msg.id):
            return
        self.stream_items += 1
        if set(self.symbols).intersection(msg.symbols):
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

    def summary(self) -> dict[str, object]:
        return {
            "stream_items": self.stream_items,
            "stream_watchlist_items": self.watchlist_items,
            "duplicates_dropped": self.dedupe.duplicates,
            "heartbeats": self.heartbeats,
        }


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
        subscribe={"news": list(monitor.symbols)},
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
