"""Extract sections from wiki pages for token-efficient agent reads."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .links import extract_wikilinks

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass
class SectionContent:
    heading: str
    level: int
    content: str
    outbound_links: list[str]


def list_headings(text: str) -> list[tuple[int, str]]:
    """Return (level, title) for each markdown heading."""
    headings: list[tuple[int, str]] = []
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip()))
    return headings


def _normalize_heading(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _match_heading(query: str, title: str) -> bool:
    normalized_query = _normalize_heading(query)
    normalized_title = _normalize_heading(title)
    if normalized_query == normalized_title:
        return True
    segments = re.split(r"[\s\-_/]+", normalized_title)
    if normalized_query in segments:
        return True
    return any(segment.startswith(normalized_query) for segment in segments)


def extract_section(text: str, section: str) -> SectionContent | None:
    """Return the body under the first heading that matches *section*."""
    lines = text.splitlines()
    start_idx: int | None = None
    level: int | None = None
    matched_heading: str | None = None

    for idx, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading_level = len(match.group(1))
        heading_title = match.group(2).strip()
        if _match_heading(section, heading_title):
            start_idx = idx
            level = heading_level
            matched_heading = heading_title
            break

    if start_idx is None or level is None or matched_heading is None:
        return None

    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        match = HEADING_RE.match(lines[idx])
        if match and len(match.group(1)) <= level:
            end_idx = idx
            break

    section_lines = lines[start_idx:end_idx]
    content = "\n".join(section_lines).strip()
    outbound = sorted(extract_wikilinks(content))
    return SectionContent(
        heading=matched_heading,
        level=level,
        content=content,
        outbound_links=outbound,
    )
