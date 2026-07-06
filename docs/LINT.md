# Lint rule catalog

Run `wiki lint` (or MCP `wiki_lint`) to health-check a wiki. Filter results for agent fix loops:

```bash
wiki lint --severity error
wiki lint --category broken-link
wiki lint --severity warning --category orphan
```

## Severities

| Severity | Meaning |
|----------|---------|
| `error` | Breaks wiki integrity — fix immediately |
| `warning` | Quality issue — fix or acknowledge |
| `info` | Suggestion — optional improvement |

## Categories

| Category | Severity | Fix |
|----------|----------|-----|
| `structure` | error | Create missing `index.md`, `log.md`, or `synthesis.md` |
| `broken-link` | error | Fix or create the target page for `[[wikilink]]` |
| `ambiguous-link` | warning | Disambiguate slug collision — use full path in wikilinks |
| `ambiguous-slug` | warning | Rename pages so slugs are unique |
| `broken-markdown-link` | warning | Fix `[text](path)` links to wiki files |
| `source-missing-raw-file` | error | Add `raw_file` to source page frontmatter |
| `raw-uningested` | warning | Ingest the raw file or remove it from `raw/` |
| `raw-missing` | warning | Restore raw file or fix `raw_file` reference |
| `orphan` | warning | Add inbound wikilinks from index or related pages |
| `index-gap` | warning | Reference the page in `wiki/index.md` |
| `frontmatter` | warning | Add valid YAML frontmatter with `type`, dates |
| `invalid-source-ref` | warning | Fix `sources:` list in frontmatter |
| `contradiction-unfiled` | warning | Add entry to `wiki/contradictions.md` |
| `contradiction-hint` | info | Review prose for stale/conflicting claims |
| `missing-page` | info | Consider creating a dedicated page for repeated terms |

## Exit codes

`wiki lint` exits `1` when issues at or above `--fail-on` are found (default: `error`).

```bash
wiki lint --fail-on warning   # stricter CI gate
wiki lint --json              # machine-readable output
```