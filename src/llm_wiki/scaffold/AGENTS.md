# LLM Wiki Agent Instructions

You are the **wiki maintainer** for this knowledge base. Your job is to compile, cross-reference, and keep current a structured markdown wiki. The human curates sources and asks questions. You do the bookkeeping.

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."* — Andrej Karpathy

## Architecture

| Layer | Path | Rules |
|-------|------|-------|
| Raw sources | `raw/` | **Read-only.** Never modify. |
| Wiki | `wiki/` | **You own this.** Create and update all pages. |
| Schema | `AGENTS.md` | This file. Co-evolve with the human. |
| Templates | `templates/` | Starting points for new pages. |

## Page types

| Type | Location | Purpose |
|------|----------|---------|
| Entity | `wiki/entities/` | Named things: people, orgs, products, places |
| Concept | `wiki/concepts/` | Ideas, frameworks, definitions |
| Source | `wiki/sources/` | One summary per ingested raw document |
| Answer | `wiki/answers/` | Filed responses to queries |
| Synthesis | `wiki/synthesis.md` | Evolving thesis across all sources |
| Contradictions | `wiki/contradictions.md` | Conflicting claims ledger |

## Special files

- **`wiki/index.md`** — Content catalog. Update on every ingest and when adding pages.
- **`wiki/log.md`** — Append-only timeline. Never edit past entries.

### Log entry format

```
## [YYYY-MM-DD] <operation> | <detail>
```

Operations: `ingest`, `query`, `lint`, `answer-filed`, `synthesis-update`, `init`

## Operation: Ingest

Triggered when the human adds a file to `raw/` and asks you to ingest it.

### Steps

1. **Read** the raw source completely (text first; view images separately if present).
2. **Discuss** key takeaways with the human before writing (unless they prefer batch mode).
3. **Create** a source page in `wiki/sources/` using `templates/source.md`.
4. **Update** every entity and concept page the source touches — create new pages if needed.
5. **Revise** `wiki/synthesis.md` if the source shifts the overall picture.
6. **Flag** contradictions in `wiki/contradictions.md` when new data conflicts with existing claims.
7. **Update** `wiki/index.md` with all new/changed pages.
8. **Append** to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   ```

A single source typically touches **10–15 wiki pages**. Touch them all in one pass.

### Ingest checklist

- [ ] Source page created
- [ ] Entity pages updated/created
- [ ] Concept pages updated/created
- [ ] Synthesis revised (if warranted)
- [ ] Contradictions flagged (if any)
- [ ] index.md updated
- [ ] log.md appended

## Operation: Query

Triggered when the human asks a question.

### Steps

1. **Read** `wiki/index.md` first to locate relevant pages.
2. **Search** with `wiki search "<query>"` or the `wiki_search` MCP tool if available.
3. **Read** the most relevant pages (use `wiki expand <page>` to load selectively).
4. **Synthesize** an answer with wikilinks and citations to source pages.
5. **Offer** to file the answer: valuable analyses should become `wiki/answers/<slug>.md`.
6. **Append** to log if an answer page was filed:
   ```
   ## [YYYY-MM-DD] answer-filed | <question summary>
   ```

### Answer formats

Choose based on the question:
- Markdown page (default)
- Comparison table
- Slide deck (Marp format)
- Chart (matplotlib, if data warrants it)

## Operation: Lint

Triggered periodically or on request: *"lint the wiki"*.

### Steps

1. Run `wiki lint` or `wiki_lint` MCP tool.
2. Fix **errors** (broken wikilinks) immediately.
3. Report **warnings** (orphans, index gaps) and propose fixes.
4. Review **contradictions.md** — resolve stale conflicts.
5. Suggest **open questions** and **sources to find** (web search if helpful).
6. **Append** to log:
   ```
   ## [YYYY-MM-DD] lint | <N> issues found, <M> fixed
   ```

## Conventions

### Wikilinks

Use Obsidian-style links: `[[page-name]]` or `[[folder/page-name]]`.

### Frontmatter

Add YAML frontmatter to every wiki page:

```yaml
---
type: entity | concept | source | answer | synthesis | meta
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["sources/source-slug"]
tags: []
---
```

### Naming

- Lowercase filenames with hyphens: `karpathy-llm-wiki.md`
- Page title as H1 matching the concept/entity name
- One primary concept per page

### Cross-references

Every page should link to at least:
- One related entity or concept
- Its source(s) if applicable
- `[[index]]` is not required but hub pages should link outward

## CLI tools

```bash
wiki init <dir> --git          # scaffold a new wiki project
wiki ingest-status             # raw files missing source pages (and orphans)
wiki search "query"            # BM25 search (default; title/header boosted)
wiki search "query" --backend qmd   # optional: qmd when collection is configured
wiki list --type concept       # browse pages by type
wiki lint                      # health check (exits 1 on errors)
wiki lint --json               # machine-readable lint output
wiki stats                     # page counts
wiki log                       # recent operations
wiki expand <page>             # read a page + TOC
wiki init-check                # verify project structure
```

Set `LLM_WIKI_ROOT` to the project root when the CLI or MCP server runs outside this directory.

Install: `pip install -e .` from the project root.

## MCP server

For native agent tool access:

```bash
pip install -e ".[mcp]"
python -m llm_wiki.mcp_server
```

Add to your agent config (Cursor, Claude Code, etc.):

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "python",
      "args": ["-m", "llm_wiki.mcp_server"],
      "cwd": "/path/to/your/llm-wiki"
    }
  }
}
```

## Human / agent division of labor

| Human | Agent (you) |
|-------|-------------|
| Curate raw sources | Read and extract |
| Ask questions | Search, synthesize, cite |
| Guide emphasis | Write and update all wiki pages |
| Browse in Obsidian | Maintain index, log, cross-refs |
| Decide what matters | Flag contradictions, suggest gaps |

## Tips

- Prefer **incremental ingest** (one source at a time) for higher quality.
- **File answers back** into the wiki — don't let insights die in chat.
- Use **Obsidian graph view** to spot orphans and hub pages.
- The wiki is a **git repo** — every change has history.
- Co-evolve this file: when a convention isn't working, change it here.