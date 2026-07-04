# Demo walkthrough

A scripted tour of the LLM Wiki toolkit using the demo wiki. Run it locally or record for sharing.

## Quick run

```bash
git clone https://github.com/cobusgreyling/llm-wiki.git
cd llm-wiki
pip install -e ".[dev]"
./scripts/demo-walkthrough.sh
```

Or use Make:

```bash
make walkthrough
```

## What the script shows

1. Demo wiki stats (pages, sources, raw files)
2. BM25 search for "memex"
3. Ingest status (raw ↔ source coverage)
4. Lint health check
5. Recent log entries
6. Expand synthesis page

## Recording a terminal video

### Option A: asciinema (recommended)

```bash
brew install asciinema   # or apt install asciinema
asciinema rec demo.cast -c "./scripts/demo-walkthrough.sh"
asciinema upload demo.cast
```

### Option B: screen recording

1. Open a terminal at 80×24 or larger
2. Run `./scripts/demo-walkthrough.sh`
3. Record with QuickTime (macOS), OBS, or similar
4. Trim to ~2 minutes

### Option C: animated GIF

```bash
brew install agg vhs
# Create demo.tape with VHS, then:
vhs demo.tape
```

## Obsidian graph (optional second clip)

1. Open `examples/demo/` as an Obsidian vault
2. Open Graph view
3. Show hub pages: synthesis, karpathy-llm-wiki-gist, hybrid-search

## Suggested narration beats

- "Drop sources in raw/ — the agent ingests into interlinked wiki pages"
- "Knowledge compounds: synthesis revises, contradictions get flagged"
- "CLI and MCP tools let agents search, lint, and track ingest status"
- "Browse the graph in Obsidian — Obsidian is the IDE"