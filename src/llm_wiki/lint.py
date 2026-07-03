"""Health checks for a growing wiki."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .links import (
    WIKILINK_RE,
    WikiPage,
    build_slug_index,
    extract_wikilinks,
    inbound_links,
    iter_wiki_pages,
    resolve_link,
)

CONTRADICTION_MARKERS = re.compile(
    r"(?i)\b(contradict(?:s|ed|ion)?|conflict(?:s|ed|ing)?|disagree(?:s|d)?|"
    r"supersede(?:s|d)?|outdated|stale|deprecated)\b"
)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
VALID_TYPES = {"entity", "concept", "source", "answer", "synthesis", "meta"}
FRONTMATTER_EXEMPT = {"index", "log"}


@dataclass
class LintIssue:
    severity: str  # error | warning | info
    category: str
    page: str
    message: str


@dataclass
class LintReport:
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def infos(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "info"]


def parse_frontmatter(text: str) -> dict | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def lint_frontmatter(page: WikiPage, text: str, report: LintReport) -> None:
    if page.stem in FRONTMATTER_EXEMPT:
        return

    meta = parse_frontmatter(text)
    if meta is None:
        report.issues.append(
            LintIssue(
                "warning",
                "frontmatter",
                page.rel_path,
                "Missing or invalid YAML frontmatter",
            )
        )
        return

    page_type = meta.get("type")
    if not page_type:
        report.issues.append(
            LintIssue("warning", "frontmatter", page.rel_path, "Frontmatter missing `type` field")
        )
    elif page_type not in VALID_TYPES:
        report.issues.append(
            LintIssue(
                "warning",
                "frontmatter",
                page.rel_path,
                f"Unknown frontmatter type: {page_type!r}",
            )
        )

    if not meta.get("updated"):
        report.issues.append(
            LintIssue("warning", "frontmatter", page.rel_path, "Frontmatter missing `updated` date")
        )

    if page_type in {"entity", "concept", "source", "answer"} and not meta.get("created"):
        report.issues.append(
            LintIssue("warning", "frontmatter", page.rel_path, "Frontmatter missing `created` date")
        )


def lint_wiki(wiki_root: Path) -> LintReport:
    report = LintReport()
    pages = iter_wiki_pages(wiki_root)
    slug_index = build_slug_index(pages)
    inbound = inbound_links(pages)
    all_stems = {p.stem.lower() for p in pages}

    # Required files
    for required in ("index.md", "log.md", "synthesis.md"):
        if not (wiki_root / required).exists():
            report.issues.append(
                LintIssue("error", "structure", required, f"Missing required file: {required}")
            )

    for page in pages:
        text = page.path.read_text(encoding="utf-8", errors="replace")
        links = extract_wikilinks(text)

        lint_frontmatter(page, text, report)

        # Broken wikilinks
        for target in links:
            if resolve_link(target, slug_index) is None:
                report.issues.append(
                    LintIssue(
                        "error",
                        "broken-link",
                        page.rel_path,
                        f"Unresolved wikilink: [[{target}]]",
                    )
                )

        # Orphan pages (no inbound links), excluding index/log
        if page.stem not in ("index", "log") and not inbound.get(page.rel_path):
            report.issues.append(
                LintIssue(
                    "warning",
                    "orphan",
                    page.rel_path,
                    "No inbound wikilinks — page may be hard to discover",
                )
            )

        # Concepts mentioned in prose but missing dedicated pages (heuristic)
        mentioned = re.findall(r"`([a-z][a-z0-9-]{2,})`", text.lower())
        for term in mentioned:
            if term not in all_stems and term not in ("raw", "wiki", "agents"):
                report.issues.append(
                    LintIssue(
                        "info",
                        "missing-page",
                        page.rel_path,
                        f"Term `{term}` may deserve its own page",
                    )
                )

        # Stale / contradiction language without contradictions ledger update
        prose = WIKILINK_RE.sub(" ", text)
        if CONTRADICTION_MARKERS.search(prose) and page.stem not in ("contradictions", "index"):
            report.issues.append(
                LintIssue(
                    "info",
                    "contradiction-hint",
                    page.rel_path,
                    "Contains contradiction/staleness language — "
                    "verify contradictions.md is updated",
                )
            )

    # Index coverage: pages not listed in index.md
    index_path = wiki_root / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8", errors="replace").lower()
        for page in pages:
            if page.stem in ("index", "log"):
                continue
            if page.stem.lower() not in index_text and page.rel_path.lower() not in index_text:
                report.issues.append(
                    LintIssue(
                        "warning",
                        "index-gap",
                        page.rel_path,
                        "Page not referenced in index.md",
                    )
                )

    return report