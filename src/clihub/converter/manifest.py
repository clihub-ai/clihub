"""Convert between DetectedMetadata, Tool models, and YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from clihub.converter.detector import DetectedMetadata
from clihub.registry.models import AgentHints, InstallMethod, Tool

_TODO_WHEN = "TODO: Describe when an AI agent should use this tool"
_TODO_EXAMPLE = "TODO: Add 2-3 example commands"


def metadata_to_tool(meta: DetectedMetadata) -> Tool:
    """Convert detected metadata into a Tool model with TODO placeholders for missing fields."""
    install = InstallMethod(
        method=meta.install_method or "brew",
        package=meta.install_package or meta.name or "unknown",
        binary_name=meta.binary_name if meta.binary_name != meta.name else None,
    )

    agent_hints = AgentHints(
        when_to_use=_TODO_WHEN,
        example_usage=[_TODO_EXAMPLE],
        input_formats=[],
        output_formats=[],
    )

    return Tool(
        name=meta.name or "unknown",
        version=meta.version or "0.0.0",
        description=meta.description or "TODO: Add a description (10-200 chars)",
        author=meta.author,
        homepage=meta.homepage,
        repository=meta.repository,
        license=meta.license,
        categories=[],
        tags=[],
        install=install,
        permissions=[],
        agent_hints=agent_hints,
    )


def tool_to_yaml(tool: Tool) -> str:
    """Serialize a Tool model to a YAML string with helpful comments."""
    data = tool.model_dump(exclude_none=True, exclude_defaults=False)

    # Remove fields that are always defaulted and not useful in a manifest
    for key in ("verified", "downloads", "rating", "long_description"):
        data.pop(key, None)

    raw = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Add TODO comments for placeholder fields
    lines = []
    for line in raw.splitlines():
        lines.append(line)
        if "TODO:" in line:
            lines.append("  # ^ Fill in this field before submitting")
    return "\n".join(lines) + "\n"


def yaml_to_tool(path: str | Path) -> Tool:
    """Load a YAML manifest file and validate it as a Tool."""
    text = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    return Tool.model_validate(data)
