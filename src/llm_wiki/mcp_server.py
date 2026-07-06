"""MCP server exposing wiki operations to LLM agents.

Run with: python -m llm_wiki.mcp_server
Requires: pip install llm-wiki[mcp]
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit("MCP support requires: pip install 'llm-wiki[mcp]'") from exc

from .expand import extract_section, list_headings
from .ingest import get_ingest_status
from .links import export_graph, get_backlinks, iter_wiki_pages, resolve_page
from .lint import filter_issues, lint_wiki
from .new_page import create_page
from .paths import find_root, wiki_dir
from .search import VALID_BACKENDS, search_wiki_with_backend
from .stats import get_stats, parse_log

VALID_PAGE_TYPES = {"entity", "concept", "source", "answer", "all"}
VALID_SEVERITIES = {"all", "error", "warning", "info"}

mcp = FastMCP(
    "llm-wiki",
    instructions=(
        "Tools for operating on an LLM-maintained markdown wiki. "
        "Search pages, expand content, lint health, and inspect stats."
    ),
)


def _root() -> Path:
    return find_root()


def _issue_payload(issues: list) -> list[dict[str, str]]:
    return [
        {
            "severity": i.severity,
            "category": i.category,
            "page": i.page,
            "message": i.message,
        }
        for i in issues
    ]


@mcp.tool()
def wiki_search(query: str, limit: int = 8, backend: str = "bm25") -> str:
    """Search the wiki using BM25 (default) or qmd. Returns ranked pages with snippets."""
    if backend not in VALID_BACKENDS:
        valid = ", ".join(sorted(VALID_BACKENDS))
        return json.dumps({"error": f"Invalid backend: {backend!r}. Valid backends: {valid}"})
    try:
        results = search_wiki_with_backend(wiki_dir(_root()), query, limit=limit, backend=backend)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        return json.dumps({"error": str(exc)})
    return json.dumps(
        [
            {"path": r.page.rel_path, "score": round(r.score, 4), "snippet": r.snippet}
            for r in results
        ],
        indent=2,
    )


@mcp.tool()
def wiki_expand(page: str, section: str | None = None) -> str:
    """Read a wiki page by name or path. Pass section to return one heading block only."""
    wiki_root = wiki_dir(_root())
    resolved = resolve_page(wiki_root, page)
    if not resolved:
        return json.dumps({"error": f"Page not found: {page}"})
    text = resolved.path.read_text(encoding="utf-8")
    if section:
        extracted = extract_section(text, section)
        if not extracted:
            headings = [title for _, title in list_headings(text)]
            return json.dumps(
                {
                    "error": f"Section not found: {section}",
                    "available_headings": headings,
                }
            )
        return json.dumps(
            {
                "path": resolved.rel_path,
                "section": extracted.heading,
                "content": extracted.content,
                "outbound_links": extracted.outbound_links,
            },
            indent=2,
        )
    return json.dumps(
        {
            "path": resolved.rel_path,
            "headings": [title for _, title in list_headings(text)],
            "content": text,
        },
        indent=2,
    )


@mcp.tool()
def wiki_lint(severity: str = "all", category: str | None = None) -> str:
    """Run wiki health checks. Optionally filter by severity or category."""
    if severity not in VALID_SEVERITIES:
        valid = ", ".join(sorted(VALID_SEVERITIES))
        return json.dumps({"error": f"Invalid severity: {severity!r}. Valid: {valid}"})
    root = _root()
    report = lint_wiki(wiki_dir(root), project_root=root)
    issues = filter_issues(report.issues, severity=severity, category=category)
    return json.dumps(_issue_payload(issues), indent=2)


@mcp.tool()
def wiki_stats() -> str:
    """Return wiki statistics: page counts, raw files, log entries."""
    s = get_stats(_root())
    return json.dumps(
        {
            "total_pages": s.total_pages,
            "entities": s.entities,
            "concepts": s.concepts,
            "sources": s.sources,
            "answers": s.answers,
            "raw_files": s.raw_files,
            "log_entries": s.log_entries,
        },
        indent=2,
    )


@mcp.tool()
def wiki_list(page_type: str = "all") -> str:
    """List wiki pages. page_type: entity, concept, source, answer, or all."""
    wiki_root = wiki_dir(_root())
    pages = iter_wiki_pages(wiki_root)
    prefix_map = {
        "entity": "entities/",
        "concept": "concepts/",
        "source": "sources/",
        "answer": "answers/",
    }
    if page_type not in VALID_PAGE_TYPES:
        valid = ", ".join(sorted(VALID_PAGE_TYPES))
        return json.dumps({"error": f"Invalid page_type: {page_type!r}. Valid: {valid}"})
    if page_type != "all":
        pages = [p for p in pages if p.rel_path.startswith(prefix_map[page_type])]
    return json.dumps([{"path": p.rel_path, "stem": p.stem} for p in pages], indent=2)


@mcp.tool()
def wiki_ingest_status() -> str:
    """List raw files and whether matching source pages exist."""
    statuses = get_ingest_status(_root())
    return json.dumps(
        [
            {
                "raw_file": s.raw_file,
                "source_page": s.source_page,
                "status": s.status,
            }
            for s in statuses
        ],
        indent=2,
    )


@mcp.tool()
def wiki_recent_log(limit: int = 10) -> str:
    """Return the most recent append-only log entries."""
    entries = parse_log(wiki_dir(_root()) / "log.md", limit=limit)
    return json.dumps(entries, indent=2)


@mcp.tool()
def wiki_backlinks(page: str) -> str:
    """List pages that wikilink to the given page."""
    wiki_root = wiki_dir(_root())
    resolved = resolve_page(wiki_root, page)
    if not resolved:
        return json.dumps({"error": f"Page not found: {page}"})
    refs = get_backlinks(wiki_root, page)
    return json.dumps({"page": resolved.rel_path, "backlinks": refs}, indent=2)


@mcp.tool()
def wiki_graph() -> str:
    """Export the wiki link graph as JSON nodes and edges."""
    return json.dumps(export_graph(wiki_dir(_root())), indent=2)


@mcp.tool()
def wiki_new(
    page_type: str,
    slug: str,
    title: str | None = None,
    force: bool = False,
) -> str:
    """Create a new wiki page from templates/. page_type: entity, concept, source, answer."""
    try:
        result = create_page(
            _root(),
            page_type=page_type,
            slug=slug,
            title=title,
            force=force,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        return json.dumps({"error": str(exc)})
    return json.dumps(
        {
            "path": result.rel_path,
            "created": result.created,
            "hint": "Update wiki/index.md and add wikilinks from related pages.",
        },
        indent=2,
    )


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
