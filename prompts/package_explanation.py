"""Prompt construction for grounded package explanations."""

import json

from models.analysis import PackageAnalysisResult

PACKAGE_EXPLANATION_INSTRUCTIONS = """
You are SafePkg AI , a developer copilot for open-source libraries.

Explain the supplied package facts in clear, practical English.

Use only the supplied fact sheet. Do not invent popularity, maintenance,
compatibility, API behavior, release notes, or alternatives. If the available
facts are insufficient, state the limitation clearly.

Do not discuss malware, exploits, vulnerabilities, or security risk.
Keep guidance conditional and practical for a developer evaluating the package.
"""


def build_package_fact_sheet(analysis: PackageAnalysisResult) -> str:
    """Create a bounded JSON fact sheet for AI prompts."""

    metadata = analysis.metadata.model_dump(mode="json")
    metadata["description"] = (metadata.get("description") or "")[:6_000]
    metadata["dependencies"] = metadata["dependencies"][:50]

    payload = {
        "package_metadata": metadata,
        "deterministic_insights": [
            insight.model_dump(mode="json") for insight in analysis.insights
        ],
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_package_explanation_input(analysis: PackageAnalysisResult) -> str:
    """Build the package-explanation request from verified package facts."""

    return (
        "Generate a structured package explanation from this fact sheet:\n\n"
        f"{build_package_fact_sheet(analysis)}"
    )