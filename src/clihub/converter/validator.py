"""Validate a Tool manifest for submission to the CliHub registry."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from clihub.registry.local import get_tool
from clihub.registry.models import Tool

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_PACKAGE_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._@/\[\]-]*$")
_VALID_METHODS = {"pip", "npm", "brew", "cargo", "binary", "docker"}


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_tool(tool: Tool) -> ValidationResult:
    """Run all validation checks on a Tool and return the result."""
    result = ValidationResult()

    # Name format
    if not _NAME_RE.match(tool.name):
        result.errors.append(
            f"name '{tool.name}' must match ^[a-z0-9][a-z0-9_-]*$ (lowercase, hyphens, underscores)"
        )

    # Install method
    if tool.install.method not in _VALID_METHODS:
        result.errors.append(
            f"install.method '{tool.install.method}' must be one of: {', '.join(sorted(_VALID_METHODS))}"
        )

    # Package name format
    if not _PACKAGE_RE.match(tool.install.package):
        result.errors.append(
            f"install.package '{tool.install.package}' contains invalid characters"
        )

    # Binary name safety
    if tool.install.binary_name:
        if "/" in tool.install.binary_name or ".." in tool.install.binary_name:
            result.errors.append(
                f"install.binary_name '{tool.install.binary_name}' must not contain paths"
            )

    # Description length
    if len(tool.description) < 10:
        result.errors.append("description must be at least 10 characters")
    elif len(tool.description) > 200:
        result.errors.append("description must be 200 characters or fewer")

    # At least one category
    if not tool.categories:
        result.errors.append("at least one category is required")

    # TODO markers in required fields
    for fld, val in [("description", tool.description), ("name", tool.name)]:
        if "TODO:" in val:
            result.errors.append(f"{fld} still contains a TODO marker")

    # TODO markers in optional fields (warnings)
    if tool.agent_hints:
        if "TODO:" in tool.agent_hints.when_to_use:
            result.warnings.append("agent_hints.when_to_use still contains a TODO marker")
        if any("TODO:" in ex for ex in tool.agent_hints.example_usage):
            result.warnings.append("agent_hints.example_usage still contains a TODO marker")

    # Example usage check
    if tool.agent_hints and not tool.agent_hints.example_usage:
        result.warnings.append("agent_hints.example_usage is empty — add at least one example")

    # Duplicate check
    existing = get_tool(tool.name)
    if existing:
        result.errors.append(f"tool '{tool.name}' already exists in the local registry")

    if result.errors:
        result.valid = False

    return result
