"""Resolve wiki directory paths relative to project root."""

from __future__ import annotations

from pathlib import Path


def find_root(start: Path | None = None) -> Path:
    """Walk up from *start* (or cwd) to find the llm-wiki project root."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "wiki" / "index.md").exists() and (candidate / "AGENTS.md").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find llm-wiki root. Run from a project with wiki/index.md and AGENTS.md."
    )


def wiki_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "wiki"


def raw_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "raw"


def templates_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "templates"