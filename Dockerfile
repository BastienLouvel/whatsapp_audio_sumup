FROM python:3.12-slim

LABEL maintainer="WhatsApp Audio Summarizer"
LABEL version="1.0.0"
LABEL description="WhatsApp webhook server for audio message summarization"

WORKDIR /app

# Install ffmpeg for audio conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["uvicorn", "webhook.server:app", "--host", "0.0.0.0", "--port", "8000"]
