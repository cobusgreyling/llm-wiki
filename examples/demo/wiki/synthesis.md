---
type: synthesis
updated: 2026-07-03
source_count: 1
---

# Synthesis

## Thesis

The LLM Wiki pattern replaces ephemeral RAG retrieval with a **compounding markdown wiki** that an agent maintains. Knowledge is compiled during ingest and stays current through lint passes — not re-derived on every question.

## Key insight

The expensive part of knowledge bases is bookkeeping: cross-references, contradiction tracking, summary updates. LLMs make maintenance cost near-zero, shifting the human role to curation and questioning.

## Lineage

This pattern reconnects to [[concepts/memex|Vannevar Bush's Memex]] — associative trails between documents in a personal store. The missing piece Bush couldn't solve (who maintains it) is now the LLM's job.

## Related

- [[sources/karpathy-llm-wiki-gist]]
- [[answers/llm-wiki-vs-rag]]