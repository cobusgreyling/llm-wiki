# qmd — Local Hybrid Search for Markdown Knowledge Bases

**Author:** Tobi Lutke  
**Source:** https://github.com/tobi/qmd

## Summary

qmd is a local search engine for markdown notes and knowledge bases. It combines BM25 keyword search with vector semantic search, query expansion, and optional LLM reranking — all running locally.

## Key claims

1. **Hybrid search improves recall** — keyword search alone misses paraphrases; vectors catch semantic similarity BM25 misses.
2. **Scale matters earlier than you think** — once a wiki passes a few dozen interlinked pages, index-first navigation plus lexical search starts to miss relevant cross-references.
3. **Complements, not replaces, structured wikis** — qmd searches markdown files; it does not maintain entity pages, synthesis, or contradiction ledgers. Use it as a retrieval layer when the wiki outgrows `index.md`.

## Recommended setup

```bash
npm install -g @tobilu/qmd
qmd collection add ./wiki --name wiki
qmd embed
qmd query "how does authentication work"
```

## When to adopt

- Wiki has 30+ pages and agents report missed connections during query
- Users ask questions that span distant concept pages without direct wikilinks
- BM25 `wiki search` returns low-relevance results for paraphrased queries