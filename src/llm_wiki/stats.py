"""Wiki statistics and log helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .links import iter_wiki_pages
from .paths import raw_dir, wiki_dir

LOG_ENTRY_RE = re.compile(r"^## \[([^\]]+)\] (\w+) \| (.+)$", re.MULTILINE)


@dataclass
class WikiStats:
    total_pages: int
    entities: int
    concepts: int
    sources: int
    answers: int
    raw_files: int
    log_entries: int


def count_by_prefix(pages: list, prefix: str) -> int:
    return sum(1 for p in pages if p.rel_path.startswith(prefix))


def get_stats(root: Path) -> WikiStats:
    wiki_root = wiki_dir(root)
    pages = iter_wiki_pages(wiki_root)

    raw_path = raw_dir(root)
    raw_files = sum(
        1
        for f in raw_path.rglob("*")
        if f.is_file() and f.name.lower() not in {".gitkeep", "readme.md"}
    )

    log_entries = 0
    log_path = wiki_root / "log.md"
    if log_path.exists():
        log_entries = len(LOG_ENTRY_RE.findall(log_path.read_text(encoding="utf-8")))

    return WikiStats(
        total_pages=len(pages),
        entities=count_by_prefix(pages, "entities/"),
        concepts=count_by_prefix(pages, "concepts/"),
        sources=count_by_prefix(pages, "sources/"),
        answers=count_by_prefix(pages, "answers/"),
        raw_files=raw_files,
        log_entries=log_entries,
    )


def parse_log(log_path: Path, limit: int = 10) -> list[dict[str, str]]:
    if not log_path.exists():
        return []
    text = log_path.read_text(encoding="utf-8")
    entries = LOG_ENTRY_RE.findall(text)
    return [
        {"date": date, "operation": op, "detail": detail} for date, op, detail in entries[-limit:]
    ]
