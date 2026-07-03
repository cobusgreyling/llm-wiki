# Launch copy — ready to post

Draft text for announcing [llm-wiki](https://github.com/cobusgreyling/llm-wiki). Edit voice as needed before posting.

---

## Karpathy gist comment

> Reference implementation + tooling for this pattern: https://github.com/cobusgreyling/llm-wiki
>
> - `pip install llm-wiki && wiki init my-wiki --git` scaffolds a new wiki
> - CLI (`wiki search`, `wiki lint`) + MCP server for agents
> - Pre-populated demo wiki from your gist in `examples/demo/`
>
> Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

---

## Short post (X / LinkedIn)

**Stop re-deriving knowledge on every question.**

I built tooling for [@karpathy](https://x.com/karpathy)'s LLM Wiki pattern — a compounding knowledge base where agents maintain structured markdown instead of RAG chunk retrieval.

```bash
pip install llm-wiki
wiki init my-wiki --git
```

Drop sources in `raw/`. Your agent ingests into interlinked wiki pages. Browse the graph in Obsidian.

https://github.com/cobusgreyling/llm-wiki

---

## Hacker News (Show HN)

**Show HN: LLM Wiki – compounding knowledge base maintained by agents (Karpathy pattern)**

Classic RAG retrieves fragments at query time; nothing accumulates. Karpathy described an alternative: the LLM maintains a structured markdown wiki — entity pages, synthesis, contradictions ledger — compiled once and kept current.

I built a reference implementation with:

- `wiki init` to scaffold a new Obsidian-friendly wiki repo
- BM25 search + lint (broken links, orphans, index gaps)
- MCP server (`wiki_search`, `wiki_expand`, `wiki_lint`, …) for Cursor / Claude Code
- Demo wiki ingested from Karpathy's original gist

GitHub: https://github.com/cobusgreyling/llm-wiki

Would love feedback on the agent schema (`AGENTS.md`) and what CLI tools would help at scale.

---

## Awesome-list PR blurb

**llm-wiki** — Reference implementation of Karpathy's LLM Wiki pattern. Agents maintain a compounding markdown wiki (entities, concepts, synthesis) instead of per-query RAG retrieval. Python CLI + MCP server, Obsidian-compatible. https://github.com/cobusgreyling/llm-wiki