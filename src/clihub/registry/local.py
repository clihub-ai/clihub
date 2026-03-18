"""Load and query the bundled registry.json."""

from __future__ import annotations

import json
from importlib import resources
from functools import lru_cache

from clihub.registry.models import Tool


@lru_cache(maxsize=1)
def load_registry() -> list[Tool]:
    """Load all tools from the bundled registry.json."""
    data_files = resources.files("clihub") / "data" / "registry.json"
    raw = json.loads(data_files.read_text(encoding="utf-8"))
    return [Tool.model_validate(entry) for entry in raw]


def get_tool(name: str) -> Tool | None:
    """Look up a tool by exact name (case-insensitive)."""
    name_lower = name.lower()
    for tool in load_registry():
        if tool.name.lower() == name_lower:
            return tool
    return None


def get_all_categories() -> dict[str, int]:
    """Return a dict of category -> tool count."""
    counts: dict[str, int] = {}
    for tool in load_registry():
        for cat in tool.categories:
            counts[cat] = counts.get(cat, 0) + 1
    return dict(sorted(counts.items()))


def get_tools_by_category(category: str) -> list[Tool]:
    """Return tools matching a category (case-insensitive)."""
    cat_lower = category.lower()
    return [t for t in load_registry() if cat_lower in [c.lower() for c in t.categories]]
