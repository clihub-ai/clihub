import json as json_lib
import shutil

import click
from rich.tree import Tree

from clihub.registry.local import get_all_categories, get_tools_by_category, load_registry
from clihub.output import print_tools_table, console, is_json, json_option


@click.command("list")
@click.option("--category", "-c", default=None, help="Show tools in a category")
@click.option("--installed", is_flag=True, help="Show only installed tools")
@json_option
@click.pass_context
def list_cmd(ctx: click.Context, category: str | None, installed: bool) -> None:
    """Browse the full tool catalog.

    \b
    This is the recommended discovery command for AI agents.
    Use --json to get the full catalog with descriptions and
    agent_hints, then pick the right tool for your task.

    \b
    Agent usage:
      clihub list --json                # full catalog (all tools + hints)
      clihub list --category data --json  # narrow by category
      clihub list --installed --json    # what's already on PATH

    \b
    Human usage:
      clihub list                       # show category tree
      clihub list --category media      # tools in a category
      clihub list --installed           # installed tools

    \b
    Exit codes: 0 = success, 2 = category not found.
    """
    if installed:
        tools = load_registry()
        installed_tools = [
            t for t in tools if shutil.which(t.install.binary_name or t.name)
        ]
        if is_json(ctx):
            click.echo(json_lib.dumps([t.model_dump() for t in installed_tools], indent=2))
            return
        if not installed_tools:
            console.print("[dim]No registry tools found on PATH.[/dim]")
            return
        console.print(f"[green]{len(installed_tools)}[/green] [dim]tools installed[/dim]\n")
        print_tools_table(installed_tools, ctx)
        return

    if category:
        tools = get_tools_by_category(category)
        if not tools:
            console.print(f"[dim]No tools found in category[/dim] [bold]{category}[/bold]")
            ctx.exit(2)
            return
        print_tools_table(tools, ctx)
        return

    # Default: JSON mode returns full catalog (agent workflow), human mode shows category tree
    if is_json(ctx):
        tools = load_registry()
        click.echo(json_lib.dumps([t.model_dump() for t in tools], indent=2))
        return

    categories = get_all_categories()
    tree = Tree("[bold green]CliHub Registry[/bold green]")
    for cat, count in categories.items():
        tree.add(f"[bold]{cat}[/bold] [dim]({count} tools)[/dim]")
    console.print(tree)
