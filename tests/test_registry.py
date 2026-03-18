"""Tests for registry loading and querying."""

from clihub.registry.local import load_registry, get_tool, get_all_categories, get_tools_by_category


class TestLoadRegistry:
    def test_loads_tools(self):
        tools = load_registry()
        assert len(tools) > 0

    def test_all_tools_have_required_fields(self):
        for tool in load_registry():
            assert tool.name
            assert tool.version
            assert tool.description
            assert tool.install.method
            assert tool.install.package


class TestGetTool:
    def test_find_jq(self):
        tool = get_tool("jq")
        assert tool is not None
        assert tool.name == "jq"

    def test_case_insensitive(self):
        assert get_tool("JQ") is not None
        assert get_tool("Jq") is not None

    def test_not_found(self):
        assert get_tool("nonexistent-tool-xyz") is None


class TestCategories:
    def test_get_all_categories(self):
        cats = get_all_categories()
        assert len(cats) > 0
        assert "data" in cats
        assert cats["data"] > 0

    def test_get_tools_by_category(self):
        tools = get_tools_by_category("data")
        assert len(tools) > 0
        for t in tools:
            assert "data" in [c.lower() for c in t.categories]

    def test_category_case_insensitive(self):
        assert len(get_tools_by_category("Data")) > 0
        assert len(get_tools_by_category("DATA")) > 0

    def test_empty_category(self):
        assert get_tools_by_category("nonexistent") == []
