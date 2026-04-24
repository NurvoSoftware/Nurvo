"""Speech-to-Text service using ElevenLabs Scribe API."""

import logging

import httpx

from config import ELEVENLABS_API_KEY

logger = logging.getLogger(__name__)

_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
_TIMEOUT = 30.0

STT_USER_FACING_ERROR = "語音轉文字失敗，請稍後再試。"
_MAX_BODY_LOG = 500


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio using ElevenLabs Scribe v2.

    Returns transcribed text on success, empty string on failure.
    """
    if not ELEVENLABS_API_KEY:
        return ""

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    files = {
        "file": (filename, audio_bytes, "audio/webm"),
    }
    data = {
        "model_id": "scribe_v2",
        "language_code": "zho",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                _STT_URL, headers=headers, files=files, data=data
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
    except httpx.HTTPStatusError as e:
        body_snip = (e.response.text or "")[:_MAX_BODY_LOG]
        logger.error(
            "STT API HTTP %s: %s",
            e.response.status_code,
            body_snip,
        )
        raise ValueError(STT_USER_FACING_ERROR)
    except Exception:
        logger.exception("STT transcription failed")
        raise ValueError(STT_USER_FACING_ERROR)
