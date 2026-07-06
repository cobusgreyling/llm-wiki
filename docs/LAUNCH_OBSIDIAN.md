# Obsidian launch copy

Draft posts for Obsidian Forum and community Discord servers. Edit voice before posting.

## Where to post

| Channel | URL | Notes |
|---------|-----|-------|
| Obsidian Forum — Share & showcase | https://forum.obsidian.md/c/share-showcase/9 | Best fit: vault pattern + wikilinks |
| Obsidian Discord `#showcase` | https://discord.gg/obsidianmd | Short post + asciinema link |
| r/ObsidianMD | https://reddit.com/r/ObsidianMD | Cross-post after forum thread gains traction |

## Forum post (long)

**Title:** LLM-maintained wiki vault — agents write the graph, you browse in Obsidian

**Body:**

I built [llm-wiki](https://github.com/cobusgreyling/llm-wiki), a reference implementation of [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The idea: instead of RAG that re-retrieves chunks on every question, an LLM agent **maintains** a structured markdown wiki — entity pages, concept pages, synthesis, contradictions ledger — while you curate immutable sources in `raw/`.

Obsidian is the read path. The agent is the maintainer. Wikilinks are the schema.

**Workflow**

1. `pip install llm-wiki && wiki init my-wiki --git`
2. Clip articles to `raw/` (Web Clipper works great)
3. Tell your agent (Cursor, Claude Code, etc.): "Ingest the new source in raw/"
4. Open the vault in Obsidian — graph view shows new cross-links in real time

**Tooling shipped with the vault**

- `wiki search` — BM25 over wiki pages (title/heading boosted)
- `wiki expand <page> --section "Heading"` — read one section, not the whole note (saves tokens)
- `wiki lint` — broken wikilinks, orphans, raw/source coverage
- `wiki ingest-status` — which raw files still need source pages
- MCP server for native agent tool access

**Examples to explore**

Clone the repo and open any example as a vault:

- `examples/demo/` — Karpathy gist + qmd hybrid search (with open contradiction in `contradictions.md`)
- `examples/research/` — NLP paper notes
- `examples/reading/` — book chapter notes
- `examples/business/` — meeting transcripts + customer call notes

Terminal demo: https://asciinema.org/a/JaIKgBIXHP8nDyw0

GitHub: https://github.com/cobusgreyling/llm-wiki

Happy to answer questions about vault layout, frontmatter conventions, or agent setup.

---

## Discord post (short)

**LLM Wiki pattern + Obsidian vault tooling**

Reference impl of Karpathy's compounding wiki idea: agents maintain interlinked markdown (`entities/`, `concepts/`, `synthesis.md`, `contradictions.md`); you curate `raw/` and browse the graph in Obsidian.

```bash
pip install llm-wiki
wiki init my-wiki --git
```

CLI + MCP: search, lint, ingest-status, section-level expand.

Demo: https://asciinema.org/a/JaIKgBIXHP8nDyw0 — https://github.com/cobusgreyling/llm-wiki

Open `examples/demo/` or `examples/business/` as a vault to see a populated graph.

---

## Tips for engagement

- Attach a screenshot of Obsidian graph view from `examples/demo/`
- Mention Web Clipper → `raw/` workflow
- Link the Karpathy gist comment if the thread asks for provenance