"""Tests for installer resolver."""

import pytest
from clihub.installer.resolver import resolve_installer, get_installer, INSTALLERS
from clihub.installer.pip import PipInstaller
from clihub.installer.brew import BrewInstaller
from clihub.registry.models import Tool, InstallMethod


def make_tool(method: str = "pip", package: str = "test") -> Tool:
    return Tool(
        name="test",
        version="1.0",
        description="test",
        install=InstallMethod(method=method, package=package),
    )


class TestGetInstaller:
    def test_known_methods(self):
        for method in ["pip", "npm", "brew", "cargo"]:
            installer = get_installer(method)
            assert installer.name == method

    def test_unknown_method(self):
        with pytest.raises(ValueError):
            get_installer("unknown")


class TestResolveInstaller:
    def test_pip_available(self):
        tool = make_tool(method="pip")
        installer = resolve_installer(tool)
        assert installer is not None

    def test_force_method(self):
        tool = make_tool(method="brew")
        installer = resolve_installer(tool, force_method="pip")
        assert installer.name == "pip"

    def test_force_unavailable_method(self):
        # This will fail if the method is actually available, but tests the error path
        tool = make_tool()
        with pytest.raises((ValueError, RuntimeError)):
            resolve_installer(tool, force_method="unknown")


class TestInstallerAvailability:
    def test_pip_is_available(self):
        installer = PipInstaller()
        assert installer.is_available() is True

    def test_check_installed(self):
        installer = PipInstaller()
        assert installer.check_installed("python3") is True
        assert installer.check_installed("nonexistent_binary_xyz") is False
