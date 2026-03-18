"""clihub convert — auto-generate a manifest from an installed CLI tool."""

from __future__ import annotations

import shutil

import click

from clihub.converter.detector import run_detection
from clihub.converter.manifest import metadata_to_tool, tool_to_yaml
from clihub.output import console, err_console, is_json, json_option, print_error


@click.command()
@click.argument("tool", required=True)
@click.option("--package", "-p", default=None, help="Package name if different from binary")
@click.option("--via", default=None, type=click.Choice(["pip", "npm", "brew", "cargo"]),
              help="Package manager to query")
@click.option("--output", "-o", default="clihub.yaml", help="Output file (default: clihub.yaml)")
@json_option
@click.pass_context
def convert(ctx: click.Context, tool: str, package: str | None, via: str | None,
            output: str) -> None:
    """Convert an existing CLI tool into a clihub.yaml manifest.

    \b
    Auto-detects metadata from package managers and --help output.
    Review the generated file, then submit with `clihub submit`.

    \b
    Agent usage:
      clihub convert jq --json           # get Tool JSON without writing a file

    \b
    Human usage:
      clihub convert jq                  # generates clihub.yaml
      clihub convert rg --package ripgrep --via brew
    """
    # Check if tool exists on PATH
    if not shutil.which(tool):
        print_error(f"'{tool}' not found on PATH. Install it first, or check the name.", ctx)
        ctx.exit(1)
        return

    meta = run_detection(tool, package=package, via=via)
    tool_model = metadata_to_tool(meta)

    if is_json(ctx):
        click.echo(tool_model.model_dump_json(indent=2))
        return

    # Write YAML file
    yaml_str = tool_to_yaml(tool_model)
    with open(output, "w", encoding="utf-8") as f:
        f.write(yaml_str)

    # Print summary
    console.print(f"\n[green]✓[/green] Generated [bold]{output}[/bold]\n")

    detected = []
    todos = []
    for label, value in [
        ("name", tool_model.name),
        ("version", tool_model.version),
        ("description", tool_model.description),
        ("author", tool_model.author),
        ("homepage", tool_model.homepage),
        ("license", tool_model.license),
        ("install.method", tool_model.install.method),
        ("install.package", tool_model.install.package),
    ]:
        if value and "TODO:" not in str(value) and value != "0.0.0":
            detected.append(label)
        else:
            todos.append(label)

    # Always flag agent_hints as TODO
    todos.append("agent_hints")
    todos.append("categories")
    todos.append("tags")

    console.print(f"  [green]Detected ({len(detected)}):[/green] {', '.join(detected)}")
    console.print(f"  [yellow]TODO ({len(todos)}):[/yellow] {', '.join(todos)}")
    console.print()
    err_console.print(f"  Next: edit {output}, then run [bold]clihub submit {output}[/bold]")
