from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from family_desk_spike.config import (
    CONFIG_FILE,
    CONFIG_HASH_FILE,
    extract_emails,
    load_settings,
    parse_config,
    parse_dotenv,
    parse_expected_hash,
    read_env_file,
    sha256_hex,
)
from tests.fakes.env import FAKE_EMAIL, FAKE_KEY_ID, FAKE_SECRET, fake_env

ROOT = Path(__file__).resolve().parents[1]


def test_parse_dotenv_handles_comments_quotes_and_export() -> None:
    text = "# c\n\nA=1\nexport B=\"two words\"\nC='x=y'\nnot a pair\nD = spaced \n"
    assert parse_dotenv(text) == {"A": "1", "B": "two words", "C": "x=y", "D": "spaced"}


def test_settings_mask_secrets_in_repr_and_str() -> None:
    s = load_settings(fake_env())
    for rendered in (repr(s), str(s), s.model_dump_json()):
        assert FAKE_KEY_ID not in rendered
        assert FAKE_SECRET not in rendered
        assert FAKE_EMAIL not in rendered
    assert s.api_key_id.get_secret_value() == FAKE_KEY_ID
    assert s.paper_flag == "true"


def test_missing_values_become_empty_not_errors() -> None:
    s = load_settings({})
    assert s.api_key_id.get_secret_value() == ""
    assert s.paper_flag == ""


def test_read_env_file_absent_returns_empty(tmp_path: Path) -> None:
    assert read_env_file(tmp_path / ".env") == {}


def test_read_env_file_reads_fake_file(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("APCA_PAPER=true\n", encoding="utf-8")
    assert read_env_file(p) == {"APCA_PAPER": "true"}


@pytest.mark.parametrize(
    ("text", "n"),
    [("Name a@b.co", 1), ("Name", 0), ("a@b.co c@d.org", 2), ("x first.last+t@sub.example.com", 1)],
)
def test_extract_emails(text: str, n: int) -> None:
    assert len(extract_emails(text)) == n


def test_committed_config_parses_and_matches_its_hash() -> None:
    raw = (ROOT / CONFIG_FILE).read_bytes()
    cfg = parse_config(raw.decode("utf-8"))
    assert cfg.watchlist.symbols == ("SPY", "QQQ", "IWM", "AAPL", "MSFT")
    assert cfg.edgar.symbols == ("AAPL", "MSFT")
    assert cfg.edgar.max_requests_per_second <= 1.0
    assert cfg.alpaca.trading_base_url == "https://paper-api.alpaca.markets"
    expected = parse_expected_hash((ROOT / CONFIG_HASH_FILE).read_text(encoding="utf-8"))
    assert sha256_hex(raw) == expected
    assert b"\r\n" not in raw  # LF pinned so the hash is stable on Windows


def test_config_rejects_unknown_keys_and_unsafe_values() -> None:
    raw = (ROOT / CONFIG_FILE).read_text(encoding="utf-8")
    with pytest.raises(ValidationError):
        parse_config(raw.replace("max_requests_per_second = 1.0", "max_requests_per_second = 5.0"))
    with pytest.raises(ValidationError):
        parse_config(raw.replace("end_buffer_minutes = 30", "end_buffer_minutes = 5"))
    with pytest.raises(ValidationError):
        parse_config(raw + "\n[extra]\nbypass = true\n")


def test_config_module_is_the_only_dotenv_reader() -> None:
    pattern = re.compile(r"""["']\.env["']""")
    hits = [
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "src").rglob("*.py")
        if pattern.search(p.read_text(encoding="utf-8"))
    ]
    assert hits == ["src/family_desk_spike/config.py"]
