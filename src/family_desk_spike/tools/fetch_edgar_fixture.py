"""Owner step for B8: save one real past AAPL 8-K Atom entry, verbatim, as a test fixture.

    python -m family_desk_spike.tools.fetch_edgar_fixture

Makes one GET (plus nothing else) to the SEC per-company 8-K Atom feed for CIK
0000320193 through the shared ReadOnlyHttp client, with SEC_USER_AGENT from `.env`
(read through config). Writes the first <entry> verbatim to
tests/fixtures/edgar_aapl_8k_entry.xml with a header comment holding the source URL
and access date. The entry is SEC public data; no personal value is written.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from family_desk_spike.config import ENV_FILE, read_settings
from family_desk_spike.core.clock import SystemClock
from family_desk_spike.core.ratelimit import TokenBucket
from family_desk_spike.data.edgar import BROWSE_PATH, RateLimitedSec
from family_desk_spike.net.readonly_http import HttpxTransport, ReadOnlyHttp

SEC_BASE = "https://www.sec.gov"
FIXTURE = Path("tests/fixtures/edgar_aapl_8k_entry.xml")
PARAMS = {
    "action": "getcompany",
    "CIK": "0000320193",
    "type": "8-K",
    "dateb": "",
    "owner": "include",
    "count": "10",
    "output": "atom",
}
ENTRY = re.compile(r"<entry>.*?</entry>", re.DOTALL)


def extract_first_entry(feed_text: str) -> str:
    m = ENTRY.search(feed_text)
    if m is None:
        raise ValueError("no <entry> in the feed")
    return m.group(0)


def fixture_text(entry: str, url: str, accessed: datetime) -> str:
    header = (
        f"<!-- Real SEC EDGAR Atom entry, saved verbatim by "
        f"family_desk_spike.tools.fetch_edgar_fixture.\n"
        f"     source: {url}\n     accessed: {accessed.date().isoformat()} -->\n"
    )
    return header + entry + "\n"


async def _fetch(root: Path) -> str:
    settings = read_settings(root / ENV_FILE)
    clock = SystemClock()
    transport = HttpxTransport()
    try:
        sec = RateLimitedSec(
            http=ReadOnlyHttp(transport),
            base_url=SEC_BASE,
            user_agent=settings.sec_user_agent.get_secret_value(),
            clock=clock,
            sleep=asyncio.sleep,
            bucket=TokenBucket(rate=1.0),
        )
        resp = await sec.get(BROWSE_PATH, PARAMS)
    finally:
        await transport.aclose()
    if resp.status != 200:
        raise SystemExit(f"SEC returned HTTP {resp.status}; nothing written")
    entry = extract_first_entry(resp.body.decode("utf-8", errors="replace"))
    url = f"{SEC_BASE}{BROWSE_PATH}?{urlencode(PARAMS)}"
    (root / FIXTURE).write_text(fixture_text(entry, url, datetime.now(UTC)), encoding="utf-8")
    return str(root / FIXTURE)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Save one real AAPL 8-K Atom entry as a fixture.")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    print(f"wrote {asyncio.run(_fetch(Path(args.root)))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
