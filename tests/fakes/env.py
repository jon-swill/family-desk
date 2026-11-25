from __future__ import annotations

from dataclasses import dataclass, field

FAKE_KEY_ID = "PKFAKEKEYID0000000000"
FAKE_SECRET = "fakeSecretValue0123456789abcdefghijklmn"
FAKE_EMAIL = "owner@example.test"
FAKE_UA = f"Fake Owner {FAKE_EMAIL}"


def fake_env(**overrides: str) -> dict[str, str]:
    """A complete, valid env as `.env` would give it. Values are fake."""
    env = {
        "APCA_API_KEY_ID": FAKE_KEY_ID,
        "APCA_API_SECRET_KEY": FAKE_SECRET,
        "APCA_PAPER": "true",
        "SEC_USER_AGENT": FAKE_UA,
    }
    env.update(overrides)
    return env


@dataclass
class FakeGit:
    porcelain: str = ""
    commit: str = "0" * 40
    fail: bool = False
    calls: list[tuple[str, ...]] = field(default_factory=list)

    def status_porcelain(self, paths: tuple[str, ...]) -> str:
        self.calls.append(("status", *paths))
        if self.fail:
            raise OSError("git not found")
        return self.porcelain

    def head_commit(self) -> str:
        self.calls.append(("rev-parse",))
        return self.commit
