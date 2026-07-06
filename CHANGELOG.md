# Changelog

All notable changes to this project are documented here.

## [0.5.0] - 2026-07-06

### Added

- `wiki backlinks`, `wiki graph`, `wiki new`, `wiki watch` CLI commands
- MCP tools: `wiki_backlinks`, `wiki_graph`, `wiki_new`; `wiki_lint` severity/category filters
- `wiki lint --category` filter for agent fix loops
- Lint: `ambiguous-link`, `broken-markdown-link` categories; reduced contradiction-hint noise
- Docs: `docs/LINT.md`, `docs/MCP.md`, `docs/ARCHITECTURE.md`, `docs/OBSIDIAN.md`
- Scaffold: `.windsurf/mcp.json`, `.opencode/mcp.json` agent configs
- `scripts/ingest-checklist.sh` post-ingest helper
- `.pre-commit-config.yaml` (ruff + AGENTS.md sync)
- `py.typed` marker and explicit hatch `force-include` for scaffold templates
- Tests: path traversal, qmd mock, backlinks/graph, watch, expanded MCP/CLI coverage
- CI: Python 3.11, `ruff format --check`, pytest-cov (80% threshold)

### Changed

- `resolve_link` returns `None` for ambiguous slugs (lint reports `ambiguous-link`)
- Ingest status: removed `raw_file` guessing; new `incomplete` status for sources missing frontmatter
- `resolve_page` hardens against path traversal outside `wiki/`
- Stats raw file count excludes `README.md` (aligned with ingest)
- Bootstrap git init no longer fails when `git init` errors

### Fixed

- MCP `wiki_search` validates `backend` before calling search

## [0.4.0] - 2026-07-05

### Added

- `wiki expand --section` and MCP `wiki_expand(section=...)` for token-efficient section reads
- Stricter lint: required `raw_file` on source pages, `sources:` frontmatter validation, contradictions ledger cross-check
- `examples/business/` — meeting transcripts, customer call, and roadmap example wiki
- Launch docs: `docs/LAUNCH_OBSIDIAN.md`, `docs/LAUNCH_AWESOME.md`
- Tests for section expand, source lint rules, and business example wiki

### Changed

- `wiki expand` JSON output includes headings list when no section is specified
- README, LAUNCH.md, and AGENTS.md updated for new features and business example

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