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


def test_cli_init_check_fails_on_incomplete(tmp_path: Path):
    runner = CliRunner()
    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    (incomplete / "AGENTS.md").write_text("x")
    result = runner.invoke(main, ["--root", str(incomplete), "init-check"])
    assert result.exit_code != 0