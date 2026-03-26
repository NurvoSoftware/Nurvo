"""Chat and game session Pydantic models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SessionStatus(str, Enum):
    BRIEFING = "briefing"
    PLAYING = "playing"
    RECORDING = "recording"
    SCORING = "scoring"
    COMPLETED = "completed"


class ChatMessage(BaseModel):
    id: str
    sender: str  # "patient" | "family" | "nurse"
    content: str
    timestamp: datetime
    elapsed_seconds: float
    is_interjection: bool = False


class GameSession(BaseModel):
    session_id: str
    scenario_data: dict  # Raw scenario dict for flexibility
    conversation_history: list[ChatMessage] = []
    current_target: str = "patient"
    family_interjection_counter: int = 0
    start_time: datetime | None = None
    status: SessionStatus = SessionStatus.BRIEFING
    patient_system_prompt: str = ""
    family_system_prompt: str = ""
