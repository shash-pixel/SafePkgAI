"""Orchestration service for manifest-wide Dependency Health Reports."""

import asyncio
import re

from core.fetcher_factory import get_fetcher
from fetchers.base import PackageFetchError
from fetchers.public_advisories import PublicAdvisoryFetcher
from health.dependency_health_aggregator import DependencyHealthAggregator
from health.dependency_health_score import DependencyHealthScorer
from models.dependency_health import DependencyHealthReport
from models.dependency_health_summary import DependencyHealthSummary
from models.manifest import DependencyManifest, ManifestDependency, ManifestType
from models.package import PackageEcosystem


class DependencyHealthService:
    """Coordinate metadata, public notices, scoring, and aggregation."""

    _MAX_CONCURRENT_REQUESTS = 5

    def __init__(
        self,
        advisory_fetcher: PublicAdvisoryFetcher | None = None,
        scorer: DependencyHealthScorer | None = None,
        aggregator: DependencyHealthAggregator | None = None,
    ) -> None:
        self._advisory_fetcher = advisory_fetcher or PublicAdvisoryFetcher()
        self._scorer = scorer or DependencyHealthScorer()
        self._aggregator = aggregator or DependencyHealthAggregator()

    async def analyze_manifest(
        self,
        manifest: DependencyManifest,
    ) -> DependencyHealthSummary:
        """Create a Dependency Health Report for all direct dependencies."""

        ecosystem = self._get_ecosystem(manifest.manifest_type)
        semaphore = asyncio.Semaphore(self._MAX_CONCURRENT_REQUESTS)

        tasks = [
            self._analyze_dependency(
                dependency=dependency,
                ecosystem=ecosystem,
                semaphore=semaphore,
            )
            for dependency in manifest.dependencies
        ]

        reports = await asyncio.gather(*tasks)

        return self._aggregator.build_summary(
            manifest=manifest,
            reports=reports,
        )

    async def _analyze_dependency(
        self,
        dependency: ManifestDependency,
        ecosystem: PackageEcosystem,
        semaphore: asyncio.Semaphore,
    ) -> DependencyHealthReport:
        """Analyze one dependency while preserving failures as report data."""

        async with semaphore:
            return await self._analyze_dependency_safely(
                dependency=dependency,
                ecosystem=ecosystem,
            )

    async def _analyze_dependency_safely(
        self,
        dependency: ManifestDependency,
        ecosystem: PackageEcosystem,
    ) -> DependencyHealthReport:
        """Return a report even when registry data is unavailable."""

        requested_version = self._get_exact_version(
            dependency.version_constraint
        )
        fetcher = get_fetcher(ecosystem)

        try:
            metadata = await fetcher.fetch_package(
                package_name=dependency.name,
                version=requested_version,
            )
        except PackageFetchError as error:
            return DependencyHealthReport(
                declared_dependency=dependency,
                limitations=[
                    f"Package metadata could not be retrieved: {error}"
                ],
            )

        limitations: list[str] = []

        if dependency.version_constraint and requested_version is None:
            limitations.append(
                "Version range evaluation is not implemented yet; "
                "the latest available release was analyzed."
            )

        try:
            notices = await self._advisory_fetcher.fetch_notices(
                ecosystem=ecosystem,
                package_name=metadata.reference.name,
                version=metadata.resolved_version,
            )
        except PackageFetchError:
            notices = []
            limitations.append(
                "Public advisory notices could not be retrieved."
            )

        report = self._scorer.build_report(
            dependency=dependency,
            metadata=metadata,
            advisory_notices=notices,
        )
        report.limitations.extend(limitations)

        return report

    @staticmethod
    def _get_ecosystem(
        manifest_type: ManifestType,
    ) -> PackageEcosystem:
        """Map a manifest format to its package ecosystem."""

        if manifest_type is ManifestType.REQUIREMENTS_TXT:
            return PackageEcosystem.PYPI

        return PackageEcosystem.NPM

    @staticmethod
    def _get_exact_version(
        version_constraint: str | None,
    ) -> str | None:
        """Extract an exact version without incorrectly resolving ranges."""

        if not version_constraint:
            return None

        python_match = re.fullmatch(
            r"==\\s*([0-9][A-Za-z0-9.+_-]*)",
            version_constraint.strip(),
        )
        if python_match:
            return python_match.group(1)

        npm_match = re.fullmatch(
            r"[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?",
            version_constraint.strip(),
        )
        if npm_match:
            return version_constraint.strip()

        return None