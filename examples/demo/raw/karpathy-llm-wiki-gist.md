# LLM Wiki (Karpathy Gist)

Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
Author: Andrej Karpathy
Date: 2026-04-04

## Core idea

Instead of RAG-style retrieval from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — structured, interlinked markdown between you and raw sources.

When you add a source, the LLM reads it, extracts key information, and integrates it into the existing wiki: updating entity pages, revising topic summaries, noting contradictions, strengthening synthesis.

**The wiki is a persistent, compounding artifact.** Cross-references exist. Contradictions are flagged. Synthesis reflects everything read.

## Three layers

1. **Raw sources** — immutable curated documents
2. **The wiki** — LLM-generated markdown the agent owns entirely
3. **The schema** — AGENTS.md / CLAUDE.md telling the agent how to maintain the wiki

## Operations

- **Ingest** — process a new raw source, touch 10-15 wiki pages
- **Query** — search wiki, synthesize answer, optionally file as new page
- **Lint** — contradictions, orphans, stale claims, missing pages

## Special files

- `index.md` — content catalog, updated on every ingest
- `log.md` — append-only chronological record

## Why it works

Humans abandon wikis because maintenance grows faster than value. LLMs don't get bored, don't forget cross-references, and can touch 15 files in one pass. The human curates sources and asks questions; the LLM does bookkeeping.

Related to Vannevar Bush's Memex (1945) — associative trails between documents. Bush couldn't solve who does the maintenance. The LLM can.