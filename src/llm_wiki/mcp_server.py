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
    raise SystemExit(
        "MCP support requires: pip install 'llm-wiki[mcp]'"
    ) from exc

from .links import resolve_page
from .lint import lint_wiki
from .paths import find_root, wiki_dir
from .search import search_wiki
from .stats import get_stats, parse_log

mcp = FastMCP(
    "llm-wiki",
    instructions=(
        "Tools for operating on an LLM-maintained markdown wiki. "
        "Search pages, expand content, lint health, and inspect stats."
    ),
)


def _root() -> Path:
    return find_root()


@mcp.tool()
def wiki_search(query: str, limit: int = 8) -> str:
    """Search the wiki using BM25 ranking. Returns ranked pages with snippets."""
    results = search_wiki(wiki_dir(_root()), query, limit=limit)
    return json.dumps(
        [
            {"path": r.page.rel_path, "score": round(r.score, 4), "snippet": r.snippet}
            for r in results
        ],
        indent=2,
    )


@mcp.tool()
def wiki_expand(page: str) -> str:
    """Read a wiki page by name or path. Returns full markdown content."""
    wiki_root = wiki_dir(_root())
    resolved = resolve_page(wiki_root, page)
    if not resolved:
        return json.dumps({"error": f"Page not found: {page}"})
    return json.dumps(
        {"path": resolved.rel_path, "content": resolved.path.read_text(encoding="utf-8")}
    )


@mcp.tool()
def wiki_lint() -> str:
    """Run wiki health checks. Returns broken links, orphans, and index gaps."""
    report = lint_wiki(wiki_dir(_root()))
    return json.dumps(
        [
            {
                "severity": i.severity,
                "category": i.category,
                "page": i.page,
                "message": i.message,
            }
            for i in report.issues
        ],
        indent=2,
    )


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
    from .links import iter_wiki_pages

    wiki_root = wiki_dir(_root())
    pages = iter_wiki_pages(wiki_root)
    prefix_map = {
        "entity": "entities/",
        "concept": "concepts/",
        "source": "sources/",
        "answer": "answers/",
    }
    if page_type != "all":
        pages = [p for p in pages if p.rel_path.startswith(prefix_map[page_type])]
    return json.dumps([{"path": p.rel_path, "stem": p.stem} for p in pages], indent=2)


@mcp.tool()
def wiki_recent_log(limit: int = 10) -> str:
    """Return the most recent append-only log entries."""
    entries = parse_log(wiki_dir(_root()) / "log.md", limit=limit)
    return json.dumps(entries, indent=2)


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()