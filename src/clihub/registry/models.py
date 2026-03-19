from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator
from typing import Optional

_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._@/\[\]-]*$")


class InstallMethod(BaseModel):
    method: str = Field(description="pip | npm | brew | cargo | binary | docker")
    package: str = Field(description="Package name on the registry")
    binary_name: Optional[str] = Field(None, description="Binary name if different from package")

    @field_validator("package")
    @classmethod
    def validate_package(cls, v: str) -> str:
        if not _SAFE_NAME_RE.match(v):
            raise ValueError(f"package name '{v}' contains invalid characters")
        return v

    @field_validator("binary_name")
    @classmethod
    def validate_binary_name(cls, v: str | None) -> str | None:
        if v is not None:
            if "/" in v or "\\" in v or ".." in v:
                raise ValueError(f"binary_name '{v}' must not contain paths")
            if not re.match(r"^[a-zA-Z0-9._-]+$", v):
                raise ValueError(f"binary_name '{v}' contains invalid characters")
        return v
    binary_url: Optional[str] = Field(None, description="Direct download URL")
    alt_methods: list[str] = Field(
        default_factory=list,
        description="Alternative install methods, e.g. ['cargo', 'npm'] — use with --via",
    )


class AgentHints(BaseModel):
    when_to_use: str = Field(description="Natural language: when should an agent use this?")
    example_usage: list[str] = Field(default_factory=list, description="Example CLI commands")
    input_formats: list[str] = Field(default_factory=list)
    output_formats: list[str] = Field(default_factory=list)


class Tool(BaseModel):
    name: str
    version: str
    description: str
    long_description: Optional[str] = None
    author: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    install: InstallMethod
    permissions: list[str] = Field(default_factory=list)
    agent_hints: Optional[AgentHints] = None
    verified: bool = False
    downloads: int = 0
    rating: Optional[float] = None
