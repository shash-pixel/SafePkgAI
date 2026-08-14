"""Typed data contract for a complete Dependency Health Report."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from models.dependency_health import (
    DependencyHealthLevel,
    DependencyHealthReport,
)
from models.manifest import ManifestType


class DependencyHealthSummary(BaseModel):
    """Aggregated Dependency Health Report for one project manifest."""

    manifest_type: ManifestType
    source_name: str
    project_name: str | None = None

    dependency_reports: list[DependencyHealthReport] = Field(
        default_factory=list
    )

    aggregate_health_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    aggregate_health_level: DependencyHealthLevel = (
        DependencyHealthLevel.UNKNOWN
    )
    data_coverage_percent: int = Field(default=0, ge=0, le=100)

    dependencies_needing_attention: int = Field(default=0, ge=0)
    dependencies_with_updates: int = Field(default=0, ge=0)
    deprecated_dependencies: int = Field(default=0, ge=0)
    dependencies_with_public_notices: int = Field(default=0, ge=0)

    limitations: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )