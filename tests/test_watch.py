from pathlib import Path

from llm_wiki.watch import watch_raw


def test_watch_once_reports_pending(tmp_path: Path, capsys):
    (tmp_path / "raw").mkdir()
    (tmp_path / "wiki").mkdir()
    (tmp_path / "raw" / "pending.md").write_text("content")

    watch_raw(tmp_path, once=True)
    output = capsys.readouterr().out
    assert "pending ingest" in output
    assert "pending.md" in output
