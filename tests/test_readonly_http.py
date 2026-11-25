"""G-7 runtime guard: the shared client refuses before anything is sent."""

from __future__ import annotations

import asyncio

import pytest

from family_desk_spike.net.readonly_http import (
    ALLOWLIST,
    ReadOnlyHttp,
    RefusedRequestError,
    check_request,
)
from tests.fakes.http import FakeHttp

PAPER = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
SEC = "https://www.sec.gov"

ALLOWED_URLS = [
    f"{PAPER}/v2/account",
    f"{PAPER}/v2/positions",
    f"{PAPER}/v2/clock",
    f"{DATA}/v1beta1/news",
    f"{SEC}/cgi-bin/browse-edgar",
    f"{SEC}/files/company_tickers.json",
]

REFUSED_URLS = [
    f"{PAPER}/v2/orders",
    f"{PAPER}/v2/orders/abc",
    f"{PAPER}/v2/positions/SPY",  # DELETE here would close a position; GET is not needed
    f"{PAPER}/v2/account/configurations",
    f"{PAPER}/v2/watchlists",
    f"{PAPER}/v2/%6Frders",
    f"{PAPER}/v2/account/",
    f"{PAPER}/v2/../v2/orders",
    "https://api.alpaca.markets/v2/account",  # live host
    "https://PAPER-API.alpaca.markets.evil.test/v2/account",
    "http://paper-api.alpaca.markets/v2/account",
    "https://paper-api.alpaca.markets:8443/v2/account",
    "https://user:pw@paper-api.alpaca.markets/v2/account",
    f"{PAPER}/v2/account?x=1",
    f"{DATA}/v2/stocks/AAPL/quotes",
    f"{DATA}/v1beta1/news/../../v2/orders",
    f"{SEC}/cgi-bin/browse-edgar/",
    f"{SEC}/Archives/edgar/data/320193/",
    f"{SEC}/cgi-bin/srch-edgar",
    "https://efts.sec.gov/LATEST/search-index",
    "https://sec.gov/files/company_tickers.json",
    "https://example.com/v2/account",
]

NON_GET = ["POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "get", "Get", " GET", ""]


@pytest.mark.parametrize("url", ALLOWED_URLS)
def test_allowlisted_get_is_sent(url: str) -> None:
    fake = FakeHttp()
    client = ReadOnlyHttp(fake)
    asyncio.run(client.get(url))
    assert [c[0] for c in fake.calls] == [url]
    assert client.sent == 1


@pytest.mark.parametrize("url", REFUSED_URLS)
def test_off_allowlist_refused_before_send(url: str) -> None:
    fake = FakeHttp()
    client = ReadOnlyHttp(fake)
    with pytest.raises(RefusedRequestError):
        asyncio.run(client.get(url))
    assert fake.calls == []
    assert client.refused == 1


@pytest.mark.parametrize("method", NON_GET)
@pytest.mark.parametrize(
    "url", [f"{PAPER}/v2/orders", f"{PAPER}/v2/account", f"{SEC}/cgi-bin/browse-edgar"]
)
def test_every_non_get_verb_refused_before_send(method: str, url: str) -> None:
    fake = FakeHttp()
    client = ReadOnlyHttp(fake)
    with pytest.raises(RefusedRequestError, match="only GET"):
        asyncio.run(client.fetch(method, url))
    assert fake.calls == []


def test_allowlist_has_no_order_route() -> None:
    assert all("order" not in path for _, path in ALLOWLIST)
    assert {h for h, _ in ALLOWLIST} == {
        "paper-api.alpaca.markets",
        "data.alpaca.markets",
        "www.sec.gov",
    }


def test_check_request_returns_host_and_path() -> None:
    assert check_request("GET", f"{SEC}/files/company_tickers.json") == (
        "www.sec.gov",
        "/files/company_tickers.json",
    )
