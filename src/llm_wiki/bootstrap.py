"""Scaffold a new LLM Wiki project from bundled templates."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import date
from importlib import resources
from pathlib import Path

SCAFFOLD_PACKAGE = "llm_wiki.scaffold"


@dataclass
class BootstrapResult:
    target: Path
    files_created: list[str]
    git_initialized: bool


def _scaffold_root() -> Path:
    try:
        packaged = Path(str(resources.files(SCAFFOLD_PACKAGE)))
        if packaged.is_dir() and any(packaged.iterdir()):
            return packaged
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass

    # Editable installs and local development
    local = Path(__file__).resolve().parent / "scaffold"
    if local.is_dir():
        return local

    raise FileNotFoundError(
        "Scaffold templates are missing from the installed package. "
        "Reinstall with: pip install --force-reinstall llm-wiki"
    )


def _iter_scaffold_files() -> list[tuple[Path, str]]:
    root = _scaffold_root()
    files: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            files.append((path, rel))
    return files


def _render_content(content: str, project_name: str, today: str) -> str:
    return (
        content.replace("{{date}}", today)
        .replace("{{project_name}}", project_name)
        .replace("Repository scaffold", f"Scaffolded {project_name}")
    )


def bootstrap_wiki(
    target: Path,
    *,
    project_name: str = "my-wiki",
    init_git: bool = False,
    force: bool = False,
) -> BootstrapResult:
    """Create a new wiki project at *target* from packaged scaffold files."""
    target = target.expanduser().resolve()

    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(
            f"{target} already exists and is not empty. Use --force to scaffold anyway."
        )

    target.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    created: list[str] = []

    for src_path, rel in _iter_scaffold_files():
        dest = target / rel
        if dest.exists() and not force:
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        content = src_path.read_text(encoding="utf-8")

        if rel == "wiki/log.md":
            content = _render_content(content, project_name, today)
            if f"## [{today}] init |" not in content:
                content = content.rstrip() + f"\n\n## [{today}] init | Scaffolded {project_name}\n"

        if rel.endswith(".md") and "{{date}}" in content:
            content = _render_content(content, project_name, today)

        dest.write_text(content, encoding="utf-8")
        created.append(rel)

    git_initialized = False
    if init_git and shutil.which("git"):
        if not (target / ".git").exists():
            subprocess.run(
                ["git", "init"],
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            )
            git_initialized = True

    return BootstrapResult(target=target, files_created=created, git_initialized=git_initialized)