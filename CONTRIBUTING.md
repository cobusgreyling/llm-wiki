# Contributing

Thanks for helping improve LLM Wiki. This repo is a **template and toolkit** — PRs for tooling, docs, and example wikis are welcome.

## Development setup

```bash
git clone https://github.com/cobusgreyling/llm-wiki.git
cd llm-wiki
pip install -e ".[dev,mcp]"
```

## Important: which wiki root?

This repository is the **toolkit**, not a populated wiki. Example wikis live under `examples/`:

| Path | Purpose |
|------|---------|
| `examples/demo/` | Main demo (Karpathy gist + qmd) |
| `examples/research/` | Research / paper notes |
| `examples/reading/` | Book chapter notes |
| `examples/business/` | Meeting notes + customer calls |

Always pass `--root` when running CLI commands from the repo clone:

```bash
wiki --root examples/demo search "memex"
wiki --root examples/demo lint
make demo-search   # shortcut
```

Or set `LLM_WIKI_ROOT=examples/demo`.

## Running checks

```bash
make lint          # ruff + pytest
make sync-agents   # copy AGENTS.md to scaffold and examples
ruff check src tests
pytest -v
wiki --root examples/demo lint --severity error
```

## AGENTS.md policy

**Canonical source:** root `AGENTS.md`

After editing it, sync copies:

```bash
python scripts/sync_agents.py
```

CI verifies scaffold `AGENTS.md` matches the canonical file.

## Pull request checklist

- [ ] Tests pass (`pytest -v`)
- [ ] Ruff clean (`ruff check src tests`)
- [ ] Demo wiki lints with zero errors
- [ ] `AGENTS.md` synced if schema changed
- [ ] Version bumped in `pyproject.toml` and `src/llm_wiki/__init__.py` (maintainers)
- [ ] `CHANGELOG.md` updated for user-facing changes

## Good first issues

- Add CLI tests for new commands
- Improve lint messages or coverage
- Expand example wikis with domain-specific content
- Document Obsidian Dataview snippets
- qmd integration docs and smoke tests

## Releases

Maintainers: see [MAINTAINERS.md](MAINTAINERS.md).