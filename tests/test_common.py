"""Tests for LLM common utilities."""

import pytest

from llm.common import detect_audio_format, AUDIO_SIGNATURES


class TestDetectAudioFormat:
    """Tests for detect_audio_format function."""

    def test_detect_ogg_format(self):
        """Test OGG format detection."""
        ogg_header = b"OggS" + b"\x00" * 100
        assert detect_audio_format(ogg_header) == "ogg"

    def test_detect_mp3_id3_format(self):
        """Test MP3 with ID3 header detection."""
        mp3_header = b"ID3" + b"\x00" * 100
        assert detect_audio_format(mp3_header) == "mp3"

    def test_detect_mp3_sync_format(self):
        """Test MP3 with sync word detection."""
        mp3_header = b"\xff\xfb" + b"\x00" * 100
        assert detect_audio_format(mp3_header) == "mp3"

    def test_detect_wav_format(self):
        """Test WAV format detection."""
        wav_header = b"RIFF" + b"\x00" * 100
        assert detect_audio_format(wav_header) == "wav"

    def test_detect_flac_format(self):
        """Test FLAC format detection."""
        flac_header = b"fLaC" + b"\x00" * 100
        assert detect_audio_format(flac_header) == "flac"

    def test_detect_mp4_format(self):
        """Test MP4/M4A format detection."""
        mp4_header = b"\x00\x00\x00\x20ftyp" + b"\x00" * 100
        assert detect_audio_format(mp4_header) == "mp4"

    def test_detect_unknown_format_defaults_to_mp3(self):
        """Test unknown format defaults to mp3."""
        unknown_header = b"\x00\x01\x02\x03" * 25
        assert detect_audio_format(unknown_header) == "mp3"

    def test_detect_empty_data_defaults_to_mp3(self):
        """Test empty data defaults to mp3."""
        assert detect_audio_format(b"") == "mp3"


class TestAudioSignatures:
    """Tests for AUDIO_SIGNATURES constant."""

    def test_signatures_are_bytes(self):
        """Test all signatures are bytes."""
        for sig in AUDIO_SIGNATURES.keys():
            assert isinstance(sig, bytes)

    def test_formats_are_strings(self):
        """Test all formats are strings."""
        for fmt in AUDIO_SIGNATURES.values():
            assert isinstance(fmt, str)

    def test_expected_formats_present(self):
        """Test expected formats are present."""
        formats = set(AUDIO_SIGNATURES.values())
        assert "ogg" in formats
        assert "mp3" in formats
        assert "wav" in formats
        assert "flac" in formats
