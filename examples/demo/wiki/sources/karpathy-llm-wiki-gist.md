---
type: source
created: 2026-07-03
updated: 2026-07-03
raw_file: "karpathy-llm-wiki-gist.md"
author: "Andrej Karpathy"
date_published: "2026-04-04"
tags: [pattern, knowledge-base]
---

# Karpathy LLM Wiki Gist

## Summary

Karpathy describes a pattern for personal knowledge bases where an LLM agent incrementally builds and maintains a markdown wiki between the user and immutable raw sources. Three layers: raw sources, wiki, and schema. Three operations: ingest, query, lint.

## Key takeaways

1. The wiki is a **persistent, compounding artifact** — not re-derived per query like RAG.
2. Humans curate sources and ask questions; the LLM handles summarizing, cross-referencing, and bookkeeping.
3. `index.md` and `log.md` are special navigation files; the index works well to ~100 sources without embedding infrastructure.

## Entities mentioned

- [[entities/andrej-karpathy]]
- [[entities/vannevar-bush]]

## Concepts mentioned

- [[concepts/compounding-knowledge]]
- [[concepts/rag]]
- [[concepts/memex]]
- [[concepts/wiki-ingest]]
- [[concepts/wiki-lint]]

## Quotes

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*

## Raw reference

`raw/karpathy-llm-wiki-gist.md`