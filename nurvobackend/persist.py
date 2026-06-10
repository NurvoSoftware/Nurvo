"""Persist completed session data to PostgreSQL. Best-effort: never raises."""

import logging
import uuid
from datetime import datetime, timezone

from models.chat import GameSession
from models.score import ScoreResult
from db import get_pool

log = logging.getLogger(__name__)

_TIME_TO_DIFFICULTY = {600: "easy", 480: "medium", 360: "hard"}


async def save_completed_session(session: GameSession, score: ScoreResult) -> None:
    try:
        pool = get_pool()
        sd = session.scenario_data
        pp = sd["patient_profile"]
        pd = sd["pain_details"]
        now = datetime.now(timezone.utc)
        difficulty = _TIME_TO_DIFFICULTY.get(sd.get("time_limit_seconds", 480), "medium")
        scenario_uuid = uuid.uuid4()

        chat_messages = [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "elapsed_seconds": m.elapsed_seconds,
                "is_interjection": m.is_interjection,
                "is_proactive": m.is_proactive,
            }
            for m in session.conversation_history
        ]

        ds = score.dimension_scores

        async with pool.acquire() as conn:
            async with conn.transaction():

                # 1. game_sessions
                await conn.execute(
                    """
                    INSERT INTO public.game_sessions
                        (id, user_id, difficulty, status, time_limit_seconds,
                         started_at, completed_at, created_at, chat_messages)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                    ON CONFLICT (id) DO UPDATE SET
                        status        = EXCLUDED.status,
                        completed_at  = EXCLUDED.completed_at,
                        chat_messages = EXCLUDED.chat_messages
                    """,
                    uuid.UUID(session.session_id),
                    None,
                    difficulty,
                    "completed",
                    sd.get("time_limit_seconds", 480),
                    session.start_time,
                    now,
                    session.start_time or now,
                    chat_messages,  # list[dict] — jsonb codec handles serialization
                )

                # 2. scenarios
                await conn.execute(
                    """
                    INSERT INTO public.scenarios
                        (id, session_id, patient_name, patient_age, patient_gender,
                         patient_diagnosis, patient_medications, patient_medical_history,
                         patient_allergies, pain_location, pain_severity, pain_type,
                         pain_duration, pain_onset, pain_aggravating_factors,
                         pain_relieving_factors, pain_associated_symptoms,
                         communication_challenges, correct_answers, created_at)
                    VALUES
                        ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20)
                    ON CONFLICT (session_id) DO NOTHING
                    """,
                    scenario_uuid,
                    uuid.UUID(session.session_id),
                    pp["name"],
                    pp["age"],
                    pp["gender"],
                    pp["diagnosis"],
                    pp["medications"],
                    pp["medical_history"],
                    pp["allergies"],
                    pd["location"],
                    pd["severity"],
                    pd["type"],
                    pd["duration"],
                    pd["onset"],
                    pd["aggravating_factors"],
                    pd["relieving_factors"],
                    pd["associated_symptoms"],
                    sd.get("communication_challenges", []),
                    sd.get("correct_answers", {}),
                    now,
                )

                # 3. family_members
                for i, fm in enumerate(sd.get("family_members", [])):
                    await conn.execute(
                        """
                        INSERT INTO public.family_members
                            (id, scenario_id, member_index, name, gender,
                             relationship_role, personality, emotional_state,
                             interjection_triggers)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                        """,
                        uuid.uuid4(),
                        scenario_uuid,
                        i,
                        fm["name"],
                        fm["gender"],
                        fm["relationship"],
                        fm["personality"],
                        fm["emotional_state"],
                        fm.get("interjection_triggers", []),
                    )

                # 4. score_results
                await conn.execute(
                    """
                    INSERT INTO public.score_results
                        (id, session_id, overall_score, level_label,
                         score_empathy, score_guided_questioning, score_family_calming,
                         score_info_gathering, score_response_fluency,
                         strengths, improvements, key_moments, evaluated_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                    ON CONFLICT (session_id) DO NOTHING
                    """,
                    uuid.uuid4(),
                    uuid.UUID(session.session_id),
                    score.overall_score,
                    score.level_label,
                    ds.empathy,
                    ds.guided_questioning,
                    ds.family_calming,
                    ds.info_gathering,
                    ds.response_fluency,
                    score.strengths,
                    score.improvements,
                    [k.model_dump() for k in score.key_moments],
                    now,
                )

        log.info("Session %s persisted to DB (%d messages)", session.session_id, len(chat_messages))

    except Exception as exc:
        log.error("DB persist failed for session %s: %s", session.session_id, exc)
