"""Tests for the converter detection, manifest, and validation pipeline."""

from __future__ import annotations

import json
import tempfile
from unittest.mock import patch

import pytest

from clihub.converter.detector import (
    DetectedMetadata,
    _SEMVER_RE,
    detect_binary,
    detect_version,
    detect_help,
    detect_brew,
    detect_pip,
    detect_npm,
    guess_package_manager,
)
from clihub.converter.manifest import metadata_to_tool, tool_to_yaml, yaml_to_tool
from clihub.converter.validator import validate_tool
from clihub.registry.models import Tool


# ── Version regex ──

class TestSemverRegex:
    @pytest.mark.parametrize("text,expected", [
        ("jq-1.7.1", "1.7.1"),
        ("ripgrep 14.1.0", "14.1.0"),
        ("v2.3.4", "2.3.4"),
        ("tool version 0.9.12-beta", "0.9.12-beta"),
        ("3.0", "3.0"),
        ("name 1.2.3+build.456", "1.2.3+build.456"),
    ])
    def test_version_extraction(self, text, expected):
        m = _SEMVER_RE.search(text)
        assert m is not None
        assert m.group(1) == expected

    def test_no_version(self):
        assert _SEMVER_RE.search("no version here") is None


# ── Detectors with mocked subprocess ──

def _mock_run(stdout="", stderr="", returncode=0):
    """Create a mock subprocess.run result."""
    class FakeResult:
        def __init__(self):
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode
    return FakeResult()


class TestDetectBinary:
    def test_found(self):
        with patch("clihub.converter.detector.shutil.which", return_value="/usr/bin/jq"):
            meta = detect_binary("jq")
        assert meta.name == "jq"
        assert meta.binary_name == "jq"

    def test_not_found(self):
        with patch("clihub.converter.detector.shutil.which", return_value=None):
            meta = detect_binary("nonexistent")
        assert meta.name is None


class TestDetectVersion:
    def test_extracts_version(self):
        with patch("clihub.converter.detector._run_cmd", return_value="jq-1.7.1"):
            meta = detect_version("jq")
        assert meta.version == "1.7.1"

    def test_no_version(self):
        with patch("clihub.converter.detector._run_cmd", return_value=None):
            meta = detect_version("jq")
        assert meta.version is None


class TestDetectHelp:
    def test_extracts_description(self):
        help_text = "Usage: jq [OPTIONS]\nLightweight command-line JSON processor\n  -r  raw output"
        with patch("clihub.converter.detector._run_cmd", return_value=help_text):
            meta = detect_help("jq")
        assert meta.description == "Lightweight command-line JSON processor"
        assert meta.help_text == help_text

    def test_no_help(self):
        with patch("clihub.converter.detector._run_cmd", return_value=None):
            meta = detect_help("jq")
        assert meta.description is None


class TestDetectBrew:
    def test_parses_brew_json(self):
        brew_json = json.dumps({
            "formulae": [{
                "desc": "Lightweight JSON processor",
                "homepage": "https://jqlang.github.io/jq/",
                "license": "MIT",
                "versions": {"stable": "1.7.1"},
            }]
        })
        with patch("clihub.converter.detector.shutil.which", return_value="/usr/local/bin/brew"):
            with patch("clihub.converter.detector._run_cmd", return_value=brew_json):
                meta = detect_brew("jq")
        assert meta.description == "Lightweight JSON processor"
        assert meta.homepage == "https://jqlang.github.io/jq/"
        assert meta.license == "MIT"
        assert meta.version == "1.7.1"
        assert meta.install_method == "brew"

    def test_no_brew(self):
        with patch("clihub.converter.detector.shutil.which", return_value=None):
            meta = detect_brew("jq")
        assert meta.install_method is None


class TestDetectPip:
    def test_parses_pip_show(self):
        pip_out = (
            "Name: black\n"
            "Version: 24.3.0\n"
            "Summary: The uncompromising code formatter\n"
            "Author: Lukasz Langa\n"
            "License: MIT\n"
            "Home-page: https://github.com/psf/black\n"
        )
        with patch("clihub.converter.detector.shutil.which", return_value="/usr/bin/pip3"):
            with patch("clihub.converter.detector._run_cmd", return_value=pip_out):
                meta = detect_pip("black")
        assert meta.install_method == "pip"
        assert meta.description == "The uncompromising code formatter"
        assert meta.author == "Lukasz Langa"
        assert meta.version == "24.3.0"


class TestDetectNpm:
    def test_parses_npm_json(self):
        npm_json = json.dumps({
            "name": "prettier",
            "version": "3.2.5",
            "description": "Prettier is an opinionated code formatter",
            "homepage": "https://prettier.io",
            "license": "MIT",
            "author": {"name": "James Long"},
            "repository": {"type": "git", "url": "git+https://github.com/prettier/prettier.git"},
        })
        with patch("clihub.converter.detector.shutil.which", return_value="/usr/local/bin/npm"):
            with patch("clihub.converter.detector._run_cmd", return_value=npm_json):
                meta = detect_npm("prettier")
        assert meta.install_method == "npm"
        assert meta.description == "Prettier is an opinionated code formatter"
        assert meta.author == "James Long"
        assert meta.repository == "https://github.com/prettier/prettier"


class TestGuessPackageManager:
    def test_picks_first_hit(self):
        def fake_brew(pkg):
            return DetectedMetadata(install_method="brew", install_package=pkg)

        with patch("clihub.converter.detector.detect_brew", side_effect=fake_brew):
            meta = guess_package_manager("jq")
        assert meta.install_method == "brew"

    def test_falls_through(self):
        empty = DetectedMetadata()
        with patch("clihub.converter.detector.detect_brew", return_value=empty):
            with patch("clihub.converter.detector.detect_pip", return_value=empty):
                with patch("clihub.converter.detector.detect_npm", return_value=empty):
                    with patch("clihub.converter.detector.detect_cargo", return_value=empty):
                        meta = guess_package_manager("unknown")
        assert meta.install_method is None


# ── Manifest ──

class TestMetadataToTool:
    def test_fills_defaults(self):
        meta = DetectedMetadata(name="mytool", version="1.0.0", description="A tool")
        tool = metadata_to_tool(meta)
        assert tool.name == "mytool"
        assert tool.version == "1.0.0"
        assert tool.install.method == "brew"  # default
        assert tool.agent_hints is not None
        assert "TODO:" in tool.agent_hints.when_to_use

    def test_missing_version_gets_placeholder(self):
        meta = DetectedMetadata(name="mytool")
        tool = metadata_to_tool(meta)
        assert tool.version == "0.0.0"

    def test_binary_name_same_as_name_is_none(self):
        meta = DetectedMetadata(name="jq", binary_name="jq")
        tool = metadata_to_tool(meta)
        assert tool.install.binary_name is None


class TestYamlRoundtrip:
    def test_roundtrip(self):
        meta = DetectedMetadata(
            name="testtool",
            version="2.0.0",
            description="A test tool for testing",
            install_method="pip",
            install_package="testtool",
        )
        tool = metadata_to_tool(meta)
        yaml_str = tool_to_yaml(tool)

        # Write to temp file and read back
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            f.flush()
            restored = yaml_to_tool(f.name)

        assert restored.name == tool.name
        assert restored.version == tool.version
        assert restored.install.method == tool.install.method


# ── Validator ──

class TestValidator:
    def _make_valid_tool(self, **overrides) -> Tool:
        defaults = {
            "name": "my-new-tool",
            "version": "1.0.0",
            "description": "A perfectly valid tool for testing validation",
            "categories": ["utility"],
            "install": {"method": "pip", "package": "my-new-tool"},
            "agent_hints": {
                "when_to_use": "When you need to test things",
                "example_usage": ["my-new-tool --help"],
            },
        }
        defaults.update(overrides)
        return Tool.model_validate(defaults)

    def test_valid_tool_passes(self):
        tool = self._make_valid_tool()
        result = validate_tool(tool)
        assert result.valid is True
        assert result.errors == []

    def test_bad_name_format(self):
        tool = self._make_valid_tool(name="My Tool!")
        result = validate_tool(tool)
        assert not result.valid
        assert any("name" in e for e in result.errors)

    def test_short_description(self):
        tool = self._make_valid_tool(description="Short")
        result = validate_tool(tool)
        assert not result.valid
        assert any("description" in e for e in result.errors)

    def test_no_categories(self):
        tool = self._make_valid_tool(categories=[])
        result = validate_tool(tool)
        assert not result.valid
        assert any("category" in e for e in result.errors)

    def test_invalid_install_method(self):
        tool = self._make_valid_tool(install={"method": "apt", "package": "x"})
        result = validate_tool(tool)
        assert not result.valid
        assert any("install.method" in e for e in result.errors)

    def test_todo_in_description_is_error(self):
        tool = self._make_valid_tool(description="TODO: Add a description (10-200 chars)")
        result = validate_tool(tool)
        assert not result.valid

    def test_todo_in_agent_hints_is_warning(self):
        tool = self._make_valid_tool(
            agent_hints={
                "when_to_use": "TODO: Describe when an AI agent should use this tool",
                "example_usage": ["real-example --flag"],
            },
        )
        result = validate_tool(tool)
        assert result.valid  # warnings don't block
        assert len(result.warnings) > 0

    def test_duplicate_name_error(self):
        # "jq" is in the bundled registry
        tool = self._make_valid_tool(name="jq")
        result = validate_tool(tool)
        assert not result.valid
        assert any("already exists" in e for e in result.errors)
