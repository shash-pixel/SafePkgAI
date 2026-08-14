"""Prompt construction for Gemini Dependency Health explanations."""

import json

from models.dependency_health_summary import DependencyHealthSummary

DEPENDENCY_HEALTH_INSTRUCTIONS = """
You are PackageMind AI, a developer productivity copilot.

Explain the supplied Dependency Health Report in practical, clear language.
Use only the supplied facts. Do not invent package metadata, compatibility
claims, popularity data, release notes, or upgrade paths.

Public advisory notices are factual, publicly reported package-version notices.
Do not claim that a package is secure, unsafe, exploitable, or vulnerability-free.
Do not describe the application as a cybersecurity tool.
"""


def build_dependency_health_input(
    summary: DependencyHealthSummary,
) -> str:
    """Create a bounded factual JSON input for Gemini."""

    report_data = summary.model_dump(mode="json")
    report_data["dependency_reports"] = report_data["dependency_reports"][:50]

    return (
        "Explain this Dependency Health Report:\n\n"
        f"{json.dumps(report_data, ensure_ascii=False, indent=2)}"
    )