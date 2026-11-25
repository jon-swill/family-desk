import tomllib
from pathlib import Path

import family_desk_spike

ROOT = Path(__file__).resolve().parents[1]


def test_package_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert family_desk_spike.__version__ == project["version"]


def test_no_source_file_is_git_ignored() -> None:
    """A broad .gitignore rule once hid src/family_desk_spike/data/ from a commit."""
    import subprocess

    files = [str(p.relative_to(ROOT)) for p in (ROOT / "src").rglob("*.py")]
    done = subprocess.run(  # noqa: S603 - fixed argv
        ["git", "check-ignore", "--no-index", *files],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.stdout.strip() == "", f"ignored source files: {done.stdout}"
