"""clihub submit — validate a manifest and generate a PR-ready registry entry."""

from __future__ import annotations

import json as json_lib

import click

from clihub.converter.manifest import yaml_to_tool
from clihub.converter.validator import validate_tool
from clihub.output import console, err_console, is_json, json_option, print_error


@click.command()
@click.argument("manifest", default="clihub.yaml", type=click.Path(exists=True))
@click.option("--validate-only", is_flag=True, help="Only validate, don't generate output")
@json_option
@click.pass_context
def submit(ctx: click.Context, manifest: str, validate_only: bool) -> None:
    """Validate a clihub.yaml and generate a PR-ready registry entry.

    \b
    Agent usage:
      clihub submit clihub.yaml --json    # validate + get JSON entry

    \b
    Human usage:
      clihub submit clihub.yaml           # validate + print PR instructions
      clihub submit --validate-only       # just check the manifest
    """
    # Load and parse YAML
    try:
        tool = yaml_to_tool(manifest)
    except Exception as e:
        print_error(f"Failed to parse {manifest}: {e}", ctx)
        ctx.exit(1)
        return

    # Validate
    result = validate_tool(tool)

    if is_json(ctx):
        out = {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        if result.valid:
            out["tool"] = tool.model_dump()
        click.echo(json_lib.dumps(out, indent=2))
        if not result.valid:
            ctx.exit(1)
        return

    # Print validation results
    if result.errors:
        err_console.print(f"\n[red]✗[/red] Validation failed ({len(result.errors)} errors)\n")
        for err in result.errors:
            err_console.print(f"  [red]•[/red] {err}")
        if result.warnings:
            err_console.print()
            for w in result.warnings:
                err_console.print(f"  [yellow]![/yellow] {w}")
        ctx.exit(1)
        return

    # Validation passed
    n_fields = len([v for v in tool.model_dump().values() if v is not None])
    console.print(
        f"\n[green]✓[/green] Validated {n_fields} fields"
        + (f" ({len(result.warnings)} warnings)" if result.warnings else "")
    )
    for w in result.warnings:
        console.print(f"  [yellow]![/yellow] {w}")

    if validate_only:
        return

    # Generate PR-ready JSON
    entry = tool.model_dump(exclude_none=True)
    # Remove fields not needed in registry.json
    for key in ("verified", "source"):
        entry.pop(key, None)

    json_str = json_lib.dumps(entry, indent=2)

    console.print("\n[bold]Add this to src/clihub/data/registry.json:[/bold]\n")
    console.print(json_str)
    console.print("\n[dim]Or submit a PR:[/dim]")
    console.print("  1. Fork github.com/ZiYang-xie/clihub")
    console.print("  2. Add the JSON above to src/clihub/data/registry.json")
    console.print(f"  3. PR title: \"Add {tool.name} to registry\"")
