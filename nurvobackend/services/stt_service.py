"""Speech-to-Text service using ElevenLabs Scribe API."""

import httpx

from config import ELEVENLABS_API_KEY

_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
_TIMEOUT = 30.0


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
        error_detail = e.response.text
        print(f"[stt_service] API error: {e.response.status_code} - {error_detail}", flush=True)
        raise ValueError(f"STT API 錯誤: {error_detail}")
    except Exception as e:
        print(f"[stt_service] Transcription failed: {e}", flush=True)
        raise ValueError(f"STT 系統錯誤: {str(e)}")
