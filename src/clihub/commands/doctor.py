import json as json_lib
import platform
import shutil
import sys
from pathlib import Path

import click
from rich.table import Table

from clihub.output import console, is_json, json_option


CHECKS = [
    ("Python >= 3.10", lambda: sys.version_info >= (3, 10), f"Python {platform.python_version()}"),
    ("pip", lambda: shutil.which("pip") is not None or shutil.which("pip3") is not None, "pip"),
    ("npm", lambda: shutil.which("npm") is not None, "npm"),
    ("brew", lambda: shutil.which("brew") is not None, "brew"),
    ("cargo", lambda: shutil.which("cargo") is not None, "cargo"),
    ("docker", lambda: shutil.which("docker") is not None, "docker"),
    ("git", lambda: shutil.which("git") is not None, "git"),
    ("~/.clihub/", lambda: Path.home().joinpath(".clihub").exists(), "config dir"),
]


@click.command()
@json_option
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check system readiness and available package managers.

    \b
    Agent usage:
      clihub doctor --json            # returns [{check, ok, detail}, ...]

    \b
    Checks: Python, pip, npm, brew, cargo, docker, git, config dir.
    """
    results: list[dict] = []
    for label, check_fn, detail in CHECKS:
        ok = check_fn()
        results.append({"check": label, "ok": ok, "detail": detail})

    if is_json(ctx):
        click.echo(json_lib.dumps(results, indent=2))
        return

    table = Table(title="System Check", border_style="dim", show_header=True)
    table.add_column("Status", width=4)
    table.add_column("Check")
    table.add_column("Detail", style="dim")

    for r in results:
        icon = "[green]✓[/green]" if r["ok"] else "[red]✗[/red]"
        table.add_row(icon, r["check"], r["detail"])

    console.print(table)

    ok_count = sum(1 for r in results if r["ok"])
    console.print(f"\n[dim]{ok_count}/{len(results)} checks passed[/dim]")
