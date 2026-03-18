import click

from clihub.registry.search import search_tools
from clihub.output import print_tools_table, print_error, is_json, json_option


@click.command()
@click.argument("query")
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--limit", "-l", default=10, help="Max results (default: 10)")
@json_option
@click.pass_context
def search(ctx: click.Context, query: str, category: str | None, limit: int) -> None:
    """Search for CLI tools by keyword (fuzzy match).

    \b
    Note for agents: prefer 'clihub list --json' to get the full
    catalog and pick the right tool yourself. Fuzzy search may
    miss relevant results. Use search for quick keyword lookups.

    \b
    Examples:
      clihub search jq --json
      clihub search resize --category media
      clihub search pdf --limit 5
    """
    results = search_tools(query, category=category, limit=limit)

    if not results:
        if is_json(ctx):
            click.echo("[]")
        else:
            print_error(f"No tools found for '{query}'", ctx)
        ctx.exit(2)
        return

    print_tools_table(results, ctx)
