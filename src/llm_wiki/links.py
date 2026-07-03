"""Parse Obsidian-style wikilinks and markdown links."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class WikiPage:
    path: Path
    rel_path: str
    stem: str

    @property
    def slug(self) -> str:
        return self.stem.lower()


def iter_wiki_pages(wiki_root: Path) -> list[WikiPage]:
    pages: list[WikiPage] = []
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root).as_posix()
        pages.append(WikiPage(path=path, rel_path=rel, stem=path.stem))
    return pages


def build_slug_index(pages: list[WikiPage]) -> dict[str, list[WikiPage]]:
    index: dict[str, list[WikiPage]] = {}
    for page in pages:
        index.setdefault(page.slug, []).append(page)
        # Also index by full relative path without extension
        rel_slug = page.rel_path.removesuffix(".md").lower()
        index.setdefault(rel_slug, []).append(page)
    return index


def extract_wikilinks(text: str) -> set[str]:
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(text)}


def resolve_link(target: str, slug_index: dict[str, list[WikiPage]]) -> WikiPage | None:
    key = target.strip().lower()
    matches = slug_index.get(key)
    if not matches:
        # Try path-style: concepts/foo -> concepts/foo.md
        matches = slug_index.get(key.replace(" ", "-"))
    if not matches:
        return None
    return matches[0]


def inbound_links(pages: list[WikiPage]) -> dict[str, set[str]]:
    """Map page rel_path -> set of pages that link to it."""
    slug_index = build_slug_index(pages)
    inbound: dict[str, set[str]] = {p.rel_path: set() for p in pages}

    for page in pages:
        text = page.path.read_text(encoding="utf-8", errors="replace")
        for target in extract_wikilinks(text):
            resolved = resolve_link(target, slug_index)
            if resolved:
                inbound[resolved.rel_path].add(page.rel_path)
    return inbound