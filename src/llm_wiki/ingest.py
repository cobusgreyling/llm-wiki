"""Track which raw sources have been ingested into the wiki."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .links import iter_wiki_pages
from .lint import parse_frontmatter
from .paths import raw_dir, wiki_dir

RAW_SKIP = {".gitkeep", "readme.md"}


@dataclass
class IngestStatus:
    raw_file: str
    source_page: str | None
    status: str  # ingested | pending | orphan


def _list_raw_files(raw_root: Path) -> list[str]:
    if not raw_root.exists():
        return []
    files: list[str] = []
    for path in sorted(raw_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.lower() in RAW_SKIP:
            continue
        files.append(path.relative_to(raw_root).as_posix())
    return files


def _source_raw_map(wiki_root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for page in iter_wiki_pages(wiki_root):
        if not page.rel_path.startswith("sources/"):
            continue
        text = page.path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        raw_file = None
        if meta:
            raw_file = meta.get("raw_file")
        if not raw_file:
            # Heuristic: source slug matches raw filename stem
            raw_file = f"{page.stem}.md"
        mapping[str(raw_file)] = page.rel_path
    return mapping


def get_ingest_status(root: Path) -> list[IngestStatus]:
    """Return ingest coverage for each raw file and orphan source pages."""
    raw_root = raw_dir(root)
    wiki_root = wiki_dir(root)
    raw_files = _list_raw_files(raw_root)
    source_map = _source_raw_map(wiki_root)
    raw_set = set(raw_files)

    statuses: list[IngestStatus] = []

    for raw_file in raw_files:
        source_page = source_map.get(raw_file)
        statuses.append(
            IngestStatus(
                raw_file=raw_file,
                source_page=source_page,
                status="ingested" if source_page else "pending",
            )
        )

    for raw_file, source_page in sorted(source_map.items()):
        if raw_file not in raw_set:
            statuses.append(
                IngestStatus(
                    raw_file=raw_file,
                    source_page=source_page,
                    status="orphan",
                )
            )

    return statuses