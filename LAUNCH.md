# Launch copy — ready to post

Draft text for announcing [llm-wiki](https://github.com/cobusgreyling/llm-wiki). Edit voice as needed before posting.

## Posting checklist

Post in this order for maximum discovery:

- [ ] **Karpathy gist comment** — highest-intent audience; you're a reference implementation
- [ ] **Show HN** — use the draft below; post Tuesday–Thursday morning US time
- [ ] **X / LinkedIn** — short post with terminal demo GIF or asciinema link
- [ ] **Obsidian forum / Discord** — vault + wikilink audience
- [ ] **Awesome-list PRs** — agent memory, PKM, MCP tool lists

Before posting:

```bash
./scripts/demo-walkthrough.sh    # verify demo works
wiki --root examples/demo lint --severity error
```

Record a terminal demo: [docs/DEMO.md](docs/DEMO.md)

---

## Karpathy gist comment

> Reference implementation + tooling for this pattern: https://github.com/cobusgreyling/llm-wiki
>
> - `pip install llm-wiki && wiki init my-wiki --git` scaffolds a new wiki
> - CLI (`wiki search`, `wiki lint`, `wiki ingest-status`) + MCP server for agents
> - Demo wiki with **two ingested sources** — synthesis revision + contradictions ledger in `examples/demo/`
> - Domain examples: research papers (`examples/research/`), book notes (`examples/reading/`)
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

Demo: `./scripts/demo-walkthrough.sh` — https://github.com/cobusgreyling/llm-wiki

---

## Hacker News (Show HN)

**Show HN: LLM Wiki – compounding knowledge base maintained by agents (Karpathy pattern)**

Classic RAG retrieves fragments at query time; nothing accumulates. Karpathy described an alternative: the LLM maintains a structured markdown wiki — entity pages, synthesis, contradictions ledger — compiled once and kept current.

I built a reference implementation with:

- `wiki init` to scaffold a new Obsidian-friendly wiki repo
- BM25 search + lint (broken links, orphans, raw/source coverage)
- `wiki ingest-status` — see which raw files still need ingesting
- MCP server for Cursor / Claude Code
- Demo wiki with two sources showing synthesis revision and an open contradiction
- Optional qmd integration for hybrid search at scale

GitHub: https://github.com/cobusgreyling/llm-wiki

Would love feedback on the agent schema (`AGENTS.md`) and what CLI tools would help at scale.

---

## Awesome-list PR blurb

**llm-wiki** — Reference implementation of Karpathy's LLM Wiki pattern. Agents maintain a compounding markdown wiki (entities, concepts, synthesis, contradictions) instead of per-query RAG retrieval. Python CLI + MCP server, Obsidian-compatible, optional qmd backend. https://github.com/cobusgreyling/llm-wiki