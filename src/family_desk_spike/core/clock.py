"""Clock interface: aware UTC wall time plus a monotonic clock for intervals."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def __call__(self) -> datetime: ...

    def monotonic(self) -> float: ...


class SystemClock:
    def __call__(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return time.monotonic()
