"""Tests for Pydantic data models."""

import pytest
from clihub.registry.models import Tool, InstallMethod, AgentHints


def make_tool(**overrides) -> Tool:
    defaults = {
        "name": "test-tool",
        "version": "1.0.0",
        "description": "A test tool",
        "install": {"method": "pip", "package": "test-tool"},
    }
    defaults.update(overrides)
    return Tool.model_validate(defaults)


class TestInstallMethod:
    def test_minimal(self):
        m = InstallMethod(method="pip", package="my-pkg")
        assert m.method == "pip"
        assert m.package == "my-pkg"
        assert m.binary_name is None

    def test_with_binary_name(self):
        m = InstallMethod(method="brew", package="git-delta", binary_name="delta")
        assert m.binary_name == "delta"


class TestAgentHints:
    def test_minimal(self):
        h = AgentHints(when_to_use="Parse JSON")
        assert h.when_to_use == "Parse JSON"
        assert h.example_usage == []

    def test_full(self):
        h = AgentHints(
            when_to_use="Parse JSON",
            example_usage=["jq . file.json"],
            input_formats=["json"],
            output_formats=["json", "text"],
        )
        assert len(h.example_usage) == 1


class TestTool:
    def test_minimal(self):
        t = make_tool()
        assert t.name == "test-tool"
        assert t.verified is False
        assert t.downloads == 0
        assert t.categories == []

    def test_full(self):
        t = make_tool(
            categories=["data"],
            tags=["json"],
            verified=True,
            downloads=1000,
            rating=4.5,
            agent_hints={
                "when_to_use": "test",
                "example_usage": ["cmd --help"],
            },
        )
        assert t.verified is True
        assert t.rating == 4.5
        assert t.agent_hints.when_to_use == "test"

    def test_json_roundtrip(self):
        t = make_tool(categories=["data"], rating=4.2)
        dumped = t.model_dump_json()
        restored = Tool.model_validate_json(dumped)
        assert restored.name == t.name
        assert restored.rating == t.rating

    def test_invalid_missing_required(self):
        with pytest.raises(Exception):
            Tool.model_validate({"name": "no-install"})
