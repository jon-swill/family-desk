"""Spike runner (D16): wires D9-D15 together. Read-only: account, positions, clock,
quotes, news and filings. No trading path exists anywhere in this package.

Order of operations:
1. Startup self-check (paper host, flag, config hash, version, UA, keys, clean tree).
   Refusal happens before any network call.
2. /v2/clock, then the run-window check. Refusal happens before any stream connects.
3. Account (status and flags only), positions, startup REST news GET, CIK map.
4. Quote stream, news stream and EDGAR poller run until the duration ends or Ctrl+C.
5. Shutdown always writes a summary record, flushes and closes the log, verifies the
   chain and prints seq_last and head_hash (the anchor for D18).

Windows: Ctrl+C is handled by catching KeyboardInterrupt around asyncio.run (the
Proactor loop has no add_signal_handler); cleanup runs in `finally` blocks.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from family_desk_spike.applog import AppLog, Redactor, log_path_for, verify_lines
from family_desk_spike.broker.alpaca_readonly import AlpacaReadOnly, ApiError
from family_desk_spike.config import Settings, SpikeConfig, extract_emails
from family_desk_spike.core.clock import Clock
from family_desk_spike.core.ratelimit import TokenBucket
from family_desk_spike.core.run_window import check_run_window
from family_desk_spike.data.edgar import EdgarPoller, RateLimitedSec, load_cik_filter
from family_desk_spike.data.iex_stream import QuoteMonitor, build_quote_session
from family_desk_spike.data.news_rest import fetch_recent_news, watchlist_matches
from family_desk_spike.data.news_stream import (
    NewsMonitor,
    build_news_session,
    news_payload,
    run_news_cross_check,
)
from family_desk_spike.data.stream_client import Connector, StreamCounters
from family_desk_spike.net.readonly_http import GetTransport, ReadOnlyHttp
from family_desk_spike.parse.alpaca_rest import ParseError, SchemaDriftError
from family_desk_spike.startup import GitReader, run_startup

EXIT_OK = 0
EXIT_STARTUP_REFUSED = 2
EXIT_WINDOW_REFUSED = 3
EXIT_ERROR = 4
EXIT_INTERRUPTED = 130
CIK_CACHE = Path("data/company_tickers.json")

Sleep = Callable[[float], Awaitable[None]]


@dataclass
class Deps:
    root: Path
    transport: GetTransport
    connector: Connector
    clock: Clock
    git: GitReader | None
    env: Mapping[str, str] | None = None  # None = read .env through config
    sleep: Sleep | None = None  # None = real, stop-aware sleep
    timer_sleep: Sleep | None = None  # None = real wait for the run duration
    rand: Callable[[], float] | None = None
    close_transport: Callable[[], Awaitable[None]] | None = None


@dataclass
class RunState:
    lines: list[str] = field(default_factory=list)
    exit_code: int = EXIT_OK
    log: AppLog | None = None
    quotes: QuoteMonitor | None = None
    news: NewsMonitor | None = None
    edgar: EdgarPoller | None = None
    stream_counters: dict[str, StreamCounters] = field(default_factory=dict)
    facts: dict[str, Any] = field(default_factory=dict)
    finished: bool = False

    def say(self, line: str) -> None:
        self.lines.append(line)
        print(line, flush=True)


def _redactor(settings: Settings) -> Redactor:
    ua = settings.sec_user_agent.get_secret_value()
    return Redactor.of(
        [
            settings.api_key_id.get_secret_value(),
            settings.api_secret_key.get_secret_value(),
            ua,
            *extract_emails(ua),
        ]
    )


def _counters_summary(c: StreamCounters) -> dict[str, Any]:
    return {
        "connects": c.connects,
        "disconnects": c.disconnects,
        "reconnects": c.reconnects,
        "errors": c.errors,
        "frames": c.frames,
        "malformed": c.malformed,
        "acks": [a.model_dump(mode="json") for a in c.acks],
        "fatal": c.fatal,
    }


def build_summary(state: RunState) -> dict[str, Any]:
    out: dict[str, Any] = dict(state.facts)
    if state.quotes is not None:
        out["quotes"] = state.quotes.summary()
    if state.news is not None:
        out["news_stream"] = state.news.summary()
    if state.edgar is not None:
        out["edgar"] = state.edgar.summary()
    out["streams"] = {k: _counters_summary(v) for k, v in state.stream_counters.items()}
    return out


def finish(state: RunState) -> None:
    """Synchronous, idempotent: summary record, flush, close, verify, print the anchor."""
    if state.finished or state.log is None:
        return
    state.finished = True
    log = state.log
    with contextlib.suppress(RuntimeError):
        log.append("summary", build_summary(state))
    log.close()
    result = verify_lines(log.path.read_text(encoding="utf-8"))
    state.say(f"log={log.path.as_posix()}")
    for line in result.lines():
        state.say(line)
    s = build_summary(state)
    for key in ("positions_count", "positions_symbols", "news_rest_items", "news_rest_watchlist"):
        if key in s:
            state.say(f"{key}={s[key]}")
    for name, c in s.get("streams", {}).items():
        state.say(
            f"stream[{name}] acks={len(c['acks'])} reconnects={c['reconnects']} fatal={c['fatal']}"
        )
    if "quotes" in s:
        for sym, q in s["quotes"]["per_symbol"].items():
            state.say(
                f"quotes[{sym}] count={q['count']} per_min={q['updates_per_min']} "
                f"spread_bps_median={q['spread_bps_median']} skew_ms_median={q['skew_ms_median']}"
            )
        state.say(f"quotes stale_events={s['quotes']['stale_events']}")
    if "news_stream" in s:
        state.say(f"news_stream={s['news_stream']}")
    if "edgar" in s:
        e = s["edgar"]
        state.say(
            f"edgar cycles={e['cycles']} pre_filter_min={e['pre_filter_entries_min']} "
            f"pre_filter_max={e['pre_filter_entries_max']} matches={e['matches_total']} "
            f"max_req_in_1s={e['max_requests_in_any_1s']} mean_rps={e['mean_rps']} "
            f"errors={e['errors']} ({e['label']})"
        )


async def _timer(stop: asyncio.Event, seconds: float, sleep: Sleep | None) -> None:
    if sleep is not None:
        await sleep(seconds)
    else:
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=seconds)
    stop.set()


async def run(
    deps: Deps, duration_min: int, state: RunState, stop: asyncio.Event | None = None
) -> int:
    """The async body. Always leaves `state` ready for `finish`."""
    startup = run_startup(deps.root, live=True, git=deps.git, env=deps.env)
    for line in startup.report.lines():
        state.say(line)
    if not startup.report.ok or startup.config is None:
        state.exit_code = EXIT_STARTUP_REFUSED
        return state.exit_code
    cfg: SpikeConfig = startup.config
    settings = startup.settings
    stop = stop or asyncio.Event()

    log = AppLog(
        deps.root / log_path_for(Path(cfg.log.dir), deps.clock()),
        redactor=_redactor(settings),
        clock=deps.clock,
    ).open()
    state.log = log
    log.append(
        "startup",
        {
            "version": startup.report.package_version,
            "commit": startup.report.commit,
            "config_sha256": startup.report.config_hash,
            "duration_min": duration_min,
        },
    )
    http = ReadOnlyHttp(deps.transport)
    broker = AlpacaReadOnly(http, cfg.alpaca.trading_base_url, settings)
    try:
        try:
            clock = await broker.get_clock()
        except (ApiError, OSError) as exc:
            log.append("error", {"stage": "clock", "detail": str(exc)[:200]})
            state.say(f"refused: could not read /v2/clock ({exc})")
            state.exit_code = EXIT_ERROR
            return state.exit_code
        log.append("clock", clock.model_dump(mode="json"))
        reasons = check_run_window(
            clock,
            duration_min=duration_min,
            earliest_start_et=cfg.run.earliest_start_et,
            end_buffer_min=cfg.run.end_buffer_minutes,
        )
        if reasons:
            log.append("run_window", {"refused": reasons})
            for r in reasons:
                state.say(f"run-window REFUSED: {r}")
            state.exit_code = EXIT_WINDOW_REFUSED
            return state.exit_code
        log.append("run_window", {"refused": []})

        try:
            account, drift = await broker.get_account()
        except SchemaDriftError as exc:
            log.append("schema_drift", exc.drift.payload())
            log.append("error", {"stage": "account", "detail": str(exc)[:200]})
            state.say(f"refused: /v2/account schema drift ({exc})")
            state.exit_code = EXIT_ERROR
            return state.exit_code
        except (ApiError, OSError, ParseError) as exc:
            log.append("error", {"stage": "account", "detail": str(exc)[:200]})
            state.say(f"refused: could not read /v2/account ({exc})")
            state.exit_code = EXIT_ERROR
            return state.exit_code
        if not drift.empty:
            log.append("schema_drift", drift.payload())
            state.say(
                f"schema drift on /v2/account: missing={list(drift.missing_optional)} "
                f"unknown={list(drift.unknown)} unknown_invalid={drift.unknown_invalid_names}"
            )
        log.append(
            "account",
            {
                "status": account.status,
                "currency": account.currency,
                "trading_blocked": account.trading_blocked,
                "account_blocked": account.account_blocked,
                "pattern_day_trader": account.pattern_day_trader,
            },
        )
        positions = await broker.get_positions()
        log.append(
            "positions",
            {"count": len(positions), "items": [p.model_dump(mode="json") for p in positions]},
        )
        state.facts["positions_count"] = len(positions)
        state.facts["positions_symbols"] = sorted({p.symbol for p in positions})

        symbols = cfg.watchlist.symbols
        rest_news = await fetch_recent_news(
            http,
            data_base_url=cfg.alpaca.data_base_url,
            settings=settings,
            symbols=symbols,
            now=clock.timestamp,
            lookback_hours=cfg.news.rest_lookback_hours,
            limit=cfg.news.rest_limit,
        )
        for item in rest_news:
            log.append("news.rest", news_payload(item))
        state.facts["news_rest_items"] = len(rest_news)
        state.facts["news_rest_watchlist"] = len(watchlist_matches(rest_news, symbols))

        sec = RateLimitedSec(
            http=http,
            base_url=cfg.edgar.base_url,
            user_agent=settings.sec_user_agent.get_secret_value(),
            clock=deps.clock,
            sleep=deps.sleep or _stop_aware_sleep(stop),
            bucket=TokenBucket(rate=cfg.edgar.max_requests_per_second),
            stop=stop,
        )
        cik_filter = await load_cik_filter(sec, cfg.edgar.symbols, deps.root / CIK_CACHE, log)

        quote_session, state.quotes = build_quote_session(
            url=cfg.alpaca.stock_stream_url, connector=deps.connector, settings=settings,
            symbols=symbols, log=log, clock=deps.clock, streams=cfg.streams, stop=stop,
            sleep=deps.sleep,
        )  # fmt: skip
        news_session, state.news = build_news_session(
            url=cfg.alpaca.news_stream_url, connector=deps.connector, settings=settings,
            symbols=symbols, log=log, clock=deps.clock, streams=cfg.streams, stop=stop,
            sleep=deps.sleep,
        )  # fmt: skip
        state.news.seed([n.id for n in rest_news])
        news_monitor = state.news
        news_window_start = deps.clock()
        loop_sleep = deps.sleep or _stop_aware_sleep(stop)

        async def news_check(final: bool) -> None:
            result = await run_news_cross_check(
                news_monitor, http, data_base_url=cfg.alpaca.data_base_url, settings=settings,
                window_start=news_window_start, grace_seconds=cfg.news.cross_check_grace_seconds,
                final=final,
            )  # fmt: skip
            if result is not None and result.verdict in ("stall", "partial"):
                state.say(
                    f"STALL: news stream missed {len(result.missed_ids)} watchlist item(s) "
                    f"that REST has (verdict={result.verdict})"
                )

        async def news_cross_check_loop() -> None:
            while not stop.is_set():
                await loop_sleep(cfg.news.cross_check_seconds)
                if stop.is_set():
                    break
                await news_check(final=False)

        state.stream_counters = {"iex": quote_session.counters, "news": news_session.counters}
        poller_kwargs: dict[str, Any] = {}
        if deps.rand is not None:
            poller_kwargs["rand"] = deps.rand
            quote_session.rand = news_session.rand = deps.rand
        state.edgar = EdgarPoller(
            sec=sec, cfg=cfg.edgar, cik_filter=cik_filter, log=log, clock=deps.clock, stop=stop,
            **poller_kwargs,
        )  # fmt: skip

        tasks = [
            asyncio.create_task(quote_session.run(), name="iex"),
            asyncio.create_task(news_session.run(), name="news"),
            asyncio.create_task(state.edgar.run(), name="edgar"),
            asyncio.create_task(news_cross_check_loop(), name="news_cross_check"),
        ]
        for t in tasks:
            t.add_done_callback(_report_task_death(state, log, stop))
        timer = asyncio.create_task(_timer(stop, duration_min * 60, deps.timer_sleep), name="timer")
        try:
            await stop.wait()
        finally:
            stop.set()
            timer.cancel()
            _done, pending = await asyncio.wait(tasks, timeout=15)
            for t in pending:
                t.cancel()
            with contextlib.suppress(TimeoutError):  # final check over the whole run
                await asyncio.wait_for(news_check(final=True), timeout=20)
        return state.exit_code
    finally:
        if deps.close_transport is not None:
            with contextlib.suppress(Exception):
                await deps.close_transport()


def _report_task_death(
    state: RunState, log: AppLog, stop: asyncio.Event
) -> Callable[[asyncio.Task[Any]], None]:
    """Report a source task that ends for any reason other than a requested stop, the
    moment it happens, never only at shutdown (P-02, P-24). B10 run 1's EDGAR poller
    died on its first poll and nothing showed it for 35 minutes. A stream that returns
    on a fatal code (e.g. 402 auth failed) without raising counts too."""

    def on_done(task: asyncio.Task[Any]) -> None:
        if task.cancelled():
            return
        failure = task.exception()
        if isinstance(failure, KeyboardInterrupt):
            return
        if failure is None:
            if stop.is_set():
                return  # normal end of the run
            detail = "exited before stop"
        else:
            detail = repr(failure)[:200]
        name = task.get_name()
        failures: dict[str, str] = state.facts.setdefault("task_failures", {})
        failures[name] = detail
        with contextlib.suppress(RuntimeError):  # log already closed
            log.append("error", {"stage": name, "detail": detail})
        state.say(f"ERROR: source task '{name}' ended: {detail}"[:300])
        state.exit_code = EXIT_ERROR

    return on_done


def _stop_aware_sleep(stop: asyncio.Event) -> Sleep:
    async def sleep(seconds: float) -> None:
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=seconds)

    return sleep


def run_sync(deps: Deps, duration_min: int, stop: asyncio.Event | None = None) -> RunState:
    """asyncio.run with Windows-safe Ctrl+C handling. Always finishes the log."""
    state = RunState()
    try:
        asyncio.run(run(deps, duration_min, state, stop))
    except KeyboardInterrupt:
        state.exit_code = EXIT_INTERRUPTED
        state.say("interrupted (Ctrl+C): tasks cancelled, log flushed")
        if state.log is not None:
            with contextlib.suppress(RuntimeError):
                state.log.append("shutdown", {"reason": "KeyboardInterrupt"})
    finally:
        finish(state)
    return state
