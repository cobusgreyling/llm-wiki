"""BM25 lexical search over wiki markdown files, with optional qmd backend."""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .links import WikiPage, iter_wiki_pages

TOKEN_RE = re.compile(r"[a-z0-9]+")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

TITLE_BOOST = 3.0
HEADING_BOOST = 1.5
VALID_BACKENDS = frozenset({"bm25", "qmd"})


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


def search_wiki_qmd(
    wiki_root: Path,
    query: str,
    limit: int = 10,
) -> list[SearchResult]:
    """Search via qmd CLI when installed and configured for the wiki directory."""
    if not shutil.which("qmd"):
        raise FileNotFoundError(
            "qmd not found. Install with: npm install -g @tobilu/qmd "
            "Then: qmd collection add <wiki-root> --name wiki"
        )

    project_root = wiki_root.parent
    proc = subprocess.run(
        [
            "qmd",
            "search",
            query,
            "--json",
            "--full-path",
            "-n",
            str(limit),
            "-c",
            "wiki",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(
            f"qmd search failed (exit {proc.returncode}). "
            f"Configure a collection first: qmd collection add {wiki_root} --name wiki. "
            f"Details: {stderr}"
        )

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"qmd returned non-JSON output: {proc.stdout[:200]}") from exc

    results: list[SearchResult] = []
    items = payload if isinstance(payload, list) else payload.get("results", [])
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        file_path = item.get("path") or item.get("file") or item.get("uri", "")
        path = Path(str(file_path))
        if not path.is_absolute():
            path = (project_root / path).resolve()
        try:
            page = WikiPage(
                path=path,
                rel_path=path.relative_to(wiki_root).as_posix(),
                stem=path.stem,
            )
        except ValueError:
            continue
        score = float(item.get("score", item.get("relevance", limit - idx)))
        snippet = str(item.get("snippet", item.get("content", "")))[:160]
        results.append(SearchResult(page=page, score=score, snippet=snippet))

    return results[:limit]


def search_wiki_with_backend(
    wiki_root: Path,
    query: str,
    *,
    limit: int = 10,
    backend: str = "bm25",
    include_index: bool = True,
) -> list[SearchResult]:
    if backend not in VALID_BACKENDS:
        valid = ", ".join(sorted(VALID_BACKENDS))
        raise ValueError(f"Unknown search backend: {backend!r}. Valid backends: {valid}")
    if backend == "bm25":
        return search_wiki(wiki_root, query, limit=limit, include_index=include_index)
    return search_wiki_qmd(wiki_root, query, limit=limit)
