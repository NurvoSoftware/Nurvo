"""Regression tests for the digiRunner removal.

These lock in the post-removal contract: the chat WebSocket is reached directly at the
path-based endpoint ``/api/chat/{session_id}`` (no gateway, no ``session_join`` handshake),
the gateway-only ``/api/chat/ws`` route is gone, and every API router is still mounted.
"""

import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from main import app
from models.chat import GameSession
from session_store import create_session, delete_session


def _route_paths() -> set[str]:
    """All registered route paths (HTTP + WebSocket)."""
    return {getattr(route, "path", "") for route in app.routes}


class ChatRouteRegistrationTest(unittest.TestCase):
    def test_path_based_chat_route_is_registered(self) -> None:
        self.assertIn("/api/chat/{session_id}", _route_paths())

    def test_gateway_ws_route_is_removed(self) -> None:
        self.assertNotIn("/api/chat/ws", _route_paths())

    def test_all_api_routers_still_mounted(self) -> None:
        paths = _route_paths()
        self.assertTrue(any(p.startswith("/api/scenario") for p in paths))
        self.assertTrue(any(p.startswith("/api/record") for p in paths))
        self.assertTrue(any(p.startswith("/api/score") for p in paths))
        self.assertTrue(any(p.startswith("/api/stt") for p in paths))
        self.assertTrue(any(p.startswith("/api/health") for p in paths))


class ChatWebSocketDirectConnectTest(unittest.TestCase):
    def test_path_based_connect_starts_session_without_handshake(self) -> None:
        session_id = "route-no-gateway-session"
        create_session(
            GameSession(
                session_id=session_id,
                scenario_data={"patient_profile": {"gender": "女"}, "family_members": []},
                start_time=datetime.now(timezone.utc),
                patient_system_prompt="patient prompt",
                family_system_prompts=[],
            ),
        )
        try:
            client = TestClient(app)
            with client.websocket_connect(f"/api/chat/{session_id}") as ws:
                # Server pushes timer_update immediately — no session_join frame was sent.
                first = ws.receive_json()
            self.assertEqual(first["type"], "timer_update")
        finally:
            delete_session(session_id)

    def test_unknown_session_id_reports_session_not_found(self) -> None:
        client = TestClient(app)
        with client.websocket_connect("/api/chat/does-not-exist") as ws:
            data = ws.receive_json()
        self.assertEqual(data["type"], "error")
        self.assertEqual(data["message"], "Session not found")

    def test_legacy_ws_path_no_longer_requires_session_join(self) -> None:
        """Connecting to the old `/api/chat/ws` is now just an unknown session id ("ws"),
        not the old gateway handshake error."""
        client = TestClient(app)
        with client.websocket_connect("/api/chat/ws") as ws:
            data = ws.receive_json()
        self.assertEqual(data["type"], "error")
        self.assertEqual(data["message"], "Session not found")
        self.assertNotEqual(data["message"], "First message must be session_join")


if __name__ == "__main__":
    unittest.main()
