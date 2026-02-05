"""Common constants and utilities for LLM clients."""

import logging
import subprocess
import tempfile
from typing import Final

from config.settings import settings

logger = logging.getLogger(__name__)

# User instruction sent with audio - language neutral
USER_INSTRUCTION: Final[str] = (
    "Transcribe and summarize this audio following the instructions. "
    "Respond in the same language as the audio."
)


# Audio format detection based on magic bytes
AUDIO_SIGNATURES: Final[dict[bytes, str]] = {
    b"OggS": "ogg",
    b"ID3": "mp3",
    b"\xff\xfb": "mp3",
    b"RIFF": "wav",
    b"fLaC": "flac",
}


def detect_audio_format(audio_data: bytes) -> str:
    """
    Detect audio format based on magic bytes.

    Args:
        audio_data: Raw audio data.

    Returns:
        str: The detected format (ogg, mp3, wav, flac, mp4).
    """
    # Check known signatures
    for signature, fmt in AUDIO_SIGNATURES.items():
        if audio_data.startswith(signature):
            return fmt

    # Check for MP4/M4A (ftyp at offset 4)
    if len(audio_data) > 8 and audio_data[4:8] == b"ftyp":
        return "mp4"

    # Default
    return "mp3"


def convert_audio_to_mp3(audio_data: bytes) -> bytes:
    """
    Convert audio data to MP3 format using ffmpeg.

    Args:
        audio_data: Raw audio data in any format.

    Returns:
        bytes: Audio data in MP3 format.

    Raises:
        RuntimeError: If conversion fails or times out.
    """
    with tempfile.NamedTemporaryFile(suffix=".input", delete=True) as input_file:
        input_file.write(audio_data)
        input_file.flush()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as output_file:
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        input_file.name,
                        "-acodec",
                        "libmp3lame",
                        "-ar",
                        str(settings.ffmpeg_sample_rate),
                        "-ac",
                        "1",
                        "-b:a",
                        settings.ffmpeg_bitrate,
                        output_file.name,
                    ],
                    capture_output=True,
                    check=True,
                    timeout=settings.ffmpeg_timeout,
                )
                output_file.seek(0)
                mp3_data = output_file.read()
                logger.info(f"Converted audio to MP3, size: {len(mp3_data)} bytes")
                return mp3_data
            except subprocess.TimeoutExpired:
                raise RuntimeError(f"ffmpeg conversion timed out after {settings.ffmpeg_timeout}s")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}")
