"""Simple hybrid search over wiki markdown files."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .links import WikiPage, iter_wiki_pages

TOKEN_RE = re.compile(r"[a-z0-9]+")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

TITLE_BOOST = 3.0
HEADING_BOOST = 1.5


@dataclass
class SearchResult:
    page: WikiPage
    score: float
    snippet: str


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def extract_headings(text: str) -> list[str]:
    return HEADING_RE.findall(text)


def build_term_counts(text: str) -> tuple[Counter[str], int]:
    """Return boosted term counts and body length for BM25 scoring."""
    body_lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    body_terms = tokenize("\n".join(body_lines))
    counts = Counter(body_terms)
    body_len = len(body_terms)

    headings = extract_headings(text)
    if headings:
        for term in tokenize(headings[0]):
            counts[term] += TITLE_BOOST
        for heading in headings[1:]:
            for term in tokenize(heading):
                counts[term] += HEADING_BOOST

    return counts, body_len


def bm25_score(
    query_terms: list[str],
    doc_terms: Counter[str],
    doc_len: int,
    avg_dl: float,
    df: Counter[str],
    n_docs: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    score = 0.0
    for term in query_terms:
        if term not in doc_terms:
            continue
        tf = doc_terms[term]
        idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
        denom = tf + k1 * (1 - b + b * doc_len / avg_dl)
        score += idf * (tf * (k1 + 1)) / denom
    return score


def make_snippet(text: str, query_terms: list[str], width: int = 160) -> str:
    lower = text.lower()
    for term in query_terms:
        idx = lower.find(term)
        if idx >= 0:
            start = max(0, idx - width // 3)
            end = min(len(text), idx + width)
            snippet = text[start:end].replace("\n", " ")
            return snippet.strip()
    return text[:width].replace("\n", " ").strip()


def search_wiki(
    wiki_root: Path,
    query: str,
    limit: int = 10,
    include_index: bool = True,
) -> list[SearchResult]:
    query_terms = tokenize(query)
    if not query_terms:
        return []

    pages = iter_wiki_pages(wiki_root)
    if not include_index:
        pages = [p for p in pages if p.stem != "index"]

    corpus: list[tuple[WikiPage, Counter[str], int, str]] = []
    df: Counter[str] = Counter()

    for page in pages:
        text = page.path.read_text(encoding="utf-8", errors="replace")
        boosted_counts, body_len = build_term_counts(text)
        body_lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
        body_terms = tokenize("\n".join(body_lines))
        corpus.append((page, boosted_counts, body_len, text))
        for term in set(body_terms):
            df[term] += 1

    if not corpus:
        return []

    avg_dl = sum(item[2] for item in corpus) / len(corpus)
    n_docs = len(corpus)

    results: list[SearchResult] = []
    for page, counts, doc_len, text in corpus:
        score = bm25_score(query_terms, counts, doc_len, avg_dl, df, n_docs)
        if score > 0:
            results.append(
                SearchResult(page=page, score=score, snippet=make_snippet(text, query_terms))
            )

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]