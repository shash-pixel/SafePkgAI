"""Service for candidate-constrained AI package recommendations."""

from llm.provider import StructuredLLMProvider
from models.analysis import PackageAnalysisResult
from models.recommendation import (
    AlternativeRecommendation,
    AlternativeRecommendationDecision,
    AlternativeRecommendationSet,
)
from prompts.alternative_recommendations import (
    ALTERNATIVE_RECOMMENDATION_INSTRUCTIONS,
    build_alternative_recommendation_input,
)
from recommendations.catalog import get_alternative_candidates


class AlternativeRecommendationService:
    """Generate AI rationale for alternatives from the curated catalog."""

    def __init__(self, provider: StructuredLLMProvider) -> None:
        self._provider = provider

    async def recommend(
        self,
        analysis: PackageAnalysisResult,
    ) -> AlternativeRecommendationSet:
        """Return validated alternative recommendations for one package."""

        metadata = analysis.metadata
        candidates = get_alternative_candidates(
            metadata.reference.ecosystem,
            metadata.reference.name,
        )

        if not candidates:
            return AlternativeRecommendationSet(
                source_package=metadata.reference,
                catalog_note=(
                    "No curated alternatives are available for this package yet."
                ),
            )

        decision = await self._provider.generate(
            response_model=AlternativeRecommendationDecision,
            instructions=ALTERNATIVE_RECOMMENDATION_INSTRUCTIONS,
            input_text=build_alternative_recommendation_input(
                analysis,
                candidates,
            ),
        )

        validated_recommendations = self._validate_recommendations(
            decision,
            candidates,
        )

        return AlternativeRecommendationSet(
            source_package=metadata.reference,
            recommendations=validated_recommendations,
            catalog_note=(
                "Recommendations are selected only from the curated candidate list."
            ),
        )

    @staticmethod
    def _validate_recommendations(
        decision: AlternativeRecommendationDecision,
        candidates: list,
    ) -> list[AlternativeRecommendation]:
        """Keep only unique recommendations that match approved candidates."""

        approved_names = {
            candidate.name.casefold(): candidate.name for candidate in candidates
        }
        validated: list[AlternativeRecommendation] = []
        seen_names: set[str] = set()

        for recommendation in decision.recommendations:
            normalized_name = recommendation.alternative_name.casefold()

            if normalized_name not in approved_names:
                continue

            if normalized_name in seen_names:
                continue

            seen_names.add(normalized_name)
            validated.append(
                recommendation.model_copy(
                    update={
                        "alternative_name": approved_names[normalized_name],
                    }
                )
            )

        return validated[:2]