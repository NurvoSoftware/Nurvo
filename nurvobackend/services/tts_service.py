"""Text-to-Speech service using Eleven Labs API."""

import base64

import httpx

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_FAMILY_VOICE_ID,
    ELEVENLABS_PATIENT_VOICE_ID,
)

_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
_TIMEOUT = 15.0


async def synthesize_speech(text: str, voice_id: str) -> str:
    """Synthesize speech from text using Eleven Labs TTS API.

    Returns base64-encoded audio on success, empty string on failure.
    """
    if not ELEVENLABS_API_KEY or not voice_id:
        return ""

    url = _TTS_URL.format(voice_id=voice_id)
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            audio_bytes = response.content
            return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception:
        # Fallback to text-only on any failure
        return ""


async def get_patient_voice(text: str) -> str:
    """Get TTS audio for patient voice."""
    return await synthesize_speech(text, ELEVENLABS_PATIENT_VOICE_ID)


async def get_family_voice(text: str) -> str:
    """Get TTS audio for family member voice."""
    return await synthesize_speech(text, ELEVENLABS_FAMILY_VOICE_ID)
