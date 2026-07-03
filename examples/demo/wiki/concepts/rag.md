---
type: concept
created: 2026-07-03
updated: 2026-07-03
sources: ["sources/karpathy-llm-wiki-gist"]
tags: [retrieval]
---

# RAG

## Definition

Retrieval-Augmented Generation: upload documents, retrieve relevant chunks at query time, generate an answer. Used by NotebookLM, ChatGPT file uploads, and most knowledge systems.

## Why it matters

RAG works but has no accumulation. The LLM rediscovers knowledge from scratch on every question. Cross-document synthesis is fragile at query time.

## Connections

- Contrasts with: [[concepts/compounding-knowledge]]
- See also: [[answers/llm-wiki-vs-rag]]
- Sources: [[sources/karpathy-llm-wiki-gist]]