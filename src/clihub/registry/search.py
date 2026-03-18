"""Fuzzy + keyword search engine for the tool registry."""

from __future__ import annotations

from rapidfuzz import fuzz

from clihub.registry.models import Tool
from clihub.registry.local import load_registry


def search_tools(
    query: str,
    category: str | None = None,
    limit: int = 10,
) -> list[Tool]:
    """Search tools by fuzzy matching against name, description, tags, categories.

    Weights: name (3x), description (2x), tags (1.5x), categories (1x).
    """
    tools = load_registry()

    if category:
        cat_lower = category.lower()
        tools = [t for t in tools if cat_lower in [c.lower() for c in t.categories]]

    if not query.strip():
        return tools[:limit]

    scored: list[tuple[float, Tool]] = []
    query_lower = query.lower()

    for tool in tools:
        name_score = fuzz.partial_ratio(query_lower, tool.name.lower()) * 3.0
        desc_score = fuzz.partial_ratio(query_lower, tool.description.lower()) * 2.0

        tags_str = " ".join(tool.tags).lower()
        tags_score = fuzz.partial_ratio(query_lower, tags_str) * 1.5

        cats_str = " ".join(tool.categories).lower()
        cats_score = fuzz.partial_ratio(query_lower, cats_str) * 1.0

        # Bonus for exact name match
        if query_lower == tool.name.lower():
            name_score += 200

        # Bonus for name starts-with
        if tool.name.lower().startswith(query_lower):
            name_score += 100

        total = name_score + desc_score + tags_score + cats_score
        if total > 450:  # threshold to filter noise
            scored.append((total, tool))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [tool for _, tool in scored[:limit]]
