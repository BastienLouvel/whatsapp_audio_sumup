"""Tests for LLM factory module."""

from unittest.mock import MagicMock, patch

import pytest

from llm.factory import LLMFactory
from llm.gemini_client import GeminiClient
from llm.openai_client import OpenAIClient


class TestLLMFactory:
    """Tests for LLMFactory class."""

    def test_available_providers(self):
        """Test available_providers returns expected providers."""
        providers = LLMFactory.available_providers()
        assert "openai" in providers
        assert "gemini" in providers
        assert len(providers) == 2

    def test_create_openai_client(self):
        """Test creating OpenAI client."""
        with patch.object(OpenAIClient, "__init__", return_value=None):
            client = LLMFactory.create(provider="openai", api_key="test-key")
            assert isinstance(client, OpenAIClient)

    def test_create_gemini_client(self):
        """Test creating Gemini client."""
        with patch.object(GeminiClient, "__init__", return_value=None):
            client = LLMFactory.create(provider="gemini", api_key="test-key")
            assert isinstance(client, GeminiClient)

    def test_create_unknown_provider_raises_error(self):
        """Test creating client with unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMFactory.create(provider="unknown", api_key="test-key")

    def test_create_uses_default_provider(self):
        """Test create uses default provider from settings."""
        with patch("llm.factory.settings") as mock_settings:
            mock_settings.default_llm = "openai"
            mock_settings.get_api_key.return_value = "test-key"
            with patch.object(OpenAIClient, "__init__", return_value=None):
                client = LLMFactory.create()
                assert isinstance(client, OpenAIClient)
                mock_settings.get_api_key.assert_called_once_with("openai")

    def test_register_new_provider(self):
        """Test registering a new provider."""
        mock_client_class = MagicMock()
        LLMFactory.register("custom", mock_client_class)
        assert "custom" in LLMFactory.available_providers()
        # Clean up
        del LLMFactory._clients["custom"]
