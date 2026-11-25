from __future__ import annotations

from pathlib import Path

from family_desk_spike.applog import REDACTED, AppLog, Redactor, verify_lines
from family_desk_spike.config import extract_emails, load_settings
from tests.fakes.clock import FakeClock
from tests.fakes.env import FAKE_EMAIL, FAKE_KEY_ID, FAKE_SECRET, FAKE_UA, fake_env


def _redactor() -> Redactor:
    s = load_settings(fake_env())
    ua = s.sec_user_agent.get_secret_value()
    return Redactor.of(
        [
            s.api_key_id.get_secret_value(),
            s.api_secret_key.get_secret_value(),
            ua,
            *extract_emails(ua),
        ]
    )


def test_redacts_nested_values_and_keys() -> None:
    r = _redactor()
    payload = {
        "headers": {"APCA-API-KEY-ID": FAKE_KEY_ID, "User-Agent": FAKE_UA},
        "list": [f"secret={FAKE_SECRET}", 3, None],
        FAKE_EMAIL: "as a key",
    }
    out = r.apply(payload)
    text = repr(out)
    for v in (FAKE_KEY_ID, FAKE_SECRET, FAKE_EMAIL):
        assert v not in text
    assert out["headers"]["APCA-API-KEY-ID"] == REDACTED
    assert out["list"][0] == f"secret={REDACTED}"
    assert out["list"][1:] == [3, None]


def test_log_file_never_contains_secret_values(tmp_path: Path) -> None:
    p = tmp_path / "log.jsonl"
    log = AppLog(p, redactor=_redactor(), clock=FakeClock()).open()
    log.append("error", {"msg": f"auth failed for {FAKE_KEY_ID}:{FAKE_SECRET}", "ua": FAKE_UA})
    log.append(f"src-{FAKE_EMAIL}", {"ok": True}, source_ts=FAKE_EMAIL)
    log.close()
    raw = p.read_text(encoding="utf-8")
    for v in (FAKE_KEY_ID, FAKE_SECRET, FAKE_EMAIL, FAKE_UA):
        assert v not in raw
    assert verify_lines(raw).ok  # hash is over the redacted record


def test_tiny_values_are_not_used_for_redaction() -> None:
    r = Redactor.of(["ab", "", "abcd"])
    assert r.values == ("abcd",)
