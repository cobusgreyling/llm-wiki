"""Scaffold new wiki pages from templates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

PAGE_TYPES = {
    "entity": ("entity.md", "entities"),
    "concept": ("concept.md", "concepts"),
    "source": ("source.md", "sources"),
    "answer": ("answer.md", "answers"),
}


@dataclass
class NewPageResult:
    rel_path: str
    path: Path
    created: bool


def _slugify(value: str) -> str:
    slug = value.strip().lower().replace(" ", "-")
    slug = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in slug)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def create_page(
    root: Path,
    *,
    page_type: str,
    slug: str,
    title: str | None = None,
    force: bool = False,
) -> NewPageResult:
    if page_type not in PAGE_TYPES:
        raise ValueError(f"Unknown page type: {page_type!r}")

    template_name, folder = PAGE_TYPES[page_type]
    normalized_slug = _slugify(slug)
    if not normalized_slug:
        raise ValueError("Slug must contain at least one alphanumeric character")

    templates_dir = root / "templates"
    template_path = templates_dir / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: templates/{template_name}")

    wiki_root = root / "wiki"
    dest = wiki_root / folder / f"{normalized_slug}.md"
    if dest.exists() and not force:
        raise FileExistsError(f"Page already exists: {dest.relative_to(root)}")

    today = date.today().isoformat()
    page_title = title or _title_from_slug(normalized_slug)
    content = template_path.read_text(encoding="utf-8")
    content = (
        content.replace("{{date}}", today)
        .replace("{{title}}", page_title)
        .replace("{{slug}}", normalized_slug)
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")

    return NewPageResult(
        rel_path=dest.relative_to(wiki_root).as_posix(),
        path=dest,
        created=True,
    )
