"""parse_account: required fields fail closed, other drift is reported, values never leak."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from family_desk_spike.parse.alpaca_rest import (
    ACCOUNT_DOCUMENTED_FIELDS,
    ParseError,
    SchemaDriftError,
    parse_account,
)

FIX = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict[str, Any]:
    data = json.loads((FIX / name).read_bytes())
    assert isinstance(data, dict)
    return data


def _body(data: dict[str, Any]) -> bytes:
    return json.dumps(data).encode()


def test_current_schema_without_pattern_day_trader_parses() -> None:
    """The B10 crash, 2026-11-25: Alpaca's /v2/account no longer sends pattern_day_trader."""
    account, drift = parse_account((FIX / "alpaca_account_no_pdt.json").read_bytes())
    assert account.status == "ACTIVE" and account.currency == "USD"
    assert account.trading_blocked is False and account.account_blocked is False
    assert account.pattern_day_trader is None
    assert account.cash == Decimal("100000")
    assert drift.missing_optional == ("pattern_day_trader",)
    assert drift.missing_required == () and drift.unknown == ()
    assert not drift.empty


def test_fixture_matches_documented_fields() -> None:
    assert set(_load("alpaca_account_no_pdt.json")) == ACCOUNT_DOCUMENTED_FIELDS


def test_legacy_payload_with_pattern_day_trader_has_no_drift() -> None:
    account, drift = parse_account((FIX / "alpaca_account.json").read_bytes())
    assert account.pattern_day_trader is False
    assert drift.empty


def test_unknown_fields_reported_by_name_only() -> None:
    data = _load("alpaca_account_no_pdt.json")
    data["daytrade_count"] = 3
    data["new_secret_thing"] = "VALUE-MUST-NOT-APPEAR"
    data["bad name; DROP"] = "x"
    data["z" * 65] = "x"
    account, drift = parse_account(_body(data))
    assert account.status == "ACTIVE"
    assert drift.unknown == ("daytrade_count", "new_secret_thing")
    assert drift.unknown_invalid_names == 2
    dumped = json.dumps(drift.payload())
    assert "VALUE-MUST-NOT-APPEAR" not in dumped and "DROP" not in dumped


def test_unknown_field_names_are_capped() -> None:
    data = _load("alpaca_account_no_pdt.json")
    data.update({f"extra_{i:03d}": i for i in range(80)})
    _, drift = parse_account(_body(data))
    assert len(drift.unknown) == 50


@pytest.mark.parametrize("field", ["status", "currency", "trading_blocked", "account_blocked"])
def test_missing_required_field_fails_closed_with_drift(field: str) -> None:
    data = _load("alpaca_account_no_pdt.json")
    del data[field]
    with pytest.raises(SchemaDriftError) as info:
        parse_account(_body(data))
    assert info.value.drift.missing_required == (field,)
    assert field in str(info.value)


def test_wrong_type_still_rejected_without_echoing_values() -> None:
    data = _load("alpaca_account_no_pdt.json")
    data["trading_blocked"] = "maybe"
    data["cash"] = "not-a-number"
    with pytest.raises(ParseError) as info:
        parse_account(_body(data))
    msg = str(info.value)
    assert "trading_blocked" in msg and "cash" in msg
    assert "maybe" not in msg and "PA0000000000" not in msg
    assert info.value.__cause__ is None and info.value.__suppress_context__


def test_non_object_rejected() -> None:
    with pytest.raises(ParseError):
        parse_account(b"[]")
