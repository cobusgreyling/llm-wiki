# Architecture

LLM Wiki separates **human-curated sources** from **agent-maintained knowledge**.

```
raw/          Human drops sources (immutable)
    │
    ▼  ingest (agent reads AGENTS.md)
wiki/         Structured markdown graph
    │
    ├── index.md        Catalog — read first on queries
    ├── synthesis.md    Cross-source thesis
    ├── contradictions.md  Conflict ledger
    ├── entities/       Named things
    ├── concepts/       Ideas and frameworks
    ├── sources/        One page per raw document
    └── answers/        Filed query responses
    │
    ▼  query (search → expand → synthesize)
answers/      Optional filed responses
```

## Toolkit vs wiki

| This repo (`llm-wiki`) | Your project (`wiki init`) |
|------------------------|----------------------------|
| Python package under `src/llm_wiki/` | Markdown wiki at project root |
| CLI + MCP for read/lint/scaffold | Agent writes all `wiki/` pages |
| Examples under `examples/` | Your `raw/` and `wiki/` |

## Data flow

1. **Ingest** — Human adds `raw/article.md`. Agent creates `wiki/sources/article.md`, updates entities/concepts, revises synthesis, appends log.
2. **Query** — Agent searches (`wiki search`), expands relevant pages, synthesizes with wikilinks.
3. **Lint** — Toolkit checks links, frontmatter, raw coverage, index gaps. Agent fixes issues.

## Search backends

- **BM25** (default) — In-process lexical search with title/heading boosts.
- **qmd** (optional) — External hybrid search when the wiki outgrows BM25. Wiki pages remain source of truth.

## Agent integration

- **AGENTS.md** — Schema and operation procedures (ingest, query, lint).
- **MCP** — Native tools for search, expand, lint, backlinks, graph.
- **Obsidian** — Human browses the graph; agent maintains links.