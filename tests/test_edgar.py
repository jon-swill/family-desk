from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from family_desk_spike.applog import AppLog, verify_lines
from family_desk_spike.config import parse_config
from family_desk_spike.core.ratelimit import TokenBucket
from family_desk_spike.data.edgar import (
    EdgarPoller,
    MissingUserAgentError,
    RateLimitedSec,
    getcurrent_params,
    load_cik_filter,
)
from family_desk_spike.net.readonly_http import HttpResponse, ReadOnlyHttp
from family_desk_spike.parse.edgar import (
    CikFilterError,
    EdgarParseError,
    build_cik_filter,
    classify_symbols,
    pad_cik,
    parse_atom_feed,
    parse_company_tickers,
)
from tests.fakes.clock import FakeClock
from tests.fakes.env import FAKE_UA
from tests.fakes.http import FakeHttp

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).parent / "fixtures"
CFG = parse_config((ROOT / "config" / "spike.toml").read_text(encoding="utf-8"))
SEC = "https://www.sec.gov"
FEED_URL = f"{SEC}/cgi-bin/browse-edgar"
TICKERS_URL = f"{SEC}/files/company_tickers.json"
REAL_FIXTURE = FIX / "edgar_aapl_8k_entry.xml"
ATOM_OPEN = b'<feed xmlns="http://www.w3.org/2005/Atom">'


def _rows() -> list[tuple[str, str, str]]:
    return parse_company_tickers((FIX / "company_tickers_subset.json").read_bytes())


# --- CIK map -------------------------------------------------------------------------


def test_cik_is_zero_padded_and_matches_feed_cik() -> None:
    assert pad_cik(320193) == "0000320193"
    assert pad_cik("0000320193") == "0000320193"
    rows = dict((t, c) for t, c, _ in _rows())
    assert rows["AAPL"] == "0000320193"  # company_tickers integer cik_str 320193
    feed = parse_atom_feed((FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    assert feed.filings[0].cik == rows["AAPL"]
    with pytest.raises(EdgarParseError):
        pad_cik("12345678901")


def test_cardinality_unique_shared_none() -> None:
    info = classify_symbols(_rows(), ["AAPL", "MSFT", "IWM", "NOPE"])
    assert info["AAPL"].cardinality == "unique"
    assert info["MSFT"].cik == "0000789019"
    assert info["IWM"].cardinality == "shared"
    assert info["IWM"].tickers_on_cik == ("EFA", "IVV", "IWM")
    assert info["NOPE"].cardinality == "none"


def test_filter_accepts_only_unique_ciks() -> None:
    ok = build_cik_filter(classify_symbols(_rows(), CFG.edgar.symbols))
    assert ok == {"0000320193": "AAPL", "0000789019": "MSFT"}


def test_shared_fund_trust_cik_rejected() -> None:
    with pytest.raises(CikFilterError, match="IWM:shared"):
        build_cik_filter(classify_symbols(_rows(), ["AAPL", "IWM"]))


def test_missing_ticker_rejected() -> None:
    with pytest.raises(CikFilterError, match="ZZZZ:none"):
        build_cik_filter(classify_symbols(_rows(), ["AAPL", "ZZZZ"]))


def test_company_tickers_bad_payload() -> None:
    with pytest.raises(EdgarParseError):
        parse_company_tickers(b"not json")
    with pytest.raises(EdgarParseError):
        parse_company_tickers(b'{"0": {"ticker": "X"}}')


# --- Atom parsing --------------------------------------------------------------------


def test_getcurrent_feed_parsed() -> None:
    feed = parse_atom_feed((FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    assert feed.entries == 5
    assert feed.skipped == 1
    assert [f.cik for f in feed.filings] == [
        "0000320193",
        "0000789019",
        "0001100663",
        "0000000042",
    ]
    assert feed.filings[0].company_name == "Apple Inc."
    assert feed.filings[0].accession_number == "0001140361-26-000001"
    assert feed.filings[0].form_type == "8-K"


def test_accession_prefix_is_never_used_as_cik() -> None:
    """Entry 4's accession starts with Apple's CIK but the filer is CIK 42 (A2 finding)."""
    feed = parse_atom_feed((FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    other = feed.filings[3]
    assert other.accession_number.startswith("0000320193")
    assert other.cik == "0000000042"


def test_getcompany_feed_parsed_with_feed_level_cik() -> None:
    feed = parse_atom_feed((FIX / "edgar_getcompany_synthetic.xml").read_bytes())
    (f,) = feed.filings
    assert f.cik == "0000320193"
    assert f.company_name == "Apple Inc."
    assert f.accession_number == "0000320193-26-000010"


def test_hostile_xml_refused() -> None:
    bomb = (
        b'<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol">'
        b'<!ENTITY lol2 "&lol;&lol;&lol;">]><feed>&lol2;</feed>'
    )
    with pytest.raises(EdgarParseError, match="rejected"):
        parse_atom_feed(bomb)
    with pytest.raises(EdgarParseError):
        parse_atom_feed(b"<feed><unclosed></feed>")


@pytest.mark.skipif(
    not REAL_FIXTURE.exists(),
    reason="real AAPL 8-K fixture pending: owner runs tools.fetch_edgar_fixture (needs .env UA)",
)
def test_real_aapl_8k_entry_offline() -> None:
    text = REAL_FIXTURE.read_bytes()
    assert b"source: https://www.sec.gov/" in text and b"accessed: " in text
    feed = parse_atom_feed(ATOM_OPEN + text + b"</feed>")
    (f,) = feed.filings
    assert f.cik == "0000320193"
    assert f.form_type.startswith("8-K")
    assert build_cik_filter(classify_symbols(_rows(), ["AAPL", "MSFT"]))[f.cik] == "AAPL"


# --- Poller --------------------------------------------------------------------------


def _sec(fake: FakeHttp, clock: FakeClock) -> RateLimitedSec:
    return RateLimitedSec(
        http=ReadOnlyHttp(fake),
        base_url=SEC,
        user_agent=FAKE_UA,
        clock=clock,
        sleep=clock.sleep,
        bucket=TokenBucket(rate=CFG.edgar.max_requests_per_second),
    )


def test_refuses_to_start_without_user_agent() -> None:
    clock = FakeClock()
    with pytest.raises(MissingUserAgentError):
        RateLimitedSec(
            http=ReadOnlyHttp(FakeHttp()),
            base_url=SEC,
            user_agent="  ",
            clock=clock,
            sleep=clock.sleep,
            bucket=TokenBucket(rate=1.0),
        )


def _poll(
    tmp_path: Path, responses: list[HttpResponse], cycles: int
) -> tuple[EdgarPoller, FakeHttp, FakeClock, list[dict[str, object]]]:
    clock = FakeClock()
    fake = FakeHttp().add(FEED_URL, *responses)
    fake.add_json(TICKERS_URL, (FIX / "company_tickers_subset.json").read_bytes())
    path = tmp_path / "log.jsonl"
    log = AppLog(path, clock=clock).open()
    sec = _sec(fake, clock)
    stop = asyncio.Event()

    async def go() -> EdgarPoller:
        cik_filter = await load_cik_filter(sec, CFG.edgar.symbols, tmp_path / "ct.json", log)
        poller = EdgarPoller(sec=sec, cfg=CFG.edgar, cik_filter=cik_filter, log=log, clock=clock,
                             stop=stop, rand=lambda: 0.5)  # fmt: skip
        for _ in range(cycles):
            await clock.sleep(await poller.poll_once())
        return poller

    poller = asyncio.run(go())
    log.close()
    text = path.read_text(encoding="utf-8")
    assert verify_lines(text).ok
    assert FAKE_UA not in text  # UA is a header, never logged
    return poller, fake, clock, [json.loads(line) for line in text.splitlines()]


def test_cycle_logs_prefilter_and_matches_and_dedupes(tmp_path: Path) -> None:
    feed = HttpResponse(200, (FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    poller, fake, _, recs = _poll(tmp_path, [feed], cycles=3)
    s = poller.summary()
    assert s["ok_cycles"] == 3
    assert s["pre_filter_entries_min"] == 5
    assert s["matches_total"] == 6  # AAPL + MSFT each cycle
    assert s["new_matches"] == 2 and s["duplicates"] == 4
    assert s["label"] == "feed live + filter tested offline"
    cycles = [r["payload"] for r in recs if r["source"] == "edgar.cycle"]
    assert len(cycles) == 3 and cycles[0]["pre_filter_entries"] == 5  # type: ignore[index]
    filings = [r["payload"]["symbol"] for r in recs if r["source"] == "edgar.filing"]  # type: ignore[index]
    assert filings == ["AAPL", "MSFT"]
    url, params, headers = fake.calls[1]
    assert url == FEED_URL and params == getcurrent_params(CFG.edgar.feed_count)
    assert headers["User-Agent"] == FAKE_UA
    cik_map = next(r for r in recs if r["source"] == "edgar.cik_map")
    assert cik_map["payload"]["symbols"]["AAPL"]["cardinality"] == "unique"  # type: ignore[index]


def test_zero_entries_still_logged(tmp_path: Path) -> None:
    empty = HttpResponse(200, ATOM_OPEN + b"<title>x</title></feed>")
    poller, _, _, recs = _poll(tmp_path, [empty], cycles=2)
    cycles = [r for r in recs if r["source"] == "edgar.cycle"]
    assert len(cycles) == 2
    assert poller.summary()["cycles_with_entries"] == 0


@pytest.mark.parametrize("status", [403, 429])
def test_block_status_backs_off_at_least_ten_minutes(tmp_path: Path, status: int) -> None:
    poller, _, clock, recs = _poll(tmp_path, [HttpResponse(status, b"")], cycles=2)
    assert clock.sleeps.count(CFG.edgar.block_backoff_seconds) == 2
    assert CFG.edgar.block_backoff_seconds >= 600
    assert poller.stats.errors == {f"http_{status}": 2}
    assert any(r["source"] == "edgar.error" for r in recs)


def test_server_errors_back_off_exponentially_then_recover(tmp_path: Path) -> None:
    feed = HttpResponse(200, (FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    err = HttpResponse(503, b"")
    poller, _, clock, _ = _poll(tmp_path, [err, err, err, feed], cycles=4)
    waits = [s for s in clock.sleeps if s >= CFG.edgar.poll_seconds]
    assert waits[0] <= waits[1] <= waits[2] <= CFG.edgar.block_backoff_seconds
    assert poller.stats.ok_cycles == 1


def test_measured_rate_at_most_one_per_second(tmp_path: Path) -> None:
    feed = HttpResponse(200, (FIX / "edgar_getcurrent_synthetic.xml").read_bytes())
    poller, _, _, _ = _poll(tmp_path, [feed], cycles=20)
    s = poller.summary()
    assert s["requests"] == 21  # 1 ticker map + 20 polls
    assert s["max_requests_in_any_1s"] == 1


def test_parse_error_is_logged_not_raised(tmp_path: Path) -> None:
    poller, _, _, _ = _poll(tmp_path, [HttpResponse(200, b"<not-xml")], cycles=1)
    assert poller.stats.errors == {"parse": 1}


def test_cik_map_cache_avoids_second_fetch(tmp_path: Path) -> None:
    feed = HttpResponse(200, ATOM_OPEN + b"</feed>")
    _, fake1, _, _ = _poll(tmp_path, [feed], cycles=1)
    assert (tmp_path / "ct.json").exists()
    _, fake2, _, recs = _poll(tmp_path, [feed], cycles=1)
    assert [c[0] for c in fake2.calls].count(TICKERS_URL) == 0
    assert [c[0] for c in fake1.calls].count(TICKERS_URL) == 1
    maps = [r for r in recs if r["source"] == "edgar.cik_map"]  # same log file, two runs
    origin = maps[-1]["payload"]["origin"]  # type: ignore[index]
    assert origin == "cache"
