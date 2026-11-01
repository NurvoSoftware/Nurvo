"""Score evaluation router."""

import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import get_pool
from models.chat import SessionStatus
from models.score import DimensionScores, LatestRecord, ScoreResult
from persist import save_completed_session
from routers.deps import get_current_user
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

    score_result = await evaluate_session(session)

    session.status = SessionStatus.COMPLETED
    update_session(session)

    # Persist to DB in the background — does not block the API response
    asyncio.create_task(save_completed_session(session, score_result))

    return score_result


@router.get("/latest", response_model=LatestRecord | None)
async def latest(current_user: dict = Depends(get_current_user)) -> LatestRecord | None:
    """The caller's most recent completed session, or null for a first-time player."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT g.id AS session_id, g.difficulty, g.completed_at,
                   s.overall_score, s.level_label,
                   s.score_empathy, s.score_guided_questioning, s.score_family_calming,
                   s.score_info_gathering, s.score_response_fluency,
                   s.improvements, s.sbar_analysis
            FROM public.game_sessions g
            JOIN public.score_results s ON s.session_id = g.id
            WHERE g.user_id = $1 AND g.status = 'completed'
            ORDER BY g.completed_at DESC
            LIMIT 1
            """,
            uuid.UUID(current_user["id"]),
        )
    if row is None:
        return None

    return LatestRecord(
        session_id=str(row["session_id"]),
        difficulty=row["difficulty"],
        completed_at=row["completed_at"],
        overall_score=row["overall_score"],
        level_label=row["level_label"],
        dimension_scores=DimensionScores(
            empathy=row["score_empathy"],
            guided_questioning=row["score_guided_questioning"],
            family_calming=row["score_family_calming"],
            info_gathering=row["score_info_gathering"],
            response_fluency=row["score_response_fluency"],
        ),
        improvements=row["improvements"],
        sbar_analysis=row["sbar_analysis"],
    )
