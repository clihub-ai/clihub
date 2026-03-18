import shutil
import subprocess

import click
from rich.syntax import Syntax

from clihub.registry.local import get_tool
from clihub.output import print_tool_detail, print_error, console


@click.command()
@click.argument("tool_name")
@click.pass_context
def info(ctx: click.Context, tool_name: str) -> None:
    """Show detailed info about a tool.

    \b
    Examples:
      clihub info jq
      clihub info ripgrep
    """
    tool = get_tool(tool_name)
    if tool is None:
        print_error(f"Tool '{tool_name}' not found in registry.", ctx)
        ctx.exit(2)
        return

    print_tool_detail(tool, ctx)

    # If installed, show --help output
    binary = tool.install.binary_name or tool.name
    if shutil.which(binary):
        try:
            result = subprocess.run(
                [binary, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            help_text = result.stdout or result.stderr
            if help_text:
                console.print()
                console.print(Syntax(help_text.strip(), "text", theme="monokai", word_wrap=True))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
