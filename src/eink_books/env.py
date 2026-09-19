"""Load a local .env without adding a runtime dependency."""

from __future__ import annotations

import os
from pathlib import Path


def _env_paths() -> tuple[Path, ...]:
    here = Path(__file__).resolve()
    project_root = here.parents[2]  # eink-books/
    return (Path.cwd() / ".env", project_root / ".env")


def load_project_env() -> None:
    seen: set[Path] = set()
    for path in _env_paths():
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        _apply_env_file(resolved)


def _apply_env_file(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value
