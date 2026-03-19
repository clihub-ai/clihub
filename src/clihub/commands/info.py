import json as json_lib
import shutil
import subprocess

import click
from rich.syntax import Syntax

from clihub.registry.local import get_tool
from clihub.output import print_tool_detail, print_error, console, is_json, json_option


def _get_help_text(binary: str) -> str | None:
    """Run <binary> --help and return the output, or None."""
    try:
        result = subprocess.run(
            [binary, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return (result.stdout or result.stderr or "").strip() or None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


@click.command()
@click.argument("tool_name")
@json_option
@click.pass_context
def info(ctx: click.Context, tool_name: str) -> None:
    """Show detailed info about a tool.

    \b
    Returns metadata, install method, agent_hints (when_to_use,
    example commands), and --help output if the tool is installed.

    \b
    Agent usage:
      clihub info jq --json           # full detail + installed status + help_text

    \b
    Human usage:
      clihub info jq                  # rich panel with examples

    \b
    Exit codes: 0 = found, 2 = not found.
    """
    tool = get_tool(tool_name)
    if tool is None:
        print_error(f"Tool '{tool_name}' not found in registry.", ctx)
        ctx.exit(2)
        return

    binary = tool.install.binary_name or tool.name
    installed = shutil.which(binary) is not None
    help_text = _get_help_text(binary) if installed else None

    if is_json(ctx):
        data = tool.model_dump()
        data["installed"] = installed
        if help_text:
            data["help_text"] = help_text
        click.echo(json_lib.dumps(data, indent=2))
        return

    print_tool_detail(tool, ctx)

    if help_text:
        console.print()
        console.print(Syntax(help_text, "text", theme="monokai", word_wrap=True))
