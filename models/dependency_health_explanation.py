"""Typed Gemini output for Dependency Health Report explanations."""

from pydantic import BaseModel, Field


class DependencyHealthExplanation(BaseModel):
    """Developer-friendly explanation of a Dependency Health Report."""

    overall_summary: str
    health_highlights: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)