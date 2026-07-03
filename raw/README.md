# Raw Sources

Immutable source documents live here. The LLM **reads** from this directory but **never modifies** files in it.

## What to put here

- Clipped web articles (markdown)
- PDFs, papers, reports
- Meeting transcripts
- Book chapter notes
- Images and data files (`assets/` subfolder recommended)

## Conventions

- One file per source when possible
- Use descriptive filenames: `2026-04-02-karpathy-llm-wiki.md`
- Keep originals intact — all synthesis happens in `wiki/`

## Ingest workflow

1. Drop a new file into `raw/`
2. Tell your agent: **"Ingest the new source in raw/"**
3. Review the wiki updates in Obsidian or your editor

See [AGENTS.md](../AGENTS.md) for the full ingest protocol.