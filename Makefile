.PHONY: help demo demo-search demo-lint demo-stats demo-ingest test lint sync-agents walkthrough format

ROOT := $(CURDIR)
DEMO := examples/demo

help:
	@echo "LLM Wiki development shortcuts"
	@echo ""
	@echo "  make demo          Show demo wiki stats"
	@echo "  make demo-search   Search demo wiki for 'memex'"
	@echo "  make demo-lint     Lint demo wiki (errors only)"
	@echo "  make demo-ingest   Show ingest status for demo wiki"
	@echo "  make walkthrough   Run scripted demo terminal tour"
	@echo "  make test          Run pytest"
	@echo "  make lint          Ruff + pytest"
	@echo "  make sync-agents   Copy AGENTS.md to scaffold and examples"

demo:
	wiki --root $(DEMO) stats

demo-search:
	wiki --root $(DEMO) search "memex"

demo-lint:
	wiki --root $(DEMO) lint --severity error

demo-stats:
	wiki --root $(DEMO) stats

demo-ingest:
	wiki --root $(DEMO) ingest-status

walkthrough:
	./scripts/demo-walkthrough.sh

test:
	pytest -v

lint:
	ruff check src tests
	ruff format --check src tests
	pytest -v

format:
	ruff format src tests
	ruff check src tests --fix

sync-agents:
	python scripts/sync_agents.py