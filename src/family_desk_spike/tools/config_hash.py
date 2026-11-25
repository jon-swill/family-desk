"""Print or write the sha256 of config/spike.toml.

Usage: `python -m family_desk_spike.tools.config_hash [--write]`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from family_desk_spike.config import CONFIG_FILE, CONFIG_HASH_FILE, sha256_hex


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="write config/spike.toml.sha256")
    ap.add_argument("--root", default=".", help="repo root")
    args = ap.parse_args(argv)
    root = Path(args.root)
    digest = sha256_hex((root / CONFIG_FILE).read_bytes())
    line = f"{digest}  spike.toml\n"
    if args.write:
        (root / CONFIG_HASH_FILE).write_text(line, encoding="utf-8", newline="\n")
    print(line, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
