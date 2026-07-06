# Launch copy — ready to post

Draft text for announcing [llm-wiki](https://github.com/cobusgreyling/llm-wiki). Edit voice as needed before posting.

## Posting checklist

Post in this order for maximum discovery:

- [x] **Karpathy gist comment** — posted 2026-07-05: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6235480
- [ ] **Show HN** — use the draft below; post Tuesday–Thursday 9–11am US Eastern
- [ ] **X / LinkedIn** — short post with asciinema: https://asciinema.org/a/JaIKgBIXHP8nDyw0
- [ ] **Obsidian forum / Discord** — draft ready: [docs/LAUNCH_OBSIDIAN.md](docs/LAUNCH_OBSIDIAN.md)
- [ ] **Awesome-list PRs** — targets and blurbs: [docs/LAUNCH_AWESOME.md](docs/LAUNCH_AWESOME.md)

Before posting:

```bash
./scripts/demo-walkthrough.sh    # verify demo works
wiki --root examples/demo lint --severity error
```

Terminal demo recorded: https://asciinema.org/a/JaIKgBIXHP8nDyw0 (cast in `assets/demo.cast`). Re-record: [docs/DEMO.md](docs/DEMO.md).

> **Note:** Authenticate the asciinema CLI (`asciinema auth`) so the upload is not auto-deleted after 7 days.

---

## Karpathy gist comment

> Reference implementation + tooling for this pattern: https://github.com/cobusgreyling/llm-wiki
>
> - `pip install llm-wiki && wiki init my-wiki --git` scaffolds a new wiki
> - CLI (`wiki search`, `wiki lint`, `wiki ingest-status`) + MCP server for agents
> - Demo wiki with **two ingested sources** — synthesis revision + contradictions ledger in `examples/demo/`
> - Domain examples: research (`examples/research/`), book notes (`examples/reading/`), business meetings (`examples/business/`)
> - Section-level expand: `wiki expand synthesis --section "Thesis"` (token-efficient reads)
> - Optional qmd backend when the wiki outgrows BM25: `wiki search "query" --backend qmd`
>
> Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

---

## Short post (X / LinkedIn)

**Stop re-deriving knowledge on every question.**

I built tooling for [@karpathy](https://x.com/karpathy)'s LLM Wiki pattern — a compounding knowledge base where agents maintain structured markdown instead of RAG chunk retrieval.

```bash
pip install llm-wiki
wiki init my-wiki --git
wiki ingest-status
```

Drop sources in `raw/`. Your agent ingests into interlinked wiki pages. Browse the graph in Obsidian.

New: `wiki expand <page> --section "Heading"` for token-efficient reads. Business team example in `examples/business/`.

Demo: https://asciinema.org/a/JaIKgBIXHP8nDyw0 — https://github.com/cobusgreyling/llm-wiki

---

## Hacker News (Show HN)

**Show HN: LLM Wiki – compounding knowledge base maintained by agents (Karpathy pattern)**

Classic RAG retrieves fragments at query time; nothing accumulates. Karpathy described an alternative: the LLM maintains a structured markdown wiki — entity pages, synthesis, contradictions ledger — compiled once and kept current.

I built a reference implementation with:

- `wiki init` to scaffold a new Obsidian-friendly wiki repo
- BM25 search + lint (broken links, orphans, raw/source coverage)
- `wiki ingest-status` — see which raw files still need ingesting
- `wiki expand --section` — read one heading block, not the whole page
- Stricter lint — source `raw_file` required, `sources:` frontmatter validated, contradictions ledger checks
- MCP server for Cursor / Claude Code
- Demo wiki with two sources showing synthesis revision and an open contradiction
- Domain examples: research, reading, **business** (meetings + customer calls)
- Optional qmd integration for hybrid search at scale

GitHub: https://github.com/cobusgreyling/llm-wiki

Terminal demo: https://asciinema.org/a/JaIKgBIXHP8nDyw0

Would love feedback on the agent schema (`AGENTS.md`) and what CLI tools would help at scale.

---

## Awesome-list PR blurb

**llm-wiki** — Reference implementation of Karpathy's LLM Wiki pattern. Agents maintain a compounding markdown wiki (entities, concepts, synthesis, contradictions) instead of per-query RAG retrieval. Python CLI + MCP server, Obsidian-compatible, optional qmd backend. https://github.com/cobusgreyling/llm-wiki