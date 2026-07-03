"""CLI for llm-wiki operations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .links import iter_wiki_pages, resolve_page
from .lint import lint_wiki
from .paths import find_root, wiki_dir
from .search import search_wiki
from .stats import get_stats, parse_log

console = Console()


def _root_option(func):
    return click.option(
        "--root",
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        default=None,
        help="Path to llm-wiki project root (auto-detected by default).",
    )(func)


@click.group()
@click.version_option(__version__, prog_name="wiki")
@_root_option
@click.pass_context
def main(ctx: click.Context, root: Path | None) -> None:
    """LLM Wiki toolkit — search, lint, and inspect your compounding knowledge base."""
    ctx.ensure_object(dict)
    try:
        ctx.obj["root"] = root or find_root()
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


@main.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, as_json: bool) -> None:
    """Search wiki pages using BM25 ranking."""
    root: Path = ctx.obj["root"]
    results = search_wiki(wiki_dir(root), query, limit=limit)

    if as_json:
        payload = [
            {"path": r.page.rel_path, "score": round(r.score, 4), "snippet": r.snippet}
            for r in results
        ]
        console.print_json(json.dumps(payload))
        return

    if not results:
        console.print(f"[yellow]No results for:[/] {query}")
        return

    table = Table(title=f'Search: "{query}"', show_header=True)
    table.add_column("Score", justify="right", style="cyan")
    table.add_column("Page", style="bold")
    table.add_column("Snippet")

    for r in results:
        snippet = r.snippet
        if len(snippet) > 120:
            snippet = snippet[:120] + "…"
        table.add_row(f"{r.score:.2f}", r.page.rel_path, snippet)

    console.print(table)


@main.command()
@click.option("--severity", type=click.Choice(["all", "error", "warning", "info"]), default="all")
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.option(
    "--fail-on",
    type=click.Choice(["error", "warning", "none"]),
    default="error",
    show_default=True,
    help="Exit with code 1 when issues at or above this severity are found.",
)
@click.pass_context
def lint(ctx: click.Context, severity: str, as_json: bool, fail_on: str) -> None:
    """Health-check the wiki for broken links, orphans, and index gaps."""
    root: Path = ctx.obj["root"]
    report = lint_wiki(wiki_dir(root))

    issues = report.issues
    if severity != "all":
        issues = [i for i in issues if i.severity == severity]

    if as_json:
        payload = [
            {
                "severity": i.severity,
                "category": i.category,
                "page": i.page,
                "message": i.message,
            }
            for i in issues
        ]
        console.print_json(json.dumps(payload))
    elif not issues:
        console.print("[green]✓ Wiki looks healthy — no issues found.[/]")
    else:
        table = Table(title="Lint Report", show_header=True)
        table.add_column("Severity")
        table.add_column("Category")
        table.add_column("Page")
        table.add_column("Message")

        color = {"error": "red", "warning": "yellow", "info": "blue"}
        for issue in issues:
            table.add_row(
                f"[{color[issue.severity]}]{issue.severity}[/]",
                issue.category,
                issue.page,
                issue.message,
            )

        console.print(table)
        console.print(
            f"\n[bold]{len(report.errors)}[/] errors, "
            f"[bold]{len(report.warnings)}[/] warnings, "
            f"[bold]{len(report.infos)}[/] info"
        )

    if fail_on != "none":
        thresholds = {"error": 0, "warning": 1, "info": 2}
        severity_rank = {"error": 0, "warning": 1, "info": 2}
        cutoff = thresholds[fail_on]
        failing = [i for i in report.issues if severity_rank[i.severity] <= cutoff]
        if failing:
            sys.exit(1)


@main.command("list")
@click.option(
    "--type",
    "page_type",
    type=click.Choice(["entity", "concept", "source", "answer", "all"]),
    default="all",
    show_default=True,
)
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def list_pages(ctx: click.Context, page_type: str, as_json: bool) -> None:
    """List wiki pages (useful for agents exploring the catalog)."""
    root: Path = ctx.obj["root"]
    pages = iter_wiki_pages(wiki_dir(root))

    prefix_map = {
        "entity": "entities/",
        "concept": "concepts/",
        "source": "sources/",
        "answer": "answers/",
    }
    if page_type != "all":
        pages = [p for p in pages if p.rel_path.startswith(prefix_map[page_type])]

    if as_json:
        payload = [{"path": p.rel_path, "stem": p.stem} for p in pages]
        console.print_json(json.dumps(payload))
        return

    if not pages:
        console.print("[yellow]No pages found.[/]")
        return

    for page in pages:
        console.print(page.rel_path)


@main.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show wiki statistics."""
    root: Path = ctx.obj["root"]
    s = get_stats(root)

    table = Table(title="Wiki Stats", show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Total pages", str(s.total_pages))
    table.add_row("Entities", str(s.entities))
    table.add_row("Concepts", str(s.concepts))
    table.add_row("Sources", str(s.sources))
    table.add_row("Answers", str(s.answers))
    table.add_row("Raw files", str(s.raw_files))
    table.add_row("Log entries", str(s.log_entries))
    console.print(table)


@main.command("log")
@click.option("--limit", "-n", default=10, show_default=True)
@click.pass_context
def show_log(ctx: click.Context, limit: int) -> None:
    """Show recent log entries."""
    root: Path = ctx.obj["root"]
    entries = parse_log(wiki_dir(root) / "log.md", limit=limit)

    if not entries:
        console.print("[yellow]No log entries found.[/]")
        return

    for e in entries:
        console.print(f"[cyan]{e['date']}[/] [bold]{e['operation']}[/] — {e['detail']}")


@main.command()
@click.argument("page")
@click.pass_context
def expand(ctx: click.Context, page: str) -> None:
    """Print a wiki page and its table of contents (for agent context windows)."""
    root: Path = ctx.obj["root"]
    wiki_root = wiki_dir(root)

    resolved = resolve_page(wiki_root, page)
    if not resolved:
        raise click.ClickException(f"Page not found: {page}")

    text = resolved.path.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("#")]

    console.print(Panel.fit(f"[bold]{resolved.rel_path}[/]", title="Wiki Page"))
    if headings:
        console.print("[bold]Table of contents[/]")
        for h in headings:
            console.print(f"  {h}")
        console.print()
    console.print(text)


@main.command()
@click.pass_context
def init_check(ctx: click.Context) -> None:
    """Verify project structure is ready for agent operations."""
    root: Path = ctx.obj["root"]
    required = [
        root / "AGENTS.md",
        root / "wiki" / "index.md",
        root / "wiki" / "log.md",
        root / "wiki" / "synthesis.md",
        root / "raw",
        root / "templates",
    ]

    ok = True
    for path in required:
        exists = path.exists()
        mark = "[green]✓[/]" if exists else "[red]✗[/]"
        console.print(f"{mark} {path.relative_to(root)}")
        ok = ok and exists

    if ok:
        console.print(
            "\n[green]Project is ready. Open AGENTS.md in your agent and start ingesting.[/]"
        )
    else:
        raise click.ClickException("Project structure is incomplete.")


if __name__ == "__main__":
    main()