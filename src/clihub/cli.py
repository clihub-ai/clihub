import click

from clihub import __version__


@click.group()
@click.version_option(version=__version__, prog_name="clihub")
@click.option("--json", "json_output", is_flag=True, hidden=True, help="JSON output for agents")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, quiet: bool) -> None:
    """CliHub — The App Store for AI Agents.

    \b
    Discover, install, and manage CLI tools.
    The protocol is --help. That's it.

    \b
    Quick start:
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

cli.add_command(search)
cli.add_command(install)
cli.add_command(info)
cli.add_command(list_cmd)
cli.add_command(doctor)
