import tomllib
from pathlib import Path

import family_desk_spike

ROOT = Path(__file__).resolve().parents[1]


def test_package_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert family_desk_spike.__version__ == project["version"]
