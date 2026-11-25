"""Pure EDGAR parsers: 8-K Atom feeds (getcurrent and per-company) and the SEC
`company_tickers.json` CIK map with cardinality (P-05). XML goes through defusedxml
(no DTDs, no entity expansion)."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal
from xml.etree.ElementTree import Element  # type only; parsing uses defusedxml

from defusedxml.ElementTree import fromstring
from pydantic import ValidationError

from family_desk_spike.models import MAX_TEXT, Filing8K

ATOM = "{http://www.w3.org/2005/Atom}"
ACCESSION_IN_ID = re.compile(r"accession-number=(\d{10}-\d{2}-\d{6})")
CIK_IN_TITLE = re.compile(r"\((\d{10})\)")
CIK_IN_LINK = re.compile(r"/edgar/data/(\d{1,10})/")
NAME_IN_TITLE = re.compile(r"^\s*\S+\s+-\s+(.*?)\s+\(\d{10}\)")


class EdgarParseError(ValueError):
    pass


def pad_cik(cik: int | str) -> str:
    digits = str(cik).strip()
    if not digits.isdigit() or len(digits) > 10:
        raise EdgarParseError(f"not a CIK: {cik!r}")
    return digits.zfill(10)


@dataclass(frozen=True)
class FeedParse:
    filings: list[Filing8K]
    entries: int  # pre-filter entry count (all entries in the feed)
    skipped: int  # entries we could not parse into a Filing8K


def _text(el: Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _find(el: Element, tag: str) -> Element | None:
    """Find a child in the Atom namespace, or un-namespaced (per-company <content>)."""
    found = el.find(f"{ATOM}{tag}")
    if found is None:
        found = el.find(tag)
    return found


def _entry_to_filing(entry: Element, feed_cik: str | None, feed_name: str | None) -> Filing8K:
    title = _text(_find(entry, "title"))
    link_el = _find(entry, "link")
    link = link_el.get("href") if link_el is not None else None
    cat = _find(entry, "category")
    form = (cat.get("term") if cat is not None else None) or title.split(" - ")[0].strip()
    acc_match = ACCESSION_IN_ID.search(_text(_find(entry, "id")))
    content = _find(entry, "content")
    accession = acc_match.group(1) if acc_match else None
    if accession is None and content is not None:
        accession = _text(content.find("accession-number")) or _text(
            content.find(f"{ATOM}accession-number")
        )
    if not accession:
        raise EdgarParseError("entry has no accession number")
    # CIK sources, most to least specific. Never the accession number's prefix: that is
    # the submitter's CIK, which may be a filing agent (A2 finding).
    cik: str | None = None
    m = CIK_IN_TITLE.search(title)  # getcurrent: "8-K - Name (0000320193) (Filer)"
    if m:
        cik = m.group(1)
    elif feed_cik:  # per-company feed: feed-level <company-info><cik>
        cik = feed_cik
    elif link and (lm := CIK_IN_LINK.search(link)):
        cik = pad_cik(lm.group(1))
    if cik is None:
        raise EdgarParseError("entry has no CIK")
    name_m = NAME_IN_TITLE.search(title)
    name = name_m.group(1) if name_m else (feed_name or "")
    return Filing8K(
        accession_number=accession,
        cik=pad_cik(cik),
        company_name=name[:MAX_TEXT],
        form_type=form,
        updated=_text(_find(entry, "updated")),
        link=link,
    )


def parse_atom_feed(body: bytes) -> FeedParse:
    try:
        root = fromstring(body)
    except Exception as exc:  # defusedxml raises several types; all mean "refuse"
        raise EdgarParseError(f"feed rejected: {type(exc).__name__}") from exc
    info = root.find(f"{ATOM}company-info")
    if info is None:
        info = root.find("company-info")
    feed_cik = feed_name = None
    if info is not None:
        cik_text = _text(_find(info, "cik"))
        feed_cik = pad_cik(cik_text) if cik_text else None
        feed_name = _text(_find(info, "conformed-name")) or None
    entries = root.findall(f"{ATOM}entry")
    filings: list[Filing8K] = []
    skipped = 0
    for entry in entries:
        try:
            filings.append(_entry_to_filing(entry, feed_cik, feed_name))
        except (EdgarParseError, ValidationError):
            skipped += 1
    return FeedParse(filings=filings, entries=len(entries), skipped=skipped)


# --- CIK map ---------------------------------------------------------------------------

Cardinality = Literal["unique", "shared", "none"]


@dataclass(frozen=True)
class CikInfo:
    symbol: str
    cardinality: Cardinality
    cik: str | None
    tickers_on_cik: tuple[str, ...]


def parse_company_tickers(body: bytes) -> list[tuple[str, str, str]]:
    """Rows of (ticker, 10-digit CIK, title) from SEC company_tickers.json."""
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise EdgarParseError("company_tickers.json is not valid JSON") from exc
    rows = data.values() if isinstance(data, dict) else data
    out: list[tuple[str, str, str]] = []
    for row in rows:
        if not isinstance(row, dict) or "cik_str" not in row or "ticker" not in row:
            raise EdgarParseError("company_tickers.json row missing cik_str/ticker")
        out.append((str(row["ticker"]).upper(), pad_cik(row["cik_str"]), str(row.get("title", ""))))
    return out


def classify_symbols(
    rows: Iterable[tuple[str, str, str]], symbols: Sequence[str]
) -> dict[str, CikInfo]:
    rows = list(rows)
    by_cik: dict[str, set[str]] = {}
    by_ticker: dict[str, set[str]] = {}
    for ticker, cik, _ in rows:
        by_cik.setdefault(cik, set()).add(ticker)
        by_ticker.setdefault(ticker, set()).add(cik)
    out: dict[str, CikInfo] = {}
    for sym in (s.upper() for s in symbols):
        ciks = by_ticker.get(sym, set())
        if not ciks:
            out[sym] = CikInfo(sym, "none", None, ())
            continue
        if len(ciks) > 1:
            out[sym] = CikInfo(sym, "shared", None, ())
            continue
        (cik,) = ciks
        tickers = tuple(sorted(by_cik[cik]))
        out[sym] = CikInfo(sym, "unique" if tickers == (sym,) else "shared", cik, tickers)
    return out


class CikFilterError(ValueError):
    pass


def build_cik_filter(info: dict[str, CikInfo]) -> dict[str, str]:
    """CIK -> symbol for the 8-K filter. Refuses any shared or missing CIK (P-05)."""
    bad = [f"{i.symbol}:{i.cardinality}" for i in info.values() if i.cardinality != "unique"]
    if bad:
        raise CikFilterError("8-K filter refuses non-unique CIKs: " + ", ".join(sorted(bad)))
    return {i.cik: i.symbol for i in info.values() if i.cik is not None}
