# Maintainer guide

## PyPI publishing

Releases publish automatically when a [GitHub Release](https://github.com/cobusgreyling/llm-wiki/releases) is created. The workflow is [`.github/workflows/publish.yml`](.github/workflows/publish.yml).

### One-time setup

1. **Create the PyPI project** at [pypi.org](https://pypi.org) — project name: `llm-wiki`.

2. **Add a trusted publisher** (PyPI → your project → Publishing → Add trusted publisher):

   | Field | Value |
   |-------|-------|
   | PyPI project name | `llm-wiki` |
   | Owner | `cobusgreyling` |
   | Repository | `llm-wiki` |
   | Workflow name | `publish.yml` |
   | Environment | `pypi` |

3. **GitHub environment** — already configured as `pypi` in repo Settings → Environments (no secrets required).

4. **Publish** — create or re-publish a release (e.g. `v0.2.1`). The [Publish workflow](https://github.com/cobusgreyling/llm-wiki/actions/workflows/publish.yml) runs on `release: published`.

### Troubleshooting

If publish fails with `invalid-publisher: valid token, but no corresponding publisher`, the trusted publisher on PyPI does not match the workflow claims. Expected claims (from the last failed run):

```
sub:               repo:cobusgreyling/llm-wiki:environment:pypi
repository:        cobusgreyling/llm-wiki
repository_owner:  cobusgreyling
workflow_ref:      cobusgreyling/llm-wiki/.github/workflows/publish.yml@refs/tags/<tag>
environment:       pypi
```

Verify every field matches exactly on PyPI, then re-run the failed workflow or publish a new patch release.

### Verify after publish

```bash
pip install llm-wiki
wiki --version
wiki init /tmp/test-wiki --git
wiki --root /tmp/test-wiki init-check
pip install "llm-wiki[mcp]"
python -m llm_wiki.mcp_server  # should start without import errors
```

## Release checklist

- [ ] Version bumped in `pyproject.toml`
- [ ] `CHANGELOG.md` updated (release notes)
- [ ] `src/llm_wiki/__init__.py` version matches `pyproject.toml`
- [ ] `python scripts/sync_agents.py` run if `AGENTS.md` changed
- [ ] CI green on `main`
- [ ] GitHub Release created with tag `vX.Y.Z`
- [ ] Publish workflow succeeded
- [ ] `pip install llm-wiki` works from a clean environment