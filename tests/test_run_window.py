from __future__ import annotations

from datetime import datetime

import pytest

from family_desk_spike.core.run_window import ET, check_run_window
from family_desk_spike.models import MarketClock


def _clock(now: str, close: str, is_open: bool = True) -> MarketClock:
    return MarketClock(
        timestamp=datetime.fromisoformat(now).replace(tzinfo=ET),
        is_open=is_open,
        next_open=datetime.fromisoformat("2026-12-01T09:30").replace(tzinfo=ET),
        next_close=datetime.fromisoformat(close).replace(tzinfo=ET),
    )


FULL_CLOSE = "2026-11-30T16:00"


def test_inside_window_allowed() -> None:
    assert check_run_window(_clock("2026-11-30T10:30", FULL_CLOSE), duration_min=35) == []
    # Ends exactly at 15:30 ET: allowed.
    assert check_run_window(_clock("2026-11-30T14:55", FULL_CLOSE), duration_min=35) == []


def test_closed_market_refused() -> None:
    reasons = check_run_window(
        _clock("2026-11-30T10:30", FULL_CLOSE, is_open=False), duration_min=35
    )
    assert any("market closed" in r for r in reasons)


def test_before_ten_et_refused() -> None:
    reasons = check_run_window(_clock("2026-11-30T09:45", FULL_CLOSE), duration_min=35)
    assert any("before 10:00 ET" in r for r in reasons)


def test_run_crossing_buffer_refused() -> None:
    reasons = check_run_window(_clock("2026-11-30T15:00", FULL_CLOSE), duration_min=35)
    assert any("after next_close - 30 min (15:30 ET)" in r for r in reasons)


def test_half_day_close_refused() -> None:
    """27 Nov 2026 closes at 13:00 ET; a 35-minute run from 12:00 ends 12:35 > 12:30."""
    reasons = check_run_window(_clock("2026-11-27T12:00", "2026-11-27T13:00"), duration_min=35)
    assert any("12:30 ET" in r for r in reasons)
    assert check_run_window(_clock("2026-11-27T11:30", "2026-11-27T13:00"), duration_min=35) == []


def test_dst_is_handled_by_zoneinfo() -> None:
    """Summer (EDT, UTC-4) and winter (EST, UTC-5) both put 10:00 ET at the right UTC time."""
    summer = _clock("2026-07-01T10:00", "2026-07-01T16:00")
    winter = _clock("2026-12-01T10:00", "2026-12-01T16:00")
    assert summer.timestamp.utcoffset() != winter.timestamp.utcoffset()
    assert check_run_window(summer, duration_min=35) == []
    assert check_run_window(winter, duration_min=35) == []


@pytest.mark.parametrize("minutes", [0, -5])
def test_non_positive_duration_refused(minutes: int) -> None:
    assert check_run_window(_clock("2026-11-30T10:30", FULL_CLOSE), duration_min=minutes)
