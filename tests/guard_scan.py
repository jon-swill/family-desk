"""Static guard for Phase 1 (D8, G-7): no route to an order, no trading SDK, GET only.

The scanner lives in tests/ on purpose, so src/ never has to name what it forbids.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SPIKE_PACKAGE = "family_desk_spike"

# Text patterns forbidden anywhere under src/ and config/ (case-insensitive).
FORBIDDEN_TEXT: dict[str, re.Pattern[str]] = {
    "order endpoint path": re.compile(r"/v\d+/orders", re.IGNORECASE),
    "orders path segment": re.compile(r"(?<![A-Za-z0-9_])orders(?![A-Za-z0-9_])", re.IGNORECASE),
    "submit_order": re.compile(r"submit_order", re.IGNORECASE),
    "cancel_order": re.compile(r"cancel_order", re.IGNORECASE),
    "replace_order": re.compile(r"replace_order", re.IGNORECASE),
    "close_position": re.compile(r"close_(all_)?positions?", re.IGNORECASE),
    "non-GET HTTP verb": re.compile(r"(?<![A-Za-z0-9_])(POST|PUT|PATCH|DELETE)(?![A-Za-z0-9_])"),
}

# Top-level modules a src/ file may never import.
FORBIDDEN_IMPORTS = frozenset(
    {"alpaca", "alpaca_trade_api", "nautilus_trader", "lean", "vectorbt", "ib_insync", "ibapi"}
)

# Distributions that may never appear in a lock file.
FORBIDDEN_DISTS = frozenset(
    {
        "alpaca-py",
        "alpaca-trade-api",
        "nautilus-trader",
        "lean",
        "vectorbt",
        "vectorbtpro",
        "ib-insync",
        "ibapi",
        "schwab-py",
        "robin-stocks",
    }
)

# Method calls that send a non-GET request on common HTTP clients.
FORBIDDEN_CALL_ATTRS = frozenset(
    {"post", "put", "patch", "delete", "request", "build_request", "options", "head"}
)

LOCK_LINE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==")


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    rule: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}"


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _norm_dist(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def scan_text(path: Path, root: Path) -> list[Violation]:
    out: list[Violation] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for rule, pattern in FORBIDDEN_TEXT.items():
            if pattern.search(line):
                out.append(Violation(_rel(path, root), lineno, rule))
    return out


def _imported_modules(tree: ast.AST) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append((node.lineno, node.module))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name | ast.Attribute)
            and (getattr(node.func, "id", None) or getattr(node.func, "attr", None))
            in {"__import__", "import_module"}
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            found.append((node.lineno, node.args[0].value))
    return found


def scan_src_python(path: Path, root: Path) -> list[Violation]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: list[Violation] = []
    rel = _rel(path, root)
    for lineno, module in _imported_modules(tree):
        if module.split(".")[0] in FORBIDDEN_IMPORTS:
            out.append(Violation(rel, lineno, f"forbidden import {module}"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr.lower() in FORBIDDEN_CALL_ATTRS
        ):
            out.append(Violation(rel, node.lineno, f"forbidden call .{node.func.attr}()"))
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.strip().upper() in {"POST", "PUT", "PATCH", "DELETE"}
        ):
            out.append(Violation(rel, node.lineno, "non-GET HTTP verb literal"))
    return out


def scan_lock(path: Path, root: Path) -> list[Violation]:
    out: list[Violation] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = LOCK_LINE.match(line.strip())
        if m and _norm_dist(m.group(1)) in FORBIDDEN_DISTS:
            out.append(Violation(_rel(path, root), lineno, f"forbidden dependency {m.group(1)}"))
    return out


def scan_outside_imports(path: Path, root: Path) -> list[Violation]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [
        Violation(_rel(path, root), lineno, f"imports {SPIKE_PACKAGE} from outside it")
        for lineno, module in _imported_modules(tree)
        if module.split(".")[0] == SPIKE_PACKAGE
    ]


def scan_tests_for_mock(path: Path, root: Path) -> list[Violation]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"mock", "unittest.mock", "pytest_mock"}:
                    out.append(Violation(_rel(path, root), node.lineno, "mock import"))
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = {a.name for a in node.names}
            if node.module in {"unittest.mock", "mock", "pytest_mock"} or (
                node.module == "unittest" and "mock" in names
            ):
                out.append(Violation(_rel(path, root), node.lineno, "mock import"))
    return out


_SKIP_DIRS = {".venv", ".git", ".claude", "__pycache__", "build", ".mypy_cache", ".ruff_cache"}


def _files(base: Path, pattern: str) -> list[Path]:
    if not base.exists():
        return []
    return sorted(
        p
        for p in base.rglob(pattern)
        if p.is_file() and not (_SKIP_DIRS & set(p.relative_to(base).parts))
    )


def scan_repo(root: Path) -> list[Violation]:
    """Every rule over a repo tree rooted at `root`."""
    out: list[Violation] = []
    src = root / "src"
    for base in (src, root / "config"):
        for path in _files(base, "*"):
            if path.suffix in {".py", ".toml", ".json", ".txt", ".cfg", ".ini", ".yaml", ".yml"}:
                out.extend(scan_text(path, root))
    for path in _files(src, "*.py"):
        out.extend(scan_src_python(path, root))
    for path in sorted(root.glob("requirements*.lock")):
        out.extend(scan_lock(path, root))
    spike_dir = src / SPIKE_PACKAGE
    tests_dir = root / "tests"
    for path in _files(root, "*.py"):
        if spike_dir in path.parents or tests_dir in path.parents:
            continue
        out.extend(scan_outside_imports(path, root))
    for path in _files(tests_dir, "*.py"):
        out.extend(scan_tests_for_mock(path, root))
    return out
