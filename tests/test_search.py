from pathlib import Path

from llm_wiki.search import build_term_counts, search_wiki, tokenize


def test_search_demo_wiki():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    results = search_wiki(demo_wiki, "memex", limit=5)
    assert results
    assert any("memex" in r.page.stem for r in results)


def test_search_empty_query():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    assert search_wiki(demo_wiki, "   ", limit=5) == []


def test_title_boost_ranks_heading_match_higher():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    results = search_wiki(demo_wiki, "wiki lint", limit=5)
    assert results
    assert results[0].page.rel_path == "concepts/wiki-lint.md"


def test_build_term_counts_boosts_title_terms():
    text = "# Transformer Architecture\n\nBody mentions transformers once."
    counts, body_len = build_term_counts(text)
    assert body_len == len(tokenize("Body mentions transformers once."))
    assert counts["transformer"] > counts["mentions"]
