"""Typed data contracts for dependency health reporting."""

from enum import StrEnum

from pydantic import BaseModel, Field

from models.manifest import ManifestDependency
from models.package import PackageMetadata


class DependencyHealthLevel(StrEnum):
    """Developer-facing health labels for dependencies."""

    HEALTHY = "healthy"
    REVIEW_RECOMMENDED = "review_recommended"
    NEEDS_ATTENTION = "needs_attention"
    UNKNOWN = "unknown"


class DependencyHealthObservation(BaseModel):
    """One factual observation that contributes to package health."""

    code: str
    title: str
    description: str
    points_awarded: int = Field(ge=0)
    points_possible: int = Field(ge=0)


class PublicAdvisoryNotice(BaseModel):
    """A publicly reported package-version advisory notice."""

    advisory_id: str
    summary: str | None = None
    details_url: str | None = None


class DependencyHealthReport(BaseModel):
    """Health result for one direct dependency in a project manifest."""

    declared_dependency: ManifestDependency
    package_metadata: PackageMetadata | None = None
    health_score: int | None = Field(default=None, ge=0, le=100)
    health_level: DependencyHealthLevel = DependencyHealthLevel.UNKNOWN
    data_coverage_percent: int = Field(default=0, ge=0, le=100)

    observations: list[DependencyHealthObservation] = Field(default_factory=list)
    public_advisory_notices: list[PublicAdvisoryNotice] = Field(
        default_factory=list
    )
    version_recommendation: str | None = None
    limitations: list[str] = Field(default_factory=list)