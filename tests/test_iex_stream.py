from __future__ import annotations

import asyncio
import json
from pathlib import Path

from family_desk_spike.applog import AppLog, verify_lines
from family_desk_spike.config import load_settings, parse_config
from family_desk_spike.data.iex_stream import QuoteMonitor, build_quote_session
from family_desk_spike.data.stream_client import StreamCounters
from tests.fakes.clock import FakeClock
from tests.fakes.env import FAKE_KEY_ID, FAKE_SECRET, fake_env
from tests.fakes.websocket import (
    AUTHENTICATED,
    CONNECTED,
    Close,
    FakeConnector,
    FakeWebSocket,
    Stall,
    Step,
    frame,
)

ROOT = Path(__file__).resolve().parents[1]
CFG = parse_config((ROOT / "config" / "spike.toml").read_text(encoding="utf-8"))
WATCH = CFG.watchlist.symbols
ACK = frame({"T": "subscription", "trades": [], "quotes": list(WATCH), "bars": []})


def quote(sym: str, bp: float, ap: float, t: str = "2026-11-30T15:30:00Z") -> str:
    return frame(
        {"T": "q", "S": sym, "bp": bp, "bs": 1, "ap": ap, "as": 1, "bx": "V", "ax": "V", "c": ["R"],
         "z": "C", "t": t}
    )  # fmt: skip


def _run(
    tmp_path: Path, sessions: list[list[Step] | BaseException]
) -> tuple[StreamCounters, QuoteMonitor, FakeConnector, FakeClock, list[dict[str, object]]]:
    clock = FakeClock()
    stop = asyncio.Event()
    sockets: list[FakeWebSocket | BaseException] = [
        s if isinstance(s, BaseException) else FakeWebSocket(list(s), clock) for s in sessions
    ]
    last = next((s for s in reversed(sockets) if isinstance(s, FakeWebSocket)), None)
    if last is not None:
        last.on_exhausted = stop.set
    connector = FakeConnector(sockets, on_exhausted=stop.set)
    path = tmp_path / "log.jsonl"
    log = AppLog(path, clock=clock).open()
    session, monitor = build_quote_session(
        url=CFG.alpaca.stock_stream_url,
        connector=connector,
        settings=load_settings(fake_env()),
        symbols=WATCH,
        log=log,
        clock=clock,
        streams=CFG.streams,
        stop=stop,
        sleep=clock.sleep,
    )
    counters = asyncio.run(session.run())
    log.close()
    text = path.read_text(encoding="utf-8")
    assert verify_lines(text).ok
    assert FAKE_KEY_ID not in text and FAKE_SECRET not in text  # auth frame never logged
    return counters, monitor, connector, clock, [json.loads(line) for line in text.splitlines()]


def _events(records: list[dict[str, object]], name: str) -> list[str]:
    return [
        str(r["payload"]["event"])  # type: ignore[index]
        for r in records
        if r["source"] == f"{name}.event"
    ]


def test_happy_path_auth_subscribe_ack_quotes(tmp_path: Path) -> None:
    counters, monitor, connector, _, recs = _run(
        tmp_path,
        [[CONNECTED, AUTHENTICATED, ACK, quote("AAPL", 230.10, 230.14), quote("SPY", 600, 600.02)]],
    )
    assert connector.urls == ["wss://stream.data.alpaca.markets/v2/iex"]
    assert len(counters.acks) == 1 and counters.acks[0].quotes == WATCH
    assert [r["source"] for r in recs].count("iex.ack") == 1
    assert [r["source"] for r in recs].count("quote") == 2
    assert _events(recs, "iex")[:4] == ["connecting", "connected", "authenticated", "subscribed"]
    s = monitor.summary()["per_symbol"]
    assert isinstance(s, dict)
    assert s["AAPL"]["count"] == 1 and s["MSFT"]["count"] == 0
    assert s["AAPL"]["spread_bps_median"] is not None


def test_auth_and_subscribe_frames_sent_in_order(tmp_path: Path) -> None:
    clock = FakeClock()
    stop = asyncio.Event()
    ws = FakeWebSocket([CONNECTED, AUTHENTICATED, ACK], clock, on_exhausted=stop.set)
    log = AppLog(tmp_path / "l.jsonl", clock=clock).open()
    session, _ = build_quote_session(
        url="wss://x", connector=FakeConnector([ws]), settings=load_settings(fake_env()),
        symbols=WATCH, log=log, clock=clock, streams=CFG.streams, stop=stop, sleep=clock.sleep,
    )  # fmt: skip
    asyncio.run(session.run())
    log.close()
    sent = [json.loads(s) for s in ws.sent]
    assert sent[0] == {"action": "auth", "key": FAKE_KEY_ID, "secret": FAKE_SECRET}
    assert sent[1] == {"action": "subscribe", "quotes": list(WATCH)}


def test_silent_stall_marks_every_symbol_stale_then_fresh(tmp_path: Path) -> None:
    _, monitor, _, _, recs = _run(
        tmp_path,
        [[CONNECTED, AUTHENTICATED, ACK, Stall(61), quote("AAPL", 1, 1.01)]],
    )
    stale = [r["payload"] for r in recs if r["source"] == "iex.staleness"]
    states = [(p["symbol"], p["state"]) for p in stale]  # type: ignore[index]
    assert {s for s, st in states if st == "stale"} == set(WATCH)
    assert ("AAPL", "fresh") in states
    assert monitor.tracker.stale == set(WATCH) - {"AAPL"}


def test_disconnect_then_reconnect_with_backoff(tmp_path: Path) -> None:
    counters, _, connector, clock, recs = _run(
        tmp_path,
        [
            [CONNECTED, AUTHENTICATED, ACK, Close("server going away")],
            [CONNECTED, AUTHENTICATED, ACK, quote("MSFT", 400, 400.1)],
        ],
    )
    assert counters.disconnects == 1 and counters.connects == 2
    assert len(connector.urls) == 2
    ev = _events(recs, "iex")
    assert "disconnected" in ev and "reconnect_scheduled" in ev
    assert len(clock.sleeps) == 1
    assert CFG.streams.backoff_initial_seconds / 2 <= clock.sleeps[0]
    assert clock.sleeps[0] <= CFG.streams.backoff_max_seconds


def test_connection_limit_error_waits_long_backoff(tmp_path: Path) -> None:
    limit = frame({"T": "error", "code": 406, "msg": "connection limit exceeded"})
    counters, _, _, clock, _ = _run(
        tmp_path, [[CONNECTED, AUTHENTICATED, limit], [CONNECTED, AUTHENTICATED, ACK]]
    )
    assert clock.sleeps[0] == CFG.streams.connection_limit_backoff_seconds
    assert counters.errors == 1 and len(counters.acks) == 1


def test_auth_failure_is_fatal_no_reconnect(tmp_path: Path) -> None:
    failed = frame({"T": "error", "code": 402, "msg": "auth failed"})
    counters, _, connector, clock, recs = _run(tmp_path, [[CONNECTED, failed], [CONNECTED]])
    assert counters.fatal == "code=402 msg=auth failed"
    assert len(connector.urls) == 1
    assert clock.sleeps == []
    assert "error" in _events(recs, "iex")


def test_repeated_connect_failures_never_hot_loop(tmp_path: Path) -> None:
    failures: list[list[Step] | BaseException] = [OSError("refused") for _ in range(12)]
    counters, _, _conn, clock, _ = _run(tmp_path, failures)
    assert counters.errors >= 12
    assert len(clock.sleeps) >= 12
    assert min(clock.sleeps) >= CFG.streams.backoff_initial_seconds / 2
    assert max(clock.sleeps) <= CFG.streams.backoff_max_seconds
    assert clock.sleeps[-1] >= CFG.streams.backoff_max_seconds / 2  # grew to the cap


def test_malformed_and_trade_frames_counted(tmp_path: Path) -> None:
    trade = frame({"T": "t", "S": "SPY", "p": 1})
    counters, _, _, _, _ = _run(tmp_path, [[CONNECTED, AUTHENTICATED, ACK, "garbage{", trade]])
    assert counters.malformed == 1 and counters.ignored == 1
