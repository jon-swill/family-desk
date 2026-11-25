from __future__ import annotations

import pytest

from family_desk_spike.core.backoff import backoff_delay
from family_desk_spike.core.staleness import SeriesStats, StalenessTracker, summarize


def test_stale_reported_once_then_fresh() -> None:
    t = StalenessTracker(stale_after=60, started_at=0, keys=("A", "B"))
    assert t.observe("A", 10) == []
    assert t.check(59) == []
    assert [k for k, s, _ in t.check(61) if s == "stale"] == ["B"]  # B never seen
    assert t.check(62) == []  # once only
    assert [k for k, s, _ in t.check(71)] == ["A"]
    fresh = t.observe("A", 80)
    assert fresh == [("A", "fresh", 70)]
    assert t.stale == {"B"}
    assert t.max_gap["A"] == 70
    assert t.stale_events == {"B": 1, "A": 1}


def test_series_stats_summary() -> None:
    s = SeriesStats()
    for i in range(10):
        s.add(float(i), 100.0 + i)
    s.add(None, None)
    out = s.summary(duration_s=120)
    assert out["count"] == 11
    assert out["updates_per_min"] == 5.5
    assert out["spread_bps_median"] == 4.5
    assert out["spread_bps_p95"] == 9.0
    assert out["skew_ms_median"] == 104.5


def test_summarize_includes_unseen_keys() -> None:
    out = summarize({}, ["X"], 60)
    assert out["X"]["count"] == 0 and out["X"]["spread_bps_median"] is None


@pytest.mark.parametrize("r", [0.0, 0.5, 1.0])
def test_backoff_capped_and_never_zero(r: float) -> None:
    delays = [backoff_delay(a, initial=1, maximum=60, rand=lambda: r) for a in range(1, 20)]
    assert all(0.5 <= d <= 60 for d in delays)
    assert delays[-1] >= 30
    assert delays == sorted(delays)


def test_backoff_floor_and_validation() -> None:
    assert backoff_delay(1, initial=1, maximum=60, rand=lambda: 0, floor=600) == 600
    with pytest.raises(ValueError, match="1-based"):
        backoff_delay(0, initial=1, maximum=60, rand=lambda: 0)
