"""Regression tests for session ownership persistence.

``save_completed_session`` used to write a literal ``None`` into
``game_sessions.user_id``, so a finished game was never linked to the nurse who
played (and paid 30 credits for) it. Every per-user query — score history, class
leaderboards, homework completion — joins on that column, so it silently returned
nothing. These tests lock in that the authenticated identity captured at
``/scenario/generate`` reaches the database as a real ``uuid.UUID``.

They also lock in that a persist failure is logged *with its traceback*: the bare
``log.error`` that used to sit in the ``except`` is what let the bug survive
unnoticed from the day the module was written.
"""

import logging
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import persist
from models.chat import GameSession
from models.score import DimensionScores, ScoreResult

_GAME_SESSIONS_INSERT = "INSERT INTO public.game_sessions"


class _AsyncCtx:
    """Minimal async context manager standing in for asyncpg's acquire()/transaction()."""

    def __init__(self, value: object = None) -> None:
        self._value = value

    async def __aenter__(self) -> object:
        return self._value

    async def __aexit__(self, *exc: object) -> bool:
        return False


class _FakeConn:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def transaction(self) -> _AsyncCtx:
        return _AsyncCtx()

    async def execute(self, sql: str, *args: object) -> None:
        self.calls.append((sql, args))


class _FakePool:
    def __init__(self, conn: _FakeConn) -> None:
        self._conn = conn

    def acquire(self) -> _AsyncCtx:
        return _AsyncCtx(self._conn)


def _make_session(session_id: str, user_id: str | None) -> GameSession:
    return GameSession(
        session_id=session_id,
        user_id=user_id,
        scenario_data={
            "time_limit_seconds": 480,
            "patient_profile": {
                "name": "王小明",
                "age": 68,
                "gender": "男",
                "diagnosis": "術後疼痛",
                "medications": [],
                "medical_history": [],
                "allergies": [],
            },
            "pain_details": {
                "location": "腹部",
                "severity": 7,
                "type": "刺痛",
                "duration": "2 小時",
                "onset": "手術後",
                "aggravating_factors": [],
                "relieving_factors": [],
                "associated_symptoms": [],
            },
            "communication_challenges": [],
            "correct_answers": {},
            "family_members": [],
        },
        start_time=datetime.now(timezone.utc),
        patient_system_prompt="patient prompt",
        family_system_prompts=[],
    )


def _make_score(session_id: str) -> ScoreResult:
    return ScoreResult(
        session_id=session_id,
        overall_score=80,
        level_label="良好",
        dimension_scores=DimensionScores(
            empathy=16,
            guided_questioning=16,
            family_calming=16,
            info_gathering=16,
            response_fluency=16,
        ),
        strengths=[],
        improvements=[],
        key_moments=[],
    )


class PersistUserIdTest(unittest.IsolatedAsyncioTestCase):
    def _game_sessions_args(self, conn: _FakeConn) -> tuple:
        for sql, args in conn.calls:
            if _GAME_SESSIONS_INSERT in sql:
                return args
        self.fail("no INSERT INTO public.game_sessions was executed")

    async def test_authenticated_user_id_is_written_as_uuid(self) -> None:
        session_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        conn = _FakeConn()

        with patch.object(persist, "get_pool", return_value=_FakePool(conn)):
            await persist.save_completed_session(
                _make_session(session_id, user_id), _make_score(session_id)
            )

        args = self._game_sessions_args(conn)
        # $2 is user_id — asyncpg will not coerce a str into a uuid column.
        self.assertEqual(args[1], uuid.UUID(user_id))
        self.assertIsInstance(args[1], uuid.UUID)

    async def test_session_without_user_id_still_persists_as_null(self) -> None:
        """Legacy in-memory sessions created before the fix carry no owner."""
        session_id = str(uuid.uuid4())
        conn = _FakeConn()

        with patch.object(persist, "get_pool", return_value=_FakePool(conn)):
            await persist.save_completed_session(
                _make_session(session_id, None), _make_score(session_id)
            )

        self.assertIsNone(self._game_sessions_args(conn)[1])


class PersistFailureLoggingTest(unittest.IsolatedAsyncioTestCase):
    async def test_failure_is_logged_with_traceback(self) -> None:
        session_id = str(uuid.uuid4())

        def _boom() -> None:
            raise RuntimeError("pool exploded")

        with patch.object(persist, "get_pool", side_effect=_boom):
            with self.assertLogs(persist.log, level=logging.ERROR) as captured:
                await persist.save_completed_session(
                    _make_session(session_id, str(uuid.uuid4())), _make_score(session_id)
                )

        # log.exception attaches exc_info; log.error does not. Without the traceback
        # a persist failure is invisible, which is how the user_id bug survived.
        self.assertIsNotNone(captured.records[0].exc_info)


if __name__ == "__main__":
    unittest.main()
