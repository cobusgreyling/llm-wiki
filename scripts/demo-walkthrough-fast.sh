#!/usr/bin/env bash
# Fast terminal tour for asciinema recording (no pauses).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="$ROOT/examples/demo"

if command -v wiki >/dev/null 2>&1; then
  WIKI_BIN="wiki"
elif [[ -x "$ROOT/.venv/bin/wiki" ]]; then
  WIKI_BIN="$ROOT/.venv/bin/wiki"
else
  pip install -e "$ROOT" >/dev/null
  WIKI_BIN="wiki"
fi
WIKI="$WIKI_BIN --root $DEMO"

echo "═══════════════════════════════════════════════════════════"
echo " LLM Wiki — Demo walkthrough"
echo " Repo: $ROOT"
echo " Wiki: $DEMO"
echo "═══════════════════════════════════════════════════════════"

echo ""
echo "▶ Wiki stats"
$WIKI stats

echo ""
echo "▶ Search: memex (BM25)"
$WIKI search "memex" -n 5

echo ""
echo "▶ Ingest status (raw ↔ source coverage)"
$WIKI ingest-status

echo ""
echo "▶ Lint (errors only)"
$WIKI lint --severity error

echo ""
echo "▶ Recent log"
$WIKI log -n 5

echo ""
echo "▶ Expand synthesis (first lines)"
$WIKI expand synthesis | head -n 30

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " Done. Open examples/demo/ in Obsidian for the graph view."
echo " Next: cp your-file.md $DEMO/raw/ && ask your agent to ingest."
echo "═══════════════════════════════════════════════════════════"