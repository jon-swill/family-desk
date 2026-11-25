from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from family_desk_spike.broker.alpaca_readonly import AlpacaReadOnly, ApiError
from family_desk_spike.broker.readonly import ReadOnlyBroker
from family_desk_spike.config import load_settings
from family_desk_spike.data.news_rest import fetch_recent_news, news_params, watchlist_matches
from family_desk_spike.net.readonly_http import HttpResponse, ReadOnlyHttp
from tests.fakes.env import FAKE_KEY_ID, FAKE_SECRET, fake_env
from tests.fakes.http import FakeHttp

FIX = Path(__file__).parent / "fixtures"
PAPER = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
WATCH = ("SPY", "QQQ", "IWM", "AAPL", "MSFT")


def _broker(fake: FakeHttp) -> AlpacaReadOnly:
    return AlpacaReadOnly(ReadOnlyHttp(fake), PAPER, load_settings(fake_env()))


def test_adapter_satisfies_protocol() -> None:
    broker: ReadOnlyBroker = _broker(FakeHttp())
    assert "SECRET" not in repr(broker).upper()


def test_account_positions_clock_parsed() -> None:
    fake = (
        FakeHttp()
        .add_json(f"{PAPER}/v2/account", (FIX / "alpaca_account.json").read_bytes())
        .add_json(f"{PAPER}/v2/positions", (FIX / "alpaca_positions_spy.json").read_bytes())
        .add_json(f"{PAPER}/v2/clock", (FIX / "alpaca_clock_open.json").read_bytes())
    )
    b = _broker(fake)
    account, _drift = asyncio.run(b.get_account())
    positions = asyncio.run(b.get_positions())
    clock = asyncio.run(b.get_clock())
    assert account.status == "ACTIVE" and account.cash == Decimal("100000")
    assert not hasattr(account, "account_number")
    assert "PA0000000000" not in account.model_dump_json()
    assert [(p.symbol, p.qty, p.side) for p in positions] == [("SPY", Decimal("1"), "long")]
    assert clock.is_open
    assert clock.next_close.astimezone(UTC) == datetime(2026, 11, 30, 21, 0, tzinfo=UTC)
    _url, params, headers = fake.calls[0]
    assert headers["APCA-API-KEY-ID"] == FAKE_KEY_ID
    assert headers["APCA-API-SECRET-KEY"] == FAKE_SECRET
    assert params == {}


def test_empty_positions_list() -> None:
    fake = FakeHttp().add_json(f"{PAPER}/v2/positions", b"[]")
    assert asyncio.run(_broker(fake).get_positions()) == []


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_non_2xx_raises_without_body(status: int) -> None:
    fake = FakeHttp().add(f"{PAPER}/v2/account", HttpResponse(status, b'{"secret":"x"}'))
    with pytest.raises(ApiError) as info:
        asyncio.run(_broker(fake).get_account())
    assert info.value.status == status
    assert "secret" not in str(info.value)


def test_news_rest_get_params_and_metadata_only() -> None:
    fake = FakeHttp().add_json(f"{DATA}/v1beta1/news", (FIX / "alpaca_news_page.json").read_bytes())
    now = datetime(2026, 11, 30, 15, 0, tzinfo=UTC)
    items = asyncio.run(
        fetch_recent_news(
            ReadOnlyHttp(fake),
            data_base_url=DATA,
            settings=load_settings(fake_env()),
            symbols=WATCH,
            now=now,
            lookback_hours=24,
            limit=50,
        )
    )
    _, params, _ = fake.calls[0]
    assert params == news_params(WATCH, now, 24, 50)
    assert params["start"] == "2026-11-29T15:00:00Z"
    assert params["symbols"] == "SPY,QQQ,IWM,AAPL,MSFT"
    assert len(items) == 2
    dumped = "".join(i.model_dump_json() for i in items)
    assert "MUST NOT BE STORED" not in dumped
    assert [n.id for n in watchlist_matches(items, WATCH)] == [40000001]
    # Hostile headline is kept as inert data, nothing more.
    assert items[1].headline.startswith("Ignore previous instructions")
