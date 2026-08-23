"""Typed models for saved Dependency Health Report history."""

from datetime import datetime

from pydantic import BaseModel

from models.dependency_health import DependencyHealthLevel
from models.manifest import ManifestType


class ScanHistoryEntry(BaseModel):
    """Compact metadata for one saved Dependency Health Report."""

    scan_id: int
    source_name: str
    manifest_type: ManifestType
    project_name: str | None = None

    aggregate_health_score: int | None = None
    aggregate_health_level: DependencyHealthLevel
    data_coverage_percent: int
    dependency_count: int

    generated_at: datetime
    saved_at: datetime