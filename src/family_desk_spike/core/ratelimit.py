"""Token bucket and measured request rate (pure; C-7: <=1 EDGAR request per second)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    """`rate` tokens per second, at most `capacity` banked. Capacity 1 means requests are
    spaced at least 1/rate seconds apart, so no 1-second window holds more than `rate`."""

    rate: float
    capacity: float = 1.0
    tokens: float = field(init=False)
    last: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.rate <= 0 or self.capacity < 1:
            raise ValueError("rate must be > 0 and capacity >= 1")
        self.tokens = self.capacity

    def _refill(self, now: float) -> None:
        if self.last is not None:
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now

    def wait_time(self, now: float) -> float:
        """Seconds to wait before a token is available (0 if one is available now)."""
        self._refill(now)
        return 0.0 if self.tokens >= 1 else (1 - self.tokens) / self.rate

    def take(self, now: float) -> None:
        self._refill(now)
        if self.tokens < 1:
            raise RuntimeError("no token available; call wait_time first")
        self.tokens -= 1


@dataclass
class RateMeter:
    """Records request times; reports the busiest 1-second window and the mean rate."""

    times: list[float] = field(default_factory=list)

    def record(self, now: float) -> None:
        self.times.append(now)

    def max_in_window(self, window: float = 1.0) -> int:
        best = 0
        q: deque[float] = deque()
        for t in self.times:
            q.append(t)
            while q and t - q[0] >= window:
                q.popleft()
            best = max(best, len(q))
        return best

    def mean_rate(self) -> float | None:
        if len(self.times) < 2:
            return None
        span = self.times[-1] - self.times[0]
        return (len(self.times) - 1) / span if span > 0 else None
