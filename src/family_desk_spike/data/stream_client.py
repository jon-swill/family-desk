"""Alpaca WebSocket session runner shared by the quote and news streams (D13, D14, NFR-4).

Message-driven state machine: `connected` -> send auth; `authenticated` -> send
subscribe; `subscription` -> log the ack. Every connect, disconnect, error, stall and
reconnect is logged as a StreamEvent; nothing is silent. Auth frames are never logged.

Error policy (codes per Alpaca's stream docs; confirmed in A2):
- connection limit (406): wait `connection_limit_backoff_seconds`, then reconnect.
- auth failed / insufficient subscription / bad request (400, 402, 405, 409, 410):
  fatal for this stream. It stops; other sources keep running. No hot reconnect loop.
- anything else, or a dropped connection: capped exponential backoff with jitter.
"""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Protocol

from family_desk_spike.applog import AppLog
from family_desk_spike.config import Settings
from family_desk_spike.core.backoff import backoff_delay
from family_desk_spike.core.clock import Clock
from family_desk_spike.models import NewsItem, Quote, StreamControl, StreamEvent, SubscriptionAck
from family_desk_spike.parse.stream import Message, parse_frame

CONNECTION_LIMIT = 406
FATAL_CODES = frozenset({400, 402, 405, 409, 410})


class StreamClosedError(ConnectionError):
    """The socket closed (cleanly or not)."""


class WebSocketLike(Protocol):
    async def send(self, data: str) -> None: ...

    async def recv(self) -> str | bytes: ...

    async def close(self) -> None: ...


Connector = Callable[[str], Awaitable[WebSocketLike]]
Sleep = Callable[[float], Awaitable[None]]


@dataclass
class StreamCounters:
    connects: int = 0
    disconnects: int = 0
    reconnects: int = 0
    errors: int = 0
    frames: int = 0
    malformed: int = 0
    ignored: int = 0
    acks: list[SubscriptionAck] = field(default_factory=list)
    fatal: str | None = None


@dataclass
class StreamSession:
    name: str
    url: str
    connector: Connector
    settings: Settings
    subscribe: dict[str, list[str]]
    log: AppLog
    clock: Clock
    on_message: Callable[[Message], None]
    on_tick: Callable[[], None]
    stop: asyncio.Event
    backoff_initial: float = 1.0
    backoff_max: float = 60.0
    connection_limit_backoff: float = 60.0
    poll_seconds: float = 1.0
    rand: Callable[[], float] = field(default=random.random)  # noqa: S311 - jitter, not crypto
    sleep: Sleep | None = None
    counters: StreamCounters = field(default_factory=StreamCounters)

    def event(self, event: str, detail: str = "") -> None:
        ev = StreamEvent.model_validate(
            {"stream": self.name, "event": event, "detail": detail, "at": self.clock()}
        )
        self.log.append(f"{self.name}.event", ev.model_dump(mode="json"))

    async def _sleep(self, seconds: float) -> None:
        if self.sleep is not None:
            await self.sleep(seconds)
            return
        try:
            await asyncio.wait_for(self.stop.wait(), timeout=seconds)
        except TimeoutError:
            pass

    def _auth_frame(self) -> str:
        return json.dumps(
            {
                "action": "auth",
                "key": self.settings.api_key_id.get_secret_value(),
                "secret": self.settings.api_secret_key.get_secret_value(),
            }
        )

    def _subscribe_frame(self) -> str:
        return json.dumps({"action": "subscribe", **self.subscribe})

    async def run(self) -> StreamCounters:
        attempt = 0
        while not self.stop.is_set():
            wait = await self._one_connection()
            if self.counters.fatal is not None or self.stop.is_set():
                break
            if wait == "subscribed":
                attempt = 0
                wait = None
            attempt += 1
            delay = (
                self.connection_limit_backoff
                if wait == "limit"
                else backoff_delay(
                    attempt, initial=self.backoff_initial, maximum=self.backoff_max, rand=self.rand
                )
            )
            self.counters.reconnects += 1
            self.event("reconnect_scheduled", f"attempt={attempt} delay_s={delay:.2f}")
            await self._sleep(delay)
        return self.counters

    async def _one_connection(self) -> str | None:
        """Returns 'limit' after a connection-limit error, 'subscribed' if a subscription
        was acknowledged before the drop, else None."""
        self.event("connecting", self.url)
        try:
            ws = await self.connector(self.url)
        except (OSError, StreamClosedError, TimeoutError) as exc:
            self.counters.errors += 1
            self.event("error", f"connect failed: {type(exc).__name__}")
            return None
        self.counters.connects += 1
        subscribed = False
        try:
            while not self.stop.is_set():
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=self.poll_seconds)
                except TimeoutError:
                    self.on_tick()
                    continue
                self.counters.frames += 1
                frame = parse_frame(raw, self.name)
                self.counters.malformed += frame.malformed
                self.counters.ignored += frame.ignored
                for msg in frame.messages:
                    outcome = await self._handle(ws, msg)
                    if outcome == "subscribed":
                        subscribed = True
                    elif outcome in ("limit", "fatal", "error"):
                        return "limit" if outcome == "limit" else None
                self.on_tick()
        except OSError as exc:  # StreamClosedError is an OSError
            self.counters.disconnects += 1
            self.event("disconnected", f"{type(exc).__name__}: {str(exc)[:200] or 'closed'}")
            return "subscribed" if subscribed else None
        finally:
            await _close_quietly(ws)
        return None

    async def _handle(self, ws: WebSocketLike, msg: Message) -> str | None:
        if isinstance(msg, StreamControl):
            if msg.kind == "success" and msg.msg == "connected":
                self.event("connected")
                await ws.send(self._auth_frame())
            elif msg.kind == "success" and msg.msg == "authenticated":
                self.event("authenticated")
                await ws.send(self._subscribe_frame())
            elif msg.kind == "error":
                self.counters.errors += 1
                self.event("error", f"code={msg.code} msg={msg.msg}")
                if msg.code == CONNECTION_LIMIT:
                    return "limit"
                if msg.code in FATAL_CODES:
                    self.counters.fatal = f"code={msg.code} msg={msg.msg}"
                    return "fatal"
                return "error"
            return None
        if isinstance(msg, SubscriptionAck):
            self.counters.acks.append(msg)
            self.log.append(f"{self.name}.ack", msg.model_dump(mode="json"))
            self.event("subscribed", _ack_detail(msg))
            return "subscribed"
        if isinstance(msg, Quote | NewsItem):
            self.on_message(msg)
        return None


def _ack_detail(ack: SubscriptionAck) -> str:
    parts = [
        f"{k}={','.join(v)}"
        for k, v in (("quotes", ack.quotes), ("news", ack.news), ("trades", ack.trades))
        if v
    ]
    return " ".join(parts) or "empty"


async def _close_quietly(ws: WebSocketLike) -> None:
    try:
        await ws.close()
    except (OSError, StreamClosedError):
        pass


def symbols_list(symbols: Sequence[str]) -> list[str]:
    return [s.upper() for s in symbols]


# --- I/O edge -------------------------------------------------------------------------


class WebsocketsAdapter:
    """Wraps a `websockets` client connection; maps its close errors to StreamClosedError."""

    def __init__(self, conn: object) -> None:
        self._conn = conn

    async def send(self, data: str) -> None:
        from websockets.exceptions import ConnectionClosed

        try:
            await self._conn.send(data)  # type: ignore[attr-defined]
        except ConnectionClosed as exc:
            raise StreamClosedError(f"close code={exc.rcvd.code if exc.rcvd else None}") from exc

    async def recv(self) -> str | bytes:
        from websockets.exceptions import ConnectionClosed

        try:
            data: str | bytes = await self._conn.recv()  # type: ignore[attr-defined]
        except ConnectionClosed as exc:
            raise StreamClosedError(f"close code={exc.rcvd.code if exc.rcvd else None}") from exc
        return data

    async def close(self) -> None:
        await self._conn.close()  # type: ignore[attr-defined]


async def websockets_connector(url: str) -> WebSocketLike:
    from websockets.asyncio.client import connect

    conn = await connect(url, open_timeout=15, max_size=2**22, ping_interval=20)
    return WebsocketsAdapter(conn)
