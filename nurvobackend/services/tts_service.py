"""Text-to-Speech service using Eleven Labs API."""

import base64
import logging

import httpx

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_FAMILY_VOICE_ID_0,
    ELEVENLABS_FAMILY_VOICE_ID_1,
    ELEVENLABS_FAMILY_VOICE_ID_2,
    ELEVENLABS_PATIENT_VOICE_ID,
)

logger = logging.getLogger(__name__)

_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
_TIMEOUT = 15.0


async def synthesize_speech(text: str, voice_id: str) -> str:
    """Synthesize speech from text using Eleven Labs TTS API.

    Returns base64-encoded audio on success, empty string on failure.
    """
    if not ELEVENLABS_API_KEY or not voice_id:
        logger.warning("TTS skipped: ELEVENLABS_API_KEY or voice_id is empty")
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
    except httpx.HTTPStatusError as exc:
        logger.error("TTS API error %s: %s", exc.response.status_code, exc.response.text[:200])
        return ""
    except Exception as exc:
        logger.error("TTS failed: %s", exc)
        return ""


async def get_patient_voice(text: str) -> str:
    """Get TTS audio for patient voice."""
    return await synthesize_speech(text, ELEVENLABS_PATIENT_VOICE_ID)


async def get_family_voice(text: str, family_index: int = 0) -> str:
    """Get TTS audio for family member voice."""
    voices = [
        ELEVENLABS_FAMILY_VOICE_ID_0,
        ELEVENLABS_FAMILY_VOICE_ID_1,
        ELEVENLABS_FAMILY_VOICE_ID_2,
    ]
    voice_id = voices[family_index] if 0 <= family_index < len(voices) else voices[0]
    return await synthesize_speech(text, voice_id)
