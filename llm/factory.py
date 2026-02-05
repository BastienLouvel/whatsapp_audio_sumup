"""LLM Factory for instantiating the appropriate LLM client."""

import logging
from typing import Optional

from config.settings import LLMProvider, settings
from llm.base_llm import BaseLLM
from llm.gemini_client import GeminiClient
from llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory class for creating LLM client instances.

    Uses the Factory pattern to instantiate the appropriate client
    based on the provider name.
    """

    _clients: dict[str, type[BaseLLM]] = {
        "openai": OpenAIClient,
        "gemini": GeminiClient,
    }

    @classmethod
    def create(
        cls,
        provider: Optional[LLMProvider] = None,
        api_key: Optional[str] = None,
    ) -> BaseLLM:
        """
        Create an LLM client instance.

        Args:
            provider: The LLM provider name. Uses default if not specified.
            api_key: The API key. Uses settings if not specified.

        Returns:
            BaseLLM: An instance of the appropriate LLM client.

        Raises:
            ValueError: If the provider is not recognized.
        """
        # Use default provider if not specified
        if provider is None:
            provider = settings.default_llm
            logger.info(f"Using default LLM provider: {provider}")

        # Validate provider
        if provider not in cls._clients:
            available = list(cls._clients.keys())
            raise ValueError(f"Unknown provider: {provider}. Available: {available}")

        # Get API key from settings if not provided
        if api_key is None:
            api_key = settings.get_api_key(provider)

        # Create and return client
        client_class = cls._clients[provider]
        logger.info(f"Creating {provider} client")
        return client_class(api_key)

    @classmethod
    def available_providers(cls) -> list[str]:
        """
        Get list of available LLM providers.

        Returns:
            list[str]: List of provider names.
        """
        return list(cls._clients.keys())

    @classmethod
    def register(cls, name: str, client_class: type[BaseLLM]) -> None:
        """
        Register a new LLM client class.

        Args:
            name: The provider name.
            client_class: The client class to register.
        """
        cls._clients[name] = client_class
        logger.info(f"Registered new LLM provider: {name}")
