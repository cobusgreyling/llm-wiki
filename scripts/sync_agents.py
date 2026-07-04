#!/usr/bin/env python3
"""Copy canonical AGENTS.md to scaffold and example wikis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "AGENTS.md"
TARGETS = [
    ROOT / "src" / "llm_wiki" / "scaffold" / "AGENTS.md",
    ROOT / "examples" / "demo" / "AGENTS.md",
    ROOT / "examples" / "research" / "AGENTS.md",
    ROOT / "examples" / "reading" / "AGENTS.md",
]


def main() -> int:
    if not CANONICAL.exists():
        print(f"Missing canonical file: {CANONICAL}", file=sys.stderr)
        return 1

    content = CANONICAL.read_text(encoding="utf-8")
    for target in TARGETS:
        if not target.parent.exists():
            continue
        target.write_text(content, encoding="utf-8")
        print(f"Synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())