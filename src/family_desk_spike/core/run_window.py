"""Run-window check (pure; inv. 14, R-24, F-06). There is no bypass flag anywhere:
off-hours behaviour is exercised only in tests through a fake clock.

A live run may start only when the market is open per Alpaca's /v2/clock, at or after
10:00 ET, and its planned end must be at or before next_close minus the buffer
(15:30 ET on a full day, earlier on a half-day such as 27 Nov 2026).
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from family_desk_spike.models import MarketClock

ET = ZoneInfo("America/New_York")


def parse_hhmm(text: str) -> time:
    hh, mm = text.split(":")
    return time(int(hh), int(mm))


def check_run_window(
    clock: MarketClock,
    *,
    duration_min: int,
    earliest_start_et: str = "10:00",
    end_buffer_min: int = 30,
) -> list[str]:
    """Reasons to refuse (empty list = allowed). `clock.timestamp` is the broker's now."""
    reasons: list[str] = []
    if duration_min <= 0:
        reasons.append("duration must be positive")
    now_et = clock.timestamp.astimezone(ET)
    if not clock.is_open:
        reasons.append("market closed per /v2/clock")
    earliest = datetime.combine(now_et.date(), parse_hhmm(earliest_start_et), tzinfo=ET)
    if now_et < earliest:
        reasons.append(f"start {now_et:%H:%M} ET is before {earliest_start_et} ET")
    planned_end = clock.timestamp + timedelta(minutes=max(duration_min, 0))
    latest_end = clock.next_close - timedelta(minutes=end_buffer_min)
    if planned_end > latest_end:
        reasons.append(
            f"planned end {planned_end.astimezone(ET):%H:%M} ET is after next_close - "
            f"{end_buffer_min} min ({latest_end.astimezone(ET):%H:%M} ET)"
        )
    if clock.next_close <= clock.timestamp:
        reasons.append("next_close is not in the future")
    return reasons
