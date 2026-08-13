"""Interfaces and errors for structured LLM generation."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

OutputModel = TypeVar("OutputModel", bound=BaseModel)


class LLMConfigurationError(RuntimeError):
    """Raised when required LLM configuration is unavailable."""


class LLMGenerationError(RuntimeError):
    """Raised when an LLM response cannot be generated or validated."""


class StructuredLLMProvider(ABC):
    """Defines a provider that returns validated structured output."""

    @abstractmethod
    async def generate(
        self,
        response_model: type[OutputModel],
        instructions: str,
        input_text: str,
    ) -> OutputModel:
        """Generate and validate one structured response."""