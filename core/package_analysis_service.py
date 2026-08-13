"""Application service for factual package analysis."""

from core.fetcher_factory import get_fetcher
from insights.package_insights import PackageInsightEngine
from models.analysis import PackageAnalysisResult
from models.package import PackageEcosystem


class PackageAnalysisService:
    """Coordinate fetching and deterministic analysis for one package."""

    def __init__(
        self,
        insight_engine: PackageInsightEngine | None = None,
    ) -> None:
        self._insight_engine = insight_engine or PackageInsightEngine()

    async def analyze_package(
        self,
        ecosystem: PackageEcosystem,
        package_name: str,
        version: str | None = None,
    ) -> PackageAnalysisResult:
        """Fetch package metadata and derive developer-oriented insights."""

        fetcher = get_fetcher(ecosystem)
        metadata = await fetcher.fetch_package(package_name, version)
        insights = self._insight_engine.analyze(metadata)

        return PackageAnalysisResult(
            metadata=metadata,
            insights=insights,
        )