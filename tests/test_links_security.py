from pathlib import Path

from llm_wiki.links import (
    build_slug_index,
    export_graph,
    get_backlinks,
    is_ambiguous_link,
    iter_wiki_pages,
    resolve_link,
    resolve_page,
)


def test_resolve_page_rejects_path_traversal(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    wiki_root.mkdir()
    (wiki_root / "safe.md").write_text("# Safe")

    secret = tmp_path / "secret.md"
    secret.write_text("# Secret")

    assert resolve_page(wiki_root, "../secret") is None
    assert resolve_page(wiki_root, "../secret.md") is None


def test_resolve_link_returns_none_for_ambiguous_slug(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    entities = wiki_root / "entities"
    concepts = wiki_root / "concepts"
    entities.mkdir(parents=True)
    concepts.mkdir(parents=True)
    (entities / "foo.md").write_text("# Foo entity")
    (concepts / "foo.md").write_text("# Foo concept")

    pages = iter_wiki_pages(wiki_root)
    slug_index = build_slug_index(pages)
    assert is_ambiguous_link("foo", slug_index)
    assert resolve_link("foo", slug_index) is None


def test_get_backlinks_and_graph(tmp_path: Path):
    wiki_root = tmp_path / "wiki"
    entities = wiki_root / "entities"
    concepts = wiki_root / "concepts"
    entities.mkdir(parents=True)
    concepts.mkdir(parents=True)
    (entities / "alice.md").write_text("# Alice\n\nSee [[bob]].")
    (concepts / "bob.md").write_text("# Bob\n\nMentioned by [[alice]].")

    assert get_backlinks(wiki_root, "bob") == ["entities/alice.md"]

    graph = export_graph(wiki_root)
    assert len(graph["nodes"]) == 2
    assert any(
        e["from"] == "entities/alice.md" and e["to"] == "concepts/bob.md" for e in graph["edges"]
    )
