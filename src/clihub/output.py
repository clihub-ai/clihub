"""Rich formatting helpers with JSON mode support."""

from __future__ import annotations

import json as json_lib
from functools import wraps

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from clihub.registry.models import Tool

console = Console()
err_console = Console(stderr=True)


def is_json(ctx: click.Context) -> bool:
    return ctx.obj.get("json", False)


def is_quiet(ctx: click.Context) -> bool:
    return ctx.obj.get("quiet", False)


def json_option(f):
    """Decorator that adds --json to a subcommand and merges with the global flag."""
    @click.option("--json", "json_output", is_flag=True, help="Structured JSON output (for AI agents)")
    @wraps(f)
    def wrapper(*args, json_output=False, **kwargs):
        ctx = click.get_current_context()
        if json_output:
            ctx.obj["json"] = True
        return f(*args, **kwargs)
    return wrapper


def print_tools_table(tools: list[Tool], ctx: click.Context) -> None:
    if is_json(ctx):
        click.echo(json_lib.dumps([t.model_dump() for t in tools], indent=2))
        return

    if not tools:
        console.print("[dim]No tools found.[/dim]")
        return

    table = Table(show_header=True, header_style="bold green", border_style="dim")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold")
    table.add_column("Description", max_width=50)
    table.add_column("Source", style="dim")
    table.add_column("Category", style="dim")

    for i, tool in enumerate(tools, 1):
        source = tool.source.github if tool.source and tool.source.github else "—"
        desc = tool.description[:50] + "…" if len(tool.description) > 50 else tool.description
        cats = ", ".join(tool.categories[:2]) if tool.categories else "—"
        table.add_row(str(i), tool.name, desc, source, cats)

    console.print(table)


def print_tool_detail(tool: Tool, ctx: click.Context) -> None:
    if is_json(ctx):
        click.echo(tool.model_dump_json(indent=2))
        return

    lines: list[str] = []
    lines.append(f"[bold]{tool.name}[/bold] [dim]v{tool.version}[/dim]")
    lines.append(f"[italic]{tool.description}[/italic]")
    lines.append("")

    if tool.author:
        lines.append(f"[dim]Author:[/dim]  {tool.author}")
    if tool.homepage:
        lines.append(f"[dim]Home:[/dim]    {tool.homepage}")
    if tool.license:
        lines.append(f"[dim]License:[/dim] {tool.license}")
    if tool.categories:
        lines.append(f"[dim]Tags:[/dim]    {', '.join(tool.categories + tool.tags)}")

    lines.append("")
    lines.append(f"[dim]Install:[/dim] [green]{tool.install.method} install {tool.install.package}[/green]")

    if tool.agent_hints:
        lines.append("")
        lines.append(f"[dim]When to use:[/dim] {tool.agent_hints.when_to_use}")
        if tool.agent_hints.example_usage:
            lines.append("[dim]Examples:[/dim]")
            for ex in tool.agent_hints.example_usage:
                lines.append(f"  [green]$[/green] {ex}")

    panel = Panel(
        Text.from_markup("\n".join(lines)),
        title=f"[green]{tool.name}[/green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def print_success(msg: str, ctx: click.Context) -> None:
    if is_json(ctx):
        click.echo(json_lib.dumps({"status": "success", "message": msg}))
        return
    console.print(f"[green]✓[/green] {msg}")


def print_error(msg: str, ctx: click.Context) -> None:
    if is_json(ctx):
        click.echo(json_lib.dumps({"status": "error", "message": msg}), err=True)
        return
    err_console.print(f"[red]✗[/red] {msg}")


def print_warning(msg: str, ctx: click.Context) -> None:
    if is_json(ctx):
        click.echo(json_lib.dumps({"status": "warning", "message": msg}), err=True)
        return
    err_console.print(f"[yellow]![/yellow] {msg}")
