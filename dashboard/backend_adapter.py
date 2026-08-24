"""Thin Streamlit adapter over the existing SafePkg AI services."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from core.package_analysis_service import PackageAnalysisService
from core.project_analysis_service import ProjectAnalysisService
from database.scan_history_repository import ScanHistoryRepository
from models.analysis import PackageAnalysisResult
from models.dependency_health_summary import DependencyHealthSummary
from models.package import PackageEcosystem
from models.scan_history import ScanHistoryEntry


class UploadedManifest(Protocol):
    name: str

    def getvalue(self) -> bytes: ...


class DashboardInputError(ValueError):
    """Raised for a manifest that the existing parser does not support."""


async def analyze_uploaded_manifest(uploaded_file: UploadedManifest) -> DependencyHealthSummary:
    """Stage an upload briefly, then call the existing file-based service."""

    filename = _validate_manifest_filename(uploaded_file.name)
    with TemporaryDirectory(prefix="packagemind-upload-") as directory:
        path = Path(directory) / filename
        path.write_bytes(uploaded_file.getvalue())
        return await ProjectAnalysisService().analyze_file(path)


async def analyze_package(
    ecosystem: PackageEcosystem, package_name: str, version: str | None = None
) -> PackageAnalysisResult:
    """Call the existing package metadata and insight pipeline."""

    return await PackageAnalysisService().analyze_package(ecosystem, package_name, version)


def save_summary(summary: DependencyHealthSummary) -> ScanHistoryEntry:
    repository = ScanHistoryRepository()
    repository.initialize()
    return repository.save(summary)


def list_history(limit: int = 50) -> list[ScanHistoryEntry]:
    repository = ScanHistoryRepository()
    repository.initialize()
    return repository.list_recent(limit)


def load_history_summary(scan_id: int) -> DependencyHealthSummary | None:
    repository = ScanHistoryRepository()
    repository.initialize()
    return repository.get_summary(scan_id)


def _validate_manifest_filename(filename: str) -> str:
    path = Path(filename)
    if path.name != filename or filename not in {"requirements.txt", "package.json"}:
        raise DashboardInputError("Upload a file named requirements.txt or package.json.")
    return filename
