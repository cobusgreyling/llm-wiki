from pathlib import Path

from llm_wiki.search import search_wiki


def test_search_demo_wiki():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    results = search_wiki(demo_wiki, "memex", limit=5)
    assert results
    assert any("memex" in r.page.stem for r in results)


def test_search_empty_query():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    assert search_wiki(demo_wiki, "   ", limit=5) == []