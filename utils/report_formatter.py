"""Terminal formatting helpers for Dependency Health Reports."""

from models.dependency_health import DependencyHealthReport
from models.dependency_health_summary import DependencyHealthSummary
from models.scan_history import ScanHistoryEntry

def format_scan_history(
    entries: list[ScanHistoryEntry],
) -> str:
    """Return recent Dependency Health Report history for the terminal."""

    if not entries:
        return "No saved Dependency Health Reports found."

    lines = [
        "Dependency Health History",
        "=" * 27,
    ]

    for entry in entries:
        score = (
            f"{entry.aggregate_health_score}/100"
            if entry.aggregate_health_score is not None
            else "Unavailable"
        )

        lines.append(
            f"#{entry.scan_id} | {entry.source_name} | {score} | "
            f"{entry.aggregate_health_level.value} | "
            f"{entry.saved_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )

    return "\n".join(lines)


def format_dependency_health_summary(
    summary: DependencyHealthSummary,
) -> str:
    """Return a readable terminal representation of a health summary."""

    score = (
        f"{summary.aggregate_health_score}/100"
        if summary.aggregate_health_score is not None
        else "Unavailable"
    )

    lines = [
        "Dependency Health Report",
        "=" * 26,
        f"Manifest: {summary.source_name}",
        f"Health Score: {score}",
        f"Health Level: {summary.aggregate_health_level.value}",
        f"Data Coverage: {summary.data_coverage_percent}%",
        f"Dependencies Needing Attention: "
        f"{summary.dependencies_needing_attention}",
        f"Dependencies With Updates: {summary.dependencies_with_updates}",
        f"Deprecated Dependencies: {summary.deprecated_dependencies}",
        f"Dependencies With Public Notices: "
        f"{summary.dependencies_with_public_notices}",
        "",
        "Dependency Details",
        "-" * 26,
    ]

    lines.extend(
        _format_dependency_report(report)
        for report in summary.dependency_reports
    )

    if summary.limitations:
        lines.extend(["", "Report Limitations"])
        lines.extend(f"- {item}" for item in summary.limitations)

    return "\n".join(lines)


def _format_dependency_report(
    report: DependencyHealthReport,
) -> str:
    """Format one direct dependency report as a compact terminal line."""

    score = (
        f"{report.health_score}/100"
        if report.health_score is not None
        else "Unavailable"
    )

    return (
        f"- {report.declared_dependency.name}: {score} "
        f"({report.health_level.value})"
    )