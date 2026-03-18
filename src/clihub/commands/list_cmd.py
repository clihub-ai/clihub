import json as json_lib
import shutil

import click
from rich.tree import Tree

from clihub.registry.local import get_all_categories, get_tools_by_category, load_registry
from clihub.output import print_tools_table, console, is_json


@click.command("list")
@click.option("--category", "-c", default=None, help="Show tools in a category")
@click.option("--installed", is_flag=True, help="Show only installed tools")
@click.pass_context
def list_cmd(ctx: click.Context, category: str | None, installed: bool) -> None:
    """Browse categories and tools.

    \b
    Examples:
      clihub list
      clihub list --category data
      clihub list --installed
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

    # Default: show category tree
    categories = get_all_categories()
    if is_json(ctx):
        click.echo(json_lib.dumps(categories, indent=2))
        return

    tree = Tree("[bold green]CliHub Registry[/bold green]")
    for cat, count in categories.items():
        tree.add(f"[bold]{cat}[/bold] [dim]({count} tools)[/dim]")
    console.print(tree)
