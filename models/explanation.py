"""Typed output contract for AI-generated package explanations."""

from pydantic import BaseModel, Field


class PackageExplanation(BaseModel):
    """Grounded developer-friendly explanation of one package."""

    package_summary: str
    primary_capabilities: list[str] = Field(default_factory=list)
    dependency_overview: str
    maintenance_overview: str
    developer_guidance: list[str] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)