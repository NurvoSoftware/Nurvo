"""Scoring engine service - evaluates game sessions via GPT-4o."""

import json
import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT
from models.chat import GameSession
from models.score import DimensionScores, KeyMoment, ScoreResult
from prompts.scoring import build_scoring_input

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Dimension weights for calculating overall score
_WEIGHTS = {
    "empathy": 0.20,
    "guided_questioning": 0.25,
    "family_calming": 0.15,
    "info_gathering": 0.25,
    "response_fluency": 0.15,
}


def _calculate_overall_score(dims: DimensionScores) -> int:
    """Calculate weighted overall score from dimension scores."""
    weighted = (
        dims.empathy * _WEIGHTS["empathy"]
        + dims.guided_questioning * _WEIGHTS["guided_questioning"]
        + dims.family_calming * _WEIGHTS["family_calming"]
        + dims.info_gathering * _WEIGHTS["info_gathering"]
        + dims.response_fluency * _WEIGHTS["response_fluency"]
    )
    return round(weighted)


def _determine_level_label(score: int) -> str:
    """Determine level label from overall score."""
    if score >= 85:
        return "優秀"
    if score >= 70:
        return "良好"
    if score >= 55:
        return "尚可"
    return "待改進"


def _build_scenario_summary(scenario_data: dict) -> str:
    """Build a human-readable scenario summary from raw scenario data."""
    patient = scenario_data.get("patient_profile", {})
    pain = scenario_data.get("pain_details", {})
    family = scenario_data.get("family_member", {})

    parts = []
    if patient:
        parts.append(
            f"病患：{patient.get('name', '未知')}，"
            f"{patient.get('age', '?')}歲{patient.get('gender', '')}，"
            f"診斷：{patient.get('diagnosis', '未知')}"
        )
    if pain:
        parts.append(
            f"疼痛部位：{pain.get('location', '未知')}，"
            f"嚴重程度：{pain.get('severity', '?')}/10，"
            f"類型：{pain.get('type', '未知')}"
        )
    if family:
        parts.append(
            f"家屬：{family.get('name', '未知')}（{family.get('relationship', '未知')}），"
            f"情緒狀態：{family.get('emotional_state', '未知')}"
        )

    challenges = scenario_data.get("communication_challenges", [])
    if challenges:
        parts.append(f"溝通挑戰：{', '.join(challenges)}")

    return "\n".join(parts)


def _build_conversation_transcript(session: GameSession) -> str:
    """Build a readable conversation transcript from chat history."""
    lines = []
    sender_labels = {"nurse": "護理師", "patient": "病患", "family": "家屬"}
    for msg in session.conversation_history:
        label = sender_labels.get(msg.sender, msg.sender)
        elapsed = f"[{msg.elapsed_seconds:.0f}s]"
        interjection = "（插話）" if msg.is_interjection else ""
        lines.append(f"{elapsed} {label}{interjection}：{msg.content}")
    return "\n".join(lines) if lines else "（無對話紀錄）"


def _compute_elapsed_seconds(session: GameSession) -> float:
    """Compute total elapsed seconds for the session."""
    if session.start_time is None:
        return 0.0
    now = datetime.now(timezone.utc)
    return (now - session.start_time).total_seconds()


async def evaluate_session(session: GameSession) -> ScoreResult:
    """Evaluate a game session and return a ScoreResult."""
    scenario_data = session.scenario_data
    correct_answers = scenario_data.get("correct_answers", {})

    # Build prompt inputs
    scenario_summary = _build_scenario_summary(scenario_data)
    expected_info = ", ".join(correct_answers.get("expected_info_gathered", []))
    ideal_empathy = ", ".join(correct_answers.get("ideal_empathy_phrases", []))
    ideal_questioning = ", ".join(correct_answers.get("ideal_questioning_sequence", []))
    calming_strategies = ", ".join(correct_answers.get("family_calming_strategies", []))
    conversation_transcript = _build_conversation_transcript(session)

    # Get patient summary from the submitted record
    patient_record = scenario_data.get("patient_record", {})
    patient_summary = patient_record.get("content", "（護理師未提交病況摘要）")

    elapsed_seconds = _compute_elapsed_seconds(session)
    time_limit = scenario_data.get("time_limit_seconds", 480)

    prompt = build_scoring_input(
        scenario_summary=scenario_summary,
        expected_info=expected_info,
        ideal_empathy=ideal_empathy,
        ideal_questioning=ideal_questioning,
        calming_strategies=calming_strategies,
        conversation_transcript=conversation_transcript,
        patient_summary=patient_summary,
        elapsed_seconds=elapsed_seconds,
        time_limit=time_limit,
    )

    try:
        response = await _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是護理溝通教育評分專家。"
                        "請嚴格以 JSON 格式回覆，不要包含其他文字。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            timeout=OPENAI_TIMEOUT,
        )

        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=502, detail="OpenAI returned empty response")

        # Strip markdown code fences if present
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        raw = json.loads(cleaned)

        # Parse dimension scores
        dim_data = raw.get("dimension_scores", {})
        dimension_scores = DimensionScores(
            empathy=int(dim_data.get("empathy", 0)),
            guided_questioning=int(dim_data.get("guided_questioning", 0)),
            family_calming=int(dim_data.get("family_calming", 0)),
            info_gathering=int(dim_data.get("info_gathering", 0)),
            response_fluency=int(dim_data.get("response_fluency", 0)),
        )

        # Calculate overall score from weighted dimensions (override GPT output)
        overall_score = _calculate_overall_score(dimension_scores)
        level_label = _determine_level_label(overall_score)

        # Parse key moments
        key_moments = []
        for km in raw.get("key_moments", []):
            key_moments.append(
                KeyMoment(
                    elapsed_seconds=float(km.get("elapsed_seconds", 0)),
                    message_id=str(km.get("message_id", "")),
                    quality=km.get("quality", "needs_improvement"),
                    description=km.get("description", ""),
                )
            )

        return ScoreResult(
            session_id=session.session_id,
            overall_score=overall_score,
            level_label=level_label,
            dimension_scores=dimension_scores,
            strengths=raw.get("strengths", []),
            improvements=raw.get("improvements", []),
            key_moments=key_moments,
        )

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse scoring JSON: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to parse scoring JSON from OpenAI: {exc}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Scoring evaluation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Scoring evaluation failed: {exc}",
        )
