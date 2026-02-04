"""Tests for webhook server."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


class TestWebhookVerification:
    """Tests for webhook verification endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch("webhook.server.settings") as mock_settings:
            mock_settings.whatsapp_verify_token = "test-token"
            mock_settings.setup_logging = MagicMock()
            mock_settings.default_style = "pro"
            mock_settings.default_llm = "openai"

            # Need to reimport after patching
            from webhook.server import app
            return TestClient(app)

    def test_verify_webhook_success(self, client):
        """Test successful webhook verification."""
        response = client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test-token",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 200
        assert response.json() == 12345

    def test_verify_webhook_invalid_token(self, client):
        """Test webhook verification with invalid token."""
        response = client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 403

    def test_verify_webhook_invalid_mode(self, client):
        """Test webhook verification with invalid mode."""
        response = client.get(
            "/webhook",
            params={
                "hub.mode": "invalid",
                "hub.verify_token": "test-token",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 403


class TestHealthCheck:
    """Tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch("webhook.server.settings") as mock_settings:
            mock_settings.setup_logging = MagicMock()
            mock_settings.default_style = "pro"
            mock_settings.default_llm = "openai"

            from webhook.server import app
            return TestClient(app)

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
