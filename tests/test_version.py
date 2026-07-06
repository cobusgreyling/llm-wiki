from pathlib import Path

import tomllib

from llm_wiki import __version__  # noqa: I001


def test_version_matches_pyproject():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert __version__ == data["project"]["version"]
