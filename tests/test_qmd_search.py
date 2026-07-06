import json
from pathlib import Path

import pytest

from llm_wiki.search import search_wiki_qmd, search_wiki_with_backend


def test_search_invalid_backend():
    with pytest.raises(ValueError, match="Unknown search backend"):
        search_wiki_with_backend(Path("/tmp/wiki"), "query", backend="invalid")


def test_search_wiki_qmd_mocked(monkeypatch, tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    wiki_root.mkdir()
    page = wiki_root / "concepts" / "memex.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Memex\n\nA device for memory.")

    payload = [
        {
            "path": str(page),
            "score": 0.92,
            "snippet": "A device for memory.",
        }
    ]

    class FakeProc:
        returncode = 0
        stdout = json.dumps(payload)
        stderr = ""

    def fake_run(*_args, **_kwargs):
        return FakeProc()

    monkeypatch.setattr("llm_wiki.search.shutil.which", lambda _cmd: "/usr/bin/qmd")
    monkeypatch.setattr("llm_wiki.search.subprocess.run", fake_run)

    results = search_wiki_qmd(wiki_root, "memex", limit=3)
    assert len(results) == 1
    assert results[0].page.rel_path == "concepts/memex.md"
