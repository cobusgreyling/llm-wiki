"""Resolve wiki directory paths relative to project root."""

from __future__ import annotations

import os
from pathlib import Path

ROOT_ENV_VAR = "LLM_WIKI_ROOT"


def find_root(start: Path | None = None) -> Path:
    """Walk up from *start* (or cwd) to find the llm-wiki project root."""
    env_root = os.environ.get(ROOT_ENV_VAR)
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if (root / "wiki" / "index.md").exists() and (root / "AGENTS.md").exists():
            return root
        raise FileNotFoundError(
            f"{ROOT_ENV_VAR}={env_root} is not a valid llm-wiki root "
            "(expected wiki/index.md and AGENTS.md)."
        )

    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "wiki" / "index.md").exists() and (candidate / "AGENTS.md").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find llm-wiki root. Run from a wiki project with wiki/index.md and "
        f"AGENTS.md, set {ROOT_ENV_VAR}, or pass --root (e.g. wiki --root examples/demo search "
        f'"query"). From a repo clone, try: make demo-search'
    )


def wiki_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "wiki"


def raw_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "raw"


def templates_dir(root: Path | None = None) -> Path:
    return (root or find_root()) / "templates"
