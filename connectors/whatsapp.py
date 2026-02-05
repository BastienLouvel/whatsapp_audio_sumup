"""WhatsApp Business API client."""

import logging
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Client for WhatsApp Business Cloud API.

    Handles sending messages and downloading media.
    """

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        """
        Initialize WhatsApp client.

        Args:
            phone_number_id: WhatsApp Business phone number ID.
            access_token: Meta API access token.
        """
        self.phone_number_id = phone_number_id or settings.whatsapp_phone_number_id
        self.access_token = access_token or settings.whatsapp_access_token
        self.base_url = settings.facebook_base_url

        if not self.phone_number_id or not self.access_token:
            raise ValueError("WhatsApp credentials not configured")

        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=settings.http_timeout,
        )
        logger.info("WhatsApp client initialized")

    async def send_message(
        self,
        to: str,
        text: str,
        reply_to_message_id: Optional[str] = None,
    ) -> dict:
        """
        Send a text message.

        Args:
            to: Recipient phone number (with country code, no +).
            text: Message text.
            reply_to_message_id: Message ID to reply to.

        Returns:
            dict: API response.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        if reply_to_message_id:
            payload["context"] = {"message_id": reply_to_message_id}

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Message sent to {to}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def download_media(self, media_id: str) -> bytes:
        """
        Download media content.

        Args:
            media_id: WhatsApp media ID.

        Returns:
            bytes: Raw media content.

        Raises:
            ValueError: If media URL is missing or file is too large.
            httpx.HTTPError: If download fails.
        """
        # Step 1: Get media URL
        url = f"{self.base_url}/{media_id}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            media_url = response.json().get("url")

            if not media_url:
                raise ValueError("No URL in media response")

            # Step 2: Download the actual media
            response = await self.client.get(media_url)
            response.raise_for_status()

            content = response.content
            content_size = len(content)

            # Check file size limit
            if content_size > settings.max_audio_size_bytes:
                raise ValueError(
                    f"Audio file too large: {content_size / 1024 / 1024:.1f}MB "
                    f"(max: {settings.max_audio_size_mb}MB)"
                )

            logger.info(f"Downloaded media {media_id}, size: {content_size} bytes")
            return content

        except httpx.HTTPError as e:
            logger.error(f"Failed to download media: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> None:
        """
        Mark a message as read.

        Args:
            message_id: Message ID to mark as read.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Marked message {message_id} as read")
        except httpx.HTTPError as e:
            logger.error(f"Failed to mark as read: {e}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
