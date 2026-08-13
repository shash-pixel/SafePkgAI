"""Prompt construction for candidate-based package recommendations."""

import json

from models.analysis import PackageAnalysisResult
from models.recommendation import AlternativeCandidate
from prompts.package_explanation import build_package_fact_sheet

ALTERNATIVE_RECOMMENDATION_INSTRUCTIONS = """
You are PackageMind AI, a developer copilot for open-source libraries.

Recommend zero, one, or two alternatives from the supplied candidate list only.
Use each alternative name exactly as provided. Do not invent packages or claim
facts that are absent from the package fact sheet or candidate descriptions.

Explain when each alternative may be a better fit, and state tradeoffs.
Do not discuss malware, exploits, vulnerabilities, or security risk.
"""


def build_alternative_recommendation_input(
    analysis: PackageAnalysisResult,
    candidates: list[AlternativeCandidate],
) -> str:
    """Build a bounded prompt with package facts and allowed alternatives."""

    candidate_data = [
        candidate.model_dump(mode="json") for candidate in candidates
    ]

    return (
        "Package fact sheet:\n"
        f"{build_package_fact_sheet(analysis)}\n\n"
        "Allowed alternative candidates:\n"
        f"{json.dumps(candidate_data, ensure_ascii=False, indent=2)}"
    )