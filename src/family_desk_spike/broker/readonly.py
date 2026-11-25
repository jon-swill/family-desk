"""Read-only broker adapter interface (FR-3, partial). No trading capability exists here."""

from __future__ import annotations

from typing import Protocol

from family_desk_spike.models import Account, MarketClock, Position


class ReadOnlyBroker(Protocol):
    async def get_account(self) -> Account: ...

    async def get_positions(self) -> list[Position]: ...

    async def get_clock(self) -> MarketClock: ...
