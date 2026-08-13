"""Typed data contracts for package alternative recommendations."""

from pydantic import BaseModel, Field

from models.package import PackageEcosystem, PackageReference


class AlternativeCandidate(BaseModel):
    """One curated alternative eligible for AI comparison."""

    name: str
    ecosystem: PackageEcosystem
    description: str


class AlternativeRecommendation(BaseModel):
    """AI-generated reasoning for one catalog-approved alternative."""

    alternative_name: str
    rationale: str
    best_for: str
    tradeoffs: list[str] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)


class AlternativeRecommendationDecision(BaseModel):
    """Intermediate LLM output before catalog validation."""

    recommendations: list[AlternativeRecommendation] = Field(default_factory=list)


class AlternativeRecommendationSet(BaseModel):
    """Validated alternatives for one analyzed package."""

    source_package: PackageReference
    recommendations: list[AlternativeRecommendation] = Field(default_factory=list)
    catalog_note: str