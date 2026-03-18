"""Auto-detect the best installer for a tool."""

from __future__ import annotations

from clihub.installer.base import BaseInstaller
from clihub.installer.pip import PipInstaller
from clihub.installer.npm import NpmInstaller
from clihub.installer.brew import BrewInstaller
from clihub.installer.cargo import CargoInstaller
from clihub.registry.models import Tool

INSTALLERS: dict[str, type[BaseInstaller]] = {
    "pip": PipInstaller,
    "npm": NpmInstaller,
    "brew": BrewInstaller,
    "cargo": CargoInstaller,
}

FALLBACK_ORDER: list[type[BaseInstaller]] = [
    BrewInstaller,
    PipInstaller,
    NpmInstaller,
    CargoInstaller,
]


def get_installer(method: str) -> BaseInstaller:
    """Get an installer by method name."""
    cls = INSTALLERS.get(method)
    if cls is None:
        raise ValueError(f"Unknown install method: {method}")
    return cls()


def resolve_installer(tool: Tool, force_method: str | None = None) -> BaseInstaller:
    """Pick the best available installer for a tool."""
    if force_method:
        installer = get_installer(force_method)
        if not installer.is_available():
            raise RuntimeError(f"{force_method} is not available on this system.")
        return installer

    method = tool.install.method
    if method in INSTALLERS:
        installer = get_installer(method)
        if installer.is_available():
            return installer

    # Fallback: try each in order
    for cls in FALLBACK_ORDER:
        inst = cls()
        if inst.is_available():
            return inst

    raise RuntimeError("No package manager available. Run `clihub doctor` for details.")
