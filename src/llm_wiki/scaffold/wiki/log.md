# Wiki Log

Append-only timeline of wiki operations. Each entry uses a consistent prefix for parsing:

```bash
grep "^## \[" log.md | tail -5   # last 5 operations
grep "ingest" log.md              # all ingests
```

---

## [{{date}}] init | Scaffolded {{project_name}}

Initialized llm-wiki from the Karpathy pattern. Wiki is ready for first source ingest.