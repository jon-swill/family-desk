"""Startup self-check (D9, G-8, invariant 17, R-13).

Every check is evaluated and every failure is reported with a reason code, so a
refusal demo can prove the check it targets (P-06). Stated limit: the config hash
detects drift, not deliberate tampering, until Phase 3 adds signed config.
"""

from __future__ import annotations

import subprocess
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from family_desk_spike.config import (
    CONFIG_FILE,
    CONFIG_HASH_FILE,
    ENV_FILE,
    Settings,
    SpikeConfig,
    extract_emails,
    load_settings,
    parse_config,
    parse_expected_hash,
    read_settings,
    sha256_hex,
)

PAPER_TRADING_BASE_URL = "https://paper-api.alpaca.markets"
PAPER_FLAG_VALUE = "true"
CLEAN_TREE_PATHS = ("src", "config")

HOST = "host"
PAPER_FLAG = "paper_flag"
CONFIG_HASH = "config_hash"
VERSION = "version"
DIRTY_TREE = "dirty_tree"
MISSING_UA = "missing_ua"
MISSING_KEY = "missing_key"


@dataclass(frozen=True)
class Failure:
    code: str
    reason: str


@dataclass(frozen=True)
class StartupReport:
    failures: tuple[Failure, ...]
    package_version: str
    config_hash: str
    commit: str | None = None
    live: bool = False

    @property
    def ok(self) -> bool:
        return not self.failures

    @property
    def codes(self) -> list[str]:
        return [f.code for f in self.failures]

    def lines(self) -> list[str]:
        """Human report. Contains no secret or UA value by construction."""
        out = [
            f"version={self.package_version}",
            f"commit={self.commit or 'n/a'}",
            f"config_sha256={self.config_hash}",
        ]
        if self.ok:
            out.append("startup OK")
        else:
            out.append(f"startup REFUSED codes={','.join(self.codes)}")
            out.extend(f"  [{f.code}] {f.reason}" for f in self.failures)
        return out


class StartupRefusedError(RuntimeError):
    def __init__(self, report: StartupReport) -> None:
        super().__init__("startup refused: " + ",".join(report.codes))
        self.report = report


class GitReader(Protocol):
    def status_porcelain(self, paths: tuple[str, ...]) -> str: ...

    def head_commit(self) -> str: ...


@dataclass(frozen=True)
class SubprocessGit:
    """Read-only git queries (status, rev-parse)."""

    cwd: str = "."
    timeout: float = 10.0
    _base: tuple[str, ...] = field(default=("git",), repr=False)

    def _run(self, *args: str) -> str:
        done = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [*self._base, *args],
            cwd=self.cwd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True,
        )
        return done.stdout

    def status_porcelain(self, paths: tuple[str, ...]) -> str:
        return self._run("status", "--porcelain", "--", *paths)

    def head_commit(self) -> str:
        return self._run("rev-parse", "HEAD").strip()


def assert_paper(trading_base_url: str, paper_flag: str) -> list[Failure]:
    out: list[Failure] = []
    if trading_base_url.rstrip("/") != PAPER_TRADING_BASE_URL:
        out.append(Failure(HOST, f"trading_base_url is not exactly {PAPER_TRADING_BASE_URL}"))
    if paper_flag != PAPER_FLAG_VALUE:
        out.append(Failure(PAPER_FLAG, f"APCA_PAPER must be exactly {PAPER_FLAG_VALUE!r}"))
    return out


def pyproject_version(pyproject_text: str) -> str:
    version = tomllib.loads(pyproject_text).get("project", {}).get("version", "")
    return str(version)


def evaluate_startup(
    *,
    settings: Settings,
    config: SpikeConfig | None,
    config_hash: str,
    expected_config_hash: str,
    package_version: str,
    pyproject_text: str,
    live: bool,
    git: GitReader | None,
    config_error: str | None = None,
) -> StartupReport:
    """Pure: evaluates every check and returns all failures with reason codes."""
    failures: list[Failure] = []

    if config is None:
        failures.append(Failure(HOST, f"config did not parse: {config_error or 'unknown'}"))
        failures.extend(f for f in assert_paper("", settings.paper_flag) if f.code != HOST)
    else:
        failures.extend(assert_paper(config.alpaca.trading_base_url, settings.paper_flag))

    if not expected_config_hash:
        failures.append(Failure(CONFIG_HASH, "no expected hash committed"))
    elif config_hash != expected_config_hash:
        failures.append(Failure(CONFIG_HASH, "config sha256 does not match committed hash"))

    expected_version = pyproject_version(pyproject_text)
    if package_version != expected_version:
        failures.append(
            Failure(VERSION, f"package {package_version!r} != pyproject.toml {expected_version!r}")
        )

    ua = settings.sec_user_agent.get_secret_value()
    n_emails = len(extract_emails(ua))
    if not ua or n_emails != 1:
        failures.append(
            Failure(
                MISSING_UA, f"SEC_USER_AGENT must be set with exactly one email (found {n_emails})"
            )
        )

    if not settings.api_key_id.get_secret_value() or not settings.api_secret_key.get_secret_value():
        failures.append(Failure(MISSING_KEY, "APCA_API_KEY_ID and APCA_API_SECRET_KEY must be set"))

    commit: str | None = None
    if live:
        if git is None:
            failures.append(Failure(DIRTY_TREE, "live run needs a git reader"))
        else:
            try:
                dirty = git.status_porcelain(CLEAN_TREE_PATHS).strip()
                commit = git.head_commit()
            except (OSError, subprocess.SubprocessError) as exc:
                failures.append(Failure(DIRTY_TREE, f"git query failed: {type(exc).__name__}"))
            else:
                if dirty:
                    n = len(dirty.splitlines())
                    failures.append(
                        Failure(DIRTY_TREE, f"{n} uncommitted change(s) under src/ or config/")
                    )

    return StartupReport(
        failures=tuple(failures),
        package_version=package_version,
        config_hash=config_hash,
        commit=commit,
        live=live,
    )


@dataclass(frozen=True)
class StartupResult:
    report: StartupReport
    settings: Settings
    config: SpikeConfig | None


def run_startup(
    root: Path, *, live: bool, git: GitReader | None, env: Mapping[str, str] | None = None
) -> StartupResult:
    """I/O edge: read `.env` (through config), config, its hash and pyproject, then check."""
    import family_desk_spike

    settings = load_settings(env) if env is not None else read_settings(root / ENV_FILE)
    config_bytes = (root / CONFIG_FILE).read_bytes()
    config: SpikeConfig | None
    config_error: str | None = None
    try:
        config = parse_config(config_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        config, config_error = None, type(exc).__name__
    hash_path = root / CONFIG_HASH_FILE
    expected = (
        parse_expected_hash(hash_path.read_text(encoding="utf-8")) if hash_path.exists() else ""
    )
    report = evaluate_startup(
        settings=settings,
        config=config,
        config_hash=sha256_hex(config_bytes),
        expected_config_hash=expected,
        package_version=family_desk_spike.__version__,
        pyproject_text=(root / "pyproject.toml").read_text(encoding="utf-8"),
        live=live,
        git=git,
        config_error=config_error,
    )
    return StartupResult(report=report, settings=settings, config=config)
