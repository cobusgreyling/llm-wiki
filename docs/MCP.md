# MCP server reference

Install and run:

```bash
pip install "llm-wiki[mcp]"
python -m llm_wiki.mcp_server
```

Set `LLM_WIKI_ROOT` to the wiki project root when the server runs outside that directory. `wiki init` pre-configures this in `.cursor/mcp.json`, `.mcp.json`, `.windsurf/mcp.json`, and `.opencode/mcp.json`.

## Tools

| Tool | Description |
|------|-------------|
| `wiki_search` | BM25 or qmd search (`backend`: `bm25` \| `qmd`) |
| `wiki_expand` | Read page; optional `section` for one heading |
| `wiki_lint` | Health check; optional `severity`, `category` filters |
| `wiki_list` | List pages by `page_type` |
| `wiki_stats` | Page and raw file counts |
| `wiki_ingest_status` | Raw ↔ source coverage |
| `wiki_recent_log` | Latest log entries |
| `wiki_backlinks` | Inbound wikilinks to a page |
| `wiki_graph` | Export link graph (nodes + edges) |
| `wiki_new` | Scaffold page from template |

## Error responses

Invalid inputs return JSON with an `error` field:

```json
{"error": "Invalid backend: 'foo'. Valid backends: bm25, qmd"}
```

Missing pages:

```json
{"error": "Page not found: missing-page"}
```

## Example agent prompts

- "Lint the wiki for errors only" → `wiki_lint(severity="error")`
- "What links to synthesis?" → `wiki_backlinks("synthesis")`
- "Create a concept page for memex" → `wiki_new(page_type="concept", slug="memex")`