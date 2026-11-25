from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import family_desk_spike
from family_desk_spike.config import CONFIG_FILE, load_settings, parse_config, sha256_hex
from family_desk_spike.startup import (
    CONFIG_HASH,
    DIRTY_TREE,
    HOST,
    MISSING_KEY,
    MISSING_UA,
    PAPER_FLAG,
    VERSION,
    StartupReport,
    assert_paper,
    evaluate_startup,
    run_startup,
)
from tests.fakes.env import FAKE_EMAIL, FAKE_KEY_ID, FAKE_SECRET, FakeGit, fake_env

ROOT = Path(__file__).resolve().parents[1]
CONFIG_TEXT = (ROOT / CONFIG_FILE).read_text(encoding="utf-8")
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
GOOD_HASH = sha256_hex(CONFIG_TEXT.encode("utf-8"))


def _eval(
    *,
    env: dict[str, str] | None = None,
    config_text: str = CONFIG_TEXT,
    expected_hash: str = GOOD_HASH,
    version: str = family_desk_spike.__version__,
    live: bool = False,
    git: FakeGit | None = None,
) -> StartupReport:
    return evaluate_startup(
        settings=load_settings(env if env is not None else fake_env()),
        config=parse_config(config_text),
        config_hash=sha256_hex(config_text.encode("utf-8")),
        expected_config_hash=expected_hash,
        package_version=version,
        pyproject_text=PYPROJECT,
        live=live,
        git=git,
    )


def test_good_config_passes() -> None:
    report = _eval()
    assert report.ok, report.lines()
    assert report.lines()[-1] == "startup OK"


def test_live_run_records_commit_on_clean_tree() -> None:
    git = FakeGit(commit="abc123")
    report = _eval(live=True, git=git)
    assert report.ok
    assert report.commit == "abc123"
    assert ("status", "src", "config") in git.calls


@pytest.mark.parametrize(
    "url",
    [
        "https://api.alpaca.markets",  # live host
        "https://paper-api.alpaca.markets.evil.test",
        "http://paper-api.alpaca.markets",
        "https://paper-api.alpaca.markets:8443",
        "",
    ],
)
def test_wrong_host_refuses_with_host_code(url: str) -> None:
    text = CONFIG_TEXT.replace(
        'trading_base_url = "https://paper-api.alpaca.markets"', f'trading_base_url = "{url}"'
    )
    report = _eval(config_text=text, expected_hash=sha256_hex(text.encode()))
    assert report.codes == [HOST]


@pytest.mark.parametrize("flag", ["", "false", "True", "1", "yes"])
def test_paper_flag_must_be_exactly_true(flag: str) -> None:
    assert _eval(env=fake_env(APCA_PAPER=flag)).codes == [PAPER_FLAG]


def test_hash_mismatch_refuses() -> None:
    assert _eval(expected_hash="0" * 64).codes == [CONFIG_HASH]
    assert _eval(expected_hash="").codes == [CONFIG_HASH]


def test_version_mismatch_refuses() -> None:
    assert _eval(version="9.9.9").codes == [VERSION]


def test_dirty_tree_refuses_live_only() -> None:
    git = FakeGit(porcelain=" M src/family_desk_spike/config.py\n M config/spike.toml\n")
    assert _eval(live=True, git=git).codes == [DIRTY_TREE]
    assert _eval(live=False, git=git).ok


def test_git_failure_or_missing_reader_refuses_live() -> None:
    assert _eval(live=True, git=FakeGit(fail=True)).codes == [DIRTY_TREE]
    assert _eval(live=True, git=None).codes == [DIRTY_TREE]


@pytest.mark.parametrize("ua", ["", "Fake Owner", "Fake a@b.co c@d.org"])
def test_missing_or_ambiguous_ua_refuses(ua: str) -> None:
    assert _eval(env=fake_env(SEC_USER_AGENT=ua)).codes == [MISSING_UA]


def test_missing_key_refuses() -> None:
    assert _eval(env=fake_env(APCA_API_SECRET_KEY="")).codes == [MISSING_KEY]


def test_every_failure_reported_together_and_report_has_no_secrets() -> None:
    """The B10 demo: editing the host also trips the hash and dirty-tree checks (P-06)."""
    text = CONFIG_TEXT.replace("https://paper-api.alpaca.markets", "https://api.alpaca.markets", 1)
    report = _eval(
        env=fake_env(APCA_PAPER="false", SEC_USER_AGENT=f"x {FAKE_EMAIL} y@z.io"),
        config_text=text,
        expected_hash=GOOD_HASH,
        version="0.0.0",
        live=True,
        git=FakeGit(porcelain=" M config/spike.toml\n"),
    )
    assert report.codes == [HOST, PAPER_FLAG, CONFIG_HASH, VERSION, MISSING_UA, DIRTY_TREE]
    rendered = "\n".join(report.lines())
    assert "startup REFUSED codes=host,paper_flag,config_hash,version,missing_ua,dirty_tree" in (
        rendered
    )
    for value in (FAKE_KEY_ID, FAKE_SECRET, FAKE_EMAIL):
        assert value not in rendered


def test_assert_paper_alone() -> None:
    assert assert_paper("https://paper-api.alpaca.markets/", "true") == []
    assert [f.code for f in assert_paper("https://api.alpaca.markets", "false")] == [
        HOST,
        PAPER_FLAG,
    ]


def _copy_repo_bits(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    shutil.copy(ROOT / "config" / "spike.toml", tmp_path / "config" / "spike.toml")
    shutil.copy(ROOT / "config" / "spike.toml.sha256", tmp_path / "config" / "spike.toml.sha256")
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    return tmp_path


def test_run_startup_reads_files(tmp_path: Path) -> None:
    root = _copy_repo_bits(tmp_path)
    result = run_startup(root, live=True, git=FakeGit(), env=fake_env())
    assert result.report.ok, result.report.lines()
    assert result.config is not None


def test_run_startup_unparseable_config_refuses_with_host(tmp_path: Path) -> None:
    root = _copy_repo_bits(tmp_path)
    (root / "config" / "spike.toml").write_text("not = [valid", encoding="utf-8")
    result = run_startup(root, live=False, git=None, env=fake_env())
    assert HOST in result.report.codes
    assert CONFIG_HASH in result.report.codes
    assert result.config is None


def test_run_startup_reads_dotenv_file_when_env_not_given(tmp_path: Path) -> None:
    root = _copy_repo_bits(tmp_path)
    (root / ".env").write_text(
        "\n".join(f"{k}={v}" for k, v in fake_env().items()) + "\n", encoding="utf-8"
    )
    assert run_startup(root, live=False, git=None).report.ok
