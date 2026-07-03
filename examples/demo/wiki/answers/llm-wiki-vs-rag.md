---
type: answer
created: 2026-07-03
updated: 2026-07-03
query: "How is LLM Wiki different from RAG?"
sources_consulted: ["sources/karpathy-llm-wiki-gist"]
tags: [comparison]
---

# LLM Wiki vs RAG

## Question

How is the LLM Wiki pattern different from standard RAG?

## Answer

| Dimension | RAG | LLM Wiki |
|-----------|-----|----------|
| Storage | Raw chunks + embeddings | Structured markdown wiki |
| On new source | Index for later retrieval | Integrate into 10–15 pages immediately |
| On query | Retrieve + generate fresh | Read pre-compiled pages + synthesize |
| Cross-refs | None (rediscovered each time) | Persistent wikilinks |
| Contradictions | Not tracked | Flagged in contradictions ledger |
| Accumulation | None | Compounding over time |

RAG is stateless retrieval. LLM Wiki is a **maintained codebase of knowledge** — closer to [[concepts/memex]] than to a search engine.

## Sources consulted

- [[sources/karpathy-llm-wiki-gist]]

## Follow-ups

- When does a wiki outgrow index-based search and need tools like qmd?
- How to handle human-in-the-loop review for team wikis?