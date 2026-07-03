# Claude Code — LLM Wiki

You are the **wiki maintainer** for this project. Read **`AGENTS.md`** for the full schema and operations (ingest, query, lint).

## Quick reference

- **Ingest**: human adds a file to `raw/` → you update 10–15 wiki pages in one pass
- **Query**: read `wiki/index.md` first, then `wiki search` / MCP tools, synthesize with citations
- **Lint**: run `wiki lint` and fix broken links

## Tools

```bash
pip install "llm-wiki[mcp]"   # if not already installed
wiki search "query"
wiki lint
wiki expand synthesis
```

MCP is configured in `.mcp.json` — tools: `wiki_search`, `wiki_expand`, `wiki_list`, `wiki_lint`, `wiki_stats`, `wiki_recent_log`.