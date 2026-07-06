def test_mcp_server_imports():
    import llm_wiki.mcp_server as mcp_server

    assert hasattr(mcp_server, "wiki_search")
    assert hasattr(mcp_server, "wiki_ingest_status")
    assert hasattr(mcp_server, "wiki_lint")


def test_mcp_expand_section(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    wiki = demo / "wiki"
    wiki.mkdir()
    (wiki / "index.md").write_text("# Index\n")
    synthesis_body = (
        "---\ntype: synthesis\nupdated: 2026-07-05\n---\n\n"
        "# Synthesis\n\n## Thesis\n\nHello [[world]].\n"
    )
    (wiki / "synthesis.md").write_text(synthesis_body)

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    payload = json.loads(mcp_server.wiki_expand("synthesis", section="Thesis"))
    assert payload["section"] == "Thesis"
    assert "Hello" in payload["content"]
    assert payload["outbound_links"] == ["world"]


def test_mcp_search_invalid_backend(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    (demo / "wiki").mkdir()
    (demo / "wiki" / "index.md").write_text("# Index")

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    payload = json.loads(mcp_server.wiki_search("query", backend="bogus"))
    assert "error" in payload


def test_mcp_lint_severity_filter(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    wiki = demo / "wiki"
    wiki.mkdir()
    (wiki / "index.md").write_text("# Index\n\n[[missing]]")
    (wiki / "log.md").write_text("# Log")
    (wiki / "synthesis.md").write_text("# Synthesis")

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    payload = json.loads(mcp_server.wiki_lint(severity="error"))
    assert any(item["category"] == "broken-link" for item in payload)


def test_mcp_backlinks_and_graph(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    wiki = demo / "wiki"
    wiki.mkdir()
    (wiki / "index.md").write_text("# Index\n\n[[hub]]")
    (wiki / "log.md").write_text("# Log")
    (wiki / "synthesis.md").write_text("# Synthesis\n\nSee [[hub]].")
    (wiki / "hub.md").write_text("# Hub")

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    backlinks = json.loads(mcp_server.wiki_backlinks("hub"))
    assert "index.md" in backlinks["backlinks"]

    graph = json.loads(mcp_server.wiki_graph())
    assert graph["edges"]


def test_mcp_new_page(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    (demo / "templates").mkdir()
    (demo / "wiki").mkdir()
    (demo / "templates" / "entity.md").write_text("# {{title}}\n")
    (demo / "wiki" / "index.md").write_text("# Index")

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    payload = json.loads(mcp_server.wiki_new("entity", "acme-corp", title="Acme Corp"))
    assert payload["path"] == "entities/acme-corp.md"


def test_mcp_list_invalid_page_type(monkeypatch, tmp_path):
    import json

    import llm_wiki.mcp_server as mcp_server

    demo = tmp_path / "wiki-project"
    demo.mkdir()
    (demo / "AGENTS.md").write_text("# Agent")
    (demo / "wiki").mkdir()
    (demo / "wiki" / "index.md").write_text("# Index\n\n[[synthesis]]")
    (demo / "wiki" / "synthesis.md").write_text("# Synthesis")

    monkeypatch.setenv("LLM_WIKI_ROOT", str(demo))
    payload = json.loads(mcp_server.wiki_list("bogus"))
    assert "error" in payload
