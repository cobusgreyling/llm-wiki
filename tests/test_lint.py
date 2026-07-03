from pathlib import Path

from llm_wiki.lint import lint_wiki, parse_frontmatter


def test_lint_demo_wiki_no_errors():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    report = lint_wiki(demo_wiki)
    assert not report.errors


def test_lint_index_skips_contradiction_hint():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    report = lint_wiki(demo_wiki)
    index_hints = [
        i
        for i in report.issues
        if i.category == "contradiction-hint" and i.page == "index.md"
    ]
    assert not index_hints


def test_parse_frontmatter():
    text = """---
type: entity
created: 2026-07-03
updated: 2026-07-03
tags: []
---

# Example
"""
    meta = parse_frontmatter(text)
    assert meta is not None
    assert meta["type"] == "entity"
    assert str(meta["created"]) == "2026-07-03"