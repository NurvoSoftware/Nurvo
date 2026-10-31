"""SBAR analysis of the nurse's submitted patient record.

The scoring LLM is asked to judge the 病況摘要 against the four SBAR sections
(Situation / Background / Assessment / Recommendation). These tests lock in that a
well-formed analysis reaches ``ScoreResult``, that a malformed one degrades to
``None`` instead of failing the whole score, and that the prompt actually asks for it.
"""

import json
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from models.chat import GameSession
from prompts.scoring import build_scoring_input
from services import scoring_engine

_SBAR = {
    "situation": {"rating": "complete", "feedback": "清楚說明病患目前疼痛 7 分"},
    "background": {"rating": "partial", "feedback": "缺少過去病史"},
    "assessment": {"rating": "missing", "feedback": "沒有寫出你的評估判斷"},
    "recommendation": {"rating": "partial", "feedback": "建議要更具體"},
}


def _llm_payload(**overrides: object) -> dict:
    payload = {
        "dimension_scores": {
            "empathy": 80,
            "guided_questioning": 70,
            "family_calming": 60,
            "info_gathering": 75,
            "response_fluency": 90,
        },
        "strengths": ["a"],
        "improvements": ["b"],
        "key_moments": [],
        "sbar_analysis": _SBAR,
    }
    payload.update(overrides)
    return payload


def _fake_completion(payload: dict) -> SimpleNamespace:
    message = SimpleNamespace(content=json.dumps(payload, ensure_ascii=False))
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _session() -> GameSession:
    return GameSession(
        session_id="s-1",
        scenario_data={
            "patient_profile": {"name": "王小明", "age": 68, "gender": "男", "diagnosis": "術後疼痛"},
            "pain_details": {"location": "腹部", "severity": 7, "type": "刺痛"},
            "family_members": [],
            "correct_answers": {},
            "patient_record": {"content": "病患腹痛 7 分，建議給止痛藥"},
        },
        start_time=datetime.now(timezone.utc),
    )


async def _evaluate(payload: dict):
    create = AsyncMock(return_value=_fake_completion(payload))
    with patch.object(scoring_engine._client.chat.completions, "create", create):
        return await scoring_engine.evaluate_session(_session())


class SbarParsingTest(unittest.IsolatedAsyncioTestCase):
    async def test_well_formed_sbar_reaches_score_result(self) -> None:
        result = await _evaluate(_llm_payload())

        self.assertIsNotNone(result.sbar_analysis)
        self.assertEqual(result.sbar_analysis.situation.rating, "complete")
        self.assertEqual(result.sbar_analysis.assessment.rating, "missing")
        self.assertEqual(result.sbar_analysis.background.feedback, "缺少過去病史")

    async def test_missing_sbar_degrades_to_none(self) -> None:
        payload = _llm_payload()
        del payload["sbar_analysis"]

        result = await _evaluate(payload)

        self.assertIsNone(result.sbar_analysis)
        self.assertEqual(result.dimension_scores.empathy, 80)

    async def test_invalid_rating_degrades_to_none_without_failing_score(self) -> None:
        bad = dict(_SBAR, situation={"rating": "excellent", "feedback": "x"})

        result = await _evaluate(_llm_payload(sbar_analysis=bad))

        self.assertIsNone(result.sbar_analysis)
        self.assertGreater(result.overall_score, 0)


class SbarPromptTest(unittest.TestCase):
    def test_prompt_asks_for_sbar_analysis_of_the_record(self) -> None:
        prompt = build_scoring_input(
            scenario_summary="",
            expected_info="",
            ideal_empathy="",
            ideal_questioning="",
            calming_strategies="",
            conversation_transcript="",
            patient_summary="病患腹痛",
            elapsed_seconds=0,
            time_limit=480,
        )

        self.assertIn("SBAR", prompt)
        self.assertIn('"sbar_analysis"', prompt)
        for key in ("situation", "background", "assessment", "recommendation"):
            self.assertIn(f'"{key}"', prompt)


if __name__ == "__main__":
    unittest.main()
