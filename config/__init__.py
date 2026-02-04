"""Configuration module for WhatsApp Audio Summarizer."""

from config.settings import Settings
from config.prompts import STYLES, get_prompt

__all__ = ["Settings", "STYLES", "get_prompt"]
