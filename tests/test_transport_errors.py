"""Real adapters map library errors to OSError subclasses (R-23, failure-check 2026-11-25).

httpx and websockets raise their own exception types, which are not OSError. Every
caller's back-off path catches OSError, so without the mapping one SEC timeout or one
refused stream handshake killed the task. These tests drive the real adapters (an
httpx MockTransport and a local socket server), not fakes."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import pytest

from family_desk_spike.applog import AppLog
from family_desk_spike.config import parse_config
from family_desk_spike.core.ratelimit import TokenBucket
from family_desk_spike.data.edgar import EdgarPoller, RateLimitedSec
from family_desk_spike.data.stream_client import StreamClosedError, websockets_connector
from family_desk_spike.net.readonly_http import HttpxTransport, ReadOnlyHttp, TransportFailureError
from tests.fakes.clock import FakeClock
from tests.fakes.env import FAKE_UA

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).parent / "fixtures"
CFG = parse_config((ROOT / "config" / "spike.toml").read_text(encoding="utf-8"))
FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"


def _transport(handler: httpx.MockTransport) -> HttpxTransport:
    return HttpxTransport(client=httpx.AsyncClient(transport=handler, follow_redirects=False))


def test_httpx_timeout_becomes_an_oserror_without_the_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    t = _transport(httpx.MockTransport(handler))

    async def go() -> None:
        try:
            await t.get(FEED, params={}, headers={}, timeout_s=1.0)
        finally:
            await t.aclose()

    with pytest.raises(TransportFailureError) as info:
        asyncio.run(go())
    assert isinstance(info.value, OSError)
    assert str(info.value) == "ReadTimeout" and "sec.gov" not in str(info.value)


def test_edgar_poller_survives_a_real_timeout_and_recovers(tmp_path: Path) -> None:
    calls = {"n": 0}
    feed = (FIX / "edgar_getcurrent_synthetic.xml").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectTimeout("timed out", request=request)
        return httpx.Response(200, content=feed)

    clock = FakeClock()
    t = _transport(httpx.MockTransport(handler))
    sec = RateLimitedSec(http=ReadOnlyHttp(t), base_url="https://www.sec.gov", user_agent=FAKE_UA,
                         clock=clock, sleep=clock.sleep, bucket=TokenBucket(rate=1.0))  # fmt: skip
    log = AppLog(tmp_path / "log.jsonl", clock=clock).open()
    poller = EdgarPoller(sec=sec, cfg=CFG.edgar, cik_filter={}, log=log, clock=clock,
                         stop=asyncio.Event(), rand=lambda: 0.5)  # fmt: skip

    async def go() -> None:
        try:
            for _ in range(2):
                await clock.sleep(await poller.poll_once())
        finally:
            await t.aclose()

    asyncio.run(go())
    log.close()
    assert poller.stats.errors == {"network": 1}
    assert poller.stats.ok_cycles == 1 and poller.stats.pre_filter_counts == [5]
    recs = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    err = next(r for r in recs if r["source"] == "edgar.error")
    assert err["payload"] == {"kind": "network", "detail": "TransportFailureError"}


def test_refused_websocket_handshake_becomes_stream_closed() -> None:
    async def serve(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await reader.readuntil(b"\r\n\r\n")
        writer.write(b"HTTP/1.1 429 Too Many Requests\r\nContent-Length: 0\r\n\r\n")
        await writer.drain()
        writer.close()

    async def go() -> None:
        server = await asyncio.start_server(serve, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            await websockets_connector(f"ws://127.0.0.1:{port}/v2/iex")
        finally:
            server.close()
            await server.wait_closed()

    with pytest.raises(StreamClosedError, match="handshake failed: InvalidStatus"):
        asyncio.run(go())
