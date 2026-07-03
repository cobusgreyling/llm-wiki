from pathlib import Path

from llm_wiki.links import (
    build_slug_index,
    extract_wikilinks,
    iter_wiki_pages,
    resolve_link,
    resolve_page,
)


def test_extract_wikilinks():
    text = "See [[entities/foo]] and [[concepts/bar|Bar concept]] for details."
    assert extract_wikilinks(text) == {"entities/foo", "concepts/bar"}


def test_resolve_link_by_slug():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    pages = iter_wiki_pages(demo_wiki)
    slug_index = build_slug_index(pages)

    resolved = resolve_link("andrej-karpathy", slug_index)
    assert resolved is not None
    assert resolved.rel_path == "entities/andrej-karpathy.md"


def test_resolve_page_by_stem():
    demo_wiki = Path(__file__).resolve().parents[1] / "examples" / "demo" / "wiki"
    resolved = resolve_page(demo_wiki, "andrej-karpathy")
    assert resolved is not None
    assert resolved.rel_path == "entities/andrej-karpathy.md"