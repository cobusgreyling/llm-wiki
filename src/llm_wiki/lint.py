"""Health checks for a growing wiki."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .links import (
    build_slug_index,
    extract_wikilinks,
    inbound_links,
    iter_wiki_pages,
    resolve_link,
)

CONTRADICTION_MARKERS = re.compile(
    r"(?i)(contradict|conflict|disagree|supersede|outdated|stale|deprecated)"
)


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
        if CONTRADICTION_MARKERS.search(text) and page.stem != "contradictions":
            report.issues.append(
                LintIssue(
                    "info",
                    "contradiction-hint",
                    page.rel_path,
                    "Contains contradiction/staleness language — verify contradictions.md is updated",
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