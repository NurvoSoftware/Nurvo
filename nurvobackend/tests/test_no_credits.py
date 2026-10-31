"""Credits are switched off: generating a scenario must not touch users.credits.

The per-game credit charge (and the 402 "點數不足" refusal) was pulled out of
main into its own branch. These tests lock in that a logged-in user can always
generate a scenario, that no UPDATE against users is issued, and that the API no
longer advertises a credit balance.
"""

import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from main import app
from models.scenario import CorrectAnswers, FamilyMember, PainDetails, PatientProfile, Scenario
from routers import scenario as scenario_router
from routers.deps import get_current_user

_USER_ID = str(uuid.uuid4())


def _scenario() -> Scenario:
    family = [
        FamilyMember(
            name=name,
            gender=gender,
            relationship=rel,
            personality="焦慮",
            emotional_state="擔心",
            interjection_triggers=["疼痛"],
        )
        for name, gender, rel in [("王太太", "女", "配偶"), ("王小明", "男", "兒子"), ("王小美", "女", "女兒")]
    ]
    return Scenario(
        patient_profile=PatientProfile(
            name="王先生",
            age=72,
            gender="男",
            diagnosis="術後疼痛",
            medications=[],
            medical_history=[],
            allergies=[],
        ),
        pain_details=PainDetails(
            location="腹部",
            severity=7,
            type="刺痛",
            duration="2 小時",
            onset="術後",
            aggravating_factors=[],
            relieving_factors=[],
            associated_symptoms=[],
        ),
        family_members=family,
        communication_challenges=[],
        correct_answers=CorrectAnswers(
            expected_info_gathered=[],
            ideal_empathy_phrases=[],
            ideal_questioning_sequence=[],
            family_calming_strategies=[],
        ),
    )


class GenerateWithoutCreditsTest(unittest.TestCase):
    def setUp(self) -> None:
        # A user with zero credits — used to get a 402 before.
        app.dependency_overrides[get_current_user] = lambda: {"id": _USER_ID, "credits": 0}
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_generate_succeeds_without_touching_credits(self) -> None:
        get_pool = MagicMock(side_effect=AssertionError("generate must not query the DB for credits"))
        with (
            patch.object(scenario_router, "generate_scenario", AsyncMock(return_value=("s-1", _scenario()))),
            patch.object(scenario_router, "get_pool", get_pool, create=True),
        ):
            res = self.client.post("/api/scenario/generate", json={"difficulty": "easy"})

        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["session_id"], "s-1")
        self.assertNotIn("credits_remaining", body)
        self.assertNotIn("correct_answers", body["scenario"])
        get_pool.assert_not_called()


if __name__ == "__main__":
    unittest.main()
