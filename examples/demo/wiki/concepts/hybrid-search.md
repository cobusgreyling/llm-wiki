---
type: concept
created: 2026-07-04
updated: 2026-07-04
sources: ["sources/qmd-hybrid-search"]
tags: [search, retrieval]
---

# Hybrid Search

## Definition

Search that combines lexical methods (BM25 keyword matching) with semantic vector similarity, optionally augmented by query expansion and reranking.

## Why it matters

Compounding wikis grow dense cross-links. Paraphrased queries may not match exact terms on relevant pages. Hybrid search improves recall without abandoning the structured wiki model.

## Connections

- Tool: qmd (`wiki search --backend qmd`)
- Contrasts with: pure BM25 in `wiki search` (default)
- Complements: [[concepts/compounding-knowledge]]
- Sources: [[sources/qmd-hybrid-search]], [[sources/karpathy-llm-wiki-gist]]