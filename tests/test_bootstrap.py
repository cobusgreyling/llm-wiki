from pathlib import Path

import pytest

from llm_wiki.bootstrap import bootstrap_wiki


def test_bootstrap_creates_project_structure(tmp_path: Path):
    target = tmp_path / "new-wiki"
    result = bootstrap_wiki(target, project_name="test-wiki")

    assert result.target == target.resolve()
    assert (target / "AGENTS.md").exists()
    assert (target / "wiki" / "index.md").exists()
    assert (target / "wiki" / "log.md").exists()
    assert (target / "templates" / "entity.md").exists()
    assert (target / "raw" / "README.md").exists()
    assert (target / ".cursor" / "mcp.json").exists()
    assert (target / ".mcp.json").exists()
    assert (target / ".windsurf" / "mcp.json").exists()
    assert (target / ".opencode" / "mcp.json").exists()
    assert (target / "CLAUDE.md").exists()
    assert "Scaffolded test-wiki" in (target / "wiki" / "log.md").read_text()

    mcp_config = (target / ".cursor" / "mcp.json").read_text()
    assert str(target.resolve()) in mcp_config
    assert "{{project_root}}" not in mcp_config


def test_bootstrap_refuses_nonempty_dir_without_force(tmp_path: Path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "notes.txt").write_text("keep")

    with pytest.raises(FileExistsError):
        bootstrap_wiki(target)
