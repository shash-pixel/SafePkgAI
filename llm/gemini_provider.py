"""Gemini-backed provider for structured PackageMind AI outputs."""

from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from config.settings import settings
from llm.provider import (
    LLMConfigurationError,
    LLMGenerationError,
    StructuredLLMProvider,
)

OutputModel = TypeVar("OutputModel", bound=BaseModel)


class GeminiStructuredProvider(StructuredLLMProvider):
    """Generate schema-validated outputs with the Google GenAI SDK."""

    def __init__(self, client: genai.Client | None = None) -> None:
        self._client = client

    async def generate(
        self,
        response_model: type[OutputModel],
        instructions: str,
        input_text: str,
    ) -> OutputModel:
        """Request Gemini JSON and validate it with the existing Pydantic model."""

        client = self._get_client()

        try:
            response = await client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=input_text,
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    max_output_tokens=settings.ai_summary_max_output_tokens,
                    response_mime_type="application/json",
                    response_json_schema=response_model.model_json_schema(),
                ),
            )
        except Exception as error:
            raise LLMGenerationError(f"Gemini could not generate a response: {error}") from error
        
        print("GEMINI RESPONSE:")
        print(response)
        
        if not response.text:
            raise LLMGenerationError("Gemini returned no text output.")

        try:
            return response_model.model_validate_json(response.text)
        except ValidationError as error:
            raise LLMGenerationError(
                f"Gemini returned output that did not match the expected schema: {error}"
            ) from error

    def _get_client(self) -> genai.Client:
        """Return an initialized client after validating local configuration."""

        if self._client is not None:
            return self._client

        if not settings.gemini_api_key:
            raise LLMConfigurationError(
                "GEMINI_API_KEY must be configured before AI generation."
            )

        self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client
