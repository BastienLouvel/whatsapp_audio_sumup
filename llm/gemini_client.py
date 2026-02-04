"""Google Gemini LLM client implementation."""

import logging

from google import genai
from google.genai import types

from config.settings import settings
from llm.base_llm import BaseLLM, SummarizationResult
from llm.common import USER_INSTRUCTION, detect_audio_format


logger = logging.getLogger(__name__)

# Mapping from generic format to MIME type
MIME_TYPES: dict[str, str] = {
    "ogg": "audio/ogg",
    "mp3": "audio/mp3",
    "wav": "audio/wav",
    "flac": "audio/flac",
    "mp4": "audio/mp4",
}


class GeminiClient(BaseLLM):
    """
    Google Gemini client for audio transcription and summarization.

    Gemini supports audio through inline data.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the Gemini client.

        Args:
            api_key: Google API key.
        """
        super().__init__(api_key)
        self.client = genai.Client(api_key=self.api_key)
        self.model = settings.gemini_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        logger.info(f"Gemini client initialized with model {self.model}")

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"

    def transcribe_and_summarize(
        self,
        audio_data: bytes,
        prompt: str,
        style: str = "pro",
    ) -> SummarizationResult:
        """
        Transcribe audio and generate a summary using Gemini.

        Args:
            audio_data: Raw audio data in bytes.
            prompt: The system prompt defining the summarization style.
            style: The name of the style being used.

        Returns:
            SummarizationResult: The result containing the summary or error.
        """
        logger.info(f"Processing audio with Gemini, style: {style}")

        try:
            audio_format = detect_audio_format(audio_data)
            mime_type = MIME_TYPES.get(audio_format, "audio/mp3")

            full_prompt = f"{prompt}\n\n{USER_INSTRUCTION}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(full_prompt),
                            types.Part.from_bytes(data=audio_data, mime_type=mime_type),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                ),
            )

            if response.text:
                summary = response.text
                logger.info(f"Gemini summarization successful, length: {len(summary)}")
                return self._create_success_result(summary, style)
            else:
                error_msg = "Gemini returned empty response"
                logger.error(error_msg)
                return self._create_error_result(error_msg, style)

        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {e}"
            logger.error(error_msg)
            return self._create_error_result(error_msg, style)
