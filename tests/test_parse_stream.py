from __future__ import annotations

import json
from decimal import Decimal

from family_desk_spike.models import NewsItem, Quote, StreamControl, SubscriptionAck
from family_desk_spike.parse.alpaca_rest import parse_news_page
from family_desk_spike.parse.stream import parse_frame

QUOTE = {
    "T": "q",
    "S": "AAPL",
    "bx": "V",
    "bp": 230.10,
    "bs": 2,
    "ax": "V",
    "ap": 230.14,
    "as": 1,
    "c": ["R"],
    "z": "C",
    "t": "2026-11-30T15:30:00.123456789Z",
}


def test_quote_parsed_with_spread() -> None:
    frame = parse_frame(json.dumps([QUOTE]), "iex")
    (q,) = frame.messages
    assert isinstance(q, Quote)
    assert q.symbol == "AAPL"
    assert q.spread is not None and abs(q.spread - Decimal("0.04")) < Decimal("1e-9")
    assert q.spread_bps is not None and Decimal(1) < q.spread_bps < Decimal(2)


def test_crossed_or_zero_quote_has_no_spread() -> None:
    crossed = parse_frame(json.dumps([{**QUOTE, "bp": 231, "ap": 230}]), "iex").messages[0]
    zero = parse_frame(json.dumps([{**QUOTE, "bp": 0}]), "iex").messages[0]
    assert isinstance(crossed, Quote) and crossed.spread is None
    assert isinstance(zero, Quote) and zero.spread_bps is None


def test_control_and_subscription_messages() -> None:
    raw = json.dumps(
        [
            {"T": "success", "msg": "connected"},
            {"T": "success", "msg": "authenticated"},
            {"T": "subscription", "trades": [], "quotes": ["SPY", "AAPL"], "bars": []},
            {"T": "error", "code": 406, "msg": "connection limit exceeded"},
        ]
    )
    msgs = parse_frame(raw, "iex").messages
    assert [type(m) for m in msgs] == [StreamControl, StreamControl, SubscriptionAck, StreamControl]
    ack = msgs[2]
    assert isinstance(ack, SubscriptionAck) and ack.quotes == ("SPY", "AAPL")
    err = msgs[3]
    assert isinstance(err, StreamControl) and err.code == 406


def test_news_stream_message_metadata_only() -> None:
    raw = json.dumps(
        [
            {
                "T": "n",
                "id": 7,
                "headline": "H" * 5000,
                "summary": "drop me",
                "content": "<p>drop me</p>",
                "author": "x",
                "created_at": "2026-11-30T15:00:00Z",
                "updated_at": "2026-11-30T15:00:00Z",
                "url": "https://example.test/n/7",
                "symbols": ["MSFT"],
                "source": "benzinga",
            }
        ]
    )
    (n,) = parse_frame(raw, "news").messages
    assert isinstance(n, NewsItem)
    assert len(n.headline) == 1000
    assert "drop me" not in n.model_dump_json()


def test_malformed_and_unknown_are_counted_not_raised() -> None:
    raw = json.dumps([{"T": "t", "S": "SPY"}, {"T": "q", "S": "SPY"}, 5, {"T": "b"}])
    frame = parse_frame(raw, "iex")
    assert frame.messages == []
    assert frame.ignored == 2
    assert frame.malformed == 2
    assert parse_frame("not json", "iex").malformed == 1
    assert parse_frame(b"\xff\xfe", "iex").malformed == 1
    assert parse_frame("42", "iex").malformed == 1


def test_single_object_frame_accepted() -> None:
    assert len(parse_frame(json.dumps({"T": "success", "msg": "connected"}), "x").messages) == 1


def test_news_page_without_token() -> None:
    items, token = parse_news_page(b'{"news": [], "next_page_token": null}')
    assert items == [] and token is None
