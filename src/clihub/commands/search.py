import click

from clihub.registry.search import search_tools
from clihub.output import print_tools_table, console


@click.command()
@click.argument("query")
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--limit", "-l", default=10, help="Max results (default: 10)")
@click.pass_context
def search(ctx: click.Context, query: str, category: str | None, limit: int) -> None:
    """Search for CLI tools.

    \b
    Examples:
      clihub search "json processing"
      clihub search resize --category media
      clihub search pdf --limit 5
    """
    results = search_tools(query, category=category, limit=limit)

    if not results:
        console.print(f"[dim]No tools found for[/dim] [bold]{query}[/bold]")
        ctx.exit(2)
        return

    print_tools_table(results, ctx)
