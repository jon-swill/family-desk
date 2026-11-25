"""EDGAR 8-K poller (D15, FR-8, C-7).

Polls the latest-filings 8-K Atom feed every `poll_seconds` (default 60) under a token
bucket of <= `max_requests_per_second` (<= 1, stricter than SEC's 10/s). All requests
go through the shared ReadOnlyHttp client with the owner's User-Agent. Every cycle logs
the pre-filter entry count and the AAPL/MSFT match count, so "no match" is visible as
"feed live, filter empty", never as silence (P-02). 403/429 back off >= block_backoff
(SEC throttles until the rate stays low for 10 minutes); 5xx back off exponentially.
"""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from family_desk_spike.applog import AppLog, utc_iso
from family_desk_spike.config import EdgarConfig
from family_desk_spike.core.backoff import backoff_delay
from family_desk_spike.core.clock import Clock
from family_desk_spike.core.ratelimit import RateMeter, TokenBucket
from family_desk_spike.data.stream_client import Sleep
from family_desk_spike.net.readonly_http import HttpResponse, ReadOnlyHttp
from family_desk_spike.parse.edgar import (
    EdgarParseError,
    build_cik_filter,
    classify_symbols,
    parse_atom_feed,
    parse_company_tickers,
)

BROWSE_PATH = "/cgi-bin/browse-edgar"
TICKERS_PATH = "/files/company_tickers.json"
BLOCK_STATUSES = frozenset({403, 429})
MIN_TOKEN_SLEEP_S = 0.02  # > one Windows clock tick (15.6 ms)


class MissingUserAgentError(ValueError):
    pass


class SecStoppedError(RuntimeError):
    """The run is stopping; no SEC request was sent."""


def getcurrent_params(count: int) -> dict[str, str]:
    return {
        "action": "getcurrent",
        "type": "8-K",
        "company": "",
        "dateb": "",
        "owner": "include",
        "start": "0",
        "count": str(count),
        "output": "atom",
    }


def sec_headers(user_agent: str) -> dict[str, str]:
    if not user_agent.strip():
        raise MissingUserAgentError("SEC_USER_AGENT is required for every SEC request")
    return {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}


@dataclass
class RateLimitedSec:
    """SEC GETs through ReadOnlyHttp, spaced by a token bucket and measured."""

    http: ReadOnlyHttp
    base_url: str
    user_agent: str
    clock: Clock
    sleep: Sleep
    bucket: TokenBucket
    meter: RateMeter = field(default_factory=RateMeter)
    stop: asyncio.Event | None = None  # set = never send; give up the token wait

    def __post_init__(self) -> None:
        sec_headers(self.user_agent)  # refuse to start without a UA

    async def get(self, path: str, params: dict[str, str] | None = None) -> HttpResponse:
        # Re-check after every sleep: a timer may wake early (Windows asyncio timers can
        # fire up to one ~15.6 ms clock tick early), so one sleep of `wait_time` seconds
        # does not guarantee a whole token. B10 run 1 died here on its first poll. Each
        # sleep is at least MIN_TOKEN_SLEEP_S, longer than one tick, so the loop always
        # makes progress instead of spinning on a sub-tick remainder.
        now = self.clock.monotonic()
        while (wait := self.bucket.wait_time(now)) > 0:
            if self.stop is not None and self.stop.is_set():
                raise SecStoppedError("stop requested while waiting for a rate-limit token")
            await self.sleep(max(wait, MIN_TOKEN_SLEEP_S))
            now = self.clock.monotonic()
        self.bucket.take(now)
        self.meter.record(now)
        return await self.http.get(
            self.base_url.rstrip("/") + path, params=params, headers=sec_headers(self.user_agent)
        )


def _read_cache(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def _write_cache(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


async def load_cik_filter(
    sec: RateLimitedSec, symbols: tuple[str, ...], cache: Path, log: AppLog
) -> dict[str, str]:
    """CIK -> symbol for the 8-K filter, from company_tickers.json (cached in /data/).
    Raises CikFilterError at startup for any shared or missing CIK."""
    cached = _read_cache(cache)
    if cached is not None:
        body, origin = cached, "cache"
    else:
        resp = await sec.get(TICKERS_PATH)
        if resp.status != 200:
            raise EdgarParseError(f"company_tickers.json HTTP {resp.status}")
        body, origin = resp.body, "sec"
        _write_cache(cache, body)
    info = classify_symbols(parse_company_tickers(body), symbols)
    log.append(
        "edgar.cik_map",
        {
            "origin": origin,
            "symbols": {
                s: {
                    "cardinality": i.cardinality,
                    "cik": i.cik,
                    "tickers_on_cik": len(i.tickers_on_cik),
                }
                for s, i in info.items()
            },
        },
    )
    return build_cik_filter(info)


@dataclass
class EdgarStats:
    cycles: int = 0
    ok_cycles: int = 0
    pre_filter_counts: list[int] = field(default_factory=list)
    matches_total: int = 0
    new_matches: int = 0
    duplicates: int = 0
    skipped_entries: int = 0
    errors: dict[str, int] = field(default_factory=dict)

    def error(self, kind: str) -> None:
        self.errors[kind] = self.errors.get(kind, 0) + 1


@dataclass
class EdgarPoller:
    sec: RateLimitedSec
    cfg: EdgarConfig
    cik_filter: dict[str, str]
    log: AppLog
    clock: Clock
    stop: asyncio.Event
    rand: Callable[[], float] = field(default=random.random)  # jitter, not crypto
    stats: EdgarStats = field(default_factory=EdgarStats)
    seen: set[tuple[str, str]] = field(default_factory=set)
    _server_errors: int = 0

    async def poll_once(self) -> float:
        """One cycle. Returns how long to wait before the next."""
        try:
            resp = await self.sec.get(BROWSE_PATH, getcurrent_params(self.cfg.feed_count))
        except SecStoppedError:
            return 0.0  # stopping before anything was sent; not a cycle
        except OSError as exc:
            self.stats.cycles += 1
            self.stats.error("network")
            self.log.append("edgar.error", {"kind": "network", "detail": type(exc).__name__})
            return self._server_backoff()
        self.stats.cycles += 1
        if resp.status in BLOCK_STATUSES:
            self.stats.error(f"http_{resp.status}")
            self.log.append(
                "edgar.error",
                {
                    "kind": "blocked",
                    "status": resp.status,
                    "backoff_s": self.cfg.block_backoff_seconds,
                },
            )
            return self.cfg.block_backoff_seconds
        if resp.status >= 500 or resp.status != 200:
            self.stats.error(f"http_{resp.status}")
            self.log.append("edgar.error", {"kind": "http", "status": resp.status})
            return self._server_backoff()
        self._server_errors = 0
        try:
            feed = parse_atom_feed(resp.body)
        except EdgarParseError as exc:
            self.stats.error("parse")
            self.log.append("edgar.error", {"kind": "parse", "detail": str(exc)[:200]})
            return self.cfg.poll_seconds
        matches = [f for f in feed.filings if f.cik in self.cik_filter]
        new = 0
        for f in matches:
            key = (f.accession_number, f.cik)
            if key in self.seen:
                self.stats.duplicates += 1
                continue
            self.seen.add(key)
            new += 1
            self.log.append(
                "edgar.filing",
                {
                    "symbol": self.cik_filter[f.cik],
                    "cik": f.cik,
                    "accession_number": f.accession_number,
                    "form_type": f.form_type,
                    "link": f.link,
                },
                source_ts=utc_iso(f.updated),
            )
        self.stats.ok_cycles += 1
        self.stats.pre_filter_counts.append(feed.entries)
        self.stats.matches_total += len(matches)
        self.stats.new_matches += new
        self.stats.skipped_entries += feed.skipped
        self.log.append(
            "edgar.cycle",
            {
                "pre_filter_entries": feed.entries,
                "parsed": len(feed.filings),
                "skipped": feed.skipped,
                "matches": len(matches),
                "new_matches": new,
                "filter": sorted(self.cik_filter.values()),
            },
        )
        return self.cfg.poll_seconds

    def _server_backoff(self) -> float:
        self._server_errors += 1
        return max(
            self.cfg.poll_seconds,
            backoff_delay(
                self._server_errors,
                initial=self.cfg.poll_seconds,
                maximum=self.cfg.block_backoff_seconds,
                rand=self.rand,
            ),
        )

    async def run(self) -> EdgarStats:
        while not self.stop.is_set():
            wait = await self.poll_once()
            if self.stop.is_set():
                break
            await self.sec.sleep(wait)
        return self.stats

    def summary(self) -> dict[str, object]:
        pre = self.stats.pre_filter_counts
        return {
            "cycles": self.stats.cycles,
            "ok_cycles": self.stats.ok_cycles,
            "pre_filter_entries_min": min(pre) if pre else None,
            "pre_filter_entries_max": max(pre) if pre else None,
            "cycles_with_entries": sum(1 for n in pre if n > 0),
            "matches_total": self.stats.matches_total,
            "new_matches": self.stats.new_matches,
            "duplicates": self.stats.duplicates,
            "skipped_entries": self.stats.skipped_entries,
            "errors": dict(self.stats.errors),
            "requests": len(self.sec.meter.times),
            "max_requests_in_any_1s": self.sec.meter.max_in_window(1.0),
            "mean_rps": _r(self.sec.meter.mean_rate()),
            "label": "feed live + filter tested offline",
        }


def _r(v: float | None) -> float | None:
    return None if v is None else round(v, 4)


def dump_summary(summary: dict[str, object]) -> str:
    return json.dumps(summary, sort_keys=True)
