"""Speech-to-Text router — accepts audio upload and returns transcribed text."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.stt_service import transcribe_audio

router = APIRouter(tags=["stt"])


@router.post("/stt/transcribe")
async def stt_transcribe(file: UploadFile = File(...)) -> dict:
    """Receive audio file and return ElevenLabs STT transcription."""
    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    try:
        text = await transcribe_audio(audio_bytes, filename=file.filename or "audio.webm")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"text": text}
