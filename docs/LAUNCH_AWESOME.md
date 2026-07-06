# Awesome-list PR targets

Copy-paste blurbs for pull requests to curated lists. Verify each list still accepts PRs before submitting.

## Standard blurb

```markdown
- [llm-wiki](https://github.com/cobusgreyling/llm-wiki) — Reference implementation of Karpathy's LLM Wiki pattern. Agents maintain a compounding markdown wiki (entities, concepts, synthesis, contradictions) instead of per-query RAG retrieval. Python CLI + MCP server, Obsidian-compatible wikilinks, optional qmd backend.
```

## Target lists

### AI / LLM agents

| List | Path to edit | Section suggestion |
|------|--------------|-------------------|
| [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | `README.md` | Knowledge / memory tools |
| [Jannchie/awesome-knowledge-management](https://github.com/Jannchie/awesome-knowledge-management) | `README.md` | LLM / agent-assisted |
| [steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | `README.md` | Applications → knowledge |

### Obsidian / PKM

| List | Path to edit | Section suggestion |
|------|--------------|-------------------|
| [kmaasrud/awesome-obsidian](https://github.com/kmaasrud/awesome-obsidian) | `README.md` | Tools or workflows |
| [learn-anything/obsidian](https://github.com/learn-anything/obsidian) | `README.md` | Plugins & tools (workflow, not a plugin) |
| [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) | N/A — skip unless you add a server component |

### MCP

| List | Path to edit | Section suggestion |
|------|--------------|-------------------|
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | `README.md` | Knowledge / search |
| [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | `README.md` | Knowledge bases |

### Python CLI

| List | Path to edit | Section suggestion |
|------|--------------|-------------------|
| [avelino/awesome-go](https://github.com/avelino/awesome-go) | N/A | Not applicable |
| [uraimo/awesome-qt-maui](https://github.com/uraimo/awesome-qt-maui) | N/A | Not applicable |

Use [awesome-python](https://github.com/vinta/awesome-python) only if you add a distinct "CLI tools" subsection for knowledge management.

## PR checklist

- [ ] List is actively maintained (merged PRs in last 6 months)
- [ ] Entry fits the list's category (don't spam unrelated sections)
- [ ] Link uses HTTPS GitHub URL
- [ ] One-line description mentions: Karpathy pattern, agents, Obsidian, CLI/MCP
- [ ] Alphabetical order preserved in target section

## Optional longer description (for lists that allow paragraphs)

```markdown
### llm-wiki

[llm-wiki](https://github.com/cobusgreyling/llm-wiki) implements the LLM Wiki pattern from Andrej Karpathy's gist: a compounding personal knowledge base where LLM agents maintain structured, interlinked markdown instead of re-deriving knowledge from raw chunks on every query.

- `wiki init` scaffolds an Obsidian-friendly vault with `AGENTS.md` schema
- CLI: BM25 search, lint, ingest-status, section-level page expand
- MCP server for Cursor, Claude Code, and other agents
- Example wikis: research papers, book notes, business meeting notes
- Optional [qmd](https://github.com/tobi/qmd) backend for hybrid search at scale
```