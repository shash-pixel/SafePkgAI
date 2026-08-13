"""Typed data contracts for open-source package analysis."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class PackageEcosystem(StrEnum):
    """Supported package ecosystems."""

    PYPI = "pypi"
    NPM = "npm"


class PackageReference(BaseModel):
    """Identifies one package in a supported ecosystem."""

    ecosystem: PackageEcosystem
    name: str
    requested_version: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject empty package names before making registry requests."""

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Package name cannot be empty.")

        return normalized_value


class PackageDependency(BaseModel):
    """A dependency declared by a package."""

    name: str
    version_constraint: str | None = None
    environment_marker: str | None = None
    raw_requirement: str


class PackageMetadata(BaseModel):
    """Normalized package facts collected from a registry."""

    reference: PackageReference
    resolved_version: str
    latest_available_version: str
    published_at: datetime | None = None
    latest_published_at: datetime | None = None
    release_count: int = Field(ge=0)

    summary: str | None = None
    description: str | None = None
    homepage_url: str | None = None
    repository_url: str | None = None
    runtime_requirements: dict[str, str] = Field(default_factory=dict)

    dependencies: list[PackageDependency] = Field(default_factory=list)
    classifiers: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    license_name : str | None = None