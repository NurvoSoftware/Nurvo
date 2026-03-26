"""Score evaluation router."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.chat import SessionStatus
from models.score import ScoreResult
from services.scoring_engine import evaluate_session
from session_store import get_session, update_session

router = APIRouter(prefix="/score", tags=["score"])


class ScoreEvaluateRequest(BaseModel):
    session_id: str


@router.post("/evaluate", response_model=ScoreResult)
async def evaluate(request: ScoreEvaluateRequest) -> ScoreResult:
    """Evaluate a completed game session and return scoring results."""
    session = get_session(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.SCORING:
        raise HTTPException(
            status_code=400,
            detail=f"Session status must be 'scoring', got '{session.status.value}'",
        )

    # Run AI evaluation
    score_result = await evaluate_session(session)

    # Update session status to completed
    session.status = SessionStatus.COMPLETED
    update_session(session)

    return score_result
