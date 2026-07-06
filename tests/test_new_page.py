from pathlib import Path

import pytest

from llm_wiki.new_page import create_page


def test_create_concept_page(tmp_path: Path):
    (tmp_path / "templates").mkdir()
    (tmp_path / "wiki").mkdir()
    (tmp_path / "templates" / "concept.md").write_text(
        "---\ntype: concept\ncreated: {{date}}\nupdated: {{date}}\n---\n\n# {{title}}\n"
    )

    result = create_page(tmp_path, page_type="concept", slug="Memex Idea", title="Memex")
    assert result.rel_path == "concepts/memex-idea.md"
    content = result.path.read_text()
    assert "# Memex" in content
    assert "type: concept" in content


def test_create_page_refuses_existing(tmp_path: Path):
    (tmp_path / "templates").mkdir()
    wiki = tmp_path / "wiki" / "entities"
    wiki.mkdir(parents=True)
    (tmp_path / "templates" / "entity.md").write_text("# {{title}}\n")
    (wiki / "acme.md").write_text("# Acme")

    with pytest.raises(FileExistsError):
        create_page(tmp_path, page_type="entity", slug="acme")
