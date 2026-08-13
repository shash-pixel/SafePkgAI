"""Deterministic developer-oriented insights from package metadata."""

from datetime import datetime, timezone

from config.insight_thresholds import insight_thresholds
from models.insight import (
    InsightCategory,
    InsightLevel,
    PackageInsight,
)
from models.package import PackageMetadata


class PackageInsightEngine:
    """Derive explainable maintenance and dependency observations."""

    def analyze(self, metadata: PackageMetadata) -> list[PackageInsight]:
        """Return deterministic insights for one package."""

        insights = [
            *self._deprecation_insights(metadata),
            *self._maintenance_insights(metadata),
            *self._release_history_insights(metadata),
            *self._runtime_insights(metadata),
            *self._dependency_insights(metadata),
            *self._documentation_insights(metadata),
        ]

        return insights

    def _deprecation_insights(
        self,
        metadata: PackageMetadata,
    ) -> list[PackageInsight]:
        if not metadata.deprecated_message:
            return []

        return [
            PackageInsight(
                code="package-deprecated",
                category=InsightCategory.DEPRECATION,
                level=InsightLevel.ATTENTION,
                title="Package marked as deprecated",
                explanation=metadata.deprecated_message,
            )
        ]

    def _maintenance_insights(
        self,
        metadata: PackageMetadata,
    ) -> list[PackageInsight]:
        if metadata.latest_published_at is None:
            return [
                PackageInsight(
                    code="release-date-unavailable",
                    category=InsightCategory.MAINTENANCE,
                    level=InsightLevel.NOTICE,
                    title="Latest release date unavailable",
                    explanation=(
                        "The package registry did not provide a release date, "
                        "so maintenance recency cannot be assessed."
                    ),
                )
            ]

        latest_release = metadata.latest_published_at
        if latest_release.tzinfo is None:
            latest_release = latest_release.replace(tzinfo=timezone.utc)

        age_days = (datetime.now(timezone.utc) - latest_release).days

        if age_days <= insight_thresholds.recent_release_days:
            level = InsightLevel.INFO
            title = "Recently maintained"
            explanation = f"A release was published {age_days} days ago."
        elif age_days <= insight_thresholds.aging_release_days:
            level = InsightLevel.NOTICE
            title = "Maintenance activity is slowing"
            explanation = f"The latest release was published {age_days} days ago."
        else:
            level = InsightLevel.ATTENTION
            title = "Limited recent release activity"
            explanation = f"The latest release was published {age_days} days ago."

        return [
            PackageInsight(
                code="release-recency",
                category=InsightCategory.MAINTENANCE,
                level=level,
                title=title,
                explanation=explanation,
            )
        ]

    def _release_history_insights(
        self,
        metadata: PackageMetadata,
    ) -> list[PackageInsight]:
        if metadata.release_count > insight_thresholds.limited_release_history_count:
            return []

        return [
            PackageInsight(
                code="limited-release-history",
                category=InsightCategory.ADOPTION,
                level=InsightLevel.NOTICE,
                title="Limited release history",
                explanation=(
                    f"The registry lists {metadata.release_count} release(s). "
                    "Review documentation and maintenance context before adoption."
                ),
            )
        ]

    @staticmethod
    def _runtime_insights(metadata: PackageMetadata) -> list[PackageInsight]:
        if not metadata.runtime_requirements:
            return []

        requirements = ", ".join(
            f"{runtime}: {constraint}"
            for runtime, constraint in metadata.runtime_requirements.items()
        )

        return [
            PackageInsight(
                code="declared-runtime-support",
                category=InsightCategory.COMPATIBILITY,
                level=InsightLevel.INFO,
                title="Declared runtime support",
                explanation=f"The package declares: {requirements}.",
            )
        ]

    @staticmethod
    def _dependency_insights(metadata: PackageMetadata) -> list[PackageInsight]:
        dependency_count = len(metadata.dependencies)

        if dependency_count == 0:
            return [
                PackageInsight(
                    code="no-direct-dependencies",
                    category=InsightCategory.DEPENDENCIES,
                    level=InsightLevel.INFO,
                    title="No declared direct dependencies",
                    explanation=(
                        "The package registry does not list runtime dependencies "
                        "for the selected version."
                    ),
                )
            ]

        return [
            PackageInsight(
                code="direct-dependency-count",
                category=InsightCategory.DEPENDENCIES,
                level=InsightLevel.INFO,
                title="Declared direct dependencies",
                explanation=(
                    f"The selected version declares {dependency_count} "
                    "direct runtime dependency or dependencies."
                ),
            )
        ]

    @staticmethod
    def _documentation_insights(
        metadata: PackageMetadata,
    ) -> list[PackageInsight]:
        if metadata.summary or metadata.description:
            return []

        return [
            PackageInsight(
                code="limited-registry-description",
                category=InsightCategory.DOCUMENTATION,
                level=InsightLevel.NOTICE,
                title="Limited registry documentation",
                explanation=(
                    "The registry does not provide a package summary or description."
                ),
            )
        ]