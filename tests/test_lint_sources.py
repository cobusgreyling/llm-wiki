from pathlib import Path

from llm_wiki.lint import lint_wiki


def _base_wiki(tmp_path: Path) -> Path:
    wiki_root = tmp_path / "wiki"
    (wiki_root / "sources").mkdir(parents=True)
    (tmp_path / "raw").mkdir()
    (wiki_root / "index.md").write_text("# Index\n")
    (wiki_root / "log.md").write_text("# Log\n")
    (wiki_root / "synthesis.md").write_text(
        "---\ntype: synthesis\nupdated: 2026-07-05\n---\n\n# Synthesis\n"
    )
    (wiki_root / "contradictions.md").write_text(
        "---\ntype: meta\nupdated: 2026-07-05\n---\n\n# Contradictions\n"
    )
    return wiki_root


def test_lint_source_missing_raw_file_is_error(tmp_path: Path):
    wiki_root = _base_wiki(tmp_path)
    (wiki_root / "sources" / "orphan.md").write_text(
        "---\ntype: source\ncreated: 2026-07-05\nupdated: 2026-07-05\n---\n\n# Orphan\n"
    )
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "source-missing-raw-file" for i in report.errors)


def test_lint_invalid_sources_frontmatter_ref(tmp_path: Path):
    wiki_root = _base_wiki(tmp_path)
    (wiki_root / "sources" / "good.md").write_text(
        "---\ntype: source\ncreated: 2026-07-05\nupdated: 2026-07-05\n"
        'raw_file: "good.md"\n---\n\n# Good\n'
    )
    (wiki_root / "concepts").mkdir(exist_ok=True)
    (wiki_root / "concepts" / "bad-ref.md").write_text(
        "---\ntype: concept\ncreated: 2026-07-05\nupdated: 2026-07-05\n"
        'sources: ["sources/missing-source"]\n---\n\n# Bad\n'
    )
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "invalid-source-ref" for i in report.warnings)


def test_lint_contradiction_unfiled_on_source_page(tmp_path: Path):
    wiki_root = _base_wiki(tmp_path)
    (wiki_root / "sources" / "conflict.md").write_text(
        "---\ntype: source\ncreated: 2026-07-05\nupdated: 2026-07-05\n"
        'raw_file: "conflict.md"\n---\n\n# Conflict\n\nThis claim contradicts the roadmap.\n'
    )
    (tmp_path / "raw" / "conflict.md").write_text("notes")
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "contradiction-unfiled" for i in report.warnings)
