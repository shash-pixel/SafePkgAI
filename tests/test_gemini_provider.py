"""Tests for the Gemini structured-output provider."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from pydantic import BaseModel

from llm.gemini_provider import GeminiProvider


class ExampleOutput(BaseModel):
    """Minimal schema used to verify provider validation."""

    value: str


def test_generate_configures_json_schema_and_validates_response() -> None:
    """Gemini JSON is passed through the existing Pydantic validation boundary."""

    generate_content = AsyncMock(
        return_value=SimpleNamespace(text='{"value": "validated"}')
    )
    client = SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content),
        )
    )

    result = asyncio.run(
        GeminiProvider(client=client).generate(
            response_model=ExampleOutput,
            instructions="Return JSON only.",
            input_text="Test input",
        )
    )

    assert result == ExampleOutput(value="validated")
    config = generate_content.await_args.kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == ExampleOutput.model_json_schema()
