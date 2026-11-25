"""Capped exponential backoff with full jitter (pure; NFR-4, F-05/R-23)."""

from __future__ import annotations

from collections.abc import Callable


def backoff_delay(
    attempt: int,
    *,
    initial: float,
    maximum: float,
    rand: Callable[[], float],
    floor: float = 0.0,
) -> float:
    """Delay before reconnect `attempt` (1-based), capped at `maximum`.

    `floor` wins over `maximum` (used for long mandated waits, e.g. an EDGAR block).
    Jitter is "equal jitter": half the capped exponential plus a random half, so the
    delay never collapses toward zero and a reconnect loop can't go hot.
    """
    if attempt < 1:
        raise ValueError("attempt is 1-based")
    capped = min(maximum, initial * float(2 ** min(attempt - 1, 60)))
    delay = capped / 2 + rand() * capped / 2
    return max(floor, min(maximum, delay))
