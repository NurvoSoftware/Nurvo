"""``GET /api/history`` and ``GET /api/history/{session_id}`` — a player's past reports.

Locks in that both queries are scoped to the authenticated user (passed as a real
UUID), that another user's session is a 404 rather than a 403 (no existence leak),
and that the detail payload has the same score shape the dashboard renders.
"""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from routers import history as history_router
from routers.deps import get_current_user
from tests.test_persist_user_id import _FakePool

_USER_ID = str(uuid.uuid4())
_SESSION_ID = uuid.uuid4()
_COMPLETED = datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc)


class _FetchConn:
    def __init__(self, rows: list[dict] | None = None, row: dict | None = None) -> None:
        self.rows = rows or []
        self.row = row
        self.calls: list[tuple[str, tuple]] = []

    async def fetch(self, sql: str, *args: object) -> list[dict]:
        self.calls.append((sql, args))
        return self.rows

    async def fetchrow(self, sql: str, *args: object) -> dict | None:
        self.calls.append((sql, args))
        return self.row


def _list_row(score: int) -> dict:
    return {
        "session_id": uuid.uuid4(),
        "difficulty": "medium",
        "completed_at": _COMPLETED,
        "patient_name": "王先生",
        "patient_diagnosis": "術後疼痛",
        "overall_score": score,
        "level_label": "良好",
    }


def _detail_row() -> dict:
    return {
        "session_id": _SESSION_ID,
        "difficulty": "hard",
        "completed_at": _COMPLETED,
        "patient_name": "王先生",
        "patient_diagnosis": "術後疼痛",
        "overall_score": 72,
        "level_label": "良好",
        "score_empathy": 80,
        "score_guided_questioning": 55,
        "score_family_calming": 70,
        "score_info_gathering": 75,
        "score_response_fluency": 85,
        "strengths": ["開場有同理"],
        "improvements": ["多用開放式問題"],
        "key_moments": [
            {"elapsed_seconds": 12.0, "message_id": "m1", "quality": "good", "description": "好"}
        ],
        "sbar_analysis": {
            k: {"rating": "partial", "feedback": "缺少建議"}
            for k in ("situation", "background", "assessment", "recommendation")
        },
    }


class HistoryRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: {"id": _USER_ID}
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def _get(self, url: str, conn: _FetchConn):
        with patch.object(history_router, "get_pool", return_value=_FakePool(conn)):
            return self.client.get(url)

    def test_list_returns_callers_sessions_in_query_order(self) -> None:
        conn = _FetchConn(rows=[_list_row(80), _list_row(60)])

        res = self._get("/api/history", conn)

        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual([item["overall_score"] for item in body], [80, 60])
        self.assertEqual(body[0]["patient_name"], "王先生")
        self.assertEqual(conn.calls[0][1], (uuid.UUID(_USER_ID),))
        self.assertIn("ORDER BY", conn.calls[0][0])

    def test_list_is_empty_for_new_player(self) -> None:
        res = self._get("/api/history", _FetchConn(rows=[]))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_detail_returns_full_score(self) -> None:
        conn = _FetchConn(row=_detail_row())

        res = self._get(f"/api/history/{_SESSION_ID}", conn)

        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["difficulty"], "hard")
        score = body["score"]
        self.assertEqual(score["session_id"], str(_SESSION_ID))
        self.assertEqual(score["overall_score"], 72)
        self.assertEqual(score["dimension_scores"]["guided_questioning"], 55)
        self.assertEqual(score["key_moments"][0]["quality"], "good")
        self.assertEqual(score["sbar_analysis"]["situation"]["rating"], "partial")
        # Ownership is enforced in SQL: session id AND caller's user id.
        self.assertEqual(conn.calls[0][1], (_SESSION_ID, uuid.UUID(_USER_ID)))

    def test_detail_without_sbar_is_null(self) -> None:
        row = {**_detail_row(), "sbar_analysis": None}  # sessions from before SBAR existed

        res = self._get(f"/api/history/{_SESSION_ID}", _FetchConn(row=row))

        self.assertEqual(res.status_code, 200, res.text)
        self.assertIsNone(res.json()["score"]["sbar_analysis"])

    def test_detail_of_someone_elses_session_is_404(self) -> None:
        res = self._get(f"/api/history/{_SESSION_ID}", _FetchConn(row=None))

        self.assertEqual(res.status_code, 404)

    def test_detail_with_malformed_id_is_404_without_querying(self) -> None:
        conn = _FetchConn()

        res = self._get("/api/history/not-a-uuid", conn)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(conn.calls, [])

    def test_requires_authentication(self) -> None:
        app.dependency_overrides.clear()

        self.assertEqual(self.client.get("/api/history").status_code, 401)
        self.assertEqual(self.client.get(f"/api/history/{_SESSION_ID}").status_code, 401)


if __name__ == "__main__":
    unittest.main()
