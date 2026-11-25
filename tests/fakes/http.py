from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass, field

from family_desk_spike.net.readonly_http import HttpResponse


@dataclass
class FakeHttp:
    """GetTransport fake. Routes by URL (no query); records every call that reached it."""

    routes: dict[str, list[HttpResponse]] = field(default_factory=dict)
    calls: list[tuple[str, dict[str, str], dict[str, str]]] = field(default_factory=list)
    default: HttpResponse = field(default_factory=lambda: HttpResponse(404, b"{}"))

    def add(self, url: str, *responses: HttpResponse) -> FakeHttp:
        self.routes.setdefault(url, []).extend(responses)
        return self

    def add_json(self, url: str, body: bytes, status: int = 200) -> FakeHttp:
        return self.add(url, HttpResponse(status, body))

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str],
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResponse:
        await asyncio.sleep(0)
        self.calls.append((url, dict(params), dict(headers)))
        queue = self.routes.get(url)
        if not queue:
            return self.default
        return queue.pop(0) if len(queue) > 1 else queue[0]
