from pathlib import Path

from llm_wiki.stats import get_stats, parse_log


def test_get_stats_demo():
    root = Path(__file__).resolve().parents[1] / "examples" / "demo"
    stats = get_stats(root)
    assert stats.total_pages >= 10
    assert stats.sources >= 2
    assert stats.raw_files >= 2
    assert stats.log_entries >= 3


def test_parse_log_order():
    log = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki" / "log.md"
    entries = parse_log(log, limit=2)
    assert len(entries) == 2
    assert entries[-1]["operation"] == "ingest"
    assert "qmd" in entries[-1]["detail"].lower()