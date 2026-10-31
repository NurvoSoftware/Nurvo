"""Scoring-related Pydantic models."""

from datetime import datetime
from typing import Literal

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


class SbarItem(BaseModel):
    rating: Literal["complete", "partial", "missing"]
    feedback: str


class SbarAnalysis(BaseModel):
    """SBAR review of the nurse's submitted patient record."""

    situation: SbarItem
    background: SbarItem
    assessment: SbarItem
    recommendation: SbarItem


class ScoreResult(BaseModel):
    session_id: str
    overall_score: int
    level_label: str
    dimension_scores: DimensionScores
    strengths: list[str]
    improvements: list[str]
    key_moments: list[KeyMoment]
    sbar_analysis: SbarAnalysis | None = None  # None if the LLM omitted or garbled it


class LatestRecord(BaseModel):
    """The player's most recent completed session, for review before the next run."""

    session_id: str
    difficulty: str
    completed_at: datetime
    overall_score: int
    level_label: str
    dimension_scores: DimensionScores
    improvements: list[str]
    sbar_analysis: SbarAnalysis | None = None


class PatientRecord(BaseModel):
    session_id: str
    content: str
    submitted_at: datetime
    time_remaining_seconds: int
