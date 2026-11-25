"""Stream-vs-REST cross-check (P-02): heartbeats with 0 items while REST has watchlist
items is a stall, not silence. Added after B10 run 1 (2026-11-25), where the stream
delivered 0 items in 35 minutes and only heartbeats proved anything."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from family_desk_spike.applog import AppLog
from family_desk_spike.config import load_settings, parse_config
from family_desk_spike.data.news_stream import NewsMonitor, cross_check, run_news_cross_check
from family_desk_spike.models import NewsItem
from family_desk_spike.net.readonly_http import HttpResponse, ReadOnlyHttp
from tests.fakes.clock import FakeClock
from tests.fakes.env import fake_env
from tests.fakes.http import FakeHttp

ROOT = Path(__file__).resolve().parents[1]
CFG = parse_config((ROOT / "config" / "spike.toml").read_text(encoding="utf-8"))
WATCH = CFG.watchlist.symbols
DATA = "https://data.alpaca.markets"
T0 = datetime(2026, 11, 30, 15, 0, tzinfo=UTC)


def item(i: int, minute: int, syms: tuple[str, ...] = ("AAPL",)) -> NewsItem:
    return NewsItem(id=i, headline="h", symbols=syms, created_at=T0 + timedelta(minutes=minute))


def check(items: list[NewsItem], seen: set[int], cutoff_min: int = 30) -> str:
    return cross_check(items, seen, WATCH, T0, T0 + timedelta(minutes=cutoff_min)).verdict


def test_rest_has_items_stream_has_none_is_a_stall() -> None:
    r = cross_check([item(1, 5), item(2, 10)], set(), WATCH, T0, T0 + timedelta(minutes=30))
    assert r.verdict == "stall" and r.missed_ids == (1, 2) and r.delivered == 0


def test_some_missed_is_partial_all_delivered_is_ok() -> None:
    assert check([item(1, 5), item(2, 10)], {1}) == "partial"
    assert check([item(1, 5), item(2, 10)], {1, 2}) == "ok"


def test_nothing_to_compare_is_no_positive_case_not_ok() -> None:
    assert check([], set()) == "no_positive_case"
    assert check([item(1, 5, ("TSLA",))], set()) == "no_positive_case"  # off-watchlist
    assert check([item(1, -5)], set()) == "no_positive_case"  # before the stream started


def test_items_newer_than_the_cutoff_are_pending_not_missed() -> None:
    r = cross_check([item(1, 5), item(2, 40)], {1}, WATCH, T0, T0 + timedelta(minutes=30))
    assert r.verdict == "ok" and r.pending == 1 and r.missed_ids == ()


def test_repeated_rest_ids_count_once() -> None:
    r = cross_check([item(1, 5), item(1, 5)], set(), WATCH, T0, T0 + timedelta(minutes=30))
    assert r.rest_watchlist == 1 and r.missed_ids == (1,)


def _page(*items: dict[str, object]) -> bytes:
    return json.dumps({"news": list(items), "next_page_token": None}).encode()


def _rest_item(i: int, created: str, syms: list[str]) -> dict[str, object]:
    return {"id": i, "headline": "Synthetic", "author": "a", "created_at": created,
            "updated_at": created, "summary": "", "content": "", "url": "", "images": [],
            "symbols": syms, "source": "benzinga"}  # fmt: skip


def _run(tmp_path: Path, http: FakeHttp, delivered: set[int]) -> list[dict[str, object]]:
    clock = FakeClock(now_utc=T0 + timedelta(minutes=40))
    path = tmp_path / "log.jsonl"
    log = AppLog(path, clock=clock).open()
    monitor = NewsMonitor(symbols=WATCH, log=log, clock=clock, heartbeat_after=60,
                          started_mono=clock.monotonic())  # fmt: skip
    monitor.stream_ids.update(delivered)
    asyncio.run(
        run_news_cross_check(
            monitor,
            ReadOnlyHttp(http),
            data_base_url=DATA,
            settings=load_settings(fake_env()),
            window_start=T0,
            grace_seconds=960,
            final=True,
        )
    )
    log.close()
    recs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    recs.append({"source": "_summary", "payload": monitor.summary()})
    return recs


def test_monitor_logs_stall_when_rest_has_what_the_stream_never_sent(tmp_path: Path) -> None:
    body = _page(_rest_item(7, "2026-11-30T15:05:00Z", ["MSFT"]))
    http = FakeHttp().add_json(f"{DATA}/v1beta1/news", body)
    recs = _run(tmp_path, http, delivered=set())
    xc = next(r for r in recs if r["source"] == "news.cross_check")["payload"]
    assert xc["verdict"] == "stall" and xc["rest_watchlist"] == 1 and xc["missed"] == 1  # type: ignore[index]
    stall = next(r for r in recs if r["source"] == "news.stall")["payload"]
    assert stall["missed_ids"] == [7]  # type: ignore[index]
    assert "Synthetic" not in json.dumps(stall)  # ids only, no headline text
    summary = recs[-1]["payload"]["cross_check"]  # type: ignore[index]
    assert summary == {"verdicts": {"stall": 1}, "missed_total": 1, "stalled": True}
    _, params, _ = http.calls[0]
    assert params["symbols"] == ",".join(WATCH)
    assert params["start"] == "2026-11-30T15:00:00Z" and params["end"] == "2026-11-30T15:40:00Z"


def test_quiet_window_logs_no_positive_case_and_no_stall(tmp_path: Path) -> None:
    """B10 run 1's real situation: REST had 0 watchlist items in the run window."""
    http = FakeHttp().add_json(f"{DATA}/v1beta1/news", _page())
    recs = _run(tmp_path, http, delivered=set())
    xc = next(r for r in recs if r["source"] == "news.cross_check")["payload"]
    assert xc["verdict"] == "no_positive_case"  # type: ignore[index]
    assert not any(r["source"] == "news.stall" for r in recs)


def test_rest_error_is_logged_never_raised(tmp_path: Path) -> None:
    http = FakeHttp().add(f"{DATA}/v1beta1/news", HttpResponse(500, b"{}"))
    recs = _run(tmp_path, http, delivered=set())
    xc = next(r for r in recs if r["source"] == "news.cross_check")["payload"]
    assert xc["verdict"] == "error"  # type: ignore[index]
