from pathlib import Path

from click.testing import CliRunner

from llm_wiki.cli import main


def _demo_root() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "demo"


def test_cli_search_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--root", str(_demo_root()), "search", "memex", "--json"])
    assert result.exit_code == 0
    assert "memex" in result.output.lower() or "snippet" in result.output


def test_cli_lint_exits_zero_on_clean_demo():
    runner = CliRunner()
    result = runner.invoke(main, ["--root", str(_demo_root()), "lint", "--fail-on", "error"])
    assert result.exit_code == 0


def test_cli_ingest_status():
    runner = CliRunner()
    result = runner.invoke(main, ["--root", str(_demo_root()), "ingest-status"])
    assert result.exit_code == 0
    assert "ingested" in result.output


def test_cli_expand_section():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--root", str(_demo_root()), "expand", "synthesis", "--section", "Thesis"],
    )
    assert result.exit_code == 0
    assert "compounding" in result.output.lower()


def test_cli_expand_section_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--root",
            str(_demo_root()),
            "expand",
            "synthesis",
            "--section",
            "Thesis",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert '"section"' in result.output
    assert "compounding markdown wiki" in result.output


def test_cli_backlinks_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--root", str(_demo_root()), "backlinks", "synthesis", "--json"],
    )
    assert result.exit_code == 0
    assert "backlinks" in result.output


def test_cli_graph_json():
    runner = CliRunner()
    result = runner.invoke(main, ["--root", str(_demo_root()), "graph", "--json"])
    assert result.exit_code == 0
    assert '"nodes"' in result.output
    assert '"edges"' in result.output


def test_cli_lint_category_filter():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--root", str(_demo_root()), "lint", "--category", "broken-link", "--json"],
    )
    assert result.exit_code == 0


def test_cli_new_page(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Agent")
    (tmp_path / "templates").mkdir()
    (tmp_path / "wiki").mkdir()
    (tmp_path / "templates" / "concept.md").write_text("# {{title}}\n")
    (tmp_path / "wiki" / "index.md").write_text("# Index")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--root", str(tmp_path), "new", "--type", "concept", "--slug", "test-topic"],
    )
    assert result.exit_code == 0
    assert (tmp_path / "wiki" / "concepts" / "test-topic.md").exists()


def test_cli_init_check_fails_on_incomplete(tmp_path: Path):
    runner = CliRunner()
    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    (incomplete / "AGENTS.md").write_text("x")
    result = runner.invoke(main, ["--root", str(incomplete), "init-check"])
    assert result.exit_code != 0
