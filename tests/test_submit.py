"""Tests for the submit command and YAML loading."""

from __future__ import annotations

import tempfile

import pytest
import yaml

from clihub.converter.manifest import yaml_to_tool
from clihub.converter.validator import validate_tool


def _write_yaml(data: dict) -> str:
    """Write a dict to a temp YAML file, return path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        return f.name


class TestYamlLoading:
    def test_valid_yaml(self):
        path = _write_yaml({
            "name": "test-submit-tool",
            "version": "1.0.0",
            "description": "A valid tool for submit testing",
            "install": {"method": "pip", "package": "test-submit-tool"},
        })
        tool = yaml_to_tool(path)
        assert tool.name == "test-submit-tool"

    def test_invalid_yaml_missing_fields(self):
        path = _write_yaml({"name": "bad"})
        with pytest.raises(Exception):
            yaml_to_tool(path)


class TestSubmitValidation:
    def test_full_valid_manifest(self):
        path = _write_yaml({
            "name": "submit-test-tool",
            "version": "1.0.0",
            "description": "A great tool for doing great things quickly",
            "categories": ["utility"],
            "tags": ["test"],
            "install": {"method": "pip", "package": "submit-test-tool"},
            "agent_hints": {
                "when_to_use": "When you need to do great things",
                "example_usage": ["submit-test-tool run"],
            },
        })
        tool = yaml_to_tool(path)
        result = validate_tool(tool)
        assert result.valid is True

    def test_manifest_with_errors(self):
        path = _write_yaml({
            "name": "BADNAME!",
            "version": "1.0.0",
            "description": "short",
            "install": {"method": "apt", "package": "x"},
        })
        tool = yaml_to_tool(path)
        result = validate_tool(tool)
        assert not result.valid
        assert len(result.errors) >= 3  # name, description, method, categories


class TestSubmitJsonOutput:
    def test_json_structure(self):
        """Verify the JSON output shape matches what submit --json would produce."""
        path = _write_yaml({
            "name": "json-test-tool",
            "version": "2.0.0",
            "description": "A perfectly valid tool with all fields",
            "categories": ["data"],
            "install": {"method": "brew", "package": "json-test-tool"},
            "agent_hints": {
                "when_to_use": "Process data",
                "example_usage": ["json-test-tool parse file.json"],
            },
        })
        tool = yaml_to_tool(path)
        result = validate_tool(tool)

        # Build the same JSON output as submit --json
        out = {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        if result.valid:
            out["tool"] = tool.model_dump()

        assert out["valid"] is True
        assert "tool" in out
        assert out["tool"]["name"] == "json-test-tool"
