"""Base LLM abstract class."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SummarizationResult:
    """Result of audio transcription and summarization."""

    summary: str
    provider: str
    style: str
    success: bool
    error: Optional[str] = None


class BaseLLM(ABC):
    """
    Abstract base class for LLM clients.

    All LLM implementations must inherit from this class and implement
    the transcribe_and_summarize method.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the LLM client.

        Args:
            api_key: API key for the LLM provider.
        """
        self.api_key = api_key
        self._validate_api_key()

    def _validate_api_key(self) -> None:
        """
        Validate that the API key is provided.

        Raises:
            ValueError: If the API key is empty.
        """
        if not self.api_key:
            raise ValueError(f"API key is required for {self.provider_name}")

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            str: The name of the LLM provider.
        """
        pass

    @abstractmethod
    def transcribe_and_summarize(
        self,
        audio_data: bytes,
        prompt: str,
        style: str = "pro",
    ) -> SummarizationResult:
        """
        Transcribe audio and generate a summary.

        Args:
            audio_data: Raw audio data in bytes (typically base64 decoded).
            prompt: The system prompt defining the summarization style.
            style: The name of the style being used (for logging/result).

        Returns:
            SummarizationResult: The result containing the summary or error.
        """
        pass

    def _create_success_result(self, summary: str, style: str) -> SummarizationResult:
        """
        Create a successful result.

        Args:
            summary: The generated summary.
            style: The style used.

        Returns:
            SummarizationResult: A successful result.
        """
        return SummarizationResult(
            summary=summary,
            provider=self.provider_name,
            style=style,
            success=True,
        )

    def _create_error_result(self, error: str, style: str) -> SummarizationResult:
        """
        Create an error result.

        Args:
            error: The error message.
            style: The style that was attempted.

        Returns:
            SummarizationResult: An error result.
        """
        return SummarizationResult(
            summary="",
            provider=self.provider_name,
            style=style,
            success=False,
            error=error,
        )
