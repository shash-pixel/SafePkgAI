"""Service for AI-generated package explanations."""

from llm.provider import StructuredLLMProvider
from models.analysis import PackageAnalysisResult
from models.explanation import PackageExplanation
from prompts.package_explanation import (
    PACKAGE_EXPLANATION_INSTRUCTIONS,
    build_package_explanation_input,
)


class PackageExplanationService:
    """Generate a grounded explanation for deterministic package analysis."""

    def __init__(self, provider: StructuredLLMProvider) -> None:
        self._provider = provider

    async def explain(
        self,
        analysis: PackageAnalysisResult,
    ) -> PackageExplanation:
        """Return a structured AI explanation of one package."""

        return await self._provider.generate(
            response_model=PackageExplanation,
            instructions=PACKAGE_EXPLANATION_INSTRUCTIONS,
            input_text=build_package_explanation_input(analysis),
        )