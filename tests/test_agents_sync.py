from pathlib import Path


def test_scaffold_agents_matches_canonical():
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "AGENTS.md").read_text(encoding="utf-8")
    scaffold = (root / "src" / "llm_wiki" / "scaffold" / "AGENTS.md").read_text(encoding="utf-8")
    assert canonical == scaffold


def test_demo_agents_matches_canonical():
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "AGENTS.md").read_text(encoding="utf-8")
    demo = (root / "examples" / "demo" / "AGENTS.md").read_text(encoding="utf-8")
    assert canonical == demo
