# WhatsApp Audio Summarizer

A FastAPI webhook server that automatically transcribes and summarizes WhatsApp audio messages using LLM (OpenAI or Google Gemini).

## Features

- Receives WhatsApp audio messages via webhook
- Automatic audio format detection and conversion (OGG → MP3)
- Transcription and summarization using OpenAI GPT-4o or Google Gemini
- Multiple summarization styles (professional, humorous, technical)
- Docker support with ngrok for local development

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   WhatsApp      │────▶│  FastAPI Server  │────▶│   LLM API   │
│   Cloud API     │◀────│    (webhook)     │◀────│ (OpenAI/    │
└─────────────────┘     └──────────────────┘     │  Gemini)    │
                               │                 └─────────────┘
                               ▼
                        ┌──────────────┐
                        │   ffmpeg     │
                        │  (audio      │
                        │  conversion) │
                        └──────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- WhatsApp Business API account ([Meta Developer Portal](https://developers.facebook.com/))
- OpenAI API key or Google API key
- Ngrok account (for local development)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/BastienLouvel/whatsapp_audio_sumup.git
   cd whatsapp_audio_sumup
   ```

2. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your credentials:
   ```env
   OPENAI_API_KEY=sk-...
   WHATSAPP_PHONE_NUMBER_ID=123456789
   WHATSAPP_ACCESS_TOKEN=EAAc...
   WHATSAPP_VERIFY_TOKEN=your_custom_token
   NGROK_AUTHTOKEN=your_ngrok_token
   ```

4. Start the services:
   ```bash
   docker compose up -d
   ```

5. Get the ngrok URL:
   ```bash
   curl -s http://localhost:4040/api/tunnels | jq '.tunnels[0].public_url'
   ```

6. Configure the webhook in Meta Developer Portal:
   - Callback URL: `https://your-ngrok-url.ngrok.io/webhook`
   - Verify Token: your `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to `messages` field

## Configuration

All configuration is done via environment variables. The following can be set in `docker-compose.yml`:

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_LLM` | `openai` | LLM provider (`openai` or `gemini`) |
| `DEFAULT_STYLE` | `pro` | Summarization style (`pro`, `humoristique`, `technique`) |
| `OPENAI_MODEL` | `gpt-4o-audio-preview` | OpenAI model |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model |
| `LLM_MAX_TOKENS` | `4096` | Maximum response tokens |
| `LLM_TEMPERATURE` | `0.7` | Response temperature |

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FACEBOOK_API_VERSION` | `v18.0` | Facebook Graph API version |
| `HTTP_TIMEOUT` | `30.0` | HTTP client timeout (seconds) |

### FFmpeg Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FFMPEG_SAMPLE_RATE` | `16000` | Audio sample rate |
| `FFMPEG_BITRATE` | `64k` | Audio bitrate |
| `FFMPEG_TIMEOUT` | `300` | Conversion timeout (seconds) |

### Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_AUDIO_SIZE_MB` | `50` | Maximum audio file size |
| `LOG_LEVEL` | `INFO` | Logging level |

## Summarization Styles

### Professional (`pro`)
Structured summary with key points, decisions, and action items.

### Humorous (`humoristique`)
Light-hearted summary with humor while preserving key information.

### Technical (`technique`)
Detailed technical summary with terminology and specifications.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | GET | Webhook verification |
| `/webhook` | POST | Receive WhatsApp messages |
| `/health` | GET | Health check |

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn webhook.server:app --reload --port 8000
```

### Project Structure

```
.
├── config/
│   ├── prompts.py      # Summarization prompts
│   └── settings.py     # Configuration management
├── connectors/
│   └── whatsapp.py     # WhatsApp API client
├── llm/
│   ├── base_llm.py     # Abstract base class
│   ├── common.py       # Shared utilities
│   ├── factory.py      # LLM factory
│   ├── gemini_client.py
│   └── openai_client.py
├── webhook/
│   └── server.py       # FastAPI application
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Troubleshooting

### Common Issues

**"Business Account locked"**
- Your WhatsApp Business account is locked by Meta. Check your Business Manager.

**Audio conversion fails**
- Ensure ffmpeg is installed and working
- Check audio file size is under the limit

**Webhook not receiving messages**
- Verify ngrok is running and URL is correct
- Check webhook subscription in Meta Developer Portal
- Ensure `messages` field is subscribed

### Logs

View logs:
```bash
docker compose logs -f whatsapp-summarizer
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
