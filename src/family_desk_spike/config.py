"""Typed settings and config. This module is the only reader of `.env`.

Secrets and the SEC User-Agent contact are held as `SecretStr`, so their repr and str
are masked. Parsing is pure; the two file readers at the bottom are the I/O edge.
"""

from __future__ import annotations

import hashlib
import re
import tomllib
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr

ENV_FILE = Path(".env")
CONFIG_FILE = Path("config/spike.toml")
CONFIG_HASH_FILE = Path("config/spike.toml.sha256")

ENV_KEY_ID = "APCA_API_KEY_ID"
ENV_SECRET = "APCA_API_SECRET_KEY"  # noqa: S105 - variable name, not a value
ENV_PAPER = "APCA_PAPER"
ENV_UA = "SEC_USER_AGENT"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")


class Settings(BaseModel):
    """Values from `.env`. Empty strings mean missing; the startup check reports them."""

    model_config = ConfigDict(frozen=True)

    api_key_id: SecretStr
    api_secret_key: SecretStr
    paper_flag: str
    sec_user_agent: SecretStr


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AlpacaConfig(_Frozen):
    trading_base_url: str
    data_base_url: str
    stock_stream_url: str
    news_stream_url: str


class WatchlistConfig(_Frozen):
    symbols: tuple[str, ...] = Field(min_length=1)


class NewsConfig(_Frozen):
    rest_lookback_hours: int = Field(gt=0, le=168)
    rest_limit: int = Field(gt=0, le=50)


class StreamsConfig(_Frozen):
    stale_after_seconds: float = Field(gt=0)
    backoff_initial_seconds: float = Field(gt=0)
    backoff_max_seconds: float = Field(gt=0)
    connection_limit_backoff_seconds: float = Field(gt=0)


class EdgarConfig(_Frozen):
    base_url: str
    symbols: tuple[str, ...]
    poll_seconds: float = Field(ge=1)
    max_requests_per_second: float = Field(gt=0, le=1.0)
    feed_count: int = Field(gt=0, le=100)
    block_backoff_seconds: float = Field(ge=600)


class RunConfig(_Frozen):
    earliest_start_et: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_buffer_minutes: int = Field(ge=30)


class LogConfig(_Frozen):
    dir: str


class SpikeConfig(_Frozen):
    alpaca: AlpacaConfig
    watchlist: WatchlistConfig
    news: NewsConfig
    streams: StreamsConfig
    edgar: EdgarConfig
    run: RunConfig
    log: LogConfig


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse KEY=VALUE lines. Blank lines and `#` comments are skipped; quotes are stripped."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.startswith("export "):
            key = key[len("export ") :]
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key.strip()] = value
    return out


def load_settings(env: Mapping[str, str]) -> Settings:
    return Settings(
        api_key_id=SecretStr(env.get(ENV_KEY_ID, "").strip()),
        api_secret_key=SecretStr(env.get(ENV_SECRET, "").strip()),
        paper_flag=env.get(ENV_PAPER, "").strip(),
        sec_user_agent=SecretStr(env.get(ENV_UA, "").strip()),
    )


def extract_emails(text: str) -> list[str]:
    return EMAIL_RE.findall(text)


def parse_config(text: str) -> SpikeConfig:
    return SpikeConfig.model_validate(tomllib.loads(text))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_expected_hash(text: str) -> str:
    """First token of a `sha256sum`-style line."""
    parts = text.split()
    return parts[0].lower() if parts else ""


# --- I/O edge -------------------------------------------------------------------------


def read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    """The only `.env` reader in the repo. Returns {} if the file is absent."""
    if not path.exists():
        return {}
    return parse_dotenv(path.read_text(encoding="utf-8"))


def read_settings(path: Path = ENV_FILE) -> Settings:
    return load_settings(read_env_file(path))
