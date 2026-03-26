"""Patient record submission router."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import GAME_TIME_LIMIT
from models.chat import SessionStatus
from models.score import PatientRecord
from session_store import get_session, update_session

router = APIRouter(prefix="/record", tags=["record"])


class RecordSubmitRequest(BaseModel):
    session_id: str
    content: str


@router.post("/submit")
async def submit_record(request: RecordSubmitRequest) -> dict:
    """Submit a patient record for a session."""
    # Validate session exists
    session = get_session(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

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
        content=request.content,
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
