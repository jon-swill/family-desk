"""Read-only broker adapter interface (FR-3, partial). No trading capability exists here."""

from __future__ import annotations

from typing import Protocol

from family_desk_spike.models import Account, MarketClock, Position
from family_desk_spike.parse.alpaca_rest import SchemaDrift


class ReadOnlyBroker(Protocol):
    async def get_account(self) -> tuple[Account, SchemaDrift]: ...

    async def get_positions(self) -> list[Position]: ...

    async def get_clock(self) -> MarketClock: ...
