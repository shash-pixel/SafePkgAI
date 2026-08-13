"""Typed data contracts for deterministic package insights."""

from enum import StrEnum

from pydantic import BaseModel


class InsightCategory(StrEnum):
    """Categories of developer-oriented package observations."""

    MAINTENANCE = "maintenance"
    ADOPTION = "adoption"
    COMPATIBILITY = "compatibility"
    DEPENDENCIES = "dependencies"
    DEPRECATION = "deprecation"
    DOCUMENTATION = "documentation"


class InsightLevel(StrEnum):
    """Priority levels for package observations."""

    INFO = "info"
    NOTICE = "notice"
    ATTENTION = "attention"


class PackageInsight(BaseModel):
    """One explainable observation derived from package metadata."""

    code: str
    category: InsightCategory
    level: InsightLevel
    title: str
    explanation: str