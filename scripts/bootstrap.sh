#!/usr/bin/env bash
# Scaffold a new LLM Wiki project.
# Usage: ./scripts/bootstrap.sh [target-dir] [--name my-wiki] [--git]
set -euo pipefail

TARGET="${1:-my-wiki}"
shift || true

if command -v wiki >/dev/null 2>&1; then
  exec wiki init "$TARGET" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python -m llm_wiki.cli init "$TARGET" "$@"
fi

echo "Install llm-wiki first: pip install llm-wiki" >&2
exit 1