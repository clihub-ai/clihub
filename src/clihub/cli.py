import click

from clihub import __version__


@click.group()
@click.version_option(version=__version__, prog_name="clihub")
@click.option("--json", "json_output", is_flag=True, help="Structured JSON output (for AI agents)")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, quiet: bool) -> None:
    """CliHub — The App Store for AI Agents.

    \b
    Discover, install, and manage CLI tools.
    Pass --json to any command for structured output.

    \b
    Agent best practice (2 steps):
      1. clihub list --json          # get full tool catalog, pick the right tool
      2. clihub install <tool>       # install it

    \b
    Human quick start:
      clihub search "resize images"
      clihub install jq
      clihub info ripgrep

    \b
    https://clihub.net
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["quiet"] = quiet


# Register subcommands
from clihub.commands.search import search  # noqa: E402
from clihub.commands.install import install  # noqa: E402
from clihub.commands.info import info  # noqa: E402
from clihub.commands.list_cmd import list_cmd  # noqa: E402
from clihub.commands.doctor import doctor  # noqa: E402
from clihub.commands.convert import convert  # noqa: E402
from clihub.commands.submit import submit  # noqa: E402

cli.add_command(search)
cli.add_command(install)
cli.add_command(info)
cli.add_command(list_cmd)
cli.add_command(doctor)
cli.add_command(convert)
cli.add_command(submit)
