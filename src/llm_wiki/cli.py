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
from .bootstrap import bootstrap_wiki
from .expand import extract_section, list_headings
from .ingest import get_ingest_status
from .links import export_graph, get_backlinks, iter_wiki_pages, resolve_page
from .lint import filter_issues, lint_wiki
from .new_page import create_page
from .paths import find_root, wiki_dir
from .search import search_wiki_with_backend
from .stats import get_stats, parse_log
from .watch import watch_raw

console = Console()


def _root_option(func):
    return click.option(
        "--root",
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        default=None,
        help="Path to llm-wiki project root (auto-detected by default).",
    )(func)


def _get_root(ctx: click.Context) -> Path:
    root = ctx.obj.get("root")
    if root is not None:
        return root
    try:
        root = find_root()
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    ctx.obj["root"] = root
    return root


@click.group()
@click.version_option(__version__, prog_name="wiki")
@_root_option
@click.pass_context
def main(ctx: click.Context, root: Path | None) -> None:
    """LLM Wiki toolkit — search, lint, and inspect your compounding knowledge base."""
    ctx.ensure_object(dict)
    ctx.obj["root"] = root


@main.command()
@click.argument("target", type=click.Path(path_type=Path))
@click.option("--name", default="my-wiki", show_default=True, help="Project name for the log.")
@click.option("--git/--no-git", default=False, help="Initialize a git repository.")
@click.option("--force", is_flag=True, help="Overwrite existing scaffold files.")
def init(target: Path, name: str, git: bool, force: bool) -> None:
    """Scaffold a new LLM Wiki project from the bundled template."""
    try:
        result = bootstrap_wiki(target, project_name=name, init_git=git, force=force)
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[green]✓[/] Created wiki at [bold]{result.target}[/]")
    for rel in result.files_created:
        console.print(f"  [dim]{rel}[/]")
    if result.git_initialized:
        console.print("[green]✓[/] Initialized git repository")
    console.print(
        "\nNext steps:\n"
        f"  cd {result.target.name}\n"
        '  pip install "llm-wiki[mcp]"   # CLI + MCP server\n'
        f"  wiki --root . init-check\n"
        "  Open AGENTS.md in your agent and start ingesting."
    )


@main.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, show_default=True)
@click.option(
    "--backend",
    type=click.Choice(["bm25", "qmd"]),
    default="bm25",
    show_default=True,
    help="Search backend: built-in BM25 or external qmd (requires qmd collection).",
)
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, backend: str, as_json: bool) -> None:
    """Search wiki pages using BM25 ranking (or qmd when configured)."""
    root = _get_root(ctx)
    try:
        results = search_wiki_with_backend(wiki_dir(root), query, limit=limit, backend=backend)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

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
@click.option("--category", default=None, help="Filter by lint category (e.g. broken-link).")
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.option(
    "--fail-on",
    type=click.Choice(["error", "warning", "none"]),
    default="error",
    show_default=True,
    help="Exit with code 1 when issues at or above this severity are found.",
)
@click.pass_context
def lint(
    ctx: click.Context,
    severity: str,
    category: str | None,
    as_json: bool,
    fail_on: str,
) -> None:
    """Health-check the wiki for broken links, orphans, and index gaps."""
    root = _get_root(ctx)
    report = lint_wiki(wiki_dir(root), project_root=root)

    issues = filter_issues(report.issues, severity=severity, category=category)

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
    root = _get_root(ctx)
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
    root = _get_root(ctx)
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
    root = _get_root(ctx)
    entries = parse_log(wiki_dir(root) / "log.md", limit=limit)

    if not entries:
        console.print("[yellow]No log entries found.[/]")
        return

    for e in entries:
        console.print(f"[cyan]{e['date']}[/] [bold]{e['operation']}[/] — {e['detail']}")


@main.command()
@click.argument("page")
@click.option(
    "--section",
    "-s",
    default=None,
    help="Return only the body under this heading (case-insensitive partial match).",
)
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def expand(ctx: click.Context, page: str, section: str | None, as_json: bool) -> None:
    """Print a wiki page and its table of contents (for agent context windows)."""
    root = _get_root(ctx)
    wiki_root = wiki_dir(root)

    resolved = resolve_page(wiki_root, page)
    if not resolved:
        raise click.ClickException(f"Page not found: {page}")

    text = resolved.path.read_text(encoding="utf-8")
    heading_list = list_headings(text)

    if section:
        extracted = extract_section(text, section)
        if not extracted:
            available = ", ".join(title for _, title in heading_list) or "(no headings)"
            raise click.ClickException(
                f"Section not found: {section!r}. Available headings: {available}"
            )
        if as_json:
            payload = {
                "path": resolved.rel_path,
                "section": extracted.heading,
                "content": extracted.content,
                "outbound_links": extracted.outbound_links,
            }
            console.print_json(json.dumps(payload))
            return

        console.print(
            Panel.fit(
                f"[bold]{resolved.rel_path}[/] → [cyan]{extracted.heading}[/]",
                title="Wiki Section",
            )
        )
        if extracted.outbound_links:
            console.print("[bold]Outbound wikilinks[/]")
            for link in extracted.outbound_links:
                console.print(f"  [[{link}]]")
            console.print()
        console.print(extracted.content)
        return

    if as_json:
        payload = {
            "path": resolved.rel_path,
            "headings": [title for _, title in heading_list],
            "content": text,
        }
        console.print_json(json.dumps(payload))
        return

    console.print(Panel.fit(f"[bold]{resolved.rel_path}[/]", title="Wiki Page"))
    if heading_list:
        console.print("[bold]Table of contents[/]")
        for level, title in heading_list:
            indent = "  " * (level - 1)
            console.print(f"{indent}{'#' * level} {title}")
        console.print()
    console.print(text)


@main.command("ingest-status")
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def ingest_status(ctx: click.Context, as_json: bool) -> None:
    """List raw files and whether they have matching wiki source pages."""
    root = _get_root(ctx)
    statuses = get_ingest_status(root)

    if as_json:
        payload = [
            {
                "raw_file": s.raw_file,
                "source_page": s.source_page,
                "status": s.status,
            }
            for s in statuses
        ]
        console.print_json(json.dumps(payload))
        return

    if not statuses:
        console.print("[yellow]No raw files or source pages found.[/]")
        return

    table = Table(title="Ingest Status", show_header=True)
    table.add_column("Status")
    table.add_column("Raw file")
    table.add_column("Source page")

    color = {"ingested": "green", "pending": "yellow", "orphan": "red", "incomplete": "magenta"}
    for item in statuses:
        table.add_row(
            f"[{color[item.status]}]{item.status}[/]",
            item.raw_file,
            item.source_page or "—",
        )
    console.print(table)


@main.command()
@click.argument("page")
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def backlinks(ctx: click.Context, page: str, as_json: bool) -> None:
    """List pages that wikilink to the given page."""
    root = _get_root(ctx)
    wiki_root = wiki_dir(root)
    resolved = resolve_page(wiki_root, page)
    if not resolved:
        raise click.ClickException(f"Page not found: {page}")

    refs = get_backlinks(wiki_root, page)
    if as_json:
        payload = {"page": resolved.rel_path, "backlinks": refs}
        console.print_json(json.dumps(payload))
        return

    console.print(f"[bold]Backlinks to {resolved.rel_path}[/]")
    if not refs:
        console.print("[yellow]No inbound wikilinks.[/]")
        return
    for ref in refs:
        console.print(ref)


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON.")
@click.pass_context
def graph(ctx: click.Context, as_json: bool) -> None:
    """Export the wiki link graph as JSON nodes and edges."""
    root = _get_root(ctx)
    payload = export_graph(wiki_dir(root))
    if as_json:
        console.print_json(json.dumps(payload))
        return

    console.print(f"[bold]{len(payload['nodes'])}[/] pages, [bold]{len(payload['edges'])}[/] links")
    for edge in payload["edges"][:20]:
        console.print(f"  {edge['from']} → {edge['to']}")
    if len(payload["edges"]) > 20:
        console.print(f"  … and {len(payload['edges']) - 20} more (use --json)")


@main.command("new")
@click.option(
    "--type",
    "page_type",
    type=click.Choice(["entity", "concept", "source", "answer"]),
    required=True,
)
@click.option("--slug", required=True, help="Filename slug (e.g. transformer-architecture).")
@click.option("--title", default=None, help="Page title (defaults from slug).")
@click.option("--force", is_flag=True, help="Overwrite an existing page.")
@click.pass_context
def new_page(
    ctx: click.Context,
    page_type: str,
    slug: str,
    title: str | None,
    force: bool,
) -> None:
    """Create a new wiki page from templates/."""
    root = _get_root(ctx)
    try:
        result = create_page(
            root,
            page_type=page_type,
            slug=slug,
            title=title,
            force=force,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[green]✓[/] Created [bold]{result.rel_path}[/]")
    console.print("Next: update wiki/index.md and add wikilinks from related pages.")


@main.command()
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--once", is_flag=True, help="Check once and exit.")
@click.pass_context
def watch(ctx: click.Context, interval: float, once: bool) -> None:
    """Watch raw/ for new files that need ingest."""
    root = _get_root(ctx)
    console.print(f"[dim]Watching {root / 'raw'} for pending ingest…[/]")
    try:
        watch_raw(root, interval=interval, once=once, on_pending=lambda msg, _: console.print(msg))
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped watching.[/]")


@main.command("init-check")
@click.pass_context
def init_check(ctx: click.Context) -> None:
    """Verify project structure is ready for agent operations."""
    root = _get_root(ctx)
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
