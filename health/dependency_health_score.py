"""Transparent scoring for PackageMind dependency health reports."""

from datetime import datetime, timezone

from models.dependency_health import (
    DependencyHealthLevel,
    DependencyHealthObservation,
    DependencyHealthReport,
    PublicAdvisoryNotice,
)
from models.manifest import ManifestDependency
from models.package import PackageMetadata


class DependencyHealthScorer:
    """Calculate explainable Dependency Health Scores from known facts."""

    _VERSION_POINTS = 20
    _MAINTENANCE_POINTS = 20
    _DEPRECATION_POINTS = 20
    _LICENSE_POINTS = 15
    _ADVISORY_POINTS = 15
    _POPULARITY_POINTS = 10

    def build_report(
        self,
        dependency: ManifestDependency,
        metadata: PackageMetadata,
        advisory_notices: list[PublicAdvisoryNotice],
    ) -> DependencyHealthReport:
        """Create one dependency health report from verified package facts."""

        observations = [
            self._version_observation(dependency, metadata),
            self._maintenance_observation(metadata),
            self._deprecation_observation(metadata),
            self._license_observation(metadata),
            self._advisory_observation(advisory_notices),
        ]

        awarded_points = sum(item.points_awarded for item in observations)
        possible_points = sum(item.points_possible for item in observations)
        score = round((awarded_points / possible_points) * 100)

        return DependencyHealthReport(
            declared_dependency=dependency,
            package_metadata=metadata,
            health_score=score,
            health_level=self._get_health_level(score),
            data_coverage_percent=round(
                (possible_points / self._total_possible_points()) * 100
            ),
            observations=observations,
            public_advisory_notices=advisory_notices,
            version_recommendation=self._build_version_recommendation(
                dependency,
                metadata,
            ),
            limitations=[
                "Popularity data is not included in this initial report.",
                "The license value is publisher-provided metadata, not legal advice.",
            ],
        )

    def _version_observation(
        self,
        dependency: ManifestDependency,
        metadata: PackageMetadata,
    ) -> DependencyHealthObservation:
        is_current = (
            dependency.version_constraint == metadata.latest_available_version
        )

        return DependencyHealthObservation(
            code="version-currency",
            title="Version currency",
            description=(
                "The declared version matches the latest available release."
                if is_current
                else (
                    f"The latest available version is "
                    f"{metadata.latest_available_version}."
                )
            ),
            points_awarded=self._VERSION_POINTS if is_current else 8,
            points_possible=self._VERSION_POINTS,
        )

    def _maintenance_observation(
        self,
        metadata: PackageMetadata,
    ) -> DependencyHealthObservation:
        if metadata.latest_published_at is None:
            return DependencyHealthObservation(
                code="maintenance-unknown",
                title="Maintenance activity unavailable",
                description="The registry did not provide a latest release date.",
                points_awarded=0,
                points_possible=0,
            )

        latest_release = metadata.latest_published_at
        if latest_release.tzinfo is None:
            latest_release = latest_release.replace(tzinfo=timezone.utc)

        age_days = (datetime.now(timezone.utc) - latest_release).days
        points = self._maintenance_points(age_days)

        return DependencyHealthObservation(
            code="maintenance-recency",
            title="Maintenance activity",
            description=f"The latest release was published {age_days} days ago.",
            points_awarded=points,
            points_possible=self._MAINTENANCE_POINTS,
        )

    def _deprecation_observation(
        self,
        metadata: PackageMetadata,
    ) -> DependencyHealthObservation:
        is_deprecated = bool(metadata.deprecated_message)

        return DependencyHealthObservation(
            code="deprecation-status",
            title="Deprecation status",
            description=(
                metadata.deprecated_message
                if is_deprecated
                else "The registry does not mark this package as deprecated."
            ),
            points_awarded=0 if is_deprecated else self._DEPRECATION_POINTS,
            points_possible=self._DEPRECATION_POINTS,
        )

    def _license_observation(
        self,
        metadata: PackageMetadata,
    ) -> DependencyHealthObservation:
        has_license = bool(metadata.license_name)

        return DependencyHealthObservation(
            code="license-clarity",
            title="Published license",
            description=(
                f"The registry lists: {metadata.license_name}."
                if has_license
                else "The registry does not provide a license label."
            ),
            points_awarded=self._LICENSE_POINTS if has_license else 0,
            points_possible=self._LICENSE_POINTS,
        )

    def _advisory_observation(
        self,
        notices: list[PublicAdvisoryNotice],
    ) -> DependencyHealthObservation:
        notice_count = len(notices)

        return DependencyHealthObservation(
            code="public-advisory-notices",
            title="Public advisory notices",
            description=(
                "No public advisory notices were returned for this exact version."
                if notice_count == 0
                else (
                    f"{notice_count} public advisory notice(s) were returned "
                    "for this exact version."
                )
            ),
            points_awarded=0 if notice_count else self._ADVISORY_POINTS,
            points_possible=self._ADVISORY_POINTS,
        )

    @staticmethod
    def _maintenance_points(age_days: int) -> int:
        if age_days <= 180:
            return 20
        if age_days <= 365:
            return 12
        if age_days <= 730:
            return 6
        return 0

    @staticmethod
    def _get_health_level(score: int) -> DependencyHealthLevel:
        if score >= 80:
            return DependencyHealthLevel.HEALTHY
        if score >= 60:
            return DependencyHealthLevel.REVIEW_RECOMMENDED
        return DependencyHealthLevel.NEEDS_ATTENTION

    @staticmethod
    def _build_version_recommendation(
        dependency: ManifestDependency,
        metadata: PackageMetadata,
    ) -> str:
        if dependency.version_constraint == metadata.latest_available_version:
            return "The declared version matches the latest available release."

        return (
            f"Review an update to {metadata.latest_available_version}; "
            "confirm compatibility before changing the project dependency."
        )

    def _total_possible_points(self) -> int:
        return (
            self._VERSION_POINTS
            + self._MAINTENANCE_POINTS
            + self._DEPRECATION_POINTS
            + self._LICENSE_POINTS
            + self._ADVISORY_POINTS
            + self._POPULARITY_POINTS
        )