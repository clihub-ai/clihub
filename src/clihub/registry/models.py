from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class InstallMethod(BaseModel):
    method: str = Field(description="pip | npm | brew | cargo | binary | docker")
    package: str = Field(description="Package name on the registry")
    binary_name: Optional[str] = Field(None, description="Binary name if different from package")
    binary_url: Optional[str] = Field(None, description="Direct download URL")


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
