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
    candidates = [
        wiki_root / page,
        wiki_root / f"{page}.md",
        wiki_root / "entities" / f"{page}.md",
        wiki_root / "concepts" / f"{page}.md",
        wiki_root / "sources" / f"{page}.md",
        wiki_root / "answers" / f"{page}.md",
    ]
    path = next((p for p in candidates if p.exists()), None)
    if not path:
        return json.dumps({"error": f"Page not found: {page}"})
    return json.dumps({"path": path.relative_to(wiki_root).as_posix(), "content": path.read_text()})


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
def wiki_recent_log(limit: int = 10) -> str:
    """Return the most recent append-only log entries."""
    entries = parse_log(wiki_dir(_root()) / "log.md", limit=limit)
    return json.dumps(entries, indent=2)


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()