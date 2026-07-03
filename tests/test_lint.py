from pathlib import Path

from llm_wiki.lint import lint_wiki


def test_lint_demo_wiki_no_errors():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    report = lint_wiki(demo_wiki)
    assert not report.errors