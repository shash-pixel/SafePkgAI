"""Tests for Dependency Health summary aggregation."""

from health.dependency_health_aggregator import DependencyHealthAggregator
from models.dependency_health import (
    DependencyHealthLevel,
    DependencyHealthReport,
)
from models.manifest import (
    DependencyManifest,
    ManifestDependency,
    ManifestType,
)


def test_build_summary_calculates_average_and_coverage() -> None:
    """Only scored reports contribute to the aggregate score."""

    manifest = DependencyManifest(
        manifest_type=ManifestType.REQUIREMENTS_TXT,
        source_name="requirements.txt",
        dependencies=[
            ManifestDependency(
                name="httpx",
                version_constraint="==0.28.1",
                group="production",
                raw_requirement="httpx==0.28.1",
            ),
            ManifestDependency(
                name="missing-package",
                version_constraint=None,
                group="production",
                raw_requirement="missing-package",
            ),
        ],
    )

    reports = [
        DependencyHealthReport(
            declared_dependency=manifest.dependencies[0],
            health_score=80,
            health_level=DependencyHealthLevel.HEALTHY,
        ),
        DependencyHealthReport(
            declared_dependency=manifest.dependencies[1],
            limitations=["Package metadata could not be retrieved."],
        ),
    ]

    summary = DependencyHealthAggregator().build_summary(
        manifest=manifest,
        reports=reports,
    )

    assert summary.aggregate_health_score == 80
    assert summary.data_coverage_percent == 50
    assert summary.aggregate_health_level is DependencyHealthLevel.HEALTHY