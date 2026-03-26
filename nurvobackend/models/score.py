"""Scoring-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel


class DimensionScores(BaseModel):
    empathy: int
    guided_questioning: int
    family_calming: int
    info_gathering: int
    response_fluency: int


class KeyMoment(BaseModel):
    elapsed_seconds: float
    message_id: str
    quality: str  # "good" | "needs_improvement"
    description: str


class ScoreResult(BaseModel):
    session_id: str
    overall_score: int
    level_label: str
    dimension_scores: DimensionScores
    strengths: list[str]
    improvements: list[str]
    key_moments: list[KeyMoment]


class PatientRecord(BaseModel):
    session_id: str
    content: str
    submitted_at: datetime
    time_remaining_seconds: int
