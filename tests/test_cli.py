"""CLI integration tests — exercises all 7 commands via Click's CliRunner."""

import json
import os
import tempfile
from unittest.mock import patch

from click.testing import CliRunner

from clihub.cli import cli


runner = CliRunner(mix_stderr=False)


def invoke(*args, json_mode=False):
    """Helper: invoke CLI with optional --json flag."""
    cmd = list(args)
    if json_mode:
        cmd = ["--json"] + cmd
    return runner.invoke(cli, cmd, catch_exceptions=False)


def invoke_json(*args):
    """Helper: invoke with --json and parse the output."""
    result = invoke(*args, json_mode=True)
    assert result.exit_code == 0, f"Non-zero exit: {result.output}\n{result.stderr}"
    return json.loads(result.output)


# ── clihub (root group) ──────────────────────────────────────────────


class TestRootGroup:
    def test_version(self):
        result = invoke("--version")
        assert result.exit_code == 0
        assert "clihub" in result.output

    def test_help(self):
        result = invoke("--help")
        assert result.exit_code == 0
        assert "search" in result.output
        assert "install" in result.output
        assert "--json" in result.output

    def test_unknown_command(self):
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0


# ── clihub search ────────────────────────────────────────────────────


class TestSearch:
    def test_search_human(self):
        result = invoke("search", "json")
        assert result.exit_code == 0
        assert "jq" in result.output

    def test_search_json(self):
        data = invoke_json("search", "json")
        assert isinstance(data, list)
        assert len(data) > 0
        names = [t["name"] for t in data]
        assert "jq" in names

    def test_search_with_category(self):
        data = invoke_json("search", "json", "--category", "data")
        names = [t["name"] for t in data]
        assert "jq" in names
        for t in data:
            assert "data" in [c.lower() for c in t["categories"]]

    def test_search_with_limit(self):
        data = invoke_json("search", "tool", "--limit", "3")
        assert len(data) <= 3

    def test_search_no_results(self):
        result = invoke("search", "zzzznonexistenttool999", json_mode=True)
        assert result.exit_code == 2
        assert result.output.strip() == "[]"

    def test_search_no_results_human(self):
        result = invoke("search", "zzzznonexistenttool999")
        assert result.exit_code == 2
        assert "No tools found" in result.stderr

    def test_search_json_via_subcommand_flag(self):
        """--json on the subcommand (not global) also works."""
        result = runner.invoke(cli, ["search", "jq", "--json"], catch_exceptions=False)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ── clihub list ──────────────────────────────────────────────────────


class TestList:
    def test_list_human(self):
        result = invoke("list")
        assert result.exit_code == 0
        assert "data" in result.output.lower()

    def test_list_json(self):
        data = invoke_json("list")
        assert isinstance(data, list)
        assert len(data) >= 100  # 104 tools in registry
        # Every tool has required fields
        for t in data:
            assert "name" in t
            assert "description" in t
            assert "install" in t
            assert "agent_hints" in t or t.get("agent_hints") is None

    def test_list_category(self):
        data = invoke_json("list", "--category", "data")
        assert len(data) > 0
        for t in data:
            assert "data" in [c.lower() for c in t["categories"]]

    def test_list_category_not_found(self):
        result = invoke("list", "--category", "zzzznonexistent")
        assert result.exit_code == 2

    def test_list_installed_json(self):
        """--installed should return a list (possibly empty)."""
        data = invoke_json("list", "--installed")
        assert isinstance(data, list)

    def test_list_json_structure(self):
        """Each tool in JSON output has agent_hints with when_to_use."""
        data = invoke_json("list")
        tools_with_hints = [t for t in data if t.get("agent_hints")]
        assert len(tools_with_hints) > 50  # most tools have hints
        for t in tools_with_hints:
            assert "when_to_use" in t["agent_hints"]


# ── clihub info ──────────────────────────────────────────────────────


class TestInfo:
    def test_info_human(self):
        result = invoke("info", "jq")
        assert result.exit_code == 0
        assert "jq" in result.output

    def test_info_json(self):
        data = invoke_json("info", "jq")
        assert data["name"] == "jq"
        assert "installed" in data
        assert isinstance(data["installed"], bool)
        assert "install" in data
        assert "description" in data

    def test_info_json_has_agent_hints(self):
        data = invoke_json("info", "jq")
        assert data["agent_hints"] is not None
        assert "when_to_use" in data["agent_hints"]
        assert "example_usage" in data["agent_hints"]

    def test_info_not_found(self):
        result = invoke("info", "zzzznonexistent", json_mode=True)
        assert result.exit_code == 2
        err = json.loads(result.stderr)
        assert err["status"] == "error"

    def test_info_not_found_human(self):
        result = invoke("info", "zzzznonexistent")
        assert result.exit_code == 2
        assert "not found" in result.stderr.lower()

    def test_info_case_insensitive(self):
        data = invoke_json("info", "JQ")
        assert data["name"] == "jq"


# ── clihub install ───────────────────────────────────────────────────


class TestInstall:
    def test_install_not_found(self):
        result = invoke("install", "zzzznonexistent", json_mode=True)
        assert result.exit_code == 2
        err = json.loads(result.stderr)
        assert err["status"] == "error"

    def test_install_not_found_human(self):
        result = invoke("install", "zzzznonexistent")
        assert result.exit_code == 2
        assert "not found" in result.stderr.lower()

    @patch("clihub.commands.install.resolve_installer")
    def test_install_already_installed(self, mock_resolve):
        """When the tool binary is already on PATH, skip install."""
        mock_installer = mock_resolve.return_value
        mock_installer.check_installed.return_value = True

        result = invoke("install", "jq", json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["already_installed"] is True
        assert data["status"] == "success"

    @patch("clihub.commands.install.resolve_installer")
    def test_install_success(self, mock_resolve):
        """Successful install returns status=success."""
        mock_installer = mock_resolve.return_value
        mock_installer.check_installed.return_value = False
        mock_installer.install.return_value = True
        mock_installer.name = "brew"

        result = invoke("install", "jq", json_mode=True)
        assert result.exit_code == 0
        # Output may contain Rich "Installing..." line before the JSON
        lines = result.output.strip().splitlines()
        json_line = next(line for line in lines if line.startswith("{"))
        data = json.loads(json_line)
        assert data["status"] == "success"
        assert "jq" in data["message"]

    @patch("clihub.commands.install.resolve_installer")
    def test_install_failure(self, mock_resolve):
        """Failed install returns exit code 1."""
        mock_installer = mock_resolve.return_value
        mock_installer.check_installed.return_value = False
        mock_installer.install.return_value = False
        mock_installer.name = "brew"

        result = invoke("install", "jq", json_mode=True)
        assert result.exit_code == 1
        err = json.loads(result.stderr)
        assert err["status"] == "error"

    @patch("clihub.commands.install.resolve_installer")
    def test_install_no_package_manager(self, mock_resolve):
        """RuntimeError from resolver → exit 1."""
        mock_resolve.side_effect = RuntimeError("No package manager available.")

        result = invoke("install", "jq", json_mode=True)
        assert result.exit_code == 1

    def test_install_via_invalid_method(self):
        """--via with an unknown method should be rejected by Click."""
        result = runner.invoke(cli, ["install", "jq", "--via", "apt"])
        assert result.exit_code != 0


# ── clihub doctor ────────────────────────────────────────────────────


class TestDoctor:
    def test_doctor_human(self):
        result = invoke("doctor")
        assert result.exit_code == 0
        assert "Python" in result.output

    def test_doctor_json(self):
        data = invoke_json("doctor")
        assert isinstance(data, list)
        assert len(data) == 8
        checks = [r["check"] for r in data]
        assert "Python >= 3.10" in checks
        assert "pip" in checks
        assert "git" in checks

    def test_doctor_json_structure(self):
        data = invoke_json("doctor")
        for r in data:
            assert "check" in r
            assert "ok" in r
            assert isinstance(r["ok"], bool)
            assert "detail" in r

    def test_doctor_python_ok(self):
        """Python >= 3.10 check should always pass in our test env."""
        data = invoke_json("doctor")
        python_check = next(r for r in data if r["check"] == "Python >= 3.10")
        assert python_check["ok"] is True


# ── clihub convert ───────────────────────────────────────────────────


class TestConvert:
    def test_convert_tool_not_on_path(self):
        result = invoke("convert", "zzzznonexistent", json_mode=True)
        assert result.exit_code == 1

    @patch("clihub.commands.convert.shutil.which", return_value="/usr/bin/python3")
    @patch("clihub.commands.convert.run_detection")
    def test_convert_json(self, mock_detect, mock_which):
        """--json mode returns tool JSON without writing a file."""
        from clihub.converter.detector import DetectedMetadata

        mock_detect.return_value = DetectedMetadata(
            name="testtool",
            version="1.0.0",
            description="A test tool",
            homepage=None,
            author=None,
            license=None,
            help_text="usage: testtool [options]",
            install_method="brew",
            install_package="testtool",
        )

        result = invoke("convert", "testtool", json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "testtool"
        assert data["version"] == "1.0.0"

    def test_convert_path_traversal(self):
        """Output path outside CWD should be rejected."""
        result = invoke("convert", "python3", "--output", "/tmp/evil.yaml")
        assert result.exit_code == 1

    @patch("clihub.commands.convert.shutil.which", return_value="/usr/bin/testtool")
    @patch("clihub.commands.convert.run_detection")
    def test_convert_writes_yaml(self, mock_detect, mock_which):
        """Human mode writes a YAML file."""
        from clihub.converter.detector import DetectedMetadata

        mock_detect.return_value = DetectedMetadata(
            name="testtool",
            version="2.0.0",
            description="Test",
            homepage=None,
            author=None,
            license=None,
            help_text=None,
            install_method=None,
            install_package=None,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "clihub.yaml")
            # Run from the temp dir so path validation passes
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = invoke("convert", "testtool", "--output", "clihub.yaml")
                assert result.exit_code == 0
                assert os.path.exists(outfile)
                with open(outfile) as f:
                    content = f.read()
                assert "testtool" in content
            finally:
                os.chdir(original_cwd)


# ── clihub submit ────────────────────────────────────────────────────


class TestSubmit:
    def _write_manifest(self, tmpdir, content):
        path = os.path.join(tmpdir, "clihub.yaml")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_submit_valid_manifest_json(self):
        manifest = """\
name: testcli
version: "1.0.0"
description: A test CLI tool for unit testing
categories: [utilities]
tags: [test]
install:
  method: pip
  package: testcli
agent_hints:
  when_to_use: When you need to test things
  example_usage:
    - testcli run
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_manifest(tmpdir, manifest)
            result = invoke("submit", path, json_mode=True)
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["valid"] is True
            assert data["errors"] == []
            assert "tool" in data
            assert data["tool"]["name"] == "testcli"

    def test_submit_invalid_manifest_json(self):
        manifest = """\
name: ""
version: "1.0.0"
description: ""
install:
  method: pip
  package: testcli
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_manifest(tmpdir, manifest)
            result = invoke("submit", path, json_mode=True)
            assert result.exit_code == 1
            data = json.loads(result.output)
            assert data["valid"] is False
            assert len(data["errors"]) > 0

    def test_submit_validate_only(self):
        manifest = """\
name: testcli
version: "1.0.0"
description: A test tool
categories: [utilities]
tags: [test]
install:
  method: pip
  package: testcli
agent_hints:
  when_to_use: When you need to test
  example_usage:
    - testcli run
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_manifest(tmpdir, manifest)
            result = invoke("submit", path, "--validate-only")
            assert result.exit_code == 0
            assert "Validated" in result.output

    def test_submit_file_not_found(self):
        result = runner.invoke(cli, ["submit", "/nonexistent/clihub.yaml"])
        assert result.exit_code != 0

    def test_submit_malformed_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_manifest(tmpdir, ": : invalid yaml [[[")
            result = invoke("submit", path, json_mode=True)
            assert result.exit_code == 1

    def test_submit_human_output(self):
        manifest = """\
name: testcli
version: "1.0.0"
description: A test tool for humans
categories: [utilities]
tags: [test]
install:
  method: pip
  package: testcli
agent_hints:
  when_to_use: When you need to test
  example_usage:
    - testcli run
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_manifest(tmpdir, manifest)
            result = invoke("submit", path)
            assert result.exit_code == 0
            assert "registry.json" in result.output


# ── output module ────────────────────────────────────────────────────


class TestOutput:
    def test_print_error_json(self):
        """Error in JSON mode goes to stderr as JSON."""
        result = invoke("info", "zzzznonexistent", json_mode=True)
        err = json.loads(result.stderr)
        assert err["status"] == "error"
        assert "not found" in err["message"].lower()

    def test_json_output_is_valid(self):
        """All JSON outputs must be parseable."""
        for cmd in [
            ["list", "--json"],
            ["search", "jq", "--json"],
            ["info", "jq", "--json"],
            ["doctor", "--json"],
        ]:
            result = runner.invoke(cli, cmd, catch_exceptions=False)
            assert result.exit_code == 0, f"Failed: {cmd}"
            json.loads(result.output)  # must not raise

    def test_exit_codes_consistency(self):
        """Exit code 2 for not-found across commands."""
        for cmd in [
            ["search", "zzzznonexistent", "--json"],
            ["info", "zzzznonexistent", "--json"],
            ["install", "zzzznonexistent", "--json"],
        ]:
            result = runner.invoke(cli, cmd, catch_exceptions=False)
            assert result.exit_code == 2, f"Expected exit 2 for {cmd}, got {result.exit_code}"
