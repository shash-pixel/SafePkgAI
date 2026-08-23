"""Tests for SQLite scan history persistence."""

from pathlib import Path

from database.scan_history_repository import ScanHistoryRepository
from models.dependency_health import DependencyHealthLevel
from models.dependency_health_summary import DependencyHealthSummary
from models.manifest import ManifestType


def test_save_list_and_load_summary(tmp_path: Path) -> None:
    """A saved report can be listed and loaded from SQLite."""

    repository = ScanHistoryRepository(
        database_path=tmp_path / "history.db"
    )
    repository.initialize()

    summary = DependencyHealthSummary(
        manifest_type=ManifestType.REQUIREMENTS_TXT,
        source_name="requirements.txt",
        aggregate_health_score=82,
        aggregate_health_level=DependencyHealthLevel.HEALTHY,
        data_coverage_percent=100,
    )

    saved_entry = repository.save(summary)
    history = repository.list_recent()
    loaded_summary = repository.get_summary(saved_entry.scan_id)

    assert len(history) == 1
    assert history[0].scan_id == saved_entry.scan_id
    assert history[0].aggregate_health_score == 82
    assert loaded_summary is not None
    assert loaded_summary.source_name == "requirements.txt"