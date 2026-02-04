"""Settings module - loads environment variables."""

import os
import logging
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

    @classmethod
    def load(cls) -> "Settings":
        """
        Load settings from environment variables.

        Returns:
            Settings: Configured settings instance.
        """
        return cls(
            # LLM
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

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


# Global settings instance
settings = Settings.load()
