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
    skip_parts = {"__pycache__"}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if skip_parts.intersection(path.parts) or path.suffix == ".pyc":
            continue
        rel = path.relative_to(root).as_posix()
        files.append((path, rel))
    return files


def _render_content(
    content: str,
    project_name: str,
    today: str,
    project_root: str,
) -> str:
    return (
        content.replace("{{date}}", today)
        .replace("{{project_name}}", project_name)
        .replace("{{project_root}}", project_root)
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
    project_root = str(target)
    created: list[str] = []

    for src_path, rel in _iter_scaffold_files():
        dest = target / rel
        if dest.exists() and not force:
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        content = src_path.read_text(encoding="utf-8")

        if "{{project_root}}" in content or "{{date}}" in content or "{{project_name}}" in content:
            content = _render_content(content, project_name, today, project_root)

        if rel == "wiki/log.md" and f"## [{today}] init |" not in content:
            content = content.rstrip() + f"\n\n## [{today}] init | Scaffolded {project_name}\n"

        dest.write_text(content, encoding="utf-8")
        created.append(rel)

    git_initialized = False
    if init_git:
        if not shutil.which("git"):
            pass
        elif not (target / ".git").exists():
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=target,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                git_initialized = True
            except subprocess.CalledProcessError:
                git_initialized = False

    return BootstrapResult(target=target, files_created=created, git_initialized=git_initialized)
