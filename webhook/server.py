"""FastAPI webhook server for WhatsApp."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request

from config.prompts import get_prompt
from config.settings import settings
from connectors.whatsapp import WhatsAppClient
from llm.factory import LLMFactory

# Setup logging
settings.setup_logging()
logger = logging.getLogger(__name__)

# Global clients
whatsapp_client: WhatsAppClient | None = None
llm_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global whatsapp_client, llm_client

    # Startup
    logger.info("Starting WhatsApp Audio Summarizer")

    # WhatsApp client (optional for testing)
    try:
        whatsapp_client = WhatsAppClient()
    except ValueError as e:
        logger.warning(f"WhatsApp client not initialized: {e}")
        whatsapp_client = None

    # LLM client (optional for testing)
    try:
        llm_client = LLMFactory.create()
    except ValueError as e:
        logger.warning(f"LLM client not initialized: {e}")
        llm_client = None

    yield

    # Shutdown
    if whatsapp_client:
        await whatsapp_client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="WhatsApp Audio Summarizer",
    description="Webhook server for WhatsApp audio message summarization",
    lifespan=lifespan,
)


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Verify webhook for WhatsApp Cloud API.

    Meta sends a GET request to verify the webhook URL.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)

    logger.warning("Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming WhatsApp webhook events.

    Processes audio messages and sends back summaries.
    """
    body = await request.json()
    logger.info(f"Webhook received: {body.get('object')}")

    try:
        # Extract message data
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        for message in messages:
            await _process_message(message)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")

    # Always return 200 to acknowledge receipt
    return {"status": "ok"}


async def _process_message(message: dict) -> None:
    """Process a single WhatsApp message."""
    message_id = message.get("id")
    message_type = message.get("type")
    sender = message.get("from")

    logger.info(f"Processing {message_type} message from {sender}")

    # Only process audio messages
    if message_type != "audio":
        logger.info(f"Skipping non-audio message type: {message_type}")
        return

    # Check clients are initialized
    if not whatsapp_client or not llm_client:
        logger.error("Clients not initialized, cannot process message")
        return

    # Mark as read
    await whatsapp_client.mark_as_read(message_id)

    # Get audio data
    audio_info = message.get("audio", {})
    media_id = audio_info.get("id")

    if not media_id:
        logger.error("No media ID in audio message")
        return

    try:
        # Download audio
        audio_data = await whatsapp_client.download_media(media_id)

        # Get prompt and summarize
        prompt = get_prompt(settings.default_style)
        result = llm_client.transcribe_and_summarize(
            audio_data=audio_data,
            prompt=prompt,
            style=settings.default_style,
        )

        # Send response
        if result.success:
            response_text = f"📝 *Résumé de l'audio*\n\n{result.summary}"
        else:
            response_text = f"❌ Erreur lors du traitement: {result.error}"

        await whatsapp_client.send_message(
            to=sender,
            text=response_text,
            reply_to_message_id=message_id,
        )

    except Exception as e:
        logger.error(f"Failed to process audio: {e}")
        await whatsapp_client.send_message(
            to=sender,
            text="❌ Désolé, une erreur s'est produite lors du traitement de l'audio.",
            reply_to_message_id=message_id,
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
