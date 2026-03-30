"""Scenario-related Pydantic models."""

from pydantic import BaseModel, field_validator


class PatientProfile(BaseModel):
    name: str
    age: int
    gender: str
    diagnosis: str
    medications: list[str]
    medical_history: list[str]
    allergies: list[str]


class PainDetails(BaseModel):
    location: str
    severity: int
    type: str
    duration: str
    onset: str
    aggravating_factors: list[str]
    relieving_factors: list[str]
    associated_symptoms: list[str]


class FamilyMember(BaseModel):
    name: str
    relationship: str
    personality: str
    emotional_state: str
    interjection_triggers: list[str]


class CorrectAnswers(BaseModel):
    expected_info_gathered: list[str]
    ideal_empathy_phrases: list[str]
    ideal_questioning_sequence: list[str]
    family_calming_strategies: list[str]


class Scenario(BaseModel):
    patient_profile: PatientProfile
    pain_details: PainDetails
    family_members: list[FamilyMember]
    communication_challenges: list[str]
    correct_answers: CorrectAnswers
    time_limit_seconds: int = 480

    @field_validator("family_members")
    @classmethod
    def exactly_three_family_members(cls, v: list[FamilyMember]) -> list[FamilyMember]:
        if len(v) != 3:
            raise ValueError(f"必須恰好有 3 位家屬，目前有 {len(v)} 位")
        return v
