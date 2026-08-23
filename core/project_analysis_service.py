## Think of project_analysis_service.py as a manager/orchestrator
## DependencyManifest :- The parser converts the raw file into a standard/common format.
## DependencyHealthService :- This service asks things like:

# Is this dependency outdated?
# Does this version have known vulnerabilities?
# Is this dependency healthy/safe?

## DependencyHealthSummary :- This is a summary of the health of the dependency, including whether it is outdated, has known vulnerabilities, and is considered healthy/safe.

"""Application service for complete project dependency analysis."""

from pathlib import Path

from analysis.dependency_health_service import DependencyHealthService
from core.manifest_parser_factory import get_manifest_parser
from models.dependency_health_summary import DependencyHealthSummary


class ProjectAnalysisService:
    """Parse a manifest and produce a Dependency Health Report."""

    def __init__(
        self,
        health_service: DependencyHealthService | None = None,
    ) -> None:
        self._health_service = health_service or DependencyHealthService()

    async def analyze_file(
        self,
        file_path: str | Path,
    ) -> DependencyHealthSummary:
        """Read, parse, and analyze one supported manifest file."""

        source_path = Path(file_path)
        content = source_path.read_text(encoding="utf-8")

        parser = get_manifest_parser(source_path)
        manifest = parser.parse(
            content=content,
            source_name=source_path.name,
        )

        return await self._health_service.analyze_manifest(manifest)