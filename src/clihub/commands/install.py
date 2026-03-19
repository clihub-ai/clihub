import click

from clihub.registry.local import get_tool
from clihub.installer.resolver import resolve_installer
import json as json_lib

from clihub.output import print_success, print_error, console, is_json, json_option


@click.command()
@click.argument("tool_name")
@click.option("--via", default=None, type=click.Choice(["pip", "npm", "brew", "cargo"]),
              help="Force a specific package manager")
@json_option
@click.pass_context
def install(ctx: click.Context, tool_name: str, via: str | None) -> None:
    """Install a CLI tool by name.

    \b
    Looks up the tool in the registry, auto-detects the best
    package manager, and installs it. Use --via to override.
    Skips if already installed.

    \b
    Agent usage:
      clihub install jq --json        # returns {"status": "success", ...}
      clihub install httpie --via pip --json

    \b
    Exit codes: 0 = success/already installed, 1 = error, 2 = not found.
    """
    tool = get_tool(tool_name)
    if tool is None:
        print_error(f"Tool '{tool_name}' not found in registry.", ctx)
        ctx.exit(2)
        return

    try:
        installer = resolve_installer(tool, force_method=via)
    except (ValueError, RuntimeError) as e:
        print_error(str(e), ctx)
        ctx.exit(1)
        return

    binary = tool.install.binary_name or tool.name
    if installer.check_installed(binary):
        if is_json(ctx):
            click.echo(json_lib.dumps({
                "status": "success",
                "message": f"{tool.name} is already installed.",
                "already_installed": True,
            }))
        else:
            console.print(f"[green]✓[/green] {tool.name} is already installed.")
        return

    console.print(
        f"[dim]Installing[/dim] [bold]{tool.name}[/bold] "
        f"[dim]via {installer.name}...[/dim]"
    )

    success = installer.install(tool.install.package)
    if not success:
        print_error(f"Failed to install {tool.name} via {installer.name}.", ctx)
        ctx.exit(1)
        return

    print_success(f"Installed {tool.name}@{tool.version} via {installer.name}", ctx)

    if tool.agent_hints and tool.agent_hints.example_usage:
        console.print("\n[dim]Try it:[/dim]")
        for ex in tool.agent_hints.example_usage[:2]:
            console.print(f"  [green]$[/green] {ex}")
