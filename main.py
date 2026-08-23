"""Command-line entry point for PackageMind AI."""

import argparse
import asyncio
from pathlib import Path

from core.project_analysis_service import ProjectAnalysisService
from llm.dependency_health_explainer import (
    DependencyHealthExplanationService,
)
from llm.gemini_provider import GeminiStructuredProvider
from llm.provider import LLMConfigurationError, LLMGenerationError
from utils.report_formatter import format_dependency_health_summary


def build_parser() -> argparse.ArgumentParser:
    """Create the PackageMind AI command-line parser."""

    parser = argparse.ArgumentParser(
        description="Generate a Dependency Health Report from a manifest file."
    )
    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to requirements.txt or package.json.",
    )
    parser.add_argument(
        "--with-ai",
        action="store_true",
        help="Generate an optional Gemini-based explanation.",
    )

    return parser


async def run_analysis(
    file_path: Path,
    include_ai_explanation: bool,
) -> None:
    """Run factual dependency analysis and optionally request Gemini guidance."""

    summary = await ProjectAnalysisService().analyze_file(file_path)

    print(format_dependency_health_summary(summary))

    if not include_ai_explanation:
        return

    explanation_service = DependencyHealthExplanationService(
        provider=GeminiStructuredProvider()
    )
    explanation = await explanation_service.explain(summary)

    print("\nAI Dependency Health Guidance")
    print("=" * 30)
    print(explanation.overall_summary)

    if explanation.health_highlights:
        print("\nHighlights:")
        for item in explanation.health_highlights:
            print(f"- {item}")

    if explanation.recommended_actions:
        print("\nRecommended Actions:")
        for item in explanation.recommended_actions:
            print(f"- {item}")

    if explanation.limitations:
        print("\nAI Limitations:")
        for item in explanation.limitations:
            print(f"- {item}")


def main() -> int:
    """Run the PackageMind AI command-line application."""

    arguments = build_parser().parse_args()

    try:
        asyncio.run(
            run_analysis(
                file_path=arguments.file,
                include_ai_explanation=arguments.with_ai,
            )
        )
    except (
        FileNotFoundError,
        OSError,
        ValueError,
        LLMConfigurationError,
        LLMGenerationError,
    ) as error:
        print(f"Analysis failed: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())