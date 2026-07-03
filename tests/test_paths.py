from pathlib import Path

import pytest

from llm_wiki.paths import ROOT_ENV_VAR, find_root


def test_find_root_via_env_var(monkeypatch):
    demo_root = Path(__file__).resolve().parents[1] / "examples" / "demo"
    monkeypatch.setenv(ROOT_ENV_VAR, str(demo_root))
    assert find_root() == demo_root.resolve()


def test_find_root_invalid_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv(ROOT_ENV_VAR, str(tmp_path))
    with pytest.raises(FileNotFoundError, match=ROOT_ENV_VAR):
        find_root()