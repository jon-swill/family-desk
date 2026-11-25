"""Per-key staleness and update-rate/spread stats (pure; FR-10, inv. 14, R-23).

Staleness here is measured and logged only. Nothing trades in Phase 1, so there is
no halting logic.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal

Transition = tuple[str, Literal["stale", "fresh"], float]


@dataclass
class StalenessTracker:
    """Tracks when each key was last seen. A key with no update for longer than
    `stale_after` becomes stale (reported once); its next update makes it fresh."""

    stale_after: float
    started_at: float
    keys: tuple[str, ...]
    last_seen: dict[str, float] = field(default_factory=dict)
    stale: set[str] = field(default_factory=set)
    max_gap: dict[str, float] = field(default_factory=dict)
    stale_events: dict[str, int] = field(default_factory=dict)

    def observe(self, key: str, now: float) -> list[Transition]:
        prev = self.last_seen.get(key, self.started_at)
        gap = now - prev
        self.max_gap[key] = max(self.max_gap.get(key, 0.0), gap)
        self.last_seen[key] = now
        if key in self.stale:
            self.stale.discard(key)
            return [(key, "fresh", gap)]
        return []

    def check(self, now: float) -> list[Transition]:
        out: list[Transition] = []
        for key in self.keys:
            gap = now - self.last_seen.get(key, self.started_at)
            if gap > self.stale_after and key not in self.stale:
                self.stale.add(key)
                self.stale_events[key] = self.stale_events.get(key, 0) + 1
                out.append((key, "stale", gap))
        return out


def _pct(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[idx]


@dataclass
class SeriesStats:
    count: int = 0
    spreads_bps: list[float] = field(default_factory=list)
    skews_ms: list[float] = field(default_factory=list)

    def add(self, spread_bps: float | None, skew_ms: float | None) -> None:
        self.count += 1
        if spread_bps is not None:
            self.spreads_bps.append(spread_bps)
        if skew_ms is not None:
            self.skews_ms.append(skew_ms)

    def summary(self, duration_s: float) -> dict[str, float | int | None]:
        minutes = duration_s / 60 if duration_s > 0 else 0.0
        return {
            "count": self.count,
            "updates_per_min": round(self.count / minutes, 2) if minutes else None,
            "spread_bps_median": _round(statistics.median(self.spreads_bps))
            if self.spreads_bps
            else None,
            "spread_bps_p95": _round(_pct(self.spreads_bps, 0.95)),
            "skew_ms_median": _round(statistics.median(self.skews_ms)) if self.skews_ms else None,
            "skew_ms_p95": _round(_pct(self.skews_ms, 0.95)),
        }


def _round(v: float | None) -> float | None:
    return None if v is None else round(v, 3)


def summarize(
    stats: dict[str, SeriesStats], keys: Iterable[str], duration_s: float
) -> dict[str, dict[str, float | int | None]]:
    return {k: stats.get(k, SeriesStats()).summary(duration_s) for k in keys}
