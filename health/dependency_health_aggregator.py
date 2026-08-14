"""Aggregate per-dependency reports into one Dependency Health Summary."""

from models.dependency_health import (
    DependencyHealthLevel,
    DependencyHealthReport,
)
from models.dependency_health_summary import DependencyHealthSummary
from models.manifest import DependencyManifest


class DependencyHealthAggregator:
    """Calculate project-level Dependency Health Report statistics."""

    def build_summary(
        self,
        manifest: DependencyManifest,
        reports: list[DependencyHealthReport],
    ) -> DependencyHealthSummary:
        """Build one aggregate summary from dependency reports."""

        scored_reports = [
            report for report in reports if report.health_score is not None
        ]

        aggregate_score = self._average_score(scored_reports)
        coverage_percent = self._coverage_percent(
            total_reports=len(reports),
            scored_reports=len(scored_reports),
        )

        return DependencyHealthSummary(
            manifest_type=manifest.manifest_type,
            source_name=manifest.source_name,
            project_name=manifest.project_name,
            dependency_reports=reports,
            aggregate_health_score=aggregate_score,
            aggregate_health_level=self._get_health_level(aggregate_score),
            data_coverage_percent=coverage_percent,
            dependencies_needing_attention=sum(
                report.health_level
                is DependencyHealthLevel.NEEDS_ATTENTION
                for report in reports
            ),
            dependencies_with_updates=sum(
                self._has_update(report) for report in reports
            ),
            deprecated_dependencies=sum(
                bool(
                    report.package_metadata
                    and report.package_metadata.deprecated_message
                )
                for report in reports
            ),
            dependencies_with_public_notices=sum(
                bool(report.public_advisory_notices)
                for report in reports
            ),
            limitations=self._build_limitations(reports, scored_reports),
        )

    @staticmethod
    def _average_score(
        reports: list[DependencyHealthReport],
    ) -> int | None:
        if not reports:
            return None

        return round(
            sum(report.health_score for report in reports if report.health_score)
            / len(reports)
        )

    @staticmethod
    def _coverage_percent(
        total_reports: int,
        scored_reports: int,
    ) -> int:
        if total_reports == 0:
            return 0

        return round((scored_reports / total_reports) * 100)

    @staticmethod
    def _get_health_level(
        score: int | None,
    ) -> DependencyHealthLevel:
        if score is None:
            return DependencyHealthLevel.UNKNOWN
        if score >= 80:
            return DependencyHealthLevel.HEALTHY
        if score >= 60:
            return DependencyHealthLevel.REVIEW_RECOMMENDED

        return DependencyHealthLevel.NEEDS_ATTENTION

    @staticmethod
    def _has_update(report: DependencyHealthReport) -> bool:
        metadata = report.package_metadata
        if metadata is None:
            return False

        return metadata.resolved_version != metadata.latest_available_version

    @staticmethod
    def _build_limitations(
        reports: list[DependencyHealthReport],
        scored_reports: list[DependencyHealthReport],
    ) -> list[str]:
        limitations: list[str] = []

        if not reports:
            limitations.append("No dependencies were found in this manifest.")

        unavailable_reports = len(reports) - len(scored_reports)
        if unavailable_reports:
            limitations.append(
                f"{unavailable_reports} dependency or dependencies could not "
                "be fully evaluated."
            )

        return limitations