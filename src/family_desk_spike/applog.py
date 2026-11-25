"""Append-only, hash-chained JSONL log (D10, NFR-6, C-10, P-01).

Each line is one record: seq, received_at_utc, source, source_ts, payload, prev_hash, hash.
`hash` is sha256 over the canonical JSON of the other six fields. The chain's head
(`seq_last`, `head_hash`) is anchored outside the log, in the committed evidence, and
`verify_log --expect-head` checks it, so tail truncation and wholesale rewrites show.

Pure functions first; `AppLog` is the I/O shell (append mode only, flush per record).
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Any

GENESIS_HASH = "0" * 64
REDACTED = "[REDACTED]"
RECORD_KEYS = ("seq", "received_at_utc", "source", "source_ts", "payload", "prev_hash")

JsonValue = Any


def canonical_json(obj: JsonValue) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_hash(body: Mapping[str, JsonValue]) -> str:
    return hashlib.sha256(canonical_json({k: body[k] for k in RECORD_KEYS}).encode()).hexdigest()


def utc_iso(ts: datetime) -> str:
    if ts.tzinfo is None:
        raise ValueError("naive datetime; all log timestamps are UTC-aware")
    return ts.astimezone(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Redactor:
    """Replaces any occurrence of a sensitive value inside payload strings."""

    values: tuple[str, ...] = ()

    @classmethod
    def of(cls, values: Iterable[str]) -> Redactor:
        # Longest first so a value containing another is fully removed; ignore tiny values.
        return cls(tuple(sorted({v for v in values if len(v) >= 4}, key=len, reverse=True)))

    def text(self, s: str) -> str:
        for v in self.values:
            if v in s:
                s = s.replace(v, REDACTED)
        return s

    def apply(self, obj: JsonValue) -> JsonValue:
        if isinstance(obj, str):
            return self.text(obj)
        if isinstance(obj, Mapping):
            return {self.text(str(k)): self.apply(v) for k, v in obj.items()}
        if isinstance(obj, list | tuple):
            return [self.apply(v) for v in obj]
        return obj


def make_record(
    *,
    seq: int,
    prev_hash: str,
    received_at: datetime,
    source: str,
    source_ts: str | None,
    payload: JsonValue,
    redactor: Redactor,
) -> dict[str, JsonValue]:
    body: dict[str, JsonValue] = {
        "seq": seq,
        "received_at_utc": utc_iso(received_at),
        "source": redactor.text(source),
        "source_ts": redactor.text(source_ts) if source_ts is not None else None,
        "payload": redactor.apply(payload),
        "prev_hash": prev_hash,
    }
    body["hash"] = record_hash(body)
    return body


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    seq_last: int
    head_hash: str
    records: int
    counts: dict[str, int]
    errors: tuple[str, ...]
    trailing_partial: bool = False

    def lines(self) -> list[str]:
        out = ["chain OK" if self.ok else "chain FAILED"]
        out.append(f"seq_last={self.seq_last}")
        out.append(f"head_hash={self.head_hash}")
        out.append(f"records={self.records}")
        out.extend(f"count[{src}]={n}" for src, n in sorted(self.counts.items()))
        if self.trailing_partial:
            out.append("trailing partial line: present (reported, not dropped)")
        out.extend(f"error: {e}" for e in self.errors)
        return out


def verify_lines(text: str, expect_head: str | None = None) -> VerifyResult:
    """Pure verifier over the file's text."""
    errors: list[str] = []
    counts: dict[str, int] = {}
    prev = GENESIS_HASH
    seq_last = 0
    records = 0
    trailing_partial = bool(text) and not text.endswith("\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for i, line in enumerate(lines, start=1):
        is_last = i == len(lines)
        if is_last and trailing_partial:
            errors.append(f"line {i}: trailing partial line ({len(line)} bytes, no newline)")
            break
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"line {i}: not valid JSON")
            break
        if not isinstance(rec, dict) or any(k not in rec for k in (*RECORD_KEYS, "hash")):
            errors.append(f"line {i}: missing record fields")
            break
        if rec["seq"] != seq_last + 1:
            errors.append(f"line {i}: seq gap: expected {seq_last + 1}, got {rec['seq']}")
            break
        if rec["prev_hash"] != prev:
            errors.append(f"line {i}: prev_hash does not link to the previous record")
            break
        if record_hash(rec) != rec["hash"]:
            errors.append(f"line {i}: hash mismatch (record altered)")
            break
        prev = rec["hash"]
        seq_last = rec["seq"]
        records += 1
        counts[str(rec["source"])] = counts.get(str(rec["source"]), 0) + 1
    if expect_head is not None and not errors and prev != expect_head.strip().lower():
        errors.append("head_hash does not match --expect-head (truncated or rewritten)")
    return VerifyResult(
        ok=not errors,
        seq_last=seq_last,
        head_hash=prev,
        records=records,
        counts=counts,
        errors=tuple(errors),
        trailing_partial=trailing_partial,
    )


def log_path_for(log_dir: Path, day: datetime) -> Path:
    return log_dir / f"{day.astimezone(UTC).date().isoformat()}.jsonl"


# --- I/O shell ------------------------------------------------------------------------


class LogCorruptError(RuntimeError):
    pass


@dataclass
class AppLog:
    """Append-only writer. Continues an existing file's chain; refuses a broken file."""

    path: Path
    redactor: Redactor = field(default_factory=Redactor)
    clock: Callable[[], datetime] = field(default=lambda: datetime.now(UTC))
    fsync: bool = False
    _fh: IO[str] | None = field(default=None, init=False, repr=False)
    _seq: int = field(default=0, init=False)
    _prev: str = field(default=GENESIS_HASH, init=False)

    def open(self) -> AppLog:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            existing = verify_lines(self.path.read_text(encoding="utf-8"))
            if not existing.ok:
                raise LogCorruptError(f"{self.path}: {'; '.join(existing.errors)}")
            self._seq, self._prev = existing.seq_last, existing.head_hash
        self._fh = self.path.open("a", encoding="utf-8", newline="\n")
        return self

    def append(self, source: str, payload: JsonValue, source_ts: str | None = None) -> int:
        if self._fh is None:
            raise RuntimeError("log not open")
        rec = make_record(
            seq=self._seq + 1,
            prev_hash=self._prev,
            received_at=self.clock(),
            source=source,
            source_ts=source_ts,
            payload=payload,
            redactor=self.redactor,
        )
        self._fh.write(canonical_json(rec) + "\n")
        self._fh.flush()
        if self.fsync:
            os.fsync(self._fh.fileno())
        self._seq, self._prev = rec["seq"], rec["hash"]
        return int(rec["seq"])

    @property
    def seq_last(self) -> int:
        return self._seq

    @property
    def head_hash(self) -> str:
        return self._prev

    def close(self) -> None:
        if self._fh is not None:
            self._fh.flush()
            self._fh.close()
            self._fh = None

    def __enter__(self) -> AppLog:
        return self.open() if self._fh is None else self

    def __exit__(self, *exc: object) -> None:
        self.close()
