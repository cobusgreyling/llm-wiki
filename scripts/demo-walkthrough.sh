#!/usr/bin/env bash
# Scripted terminal tour of the demo wiki. Safe to run in CI (read-only).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="$ROOT/examples/demo"

if command -v wiki >/dev/null 2>&1; then
  WIKI_BIN="wiki"
elif [[ -x "$ROOT/.venv/bin/wiki" ]]; then
  WIKI_BIN="$ROOT/.venv/bin/wiki"
else
  echo "Installing llm-wiki in editable mode..."
  pip install -e "$ROOT" >/dev/null
  WIKI_BIN="wiki"
fi
WIKI="$WIKI_BIN --root $DEMO"

pause() { sleep 0.8; }

echo "═══════════════════════════════════════════════════════════"
echo " LLM Wiki — Demo walkthrough"
echo " Repo: $ROOT"
echo " Wiki: $DEMO"
echo "═══════════════════════════════════════════════════════════"
pause

echo ""
echo "▶ Wiki stats"
pause
$WIKI stats
pause

echo ""
echo "▶ Search: memex (BM25)"
pause
$WIKI search "memex" -n 5
pause

echo ""
echo "▶ Ingest status (raw ↔ source coverage)"
pause
$WIKI ingest-status
pause

echo ""
echo "▶ Lint (errors only)"
pause
$WIKI lint --severity error
pause

echo ""
echo "▶ Recent log"
pause
$WIKI log -n 5
pause

echo ""
echo "▶ Expand synthesis (first lines)"
pause
$WIKI expand synthesis | head -n 30
pause

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " Done. Open examples/demo/ in Obsidian for the graph view."
echo " Next: cp your-file.md $DEMO/raw/ && ask your agent to ingest."
echo "═══════════════════════════════════════════════════════════"