"""Tests for fuzzy search engine."""

from clihub.registry.search import search_tools


class TestSearchTools:
    def test_exact_name(self):
        results = search_tools("jq")
        assert len(results) > 0
        assert results[0].name == "jq"

    def test_partial_match(self):
        results = search_tools("json")
        assert len(results) > 0
        names = [t.name for t in results]
        assert "jq" in names

    def test_description_match(self):
        results = search_tools("syntax highlighting")
        assert len(results) > 0
        names = [t.name for t in results]
        assert "bat" in names or "delta" in names

    def test_category_filter(self):
        results = search_tools("", category="media")
        assert len(results) > 0
        for t in results:
            assert "media" in [c.lower() for c in t.categories]

    def test_limit(self):
        results = search_tools("tool", limit=3)
        assert len(results) <= 3

    def test_no_results(self):
        results = search_tools("xyznonexistent123")
        assert len(results) == 0

    def test_empty_query_returns_tools(self):
        results = search_tools("", limit=5)
        assert len(results) == 5
