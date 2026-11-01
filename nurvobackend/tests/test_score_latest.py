"""``GET /api/score/latest`` — the player's previous result, shown on level select.

Locks in that the query is scoped to the authenticated user, that a first-time
player gets ``null`` (not an error), and that SBAR and improvements come back so
the player can review last time's weak spots before the next run.
"""

import json
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

import persist
from main import app
from models.score import SbarAnalysis
from routers import score as score_router
from routers.deps import get_current_user
from tests.test_persist_user_id import _FakeConn, _FakePool, _make_score, _make_session

_USER_ID = str(uuid.uuid4())

_SBAR = {
    "situation": {"rating": "complete", "feedback": "ok"},
    "background": {"rating": "partial", "feedback": "缺病史"},
    "assessment": {"rating": "missing", "feedback": "沒寫評估"},
    "recommendation": {"rating": "partial", "feedback": "不夠具體"},
}


class _FetchConn:
    def __init__(self, row: dict | None) -> None:
        self.row = row
        self.calls: list[tuple[str, tuple]] = []

    async def fetchrow(self, sql: str, *args: object) -> dict | None:
        self.calls.append((sql, args))
        return self.row


def _row(sbar: object = _SBAR) -> dict:
    return {
        "session_id": uuid.uuid4(),
        "difficulty": "medium",
        "completed_at": datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc),
        "overall_score": 72,
        "level_label": "良好",
        "score_empathy": 80,
        "score_guided_questioning": 55,
        "score_family_calming": 70,
        "score_info_gathering": 75,
        "score_response_fluency": 85,
        "improvements": ["多用開放式問題"],
        "sbar_analysis": sbar,
    }


class LatestRecordRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: {"id": _USER_ID}
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def _get(self, row: dict | None) -> tuple[object, _FetchConn]:
        conn = _FetchConn(row)
        with patch.object(score_router, "get_pool", return_value=_FakePool(conn)):
            res = self.client.get("/api/score/latest")
        return res, conn

    def test_returns_latest_record_for_current_user(self) -> None:
        res, conn = self._get(_row())

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["overall_score"], 72)
        self.assertEqual(body["difficulty"], "medium")
        self.assertEqual(body["dimension_scores"]["guided_questioning"], 55)
        self.assertEqual(body["improvements"], ["多用開放式問題"])
        self.assertEqual(body["sbar_analysis"]["assessment"]["rating"], "missing")
        # Scoped to the caller, passed as a real UUID (asyncpg won't coerce str).
        self.assertEqual(conn.calls[0][1], (uuid.UUID(_USER_ID),))

    def test_first_time_player_gets_null(self) -> None:
        res, _ = self._get(None)

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.json())

    def test_record_from_before_sbar_has_null_sbar(self) -> None:
        res, _ = self._get(_row(sbar=None))

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.json()["sbar_analysis"])

    def test_requires_authentication(self) -> None:
        app.dependency_overrides.clear()

        res = self.client.get("/api/score/latest")

        self.assertEqual(res.status_code, 401)


class PersistSbarTest(unittest.IsolatedAsyncioTestCase):
    async def _score_results_args(self, sbar: SbarAnalysis | None) -> tuple:
        session_id = str(uuid.uuid4())
        score = _make_score(session_id)
        score.sbar_analysis = sbar
        conn = _FakeConn()
        with patch.object(persist, "get_pool", return_value=_FakePool(conn)):
            await persist.save_completed_session(_make_session(session_id, _USER_ID), score)
        for sql, args in conn.calls:
            if "INSERT INTO public.score_results" in sql:
                self.assertIn("sbar_analysis", sql)
                return args
        self.fail("no INSERT INTO public.score_results was executed")

    async def test_sbar_is_written_as_dict(self) -> None:
        args = await self._score_results_args(SbarAnalysis.model_validate(_SBAR))

        self.assertEqual(args[-1], json.loads(json.dumps(_SBAR)))

    async def test_missing_sbar_is_written_as_null(self) -> None:
        args = await self._score_results_args(None)

        self.assertIsNone(args[-1])


if __name__ == "__main__":
    unittest.main()
