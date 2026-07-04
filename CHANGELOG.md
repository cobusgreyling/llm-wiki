# Changelog

All notable changes to this project are documented here.

## [0.3.0] - 2026-07-04

### Added

- `wiki ingest-status` CLI command and `wiki_ingest_status` MCP tool
- `wiki search --backend qmd` optional hybrid search via [qmd](https://github.com/tobi/qmd)
- `Makefile` with demo shortcuts (`make demo-search`, `make demo-ingest`, etc.)
- `scripts/demo-walkthrough.sh` scripted terminal tour
- `scripts/sync_agents.py` to keep `AGENTS.md` copies in sync
- `CONTRIBUTING.md`, `CHANGELOG.md`, GitHub issue templates
- Domain example wikis: `examples/research/`, `examples/reading/`
- Second demo source (qmd) with synthesis revision and open contradiction
- Expanded tests: CLI, MCP, ingest, version sync, agents sync, lint fixtures

### Changed

- Removed empty root `wiki/`, `raw/`, `templates/` to avoid clone confusion
- Lint: ambiguous slug warnings, raw/source coverage checks, deduped missing-page hints
- Search module docstring: BM25 lexical (qmd optional), not "hybrid" by default
- README, LAUNCH.md, and error messages point to `examples/demo` and `make` targets

### Fixed

- Version drift between `pyproject.toml` and `wiki --version`

## [0.2.1] - 2026-07-03

### Added

- PyPI trusted publishing documentation
- README visuals and agent config improvements

## [0.2.0] - 2026-07-03

### Added

- PyPI packaging (`pip install llm-wiki`)
- `wiki init` bootstrap with MCP configs for Cursor and Claude Code
- BM25 search with title/heading boosts
- MCP server: search, expand, list, lint, stats, recent log
- Demo wiki from Karpathy gist

## [0.1.0] - 2026-07-03

### Added

- Initial reference implementation: AGENTS.md schema, CLI, lint, CI