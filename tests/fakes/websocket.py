from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from family_desk_spike.data.stream_client import StreamClosedError, WebSocketLike
from tests.fakes.clock import FakeClock


@dataclass(frozen=True)
class Stall:
    """Connected but silent for `seconds` (one recv timeout)."""

    seconds: float


@dataclass(frozen=True)
class Close:
    reason: str = "closed by server"


@dataclass(frozen=True)
class Raise:
    exc: BaseException


Step = str | Stall | Close | Raise


def frame(*msgs: dict[str, Any]) -> str:
    return json.dumps(list(msgs))


CONNECTED = frame({"T": "success", "msg": "connected"})
AUTHENTICATED = frame({"T": "success", "msg": "authenticated"})


@dataclass
class FakeWebSocket:
    script: list[Step]
    clock: FakeClock
    on_exhausted: Callable[[], None] = lambda: None
    sent: list[str] = field(default_factory=list)
    closed: bool = False

    async def send(self, data: str) -> None:
        if self.closed:
            raise StreamClosedError("send on closed socket")
        self.sent.append(data)

    async def recv(self) -> str | bytes:
        await asyncio.sleep(0)
        if not self.script:
            self.on_exhausted()
            raise TimeoutError
        step = self.script.pop(0)
        if isinstance(step, Stall):
            self.clock.advance(step.seconds)
            raise TimeoutError
        if isinstance(step, Close):
            self.closed = True
            raise StreamClosedError(step.reason)
        if isinstance(step, Raise):
            raise step.exc
        self.clock.advance(0.01)
        return step

    async def close(self) -> None:
        self.closed = True


@dataclass
class FakeConnector:
    """Each call hands out the next socket (or raises the next exception)."""

    sockets: list[FakeWebSocket | BaseException]
    on_exhausted: Callable[[], None] = lambda: None
    urls: list[str] = field(default_factory=list)

    async def __call__(self, url: str) -> WebSocketLike:
        self.urls.append(url)
        if not self.sockets:
            self.on_exhausted()
            raise OSError("no more fake sockets")
        nxt = self.sockets.pop(0)
        if isinstance(nxt, BaseException):
            raise nxt
        return nxt
