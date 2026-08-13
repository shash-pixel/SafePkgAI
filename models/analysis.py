"""Typed output contracts for package analysis workflows."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from models.insight import PackageInsight
from models.package import PackageMetadata


class PackageAnalysisResult(BaseModel):
    """Combines normalized metadata with deterministic package insights."""

    metadata: PackageMetadata
    insights: list[PackageInsight] = Field(default_factory=list)
    analyzed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )