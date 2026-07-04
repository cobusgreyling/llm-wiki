def test_mcp_server_imports():
    import llm_wiki.mcp_server as mcp_server

    assert hasattr(mcp_server, "wiki_search")
    assert hasattr(mcp_server, "wiki_ingest_status")
    assert hasattr(mcp_server, "wiki_lint")


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