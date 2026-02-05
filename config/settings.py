"""Settings module - loads environment variables.

Environment Variables:
    OPENAI_API_KEY: OpenAI API key (required if using OpenAI)
    GOOGLE_API_KEY: Google API key (required if using Gemini)
    WHATSAPP_PHONE_NUMBER_ID: WhatsApp Business phone number ID
    WHATSAPP_ACCESS_TOKEN: Meta API access token
    WHATSAPP_VERIFY_TOKEN: Webhook verification token
    DEFAULT_LLM: Default LLM provider (openai, gemini)
    DEFAULT_STYLE: Default summarization style (pro, humoristique, technique)
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    OPENAI_MODEL: OpenAI model to use
    GEMINI_MODEL: Gemini model to use
    LLM_MAX_TOKENS: Maximum tokens for LLM response
    LLM_TEMPERATURE: Temperature for LLM response
    FACEBOOK_API_VERSION: Facebook Graph API version
    HTTP_TIMEOUT: HTTP client timeout in seconds
    FFMPEG_SAMPLE_RATE: Audio sample rate for conversion
    FFMPEG_BITRATE: Audio bitrate for conversion
    FFMPEG_TIMEOUT: FFmpeg conversion timeout in seconds
    MAX_AUDIO_SIZE_MB: Maximum audio file size in MB
"""

import logging
import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

# Load .env file
load_dotenv()


LLMProvider = Literal["openai", "gemini"]
SummarizationStyle = Literal["pro", "humoristique", "technique"]


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # LLM API Keys
    openai_api_key: str
    google_api_key: str

    # WhatsApp Business API
    whatsapp_phone_number_id: str
    whatsapp_access_token: str
    whatsapp_verify_token: str

    # Defaults
    default_llm: LLMProvider
    default_style: SummarizationStyle

    # Logging
    log_level: str

    # LLM Configuration
    openai_model: str
    gemini_model: str
    llm_max_tokens: int
    llm_temperature: float

    # API Configuration
    facebook_api_version: str
    http_timeout: float

    # FFmpeg Configuration
    ffmpeg_sample_rate: int
    ffmpeg_bitrate: str
    ffmpeg_timeout: int

    # Limits
    max_audio_size_mb: int

    @classmethod
    def load(cls) -> "Settings":
        """
        Load settings from environment variables.

        Returns:
            Settings: Configured settings instance.
        """
        return cls(
            # LLM API Keys
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            # WhatsApp
            whatsapp_phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
            whatsapp_access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
            whatsapp_verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", ""),
            # Defaults
            default_llm=os.getenv("DEFAULT_LLM", "openai"),  # type: ignore
            default_style=os.getenv("DEFAULT_STYLE", "pro"),  # type: ignore
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            # LLM Configuration
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-audio-preview"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            # API Configuration
            facebook_api_version=os.getenv("FACEBOOK_API_VERSION", "v18.0"),
            http_timeout=float(os.getenv("HTTP_TIMEOUT", "30.0")),
            # FFmpeg Configuration
            ffmpeg_sample_rate=int(os.getenv("FFMPEG_SAMPLE_RATE", "16000")),
            ffmpeg_bitrate=os.getenv("FFMPEG_BITRATE", "64k"),
            ffmpeg_timeout=int(os.getenv("FFMPEG_TIMEOUT", "300")),
            # Limits
            max_audio_size_mb=int(os.getenv("MAX_AUDIO_SIZE_MB", "50")),
        )

    def get_api_key(self, provider: LLMProvider) -> str:
        """
        Get API key for a specific provider.

        Args:
            provider: The LLM provider name.

        Returns:
            str: The API key for the specified provider.

        Raises:
            ValueError: If the API key is not configured.
        """
        keys = {
            "openai": self.openai_api_key,
            "gemini": self.google_api_key,
        }
        key = keys.get(provider, "")
        if not key:
            raise ValueError(f"API key not configured for provider: {provider}")
        return key

    @property
    def facebook_base_url(self) -> str:
        """Get Facebook Graph API base URL."""
        return f"https://graph.facebook.com/{self.facebook_api_version}"

    @property
    def max_audio_size_bytes(self) -> int:
        """Get maximum audio size in bytes."""
        return self.max_audio_size_mb * 1024 * 1024

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


# Global settings instance
settings = Settings.load()
