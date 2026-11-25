from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from family_desk_spike.config import load_settings
from family_desk_spike.tools.secret_scan import (
    LOCATIONS,
    UA_EMAIL,
    ScanRefusedError,
    run,
    scan,
    scan_values,
)
from tests.fakes.env import FAKE_EMAIL, FAKE_KEY_ID, FAKE_SECRET, FAKE_UA, fake_env


@dataclass
class FakeScanGit:
    history: bytes = b"commit 1\n+clean line\n"
    tracked: list[str] = field(default_factory=list)

    def log_patch_all(self) -> bytes:
        return self.history

    def ls_files(self) -> list[str]:
        return self.tracked


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("nothing here\n", encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "pytest_output.txt").write_text("1 passed\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme\n", encoding="utf-8")
    return tmp_path


def _assert_no_values(lines: list[str]) -> None:
    text = "\n".join(lines)
    for v in (FAKE_KEY_ID, FAKE_SECRET, FAKE_EMAIL, FAKE_UA):
        assert v not in text
        assert v.lower() not in text.lower()


def test_clean_tree_reports_not_found_everywhere(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    code, lines = run(root, load_settings(fake_env()), FakeScanGit(tracked=["README.md"]))
    assert code == 0
    assert lines[-1] == "RESULT: all not found"
    assert len(lines) == 3 * len(LOCATIONS) + 1
    assert all(line.endswith(": not found") for line in lines[:-1])
    _assert_no_values(lines)


@pytest.mark.parametrize(
    ("where", "value", "name", "loc"),
    [
        ("history", FAKE_SECRET, "APCA_API_SECRET_KEY", "git_history"),
        ("tracked", FAKE_KEY_ID, "APCA_API_KEY_ID", "tracked_files"),
        ("logs", FAKE_EMAIL.upper(), UA_EMAIL, "logs"),
        ("docs", FAKE_EMAIL, UA_EMAIL, "docs"),
    ],
)
def test_planted_fake_value_is_found(
    tmp_path: Path, where: str, value: str, name: str, loc: str
) -> None:
    root = _repo(tmp_path)
    git = FakeScanGit(tracked=["README.md"])
    if where == "history":
        git.history += f"+KEY={value}\n".encode()
    elif where == "tracked":
        (root / "README.md").write_text(f"oops {value}\n", encoding="utf-8")
    elif where == "logs":
        (root / "logs" / "spike").mkdir()
        (root / "logs" / "spike" / "x.jsonl").write_text(f'{{"ua":"{value}"}}\n', encoding="utf-8")
    else:
        (root / "docs" / "b.md").write_text(f"contact {value}\n", encoding="utf-8")
    code, lines = run(root, load_settings(fake_env()), git)
    assert code == 1
    assert f"{name} @ {loc}: found" in lines
    assert lines[-1].startswith("RESULT: FOUND")
    _assert_no_values(lines)


def test_ua_name_alone_is_not_a_value() -> None:
    values = scan_values(load_settings(fake_env()))
    assert values[UA_EMAIL] == FAKE_EMAIL.encode()
    assert set(values) == {"APCA_API_KEY_ID", "APCA_API_SECRET_KEY", UA_EMAIL}


@pytest.mark.parametrize(
    ("ua", "msg"),
    [("Fake Owner", "found 0"), (f"Fake {FAKE_EMAIL} other@example.test", "found 2")],
)
def test_refuses_without_exactly_one_email(ua: str, msg: str, tmp_path: Path) -> None:
    settings = load_settings(fake_env(SEC_USER_AGENT=ua))
    with pytest.raises(ScanRefusedError, match=msg):
        scan_values(settings)
    code, lines = run(_repo(tmp_path), settings, FakeScanGit())
    assert code == 2
    _assert_no_values(lines)


def test_refuses_when_keys_missing(tmp_path: Path) -> None:
    code, lines = run(_repo(tmp_path), load_settings(fake_env(APCA_API_KEY_ID="")), FakeScanGit())
    assert code == 2
    assert "APCA_API_KEY_ID not set" in lines[0]


def test_scan_core_is_per_location() -> None:
    found = scan({"K": b"abc"}, {"a": [b"xxabcxx"], "b": [b"nope", b"ab c"]})
    assert found == {("K", "a"): True, ("K", "b"): False}
