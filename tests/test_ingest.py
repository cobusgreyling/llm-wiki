from pathlib import Path

from llm_wiki.ingest import get_ingest_status


def test_ingest_status_demo_all_ingested():
    root = Path(__file__).resolve().parents[1] / "examples" / "demo"
    statuses = get_ingest_status(root)
    pending = [s for s in statuses if s.status == "pending"]
    orphan = [s for s in statuses if s.status == "orphan"]
    assert not pending
    assert not orphan
    assert any(s.status == "ingested" for s in statuses)


def test_ingest_status_detects_incomplete_source(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Agent")
    (tmp_path / "raw").mkdir()
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "sources").mkdir()
    (tmp_path / "wiki" / "sources" / "no-raw.md").write_text(
        "---\ntype: source\ncreated: 2026-07-05\nupdated: 2026-07-05\n---\n\n# Source\n"
    )

    statuses = get_ingest_status(tmp_path)
    assert any(s.status == "incomplete" for s in statuses)


def test_ingest_status_detects_pending(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Agent")
    (tmp_path / "raw").mkdir()
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index")
    (tmp_path / "raw" / "new-paper.md").write_text("content")

    statuses = get_ingest_status(tmp_path)
    assert len(statuses) == 1
    assert statuses[0].status == "pending"
    assert statuses[0].raw_file == "new-paper.md"
