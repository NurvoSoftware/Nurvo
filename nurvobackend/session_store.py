"""In-memory session store for game sessions."""

from models.chat import GameSession

_sessions: dict[str, GameSession] = {}


def create_session(session: GameSession) -> GameSession:
    _sessions[session.session_id] = session
    return session


def get_session(session_id: str) -> GameSession | None:
    return _sessions.get(session_id)


def update_session(session: GameSession) -> GameSession:
    _sessions[session.session_id] = session
    return session


def delete_session(session_id: str) -> bool:
    return _sessions.pop(session_id, None) is not None
