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
    extract_markdown_links,
    extract_wikilinks,
    inbound_links,
    is_ambiguous_link,
    iter_wiki_pages,
    resolve_link,
    resolve_page,
)
from .paths import raw_dir

CONTRADICTION_MARKERS = re.compile(
    r"(?i)\b(contradict(?:s|ed|ion)?|conflict(?:s|ed|ing)?|disagree(?:s|d)?|"
    r"supersede(?:s|d)?|outdated|stale|deprecated)\b"
)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
VALID_TYPES = {"entity", "concept", "source", "answer", "synthesis", "meta"}
FRONTMATTER_EXEMPT = {"index", "log"}
CONTRADICTION_LEDGER_EXEMPT = {"index", "log", "synthesis", "contradictions"}
CONTRADICTION_LEDGER_PREFIXES = ("sources/", "entities/", "answers/")


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


def filter_issues(
    issues: list[LintIssue],
    *,
    severity: str | None = None,
    category: str | None = None,
) -> list[LintIssue]:
    filtered = issues
    if severity and severity != "all":
        filtered = [i for i in filtered if i.severity == severity]
    if category:
        filtered = [i for i in filtered if i.category == category]
    return filtered


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


def _normalize_source_ref(ref: str) -> str:
    cleaned = ref.strip().lower().removesuffix(".md")
    if not cleaned.startswith("sources/"):
        cleaned = f"sources/{cleaned}"
    return cleaned


def lint_source_frontmatter(page: WikiPage, meta: dict | None, report: LintReport) -> None:
    if not page.rel_path.startswith("sources/"):
        return
    if meta is None or not meta.get("raw_file"):
        report.issues.append(
            LintIssue(
                "error",
                "source-missing-raw-file",
                page.rel_path,
                "Source page must include `raw_file` in YAML frontmatter",
            )
        )


def lint_frontmatter_source_refs(
    page: WikiPage,
    meta: dict | None,
    slug_index: dict[str, list[WikiPage]],
    report: LintReport,
) -> None:
    if meta is None:
        return
    refs = meta.get("sources")
    if refs is None:
        return
    if not isinstance(refs, list):
        report.issues.append(
            LintIssue(
                "warning",
                "invalid-source-ref",
                page.rel_path,
                "Frontmatter `sources` must be a YAML list of source page paths",
            )
        )
        return
    for ref in refs:
        if not isinstance(ref, str):
            report.issues.append(
                LintIssue(
                    "warning",
                    "invalid-source-ref",
                    page.rel_path,
                    f"Frontmatter `sources` entry must be a string, got {type(ref).__name__}",
                )
            )
            continue
        normalized = _normalize_source_ref(ref)
        if resolve_link(normalized, slug_index) is None:
            report.issues.append(
                LintIssue(
                    "warning",
                    "invalid-source-ref",
                    page.rel_path,
                    f"Frontmatter `sources` references missing page: {ref!r}",
                )
            )


def _page_in_contradictions_ledger(page: WikiPage, ledger_text: str) -> bool:
    lowered = ledger_text.lower()
    checks = {
        page.rel_path.lower(),
        page.rel_path.removesuffix(".md").lower(),
        page.stem.lower(),
        f"[[{page.stem}]]".lower(),
        f"[[{page.rel_path.removesuffix('.md')}]]".lower(),
    }
    return any(token in lowered for token in checks)


def lint_contradiction_ledger(
    page: WikiPage,
    prose: str,
    contradictions_text: str | None,
    report: LintReport,
) -> None:
    if contradictions_text is None:
        return
    if page.stem in CONTRADICTION_LEDGER_EXEMPT:
        return
    if not page.rel_path.startswith(CONTRADICTION_LEDGER_PREFIXES):
        return
    if not CONTRADICTION_MARKERS.search(prose):
        return
    if _page_in_contradictions_ledger(page, contradictions_text):
        return
    report.issues.append(
        LintIssue(
            "warning",
            "contradiction-unfiled",
            page.rel_path,
            "Contains contradiction/staleness language but is not referenced in contradictions.md",
        )
    )


def lint_markdown_links(page: WikiPage, text: str, wiki_root: Path, report: LintReport) -> None:
    for href in extract_markdown_links(text):
        if href.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = href.split("#", 1)[0].strip()
        if not target:
            continue
        if target.startswith("wiki/"):
            target = target.removeprefix("wiki/")
        resolved = resolve_page(wiki_root, target)
        if resolved is None:
            report.issues.append(
                LintIssue(
                    "warning",
                    "broken-markdown-link",
                    page.rel_path,
                    f"Unresolved markdown link: ({href})",
                )
            )


def lint_ambiguous_slugs(slug_index: dict[str, list[WikiPage]], report: LintReport) -> None:
    for slug, matches in slug_index.items():
        unique = {p.rel_path for p in matches}
        if len(unique) > 1:
            report.issues.append(
                LintIssue(
                    "warning",
                    "ambiguous-slug",
                    ", ".join(sorted(unique)),
                    f"Slug {slug!r} resolves to multiple pages — wikilinks may be ambiguous",
                )
            )


def lint_raw_source_coverage(
    wiki_root: Path,
    project_root: Path | None,
    report: LintReport,
) -> None:
    if project_root is None:
        return

    raw_root = raw_dir(project_root)
    if not raw_root.exists():
        return

    raw_files = {
        p.relative_to(raw_root).as_posix()
        for p in raw_root.rglob("*")
        if p.is_file() and p.name.lower() not in {".gitkeep", "readme.md"}
    }

    referenced_raw: set[str] = set()
    for page in iter_wiki_pages(wiki_root):
        if not page.rel_path.startswith("sources/"):
            continue
        text = page.path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        raw_file = meta.get("raw_file") if meta else None
        if raw_file:
            referenced_raw.add(str(raw_file))
            if str(raw_file) not in raw_files:
                report.issues.append(
                    LintIssue(
                        "warning",
                        "raw-missing",
                        page.rel_path,
                        f"Source references missing raw file: {raw_file}",
                    )
                )

    for raw_file in sorted(raw_files):
        if raw_file not in referenced_raw:
            report.issues.append(
                LintIssue(
                    "warning",
                    "raw-uningested",
                    f"raw/{raw_file}",
                    "Raw file has no matching source page (check raw_file frontmatter)",
                )
            )


def lint_wiki(wiki_root: Path, *, project_root: Path | None = None) -> LintReport:
    report = LintReport()
    pages = iter_wiki_pages(wiki_root)
    slug_index = build_slug_index(pages)
    inbound = inbound_links(pages)
    all_stems = {p.stem.lower() for p in pages}
    mentioned_terms: dict[str, set[str]] = {}

    lint_ambiguous_slugs(slug_index, report)

    contradictions_path = wiki_root / "contradictions.md"
    contradictions_text = (
        contradictions_path.read_text(encoding="utf-8", errors="replace")
        if contradictions_path.exists()
        else None
    )

    # Required files
    for required in ("index.md", "log.md", "synthesis.md"):
        if not (wiki_root / required).exists():
            report.issues.append(
                LintIssue("error", "structure", required, f"Missing required file: {required}")
            )

    for page in pages:
        text = page.path.read_text(encoding="utf-8", errors="replace")
        links = extract_wikilinks(text)

        meta = parse_frontmatter(text)
        lint_frontmatter(page, text, report)
        lint_source_frontmatter(page, meta, report)
        lint_frontmatter_source_refs(page, meta, slug_index, report)

        # Wikilink resolution
        for target in links:
            if is_ambiguous_link(target, slug_index):
                report.issues.append(
                    LintIssue(
                        "warning",
                        "ambiguous-link",
                        page.rel_path,
                        f"Ambiguous wikilink: [[{target}]] resolves to multiple pages",
                    )
                )
            elif resolve_link(target, slug_index) is None:
                report.issues.append(
                    LintIssue(
                        "error",
                        "broken-link",
                        page.rel_path,
                        f"Unresolved wikilink: [[{target}]]",
                    )
                )

        lint_markdown_links(page, text, wiki_root, report)

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

        # Concepts mentioned in prose but missing dedicated pages (heuristic, deduped)
        mentioned = re.findall(r"`([a-z][a-z0-9-]{2,})`", text.lower())
        for term in mentioned:
            if term in all_stems or term in ("raw", "wiki", "agents"):
                continue
            mentioned_terms.setdefault(term, set()).add(page.rel_path)

        prose = WIKILINK_RE.sub(" ", text)
        if (
            CONTRADICTION_MARKERS.search(prose)
            and page.stem not in ("contradictions", "index")
            and not page.rel_path.startswith(CONTRADICTION_LEDGER_PREFIXES)
        ):
            report.issues.append(
                LintIssue(
                    "info",
                    "contradiction-hint",
                    page.rel_path,
                    "Contains contradiction/staleness language — "
                    "verify contradictions.md is updated",
                )
            )
        lint_contradiction_ledger(page, prose, contradictions_text, report)

    for term, pages_with_term in sorted(mentioned_terms.items()):
        if len(pages_with_term) < 2:
            continue
        report.issues.append(
            LintIssue(
                "info",
                "missing-page",
                ", ".join(sorted(pages_with_term)),
                f"Term `{term}` appears on multiple pages but has no dedicated page",
            )
        )

    lint_raw_source_coverage(wiki_root, project_root, report)

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
