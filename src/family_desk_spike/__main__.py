"""`python -m family_desk_spike --duration-min N`: the Phase 1 read-only spike run.

There is deliberately no flag to bypass the paper, config-hash, clean-tree or
run-window checks (R-14, AS-14).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from family_desk_spike.core.clock import SystemClock
from family_desk_spike.data.stream_client import websockets_connector
from family_desk_spike.net.readonly_http import HttpxTransport
from family_desk_spike.runner import Deps, run_sync
from family_desk_spike.startup import SubprocessGit

MAX_DURATION_MIN = 120


def _duration(text: str) -> int:
    value = int(text)
    if not 1 <= value <= MAX_DURATION_MIN:
        raise argparse.ArgumentTypeError(f"duration must be 1..{MAX_DURATION_MIN} minutes")
    return value


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m family_desk_spike", description=__doc__)
    ap.add_argument("--duration-min", type=_duration, required=True)
    args = ap.parse_args(argv)
    root = Path.cwd()
    transport = HttpxTransport()
    deps = Deps(
        root=root,
        transport=transport,
        connector=websockets_connector,
        clock=SystemClock(),
        git=SubprocessGit(str(root)),
        close_transport=transport.aclose,
    )
    return run_sync(deps, args.duration_min).exit_code


if __name__ == "__main__":
    raise SystemExit(main())
