"""Gemini-backed explanation service for Dependency Health Reports."""

from llm.provider import StructuredLLMProvider
from models.dependency_health_explanation import (
    DependencyHealthExplanation,
)
from models.dependency_health_summary import DependencyHealthSummary
from prompts.dependency_health_report import (
    DEPENDENCY_HEALTH_INSTRUCTIONS,
    build_dependency_health_input,
)


class DependencyHealthExplanationService:
    """Generate a structured explanation from verified health facts."""

    def __init__(self, provider: StructuredLLMProvider) -> None:
        self._provider = provider

    async def explain(
        self,
        summary: DependencyHealthSummary,
    ) -> DependencyHealthExplanation:
        """Return Gemini-generated, Pydantic-validated health guidance."""

        return await self._provider.generate(
            response_model=DependencyHealthExplanation,
            instructions=DEPENDENCY_HEALTH_INSTRUCTIONS,
            input_text=build_dependency_health_input(summary),
        )