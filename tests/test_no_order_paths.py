"""D8 / G-7 guard: no order path, no trading or engine SDK, GET only, spike isolated, no mocks."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.guard_scan import scan_repo

ROOT = Path(__file__).resolve().parents[1]


def _tree(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


CLEAN = {
    "src/family_desk_spike/__init__.py": '"""ok"""\n',
    "src/family_desk_spike/net.py": "def fetch(c, u):\n    return c.get(u)\n",
    "tests/test_x.py": 'URL = "/v2/orders"  # refusal tests may name it\n',
    "requirements.lock": "httpx==0.28.1 \\\n    --hash=sha256:abc\n",
}


def test_real_repo_is_clean() -> None:
    violations = scan_repo(ROOT)
    assert violations == [], "\n".join(str(v) for v in violations)


def test_clean_synthetic_tree_passes(tmp_path: Path) -> None:
    assert scan_repo(_tree(tmp_path, CLEAN)) == []


@pytest.mark.parametrize(
    ("rel", "text", "rule"),
    [
        ("src/family_desk_spike/a.py", 'P = "/v2/orders"\n', "order endpoint path"),
        ("src/family_desk_spike/a.py", 'P = "/v2/" + "orders"\n', "orders path segment"),
        ("src/family_desk_spike/a.py", "def submit_order(): ...\n", "submit_order"),
        ("src/family_desk_spike/a.py", "x.cancel_order(1)\n", "cancel_order"),
        ("src/family_desk_spike/a.py", "x.replace_order(1)\n", "replace_order"),
        ("src/family_desk_spike/a.py", "x.close_position('SPY')\n", "close_position"),
        ("src/family_desk_spike/a.py", "x.close_all_positions()\n", "close_position"),
        ("src/family_desk_spike/a.py", 'M = "POST"\n', "non-GET HTTP verb"),
        ("src/family_desk_spike/a.py", "c.post(u)\n", "forbidden call .post()"),
        ("src/family_desk_spike/a.py", "c.delete(u)\n", "forbidden call .delete()"),
        ("src/family_desk_spike/a.py", "c.request('get', u)\n", "forbidden call .request()"),
        ("src/family_desk_spike/a.py", 'm = "put"\n', "non-GET HTTP verb literal"),
        (
            "src/family_desk_spike/a.py",
            "from alpaca.trading.client import TradingClient\n",
            "forbidden import alpaca.trading.client",
        ),
        ("src/family_desk_spike/a.py", "import nautilus_trader\n", "forbidden import"),
        ("src/family_desk_spike/a.py", "import vectorbt as vbt\n", "forbidden import"),
        ("src/family_desk_spike/a.py", "__import__('alpaca_trade_api')\n", "forbidden import"),
        ("config/spike.toml", 'path = "/v2/orders"\n', "order endpoint path"),
        ("requirements.lock", "alpaca-py==0.40.0 \\\n", "forbidden dependency"),
        ("requirements-dev.lock", "nautilus_trader==1.0 \\\n", "forbidden dependency"),
        ("requirements.lock", "vectorbt==0.28 \\\n", "forbidden dependency"),
        (
            "src/phase3/core.py",
            "from family_desk_spike import config\n",
            "imports family_desk_spike",
        ),
        ("tools/x.py", "import family_desk_spike.applog\n", "imports family_desk_spike"),
        ("tests/test_y.py", "from unittest import mock\n", "mock import"),
        ("tests/test_y.py", "from unittest.mock import MagicMock\n", "mock import"),
        ("tests/test_y.py", "import unittest.mock\n", "mock import"),
    ],
)
def test_planted_violation_is_caught(tmp_path: Path, rel: str, text: str, rule: str) -> None:
    files = dict(CLEAN)
    files[rel] = files.get(rel, "") + text
    violations = scan_repo(_tree(tmp_path, files))
    assert any(rule in v.rule for v in violations), [str(v) for v in violations]
