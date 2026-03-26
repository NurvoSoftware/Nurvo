"""Scenario generation router."""

from fastapi import APIRouter, HTTPException

from models.chat import GameSession, SessionStatus
from models.scenario import Scenario
from prompts.patient_conversation import build_patient_prompt
from prompts.family_conversation import build_family_prompt
from services.scenario_generator import generate_scenario
from session_store import create_session

router = APIRouter(prefix="/scenario", tags=["scenario"])


class _ScenarioResponse(Scenario):
    """Scenario response that excludes correct_answers from serialization."""

    class Config:
        # We override serialization at the endpoint level instead
        pass


@router.post("/generate")
async def generate_scenario_endpoint() -> dict:
    """Generate a new scenario and create a game session."""
    session_id, scenario = await generate_scenario()

    # Build system prompts for patient and family NPCs
    patient = scenario.patient_profile
    pain = scenario.pain_details
    family = scenario.family_member

    patient_system_prompt = build_patient_prompt(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        diagnosis=patient.diagnosis,
        pain_location=pain.location,
        pain_severity=pain.severity,
        pain_type=pain.type,
        pain_duration=pain.duration,
        onset=pain.onset,
        aggravating_factors=pain.aggravating_factors,
        relieving_factors=pain.relieving_factors,
        associated_symptoms=pain.associated_symptoms,
    )

    family_system_prompt = build_family_prompt(
        family_name=family.name,
        relationship=family.relationship,
        personality=family.personality,
        emotional_state=family.emotional_state,
        patient_name=patient.name,
        interjection_triggers=family.interjection_triggers,
    )

    # Create and store game session
    game_session = GameSession(
        session_id=session_id,
        scenario_data=scenario.model_dump(),
        status=SessionStatus.BRIEFING,
        patient_system_prompt=patient_system_prompt,
        family_system_prompt=family_system_prompt,
    )
    create_session(game_session)

    # Return scenario without correct_answers
    scenario_dict = scenario.model_dump()
    scenario_dict.pop("correct_answers", None)

    return {
        "session_id": session_id,
        "scenario": scenario_dict,
    }
