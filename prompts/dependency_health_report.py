"""Prompt construction for Gemini Dependency Health explanations."""

import json

from models.dependency_health_summary import DependencyHealthSummary

DEPENDENCY_HEALTH_INSTRUCTIONS = """
You are PackageMind AI, a developer productivity copilot.

Explain the supplied Dependency Health Report in practical, clear language.
Use only the supplied facts. Do not invent package metadata, compatibility
claims, popularity data, release notes, or upgrade paths.

For recommended_actions, prioritise the most useful next steps. Do not create
one near-identical action for every dependency. When several packages simply
have available updates, combine them into one action that names those packages
and recommends compatibility testing before updating. Keep distinct actions
only when their supplied facts are meaningfully different (for example,
deprecation or a public advisory notice).

Public advisory notices are factual, publicly reported package-version notices.
Do not claim that a package is secure, unsafe, exploitable, or vulnerability-free.
Do not describe the application as a cybersecurity tool.
"""


def build_dependency_health_input(
    summary: DependencyHealthSummary,
) -> str:
    """Create a small factual input for Gemini."""

    dependencies = []

    for report in summary.dependency_reports:
        dependencies.append(
            {
                "name": report.declared_dependency.name,
                "health_score": report.health_score,
                "health_level": report.health_level.value,
                "data_coverage_percent": report.data_coverage_percent,
                "observations": [
                    observation.model_dump(mode="json")
                    for observation in report.observations
                ],
                "public_advisory_notices": [
                    notice.model_dump(mode="json")
                    for notice in report.public_advisory_notices
                ],
                "version_recommendation": report.version_recommendation,
                "limitations": report.limitations,
            }
        )

    report_data = {
        "manifest": summary.source_name,
        "manifest_type": summary.manifest_type.value,
        "project_name": summary.project_name,
        "aggregate_health_score": summary.aggregate_health_score,
        "aggregate_health_level": summary.aggregate_health_level.value,
        "data_coverage_percent": summary.data_coverage_percent,
        "dependencies_needing_attention": summary.dependencies_needing_attention,
        "dependencies_with_updates": summary.dependencies_with_updates,
        "deprecated_dependencies": summary.deprecated_dependencies,
        "dependencies_with_public_notices": summary.dependencies_with_public_notices,
        "dependencies": dependencies,
        "limitations": summary.limitations,
    }

    return (
        "Explain this Dependency Health Report:\n\n"
        f"{json.dumps(report_data, ensure_ascii=False, indent=2)}"
    )
