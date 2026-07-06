from pathlib import Path

from llm_wiki.lint import lint_wiki


def _write_wiki(root: Path) -> None:
    (root / "wiki").mkdir(parents=True)
    (root / "raw").mkdir()
    (root / "wiki" / "index.md").write_text("# Index\n\n[[good-page]]")
    (root / "wiki" / "log.md").write_text("# Log\n")
    (root / "wiki" / "synthesis.md").write_text(
        "---\ntype: synthesis\nupdated: 2026-07-04\n---\n\n# Synthesis\n"
    )
    (root / "wiki" / "good-page.md").write_text(
        "---\ntype: concept\ncreated: 2026-07-04\nupdated: 2026-07-04\n---\n\n"
        "# Good\n\nSee [[missing-target]].\n"
    )


def test_lint_broken_link(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    _write_wiki(tmp_path)
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "broken-link" for i in report.errors)


def test_lint_raw_uningested(tmp_path: Path):
    _write_wiki(tmp_path)
    (tmp_path / "raw" / "orphan-raw.md").write_text("notes")
    report = lint_wiki(tmp_path / "wiki", project_root=tmp_path)
    assert any(i.category == "raw-uningested" for i in report.warnings)


def test_lint_broken_markdown_link(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    _write_wiki(tmp_path)
    (wiki_root / "good-page.md").write_text(
        (wiki_root / "good-page.md").read_text() + "\nSee [missing](concepts/nope.md).\n"
    )
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "broken-markdown-link" for i in report.warnings)


def test_lint_ambiguous_link(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    _write_wiki(tmp_path)
    (wiki_root / "entities").mkdir()
    (wiki_root / "concepts").mkdir()
    (wiki_root / "entities" / "hub.md").write_text(
        "---\ntype: entity\ncreated: 2026-07-04\nupdated: 2026-07-04\n---\n\n# Hub\n"
    )
    (wiki_root / "concepts" / "hub.md").write_text(
        "---\ntype: concept\ncreated: 2026-07-04\nupdated: 2026-07-04\n---\n\n# Hub\n"
    )
    (wiki_root / "index.md").write_text("# Index\n\n[[hub]]")
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "ambiguous-link" for i in report.warnings)


def test_lint_ambiguous_slug(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    _write_wiki(tmp_path)
    (wiki_root / "entities").mkdir()
    (wiki_root / "concepts").mkdir()
    (wiki_root / "entities" / "transformer.md").write_text(
        "---\ntype: entity\ncreated: 2026-07-04\nupdated: 2026-07-04\n---\n\n# T\n"
    )
    (wiki_root / "concepts" / "transformer.md").write_text(
        "---\ntype: concept\ncreated: 2026-07-04\nupdated: 2026-07-04\n---\n\n# T\n"
    )
    report = lint_wiki(wiki_root, project_root=tmp_path)
    assert any(i.category == "ambiguous-slug" for i in report.warnings)
