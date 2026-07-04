---
type: source
created: 2026-07-04
updated: 2026-07-04
raw_file: "qmd-hybrid-search.md"
author: "Tobi Lutke"
tags: [search, tooling]
---

# qmd Hybrid Search

## Summary

qmd adds local hybrid search (BM25 + vectors + optional reranking) for markdown knowledge bases. It is a retrieval layer, not a wiki maintainer — it complements the LLM Wiki pattern when lexical search and `index.md` navigation start to miss relevant pages.

## Key takeaways

1. Hybrid search improves recall on paraphrased queries that BM25 alone misses.
2. Quality degradation can appear before ~100 pages when cross-links are sparse.
3. qmd integrates via `wiki search --backend qmd` after `qmd collection add wiki --name wiki`.

## Entities mentioned

- [[entities/tobi-lutke]]

## Concepts mentioned

- [[concepts/hybrid-search]]
- [[concepts/compounding-knowledge]]
- [[concepts/rag]]

## Connections

- Complements: [[sources/karpathy-llm-wiki-gist]]
- See contradiction: [[contradictions]] (scale threshold for embeddings)

## Raw reference

`raw/qmd-hybrid-search.md`