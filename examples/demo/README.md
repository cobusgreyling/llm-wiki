# Demo Wiki

A pre-populated example showing what a wiki looks like after ingesting [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Open `examples/demo/wiki/` in Obsidian to explore the graph:

- 2 entity pages (Karpathy, Bush)
- 5 concept pages (compounding knowledge, RAG, Memex, ingest, lint)
- 1 source summary
- 1 filed answer (LLM Wiki vs RAG)
- 1 synthesis page

To lint the demo from the repo root:

```bash
wiki --root examples/demo lint
wiki --root examples/demo search "memex"
```