"""Tests for webhook server."""


class TestWebhookVerification:
    """Tests for webhook verification endpoint."""

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

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestWebhookPost:
    """Tests for webhook POST endpoint."""

    def test_webhook_post_returns_ok(self, client):
        """Test webhook POST returns ok status."""
        response = client.post(
            "/webhook",
            json={
                "object": "whatsapp_business_account",
                "entry": [],
            },
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_webhook_post_empty_messages(self, client):
        """Test webhook POST with empty messages."""
        response = client.post(
            "/webhook",
            json={
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "changes": [
                            {
                                "value": {
                                    "messages": [],
                                },
                            },
                        ],
                    },
                ],
            },
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
