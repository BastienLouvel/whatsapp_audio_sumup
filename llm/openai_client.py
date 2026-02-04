"""OpenAI LLM client implementation."""

import base64
import logging

import openai

from config.settings import settings
from llm.base_llm import BaseLLM, SummarizationResult
from llm.common import USER_INSTRUCTION, detect_audio_format, convert_audio_to_mp3


logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLM):
    """
    OpenAI client for audio transcription and summarization.

    Uses GPT-4o-audio-preview which supports native audio input.
    Language is auto-detected.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key.
        """
        super().__init__(api_key)
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.llm_max_tokens
        logger.info(f"OpenAI client initialized with model {self.model}")

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    def transcribe_and_summarize(
        self,
        audio_data: bytes,
        prompt: str,
        style: str = "pro",
    ) -> SummarizationResult:
        """
        Transcribe audio and generate a summary using GPT-4o.

        Uses native audio input - language is auto-detected.

        Args:
            audio_data: Raw audio data in bytes.
            prompt: The system prompt defining the summarization style.
            style: The name of the style being used.

        Returns:
            SummarizationResult: The result containing the summary or error.
        """
        logger.info(f"Processing audio with OpenAI, style: {style}")

        try:
            audio_format = detect_audio_format(audio_data)

            # OpenAI only supports wav and mp3, convert if needed
            if audio_format not in ("wav", "mp3"):
                logger.info(f"Converting {audio_format} to mp3 for OpenAI")
                audio_data = convert_audio_to_mp3(audio_data)
                audio_format = "mp3"

            audio_base64 = base64.standard_b64encode(audio_data).decode("utf-8")

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": audio_base64,
                                    "format": audio_format,
                                },
                            },
                            {"type": "text", "text": USER_INSTRUCTION},
                        ],
                    },
                ],
            )

            if response.choices and response.choices[0].message.content:
                summary = response.choices[0].message.content
                logger.info(f"OpenAI summarization successful, length: {len(summary)}")
                return self._create_success_result(summary, style)
            else:
                error_msg = "OpenAI returned empty response"
                logger.error(error_msg)
                return self._create_error_result(error_msg, style)

        except openai.APIConnectionError as e:
            error_msg = f"Connection error to OpenAI API: {e}"
            logger.error(error_msg)
            return self._create_error_result(error_msg, style)

        except openai.RateLimitError as e:
            error_msg = f"Rate limit exceeded: {e}"
            logger.error(error_msg)
            return self._create_error_result(error_msg, style)

        except openai.APIStatusError as e:
            error_msg = f"API error (status {e.status_code}): {e.message}"
            logger.error(error_msg)
            return self._create_error_result(error_msg, style)

        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {e}"
            logger.error(error_msg)
            return self._create_error_result(error_msg, style)
