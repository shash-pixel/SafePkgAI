"""Typed data contracts for dependency manifests."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ManifestType(StrEnum):
    """Supported dependency manifest formats."""

    REQUIREMENTS_TXT = "requirements.txt"
    PACKAGE_JSON = "package.json"


class ManifestDependency(BaseModel):
    """One direct dependency declared by a project."""

    name: str
    version_constraint: str | None = None
    group: str
    raw_requirement: str


class DependencyManifest(BaseModel):
    """Normalized dependencies parsed from an uploaded project manifest."""

    manifest_type: ManifestType
    source_name: str
    project_name: str | None = None
    dependencies: list[ManifestDependency] = Field(default_factory=list)