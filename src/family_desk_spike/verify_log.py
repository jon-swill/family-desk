"""Verify a spike log: `python -m family_desk_spike.verify_log <file> [--expect-head HASH]`.

Prints `chain OK` or `chain FAILED`, `seq_last`, `head_hash` and per-source counts.
Exit code 0 only when the chain verifies (and matches `--expect-head` when given).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from family_desk_spike.applog import verify_lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify an append-only spike log.")
    ap.add_argument("file", type=Path)
    ap.add_argument("--expect-head", default=None, help="anchored head_hash from the evidence")
    args = ap.parse_args(argv)
    if not args.file.exists():
        print(f"chain FAILED\nerror: {args.file} not found")
        return 2
    result = verify_lines(args.file.read_text(encoding="utf-8"), expect_head=args.expect_head)
    for line in result.lines():
        print(line)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
