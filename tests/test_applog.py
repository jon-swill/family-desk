from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from family_desk_spike import verify_log
from family_desk_spike.applog import (
    GENESIS_HASH,
    AppLog,
    LogCorruptError,
    canonical_json,
    log_path_for,
    record_hash,
    verify_lines,
)
from tests.fakes.clock import FakeClock


def _write(path: Path, n: int = 5) -> AppLog:
    log = AppLog(path, clock=FakeClock()).open()
    for i in range(n):
        log.append("quote" if i % 2 else "news", {"i": i}, source_ts=f"2026-11-30T15:30:0{i}Z")
    log.close()
    return log


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def test_append_builds_a_verifiable_chain(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    log = _write(p)
    result = verify_lines(p.read_text(encoding="utf-8"))
    assert result.ok, result.errors
    assert result.seq_last == 5 == log.seq_last
    assert result.head_hash == log.head_hash
    assert result.counts == {"news": 3, "quote": 2}
    first = json.loads(_lines(p)[0])
    assert first["prev_hash"] == GENESIS_HASH
    assert first["received_at_utc"].endswith("Z")
    assert record_hash(first) == first["hash"]


def test_reopen_continues_chain_in_append_mode(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p, 3)
    log = AppLog(p, clock=FakeClock()).open()
    log.append("edgar", {"n": 1})
    log.close()
    result = verify_lines(p.read_text(encoding="utf-8"))
    assert result.ok and result.seq_last == 4


def test_tampered_payload_detected(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p)
    lines = _lines(p)
    rec = json.loads(lines[2])
    rec["payload"] = {"i": 999}
    lines[2] = canonical_json(rec) + "\n"
    result = verify_lines("".join(lines))
    assert not result.ok
    assert "hash mismatch" in result.errors[0]
    assert result.seq_last == 2


def test_rehashed_tamper_breaks_the_link(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p)
    lines = _lines(p)
    rec = json.loads(lines[2])
    rec["payload"] = {"i": 999}
    rec["hash"] = record_hash(rec)
    lines[2] = canonical_json(rec) + "\n"
    result = verify_lines("".join(lines))
    assert not result.ok
    assert "prev_hash" in result.errors[0]


def test_mid_file_gap_detected(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p)
    lines = _lines(p)
    del lines[2]
    result = verify_lines("".join(lines))
    assert not result.ok
    assert "seq gap" in result.errors[0]


def test_tail_truncation_detected_only_against_anchor(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    log = _write(p)
    anchor = log.head_hash
    truncated = "".join(_lines(p)[:-2])
    assert verify_lines(truncated).ok  # undetectable without the anchor
    result = verify_lines(truncated, expect_head=anchor)
    assert not result.ok
    assert "expect-head" in result.errors[0]
    assert verify_lines(p.read_text(encoding="utf-8"), expect_head=anchor.upper()).ok


def test_trailing_partial_line_reported(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p, 3)
    text = p.read_text(encoding="utf-8") + '{"seq":4,"recei'
    result = verify_lines(text)
    assert not result.ok
    assert result.trailing_partial
    assert result.seq_last == 3
    assert any("trailing partial" in line for line in result.lines())


def test_open_refuses_corrupt_file(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    _write(p, 2)
    p.write_text(p.read_text(encoding="utf-8") + "garbage\n", encoding="utf-8")
    with pytest.raises(LogCorruptError):
        AppLog(p).open()


def test_naive_timestamp_rejected(tmp_path: Path) -> None:
    log = AppLog(tmp_path / "x.jsonl", clock=lambda: datetime(2026, 1, 1)).open()  # noqa: DTZ001
    with pytest.raises(ValueError, match="naive"):
        log.append("s", {})
    log.close()


def test_log_path_is_per_utc_day(tmp_path: Path) -> None:
    ts = datetime(2026, 11, 30, 23, 59, tzinfo=UTC)
    assert log_path_for(tmp_path, ts).name == "2026-11-30.jsonl"


def test_cli_prints_chain_ok_and_anchor(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = tmp_path / "log.jsonl"
    log = _write(p)
    assert verify_log.main([str(p), "--expect-head", log.head_hash]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "chain OK"
    assert f"seq_last={log.seq_last}" in out
    assert f"head_hash={log.head_hash}" in out
    assert verify_log.main([str(p), "--expect-head", "0" * 64]) == 1
    assert "chain FAILED" in capsys.readouterr().out
    assert verify_log.main([str(tmp_path / "missing.jsonl")]) == 2
