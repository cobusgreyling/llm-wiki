# Demo wiki

Populated example wiki ingested from two sources:

1. **Karpathy LLM Wiki gist** — the original pattern
2. **qmd hybrid search** — scale retrieval layer (with open contradiction in `wiki/contradictions.md`)

## Explore

```bash
wiki --root examples/demo search "memex"
wiki --root examples/demo ingest-status
wiki --root examples/demo lint
make demo-search   # from repo root
```

Open this folder as an Obsidian vault to view the graph.

## Pages

| Type | Count | Highlights |
|------|-------|------------|
| Sources | 2 | karpathy-llm-wiki-gist, qmd-hybrid-search |
| Entities | 3 | Karpathy, Bush, Tobi Lutke |
| Concepts | 6 | compounding-knowledge, rag, memex, hybrid-search, wiki-ingest, wiki-lint |
| Answers | 1 | llm-wiki-vs-rag |
| Meta | 2 | synthesis (revised thesis), contradictions (open row) |