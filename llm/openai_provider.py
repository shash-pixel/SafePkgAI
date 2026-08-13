"""OpenAI-backed provider for structured PackageMind AI outputs."""

from typing import TypeVar

from openai import APIError, AsyncOpenAI
from pydantic import BaseModel, ValidationError

from config.settings import settings
from llm.provider import (
    LLMConfigurationError,
    LLMGenerationError,
    StructuredLLMProvider,
)

OutputModel = TypeVar("OutputModel", bound=BaseModel)


class OpenAIStructuredProvider(StructuredLLMProvider):
    """Generate schema-validated outputs with the OpenAI Responses API."""

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client

    async def generate(
        self,
        response_model: type[OutputModel],
        instructions: str,
        input_text: str,
    ) -> OutputModel:
        """Request and validate one structured model response."""

        client = self._get_client()

        try:
            response = await client.responses.create(
                model=settings.openai_model,
                instructions=instructions,
                input=input_text,
                max_output_tokens=settings.ai_summary_max_output_tokens,
                text={
                    "verbosity": "low",
                    "format": {
                        "type": "json_schema",
                        "name": response_model.__name__.lower(),
                        "schema": response_model.model_json_schema(),
                        "strict": True,
                    },
                },
            )
        except APIError as error:
            raise LLMGenerationError("OpenAI could not generate a response.") from error

        if not response.output_text:
            raise LLMGenerationError("OpenAI returned no text output.")

        try:
            return response_model.model_validate_json(response.output_text)
        except ValidationError as error:
            raise LLMGenerationError(
                "OpenAI returned output that did not match the expected schema."
            ) from error

    def _get_client(self) -> AsyncOpenAI:
        """Return an initialized client after validating local configuration."""

        if self._client is not None:
            return self._client

        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY must be configured before AI generation."
            )

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client