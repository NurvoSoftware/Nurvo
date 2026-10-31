"""Past game reports for the logged-in player."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import get_pool
from models.score import DimensionScores, KeyMoment, ScoreResult
from routers.deps import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


class HistoryItem(BaseModel):
    session_id: str
    difficulty: str
    completed_at: datetime
    patient_name: str
    patient_diagnosis: str
    overall_score: int
    level_label: str


class HistoryDetail(BaseModel):
    session_id: str
    difficulty: str
    completed_at: datetime
    patient_name: str
    patient_diagnosis: str
    score: ScoreResult


# persist.py writes game_sessions, scenarios and score_results in one transaction,
# so a completed session always has all three rows — inner joins are safe.
_FROM = """
    FROM public.game_sessions g
    JOIN public.scenarios sc ON sc.session_id = g.id
    JOIN public.score_results s ON s.session_id = g.id
"""


@router.get("", response_model=list[HistoryItem])
async def list_history(current_user: dict = Depends(get_current_user)) -> list[HistoryItem]:
    """The caller's completed sessions, newest first."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT g.id AS session_id, g.difficulty, g.completed_at,
                   sc.patient_name, sc.patient_diagnosis,
                   s.overall_score, s.level_label
            {_FROM}
            WHERE g.user_id = $1 AND g.status = 'completed'
            ORDER BY g.completed_at DESC
            """,
            uuid.UUID(current_user["id"]),
        )
    return [HistoryItem(**{**dict(r), "session_id": str(r["session_id"])}) for r in rows]


@router.get("/{session_id}", response_model=HistoryDetail)
async def get_history_detail(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> HistoryDetail:
    """One past report. Someone else's session is a 404, so existence isn't leaked."""
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Report not found")

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            SELECT g.id AS session_id, g.difficulty, g.completed_at,
                   sc.patient_name, sc.patient_diagnosis,
                   s.overall_score, s.level_label,
                   s.score_empathy, s.score_guided_questioning, s.score_family_calming,
                   s.score_info_gathering, s.score_response_fluency,
                   s.strengths, s.improvements, s.key_moments
            {_FROM}
            WHERE g.id = $1 AND g.user_id = $2 AND g.status = 'completed'
            """,
            sid,
            uuid.UUID(current_user["id"]),
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return HistoryDetail(
        session_id=str(sid),
        difficulty=row["difficulty"],
        completed_at=row["completed_at"],
        patient_name=row["patient_name"],
        patient_diagnosis=row["patient_diagnosis"],
        score=ScoreResult(
            session_id=str(sid),
            overall_score=row["overall_score"],
            level_label=row["level_label"],
            dimension_scores=DimensionScores(
                empathy=row["score_empathy"],
                guided_questioning=row["score_guided_questioning"],
                family_calming=row["score_family_calming"],
                info_gathering=row["score_info_gathering"],
                response_fluency=row["score_response_fluency"],
            ),
            strengths=row["strengths"],
            improvements=row["improvements"],
            key_moments=[KeyMoment(**k) for k in row["key_moments"]],
        ),
    )
