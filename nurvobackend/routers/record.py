"""Patient record submission router."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import GAME_TIME_LIMIT
from models.chat import SessionStatus
from models.score import PatientRecord
from session_store import get_session, update_session

router = APIRouter(prefix="/record", tags=["record"])


class RecordSubmitRequest(BaseModel):
    session_id: str
    content: str = Field(..., min_length=1)


@router.post("/submit")
async def submit_record(request: RecordSubmitRequest) -> dict:
    """Submit a patient record for a session."""
    text = request.content.strip()
    if not text:
        raise HTTPException(status_code=400, detail="記錄內容不可為空白")

    # Validate session exists
    session = get_session(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == SessionStatus.BRIEFING:
        raise HTTPException(status_code=400, detail="遊戲尚未開始，無法提交護理記錄")
    if session.status in (SessionStatus.SCORING, SessionStatus.COMPLETED):
        raise HTTPException(status_code=409, detail="已提交過護理記錄")
    if session.status != SessionStatus.PLAYING:
        raise HTTPException(
            status_code=400,
            detail=f"目前狀態無法提交記錄（{session.status.value}）",
        )

    # Calculate remaining time
    now = datetime.now(timezone.utc)
    if session.start_time is not None:
        elapsed = (now - session.start_time).total_seconds()
        time_remaining = max(0, int(GAME_TIME_LIMIT - elapsed))
    else:
        time_remaining = GAME_TIME_LIMIT

    # Create patient record
    record = PatientRecord(
        session_id=request.session_id,
        content=text,
        submitted_at=now,
        time_remaining_seconds=time_remaining,
    )

    # Store record in session data and update status
    session.scenario_data["patient_record"] = record.model_dump(mode="json")
    session.status = SessionStatus.SCORING
    update_session(session)

    return {
        "status": "accepted",
        "session_id": request.session_id,
    }
