from __future__ import annotations

import pytest

from family_desk_spike.core.ratelimit import RateMeter, TokenBucket
from tests.fakes.clock import FakeClock


def test_thousand_simulated_polls_never_exceed_one_per_second() -> None:
    """D15 proof: 1,000 back-to-back requests through the bucket on a FakeClock."""
    clock = FakeClock()
    bucket = TokenBucket(rate=1.0)
    meter = RateMeter()
    for _ in range(1000):
        wait = bucket.wait_time(clock.monotonic())
        if wait > 0:
            clock.sleep_sync(wait)
        bucket.take(clock.monotonic())
        meter.record(clock.monotonic())
    assert len(meter.times) == 1000
    assert meter.max_in_window(1.0) == 1
    gaps = [b - a for a, b in zip(meter.times, meter.times[1:], strict=False)]
    assert min(gaps) >= 1.0 - 1e-9
    rate = meter.mean_rate()
    assert rate is not None and rate <= 1.0 + 1e-9


def test_take_without_token_raises() -> None:
    b = TokenBucket(rate=1.0)
    b.take(0.0)
    with pytest.raises(RuntimeError):
        b.take(0.5)
    assert b.wait_time(0.5) == pytest.approx(0.5)


def test_meter_detects_bursts() -> None:
    m = RateMeter()
    for t in (0.0, 0.2, 0.4, 2.0):
        m.record(t)
    assert m.max_in_window(1.0) == 3
    assert RateMeter().mean_rate() is None


def test_invalid_bucket() -> None:
    with pytest.raises(ValueError, match="rate"):
        TokenBucket(rate=0)
