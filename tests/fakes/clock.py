from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class FakeClock:
    """Controllable wall clock (UTC) and monotonic clock. `sleep` advances time instantly."""

    now_utc: datetime = field(default_factory=lambda: datetime(2026, 11, 30, 15, 30, tzinfo=UTC))
    mono: float = 1000.0
    sleeps: list[float] = field(default_factory=list)

    def __call__(self) -> datetime:
        return self.now_utc

    def monotonic(self) -> float:
        return self.mono

    def advance(self, seconds: float) -> None:
        self.mono += seconds
        self.now_utc += timedelta(seconds=seconds)

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.advance(max(0.0, seconds))

    def sleep_sync(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.advance(max(0.0, seconds))
