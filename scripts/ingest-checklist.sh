#!/usr/bin/env bash
# Post-ingest helper: show pending raw files and the AGENTS.md checklist.
set -euo pipefail

ROOT="${1:-.}"

echo "== Ingest status =="
wiki --root "$ROOT" ingest-status

echo ""
echo "== Ingest checklist (from AGENTS.md) =="
echo "  [ ] Source page created with raw_file frontmatter"
echo "  [ ] Entity pages updated/created"
echo "  [ ] Concept pages updated/created"
echo "  [ ] Synthesis revised (if warranted)"
echo "  [ ] Contradictions flagged (if any)"
echo "  [ ] index.md updated"
echo "  [ ] log.md appended"