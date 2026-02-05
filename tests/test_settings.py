"""Tests for settings module."""

import os
from unittest.mock import patch

import pytest

from config.settings import Settings


class TestSettings:
    """Tests for Settings class."""

    def test_load_with_defaults(self):
        """Test loading settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.load()
            assert settings.default_llm == "openai"
            assert settings.default_style == "pro"
            assert settings.log_level == "INFO"
            assert settings.openai_model == "gpt-4o-audio-preview"
            assert settings.gemini_model == "gemini-2.0-flash"
            assert settings.llm_max_tokens == 4096
            assert settings.llm_temperature == 0.7
            assert settings.facebook_api_version == "v18.0"
            assert settings.http_timeout == 30.0
            assert settings.ffmpeg_sample_rate == 16000
            assert settings.ffmpeg_bitrate == "64k"
            assert settings.ffmpeg_timeout == 300
            assert settings.max_audio_size_mb == 50

    def test_load_from_environment(self):
        """Test loading settings from environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai-key",
            "GOOGLE_API_KEY": "test-google-key",
            "DEFAULT_LLM": "gemini",
            "DEFAULT_STYLE": "technique",
            "LOG_LEVEL": "DEBUG",
            "OPENAI_MODEL": "gpt-4-turbo",
            "LLM_MAX_TOKENS": "2048",
            "HTTP_TIMEOUT": "60.0",
            "MAX_AUDIO_SIZE_MB": "100",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings.load()
            assert settings.openai_api_key == "test-openai-key"
            assert settings.google_api_key == "test-google-key"
            assert settings.default_llm == "gemini"
            assert settings.default_style == "technique"
            assert settings.log_level == "DEBUG"
            assert settings.openai_model == "gpt-4-turbo"
            assert settings.llm_max_tokens == 2048
            assert settings.http_timeout == 60.0
            assert settings.max_audio_size_mb == 100

    def test_get_api_key_openai(self):
        """Test getting OpenAI API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            settings = Settings.load()
            assert settings.get_api_key("openai") == "test-key"

    def test_get_api_key_gemini(self):
        """Test getting Gemini API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}, clear=True):
            settings = Settings.load()
            assert settings.get_api_key("gemini") == "test-key"

    def test_get_api_key_missing_raises_error(self):
        """Test getting missing API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.load()
            with pytest.raises(ValueError, match="API key not configured"):
                settings.get_api_key("openai")

    def test_facebook_base_url(self):
        """Test Facebook base URL property."""
        with patch.dict(os.environ, {"FACEBOOK_API_VERSION": "v19.0"}, clear=True):
            settings = Settings.load()
            assert settings.facebook_base_url == "https://graph.facebook.com/v19.0"

    def test_max_audio_size_bytes(self):
        """Test max audio size in bytes property."""
        with patch.dict(os.environ, {"MAX_AUDIO_SIZE_MB": "10"}, clear=True):
            settings = Settings.load()
            assert settings.max_audio_size_bytes == 10 * 1024 * 1024
