"""SQLite persistence for Dependency Health Report history."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config.settings import settings
from models.dependency_health_summary import DependencyHealthSummary
from models.scan_history import ScanHistoryEntry


class ScanHistoryRepository:
    """Save and retrieve Dependency Health Report history locally."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = database_path or settings.database_path

    def initialize(self) -> None:
        """Create the scan-history table and indexes when absent."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_history (
                    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    manifest_type TEXT NOT NULL,
                    project_name TEXT,
                    aggregate_health_score INTEGER,
                    aggregate_health_level TEXT NOT NULL,
                    data_coverage_percent INTEGER NOT NULL,
                    dependency_count INTEGER NOT NULL,
                    generated_at TEXT NOT NULL,
                    saved_at TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_scan_history_saved_at
                ON scan_history (saved_at DESC)
                """
            )

    def save(
        self,
        summary: DependencyHealthSummary,
    ) -> ScanHistoryEntry:
        """Save a complete report and return its compact history entry."""

        saved_at = datetime.now(timezone.utc)
        report_json = json.dumps(
            summary.model_dump(mode="json"),
            ensure_ascii=False,
        )

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scan_history (
                    source_name,
                    manifest_type,
                    project_name,
                    aggregate_health_score,
                    aggregate_health_level,
                    data_coverage_percent,
                    dependency_count,
                    generated_at,
                    saved_at,
                    report_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.source_name,
                    summary.manifest_type.value,
                    summary.project_name,
                    summary.aggregate_health_score,
                    summary.aggregate_health_level.value,
                    summary.data_coverage_percent,
                    len(summary.dependency_reports),
                    summary.generated_at.isoformat(),
                    saved_at.isoformat(),
                    report_json,
                ),
            )
            scan_id = cursor.lastrowid

        return ScanHistoryEntry(
            scan_id=scan_id,
            source_name=summary.source_name,
            manifest_type=summary.manifest_type,
            project_name=summary.project_name,
            aggregate_health_score=summary.aggregate_health_score,
            aggregate_health_level=summary.aggregate_health_level,
            data_coverage_percent=summary.data_coverage_percent,
            dependency_count=len(summary.dependency_reports),
            generated_at=summary.generated_at,
            saved_at=saved_at,
        )

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ScanHistoryEntry]:
        """Return recent report history, newest first."""

        if not 1 <= limit <= 100:
            raise ValueError("History limit must be between 1 and 100.")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    scan_id,
                    source_name,
                    manifest_type,
                    project_name,
                    aggregate_health_score,
                    aggregate_health_level,
                    data_coverage_percent,
                    dependency_count,
                    generated_at,
                    saved_at
                FROM scan_history
                ORDER BY saved_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._to_history_entry(row) for row in rows]

    def get_summary(
        self,
        scan_id: int,
    ) -> DependencyHealthSummary | None:
        """Return the full saved report for one scan identifier."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT report_json
                FROM scan_history
                WHERE scan_id = ?
                """,
                (scan_id,),
            ).fetchone()

        if row is None:
            return None

        return DependencyHealthSummary.model_validate_json(row["report_json"])

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection configured for dictionary-like rows."""

        self._database_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row

        return connection

    @staticmethod
    def _to_history_entry(row: sqlite3.Row) -> ScanHistoryEntry:
        """Convert one SQLite row into a typed history entry."""

        return ScanHistoryEntry(
            scan_id=row["scan_id"],
            source_name=row["source_name"],
            manifest_type=row["manifest_type"],
            project_name=row["project_name"],
            aggregate_health_score=row["aggregate_health_score"],
            aggregate_health_level=row["aggregate_health_level"],
            data_coverage_percent=row["data_coverage_percent"],
            dependency_count=row["dependency_count"],
            generated_at=row["generated_at"],
            saved_at=row["saved_at"],
        )