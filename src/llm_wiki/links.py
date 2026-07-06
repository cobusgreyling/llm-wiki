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


def extract_markdown_links(text: str) -> set[str]:
    return {m.group(1).strip() for m in MARKDOWN_LINK_RE.finditer(text)}


def _unique_pages(matches: list[WikiPage]) -> list[WikiPage]:
    seen: set[str] = set()
    unique: list[WikiPage] = []
    for page in matches:
        if page.rel_path not in seen:
            seen.add(page.rel_path)
            unique.append(page)
    return unique


def resolve_link_matches(target: str, slug_index: dict[str, list[WikiPage]]) -> list[WikiPage]:
    key = target.strip().lower()
    matches = slug_index.get(key)
    if not matches:
        matches = slug_index.get(key.replace(" ", "-"))
    if not matches:
        return []
    return _unique_pages(matches)


def is_ambiguous_link(target: str, slug_index: dict[str, list[WikiPage]]) -> bool:
    return len(resolve_link_matches(target, slug_index)) > 1


def resolve_link(target: str, slug_index: dict[str, list[WikiPage]]) -> WikiPage | None:
    matches = resolve_link_matches(target, slug_index)
    if len(matches) != 1:
        return None
    return matches[0]


def _path_within_root(root: Path, candidate: Path) -> Path | None:
    root_resolved = root.resolve()
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root_resolved)
    except ValueError:
        return None
    return resolved if resolved.is_file() else None


def resolve_page(wiki_root: Path, page: str) -> WikiPage | None:
    """Resolve a page name or path to an existing wiki file."""
    candidates = [
        wiki_root / page,
        wiki_root / f"{page}.md",
        wiki_root / "entities" / f"{page}.md",
        wiki_root / "concepts" / f"{page}.md",
        wiki_root / "sources" / f"{page}.md",
        wiki_root / "answers" / f"{page}.md",
    ]
    for candidate in candidates:
        resolved = _path_within_root(wiki_root, candidate)
        if resolved:
            return WikiPage(
                path=resolved,
                rel_path=resolved.relative_to(wiki_root.resolve()).as_posix(),
                stem=resolved.stem,
            )
    return None


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


def get_backlinks(wiki_root: Path, page: str) -> list[str]:
    """Return rel_paths of pages that wikilink to *page*."""
    resolved = resolve_page(wiki_root, page)
    if not resolved:
        return []
    pages = iter_wiki_pages(wiki_root)
    inbound = inbound_links(pages)
    return sorted(inbound.get(resolved.rel_path, ()))


def export_graph(wiki_root: Path) -> dict[str, list[dict[str, str]]]:
    """Export wiki link graph as nodes and edges."""
    pages = iter_wiki_pages(wiki_root)
    slug_index = build_slug_index(pages)
    nodes = [{"id": p.rel_path, "stem": p.stem} for p in pages]
    edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()

    for page in pages:
        text = page.path.read_text(encoding="utf-8", errors="replace")
        for target in extract_wikilinks(text):
            resolved = resolve_link(target, slug_index)
            if not resolved:
                continue
            key = (page.rel_path, resolved.rel_path)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(
                {
                    "from": page.rel_path,
                    "to": resolved.rel_path,
                    "target": target,
                }
            )

    return {"nodes": nodes, "edges": edges}
