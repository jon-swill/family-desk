"""D16: the whole runner against fakes. No network, no .env, no real clock."""

from __future__ import annotations

import asyncio
import json
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import pytest

from family_desk_spike.applog import verify_lines
from family_desk_spike.data.stream_client import WebSocketLike
from family_desk_spike.runner import (
    EXIT_INTERRUPTED,
    EXIT_OK,
    EXIT_STARTUP_REFUSED,
    EXIT_WINDOW_REFUSED,
    Deps,
    RunState,
    run_sync,
)
from tests.fakes.clock import FakeClock
from tests.fakes.env import FAKE_EMAIL, FAKE_KEY_ID, FAKE_SECRET, FakeGit, fake_env
from tests.fakes.http import FakeHttp
from tests.fakes.websocket import AUTHENTICATED, CONNECTED, FakeWebSocket, Raise, Step, frame

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).parent / "fixtures"
PAPER = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
SEC = "https://www.sec.gov"
IEX_URL = "wss://stream.data.alpaca.markets/v2/iex"
NEWS_URL = "wss://stream.data.alpaca.markets/v1beta1/news"
WATCH = ["SPY", "QQQ", "IWM", "AAPL", "MSFT"]


def _quote(sym: str) -> str:
    return frame(
        {"T": "q", "S": sym, "bp": 100, "bs": 1, "ap": 100.02, "as": 1, "bx": "V", "ax": "V",
         "c": ["R"], "z": "C", "t": "2026-11-30T15:30:00Z"}
    )  # fmt: skip


IEX_SCRIPT: list[Step] = [
    CONNECTED,
    AUTHENTICATED,
    frame({"T": "subscription", "trades": [], "quotes": WATCH, "bars": []}),
    *[_quote(s) for s in WATCH],
    _quote("AAPL"),
]
NEWS_SCRIPT: list[Step] = [
    CONNECTED,
    AUTHENTICATED,
    frame({"T": "subscription", "news": WATCH}),
    frame(
        {
            "T": "n",
            "id": 40000001,
            "headline": "dup of REST item",
            "symbols": ["AAPL"],
            "created_at": "2026-11-30T14:00:00Z",
            "url": "",
            "source": "benzinga",
        },
        {
            "T": "n",
            "id": 50,
            "headline": "fresh",
            "symbols": ["MSFT"],
            "created_at": "2026-11-30T15:31:00Z",
            "url": "",
            "source": "benzinga",
        },
    ),
]


@dataclass
class UrlConnector:
    sockets: dict[str, list[FakeWebSocket]]
    urls: list[str] = field(default_factory=list)

    async def __call__(self, url: str) -> WebSocketLike:
        self.urls.append(url)
        queue = self.sockets.get(url, [])
        if not queue:
            raise OSError("no fake socket")
        return queue.pop(0)


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    for name in ("spike.toml", "spike.toml.sha256"):
        shutil.copy(ROOT / "config" / name, tmp_path / "config" / name)
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    return tmp_path


def _fix(name: str) -> bytes:
    return (FIX / name).read_bytes()


def _http(clock_fixture: str = "alpaca_clock_open.json") -> FakeHttp:
    return (
        FakeHttp()
        .add_json(f"{PAPER}/v2/clock", (FIX / clock_fixture).read_bytes())
        .add_json(f"{PAPER}/v2/account", (FIX / "alpaca_account.json").read_bytes())
        .add_json(f"{PAPER}/v2/positions", (FIX / "alpaca_positions_spy.json").read_bytes())
        .add_json(f"{DATA}/v1beta1/news", (FIX / "alpaca_news_page.json").read_bytes())
        .add_json(f"{SEC}/files/company_tickers.json", _fix("company_tickers_subset.json"))
        .add_json(f"{SEC}/cgi-bin/browse-edgar", _fix("edgar_getcurrent_synthetic.xml"))
    )


@dataclass
class Harness:
    tmp_path: Path
    iex: list[Step] = field(default_factory=lambda: list(IEX_SCRIPT))
    news: list[Step] = field(default_factory=lambda: list(NEWS_SCRIPT))
    env: dict[str, str] = field(default_factory=fake_env)
    git: FakeGit = field(default_factory=FakeGit)
    http: FakeHttp = field(default_factory=_http)
    stop_when_streams_done: bool = True
    timer_fires: bool = False

    def run(self) -> tuple[RunState, list[dict[str, object]], str]:
        clock = FakeClock(now_utc=datetime(2026, 11, 30, 15, 30, tzinfo=UTC))
        stop = asyncio.Event()
        done: set[str] = set()

        def exhausted(name: str) -> None:
            done.add(name)
            if self.stop_when_streams_done and done >= {"iex", "news"}:
                stop.set()

        connector = UrlConnector(
            {
                IEX_URL: [FakeWebSocket(self.iex, clock, on_exhausted=lambda: exhausted("iex"))],
                NEWS_URL: [FakeWebSocket(self.news, clock, on_exhausted=lambda: exhausted("news"))],
            }
        )

        async def timer_sleep(seconds: float) -> None:
            if self.timer_fires:
                for _ in range(50):
                    await asyncio.sleep(0)
                return
            await asyncio.Event().wait()

        root = _repo(self.tmp_path)
        deps = Deps(
            root=root, transport=self.http, connector=connector, clock=clock, git=self.git,
            env=self.env, sleep=clock.sleep, timer_sleep=timer_sleep, rand=lambda: 0.5,
        )  # fmt: skip
        state = run_sync(deps, 35, stop)
        logs = list((root / "logs" / "spike").glob("*.jsonl"))
        text = logs[0].read_text(encoding="utf-8") if logs else ""
        recs = [json.loads(line) for line in text.splitlines()]
        return state, recs, text


def _sources(recs: list[dict[str, object]]) -> list[str]:
    return [str(r["source"]) for r in recs]


def test_full_run_against_fakes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    state, recs, text = Harness(tmp_path).run()
    assert state.exit_code == EXIT_OK, state.lines
    result = verify_lines(text)
    assert result.ok
    out = capsys.readouterr().out
    assert "chain OK" in out and f"head_hash={result.head_hash}" in out
    assert f"seq_last={result.seq_last}" in out
    for value in (FAKE_KEY_ID, FAKE_SECRET, FAKE_EMAIL):
        assert value not in text and value not in out
    src = _sources(recs)
    for needed in ("startup", "clock", "run_window", "account", "positions", "news.rest",
                   "edgar.cik_map", "iex.ack", "news.ack", "quote", "news.stream",
                   "edgar.cycle", "summary"):  # fmt: skip
        assert needed in src, needed
    assert src[-1] == "summary"
    summary = recs[-1]["payload"]
    assert isinstance(summary, dict)
    assert summary["positions_count"] == 1 and summary["positions_symbols"] == ["SPY"]
    assert summary["news_rest_items"] == 2 and summary["news_rest_watchlist"] == 1
    assert summary["news_stream"]["stream_items"] == 1  # REST id deduped
    assert summary["quotes"]["per_symbol"]["AAPL"]["count"] == 2
    assert summary["edgar"]["pre_filter_entries_min"] == 5
    assert summary["edgar"]["max_requests_in_any_1s"] == 1
    assert summary["edgar"]["label"] == "feed live + filter tested offline"
    assert len(summary["streams"]["iex"]["acks"]) == 1
    account = next(r for r in recs if r["source"] == "account")["payload"]
    assert "cash" not in account and "equity" not in account  # type: ignore[operator]
    assert "PA0000000000" not in text


def test_only_get_requests_to_allowlisted_paths(tmp_path: Path) -> None:
    h = Harness(tmp_path)
    h.run()
    paths = {url for url, _, _ in h.http.calls}
    assert paths <= {
        f"{PAPER}/v2/clock",
        f"{PAPER}/v2/account",
        f"{PAPER}/v2/positions",
        f"{DATA}/v1beta1/news",
        f"{SEC}/files/company_tickers.json",
        f"{SEC}/cgi-bin/browse-edgar",
    }


def test_timer_ends_the_run(tmp_path: Path) -> None:
    h = Harness(tmp_path, stop_when_streams_done=False, timer_fires=True)
    state, recs, text = h.run()
    assert state.exit_code == EXIT_OK
    assert verify_lines(text).ok and _sources(recs)[-1] == "summary"


def test_keyboard_interrupt_from_a_source_flushes_and_summarises(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    iex = [*IEX_SCRIPT[:4], Raise(KeyboardInterrupt())]
    state, recs, text = Harness(tmp_path, iex=iex, stop_when_streams_done=False).run()
    assert state.exit_code == EXIT_INTERRUPTED
    assert verify_lines(text).ok
    src = _sources(recs)
    assert "shutdown" in src and src[-1] == "summary"
    out = capsys.readouterr().out
    assert "interrupted (Ctrl+C)" in out and "chain OK" in out


def test_startup_refusal_makes_no_network_call(tmp_path: Path) -> None:
    h = Harness(tmp_path, env=fake_env(APCA_PAPER="false"))
    state, recs, _ = h.run()
    assert state.exit_code == EXIT_STARTUP_REFUSED
    assert h.http.calls == []
    assert recs == []  # refused before the log opens
    assert any("codes=paper_flag" in line for line in state.lines)


def test_dirty_tree_refuses_live_run(tmp_path: Path) -> None:
    h = Harness(tmp_path, git=FakeGit(porcelain=" M config/spike.toml\n"))
    state, _, _ = h.run()
    assert state.exit_code == EXIT_STARTUP_REFUSED
    assert h.http.calls == []


def test_closed_market_refuses_before_any_stream(tmp_path: Path) -> None:
    closed = tmp_path / "closed.json"
    closed.write_text(
        '{"timestamp":"2026-11-28T10:30:00-05:00","is_open":false,'
        '"next_open":"2026-11-30T09:30:00-05:00","next_close":"2026-11-30T16:00:00-05:00"}',
        encoding="utf-8",
    )
    http = FakeHttp().add_json(f"{PAPER}/v2/clock", closed.read_bytes())
    sub = tmp_path / "repo"
    sub.mkdir()
    h = Harness(sub, http=http)
    state, recs, text = h.run()
    assert state.exit_code == EXIT_WINDOW_REFUSED
    assert [c[0] for c in http.calls] == [f"{PAPER}/v2/clock"]
    assert "quote" not in _sources(recs) and verify_lines(text).ok
    assert any("market closed" in line for line in state.lines)
