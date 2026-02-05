"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app instance."""
    # Patch settings before importing app
    from config.settings import settings

    # Override settings for tests
    settings.whatsapp_verify_token = "test-token"
    settings.whatsapp_phone_number_id = "test-phone-id"
    settings.whatsapp_access_token = "test-access-token"
    settings.openai_api_key = "test-openai-key"
    settings.google_api_key = "test-google-key"

    from webhook.server import app
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)
