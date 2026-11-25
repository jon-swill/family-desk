"""Full-value secret scan (D20, G-10): `python -m family_desk_spike.tools.secret_scan`.

Loads the two Alpaca values and the single email address in SEC_USER_AGENT only
through `family_desk_spike.config` (the only `.env` reader). Searches git history
(`git log -p --all`), every tracked file, `logs/` and `docs/` (which includes
`logs/pytest_output.txt` when saved). Prints only `found` / `not found` per value
name and location; never a value. Exit 0 when nothing is found, 1 when anything is,
2 when it refuses to run.
"""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from family_desk_spike.config import (
    ENV_FILE,
    ENV_KEY_ID,
    ENV_SECRET,
    Settings,
    extract_emails,
    read_settings,
)

UA_EMAIL = "SEC_USER_AGENT_EMAIL"
LOCATIONS = ("git_history", "tracked_files", "logs", "docs")


class ScanRefusedError(ValueError):
    pass


def scan_values(settings: Settings) -> dict[str, bytes]:
    """The three values to look for, by name. Refuses on missing or ambiguous values."""
    key_id = settings.api_key_id.get_secret_value()
    secret = settings.api_secret_key.get_secret_value()
    emails = extract_emails(settings.sec_user_agent.get_secret_value())
    missing = [n for n, v in ((ENV_KEY_ID, key_id), (ENV_SECRET, secret)) if not v]
    if missing:
        raise ScanRefusedError(f"refusing: {', '.join(missing)} not set")
    if len(emails) != 1:
        raise ScanRefusedError(
            f"refusing: SEC_USER_AGENT must contain exactly one email address (found {len(emails)})"
        )
    return {
        ENV_KEY_ID: key_id.encode("utf-8"),
        ENV_SECRET: secret.encode("utf-8"),
        UA_EMAIL: emails[0].lower().encode("utf-8"),
    }


def _contains(blob: bytes, name: str, value: bytes) -> bool:
    # Emails are matched case-insensitively; keys exactly.
    return value in (blob.lower() if name == UA_EMAIL else blob)


def scan(
    values: Mapping[str, bytes], sources: Mapping[str, Iterable[bytes]]
) -> dict[tuple[str, str], bool]:
    """Pure core: for every (value name, location) pair, is the value present?"""
    found = {(name, loc): False for name in values for loc in sources}
    for loc, blobs in sources.items():
        for blob in blobs:
            for name, value in values.items():
                if not found[(name, loc)] and _contains(blob, name, value):
                    found[(name, loc)] = True
    return found


def report_lines(found: Mapping[tuple[str, str], bool]) -> list[str]:
    return [
        f"{name} @ {loc}: {'found' if hit else 'not found'}"
        for (name, loc), hit in sorted(found.items())
    ]


# --- I/O edge -------------------------------------------------------------------------


class ScanGit(Protocol):
    def log_patch_all(self) -> bytes: ...

    def ls_files(self) -> list[str]: ...


@dataclass(frozen=True)
class SubprocessScanGit:
    cwd: str = "."

    def _run(self, *args: str) -> bytes:
        return subprocess.run(  # noqa: S603 - fixed argv, no shell, read-only
            ["git", *args],  # noqa: S607 - git on PATH
            cwd=self.cwd,
            capture_output=True,
            check=True,
            timeout=300,
        ).stdout

    def log_patch_all(self) -> bytes:
        return self._run("log", "-p", "--all", "--no-color", "--no-ext-diff")

    def ls_files(self) -> list[str]:
        return [p for p in self._run("ls-files", "-z").decode("utf-8").split("\0") if p]


def _read_tree(base: Path) -> Iterator[bytes]:
    if not base.exists():
        return
    for p in sorted(base.rglob("*")):
        if p.is_file():
            yield p.read_bytes()


def _read_tracked(root: Path, paths: list[str]) -> Iterator[bytes]:
    for rel in paths:
        p = root / rel
        if p.is_file():
            yield p.read_bytes()


def collect_sources(root: Path, git: ScanGit) -> dict[str, Iterable[bytes]]:
    return {
        "git_history": [git.log_patch_all()],
        "tracked_files": _read_tracked(root, git.ls_files()),
        "logs": _read_tree(root / "logs"),
        "docs": _read_tree(root / "docs"),
    }


def run(root: Path, settings: Settings, git: ScanGit) -> tuple[int, list[str]]:
    try:
        values = scan_values(settings)
    except ScanRefusedError as exc:
        return 2, [str(exc)]
    found = scan(values, collect_sources(root, git))
    lines = report_lines(found)
    any_found = any(found.values())
    lines.append("RESULT: FOUND (see lines above)" if any_found else "RESULT: all not found")
    return (1 if any_found else 0), lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Full-value secret scan; prints found/not found.")
    ap.add_argument("--root", default=".", help="repo root")
    args = ap.parse_args(argv)
    root = Path(args.root)
    code, lines = run(root, read_settings(root / ENV_FILE), SubprocessScanGit(str(root)))
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
