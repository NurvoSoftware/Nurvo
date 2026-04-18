"""WebSocket chat router for real-time nurse-NPC conversation."""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import (
    GAME_TIME_LIMIT,
    PROACTIVE_ENABLED,
    PROACTIVE_IDLE_THRESHOLDS,
    RECONNECT_GRACE_SECONDS,
)
from models.chat import ChatMessage, SessionStatus
from services.conversation_engine import (
    get_npc_response,
    maybe_family_interjection,
    maybe_proactive_speak,
)
from session_store import get_session, update_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

_session_locks: dict[str, asyncio.Lock] = {}
_VALID_ACTIVITY_KINDS = {"typing_start", "typing_end", "audio_start", "audio_end", "connection_resumed"}


def _get_session_lock(session_id: str) -> asyncio.Lock:
    """Get (or create) the asyncio lock for a given session."""
    lock = _session_locks.get(session_id)
    if lock is None:
        lock = asyncio.Lock()
        _session_locks[session_id] = lock
    return lock


def _elapsed_seconds(start_time: datetime) -> float:
    """Calculate elapsed seconds from session start to now."""
    now = datetime.now(timezone.utc)
    return round((now - start_time).total_seconds(), 1)


async def _send_json(ws: WebSocket, data: dict) -> None:
    """Send a JSON message over the WebSocket."""
    await ws.send_text(json.dumps(data, ensure_ascii=False))


def _threshold_for_streak(streak: int) -> int:
    """Pick the idle threshold for the given streak (saturates at the last value)."""
    thresholds = PROACTIVE_IDLE_THRESHOLDS or [25, 20, 15]
    idx = min(streak, len(thresholds) - 1)
    return thresholds[idx]


async def _timer_task(ws: WebSocket, session_id: str, start_time: datetime) -> None:
    """Background task that sends timer updates every 30 seconds and expires the session."""
    try:
        while True:
            await asyncio.sleep(30)
            elapsed = _elapsed_seconds(start_time)
            remaining = max(0, GAME_TIME_LIMIT - int(elapsed))

            if remaining <= 0:
                await _send_json(ws, {
                    "type": "timer_expired",
                    "message": "時間已到，請前往記錄頁面提交護理記錄。",
                })
                await ws.close()
                return

            await _send_json(ws, {
                "type": "timer_update",
                "remaining_seconds": remaining,
            })
    except Exception:
        # Connection closed or other error – just stop the timer
        pass


async def _idle_monitor_task(ws: WebSocket, session_id: str, lock: asyncio.Lock) -> None:
    """Background task: check idle state every second, trigger proactive speech when due."""
    if not PROACTIVE_ENABLED:
        return

    try:
        while True:
            await asyncio.sleep(1)

            session = get_session(session_id)
            if session is None or session.start_time is None:
                continue

            if session.is_user_active:
                continue

            if session.last_activity_at is None:
                continue

            now = datetime.now(timezone.utc)
            idle_seconds = (now - session.last_activity_at).total_seconds()
            if idle_seconds < 0:
                # last_activity_at was pushed into the future (reconnection grace).
                continue

            threshold = _threshold_for_streak(session.proactive_streak)
            if idle_seconds < threshold:
                continue

            async with lock:
                # Re-validate after acquiring the lock — user may have spoken meanwhile.
                session = get_session(session_id)
                if session is None or session.start_time is None:
                    continue
                if session.is_user_active or session.last_activity_at is None:
                    continue
                idle_seconds = (now - session.last_activity_at).total_seconds()
                threshold = _threshold_for_streak(session.proactive_streak)
                if idle_seconds < threshold:
                    continue

                content, sender, audio_base64, did_speak = await maybe_proactive_speak(session)
                if not did_speak:
                    # Bump last_activity_at forward slightly so we don't re-check every second
                    # when the LLM declines; gives a short cooldown of its own.
                    session.last_activity_at = datetime.now(timezone.utc) - timedelta(seconds=threshold - 5)
                    update_session(session)
                    continue

                elapsed = _elapsed_seconds(session.start_time)
                msg_id = str(uuid.uuid4())
                message = ChatMessage(
                    id=msg_id,
                    sender=sender,
                    content=content,
                    timestamp=datetime.now(timezone.utc),
                    elapsed_seconds=elapsed,
                    is_proactive=True,
                )
                session.conversation_history.append(message)
                # Reset activity timestamp so the next idle cycle starts fresh.
                session.last_activity_at = datetime.now(timezone.utc)
                update_session(session)

                await _send_json(ws, {"type": "typing", "sender": sender})

                payload: dict = {
                    "type": "npc_message",
                    "sender": sender,
                    "content": content,
                    "message_id": msg_id,
                    "elapsed_seconds": elapsed,
                    "is_proactive": True,
                }
                if audio_base64:
                    payload["audio_base64"] = audio_base64
                await _send_json(ws, payload)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.warning("idle_monitor ended unexpectedly: %s", exc)


def _apply_activity(session, kind: str) -> None:
    """Mutate session state based on a client-side activity signal."""
    now = datetime.now(timezone.utc)
    if kind in ("typing_start", "audio_start"):
        session.is_user_active = True
    elif kind in ("typing_end", "audio_end"):
        session.is_user_active = False
        session.last_activity_at = now
    elif kind == "connection_resumed":
        session.is_user_active = False
        session.last_activity_at = now + timedelta(seconds=RECONNECT_GRACE_SECONDS)


@router.websocket("/{session_id}")
async def chat_websocket(ws: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for nurse-NPC chat interaction."""
    await ws.accept()

    # Validate session exists
    session = get_session(session_id)
    if session is None:
        await _send_json(ws, {"type": "error", "content": "Session not found"})
        await ws.close()
        return

    lock = _get_session_lock(session_id)

    # Start session timer on first connection if not already started
    if session.start_time is None:
        session.start_time = datetime.now(timezone.utc)
        session.status = SessionStatus.PLAYING

    # Seed activity tracking with a reconnection grace so idle monitor waits a beat.
    session.last_activity_at = datetime.now(timezone.utc) + timedelta(seconds=RECONNECT_GRACE_SECONDS)
    session.is_user_active = False
    update_session(session)

    # Send initial timer state
    initial_elapsed = _elapsed_seconds(session.start_time)
    initial_remaining = max(0, GAME_TIME_LIMIT - int(initial_elapsed))
    await _send_json(ws, {
        "type": "timer_update",
        "remaining_seconds": initial_remaining,
    })

    # Start background tasks
    timer = asyncio.create_task(_timer_task(ws, session_id, session.start_time))
    idle_monitor = asyncio.create_task(_idle_monitor_task(ws, session_id, lock))

    try:
        while True:
            raw = await ws.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await _send_json(ws, {"type": "error", "content": "Invalid JSON"})
                continue

            msg_type = data.get("type")

            if msg_type == "activity":
                kind = data.get("kind")
                if kind not in _VALID_ACTIVITY_KINDS:
                    await _send_json(ws, {"type": "error", "content": f"Unknown activity kind: {kind}"})
                    continue
                session = get_session(session_id)
                if session is None:
                    continue
                _apply_activity(session, kind)
                update_session(session)
                continue

            if msg_type != "nurse_message":
                await _send_json(ws, {"type": "error", "content": f"Unknown message type: {msg_type}"})
                continue

            content = data.get("content", "").strip()
            target = data.get("target", "patient")

            if not content:
                await _send_json(ws, {"type": "error", "content": "Empty message content"})
                continue

            # Reload session to get latest state
            session = get_session(session_id)
            if session is None:
                await _send_json(ws, {"type": "error", "content": "Session expired"})
                await ws.close()
                return

            elapsed = _elapsed_seconds(session.start_time)

            # Check if time already expired
            if elapsed >= GAME_TIME_LIMIT:
                await _send_json(ws, {
                    "type": "timer_expired",
                    "message": "時間已到，請前往記錄頁面提交護理記錄。",
                })
                await ws.close()
                return

            async with lock:
                session = get_session(session_id)
                if session is None:
                    await _send_json(ws, {"type": "error", "content": "Session expired"})
                    await ws.close()
                    return

                # Record nurse message in history
                nurse_msg_id = str(uuid.uuid4())
                nurse_chat = ChatMessage(
                    id=nurse_msg_id,
                    sender="nurse",
                    content=content,
                    timestamp=datetime.now(timezone.utc),
                    elapsed_seconds=elapsed,
                )
                session.conversation_history.append(nurse_chat)
                session.current_target = target
                # Nurse spoke: reset proactive state and activity tracking.
                session.proactive_streak = 0
                session.is_user_active = False
                session.last_activity_at = datetime.now(timezone.utc)
                update_session(session)

                # Send typing indicator
                await _send_json(ws, {"type": "typing", "sender": target})

                # Get NPC response (now includes audio_base64)
                try:
                    npc_text, sender, audio_base64 = await get_npc_response(session, content, target)
                except Exception as exc:
                    await _send_json(ws, {"type": "error", "content": f"NPC response error: {exc}"})
                    continue

                elapsed = _elapsed_seconds(session.start_time)
                npc_msg_id = str(uuid.uuid4())

                # Record NPC message
                npc_chat = ChatMessage(
                    id=npc_msg_id,
                    sender=sender,
                    content=npc_text,
                    timestamp=datetime.now(timezone.utc),
                    elapsed_seconds=elapsed,
                )
                session.conversation_history.append(npc_chat)
                # Reset idle baseline after NPC replies so user gets full threshold.
                session.last_activity_at = datetime.now(timezone.utc)
                update_session(session)

                # Send NPC response with optional audio
                npc_payload: dict = {
                    "type": "npc_message",
                    "sender": sender,
                    "content": npc_text,
                    "message_id": npc_msg_id,
                    "elapsed_seconds": elapsed,
                }
                if audio_base64:
                    npc_payload["audio_base64"] = audio_base64

                await _send_json(ws, npc_payload)

                # Check for family interjection when nurse talks to patient
                if target == "patient":
                    interjection_text, did_interject, interjection_audio, family_index = await maybe_family_interjection(session)

                    if did_interject:
                        family_sender = f"family_{family_index}"

                        elapsed = _elapsed_seconds(session.start_time)
                        interjection_id = str(uuid.uuid4())

                        interjection_chat = ChatMessage(
                            id=interjection_id,
                            sender=family_sender,
                            content=interjection_text,
                            timestamp=datetime.now(timezone.utc),
                            elapsed_seconds=elapsed,
                            is_interjection=True,
                        )
                        session.conversation_history.append(interjection_chat)
                        session.last_activity_at = datetime.now(timezone.utc)
                        update_session(session)

                        # Send typing indicator for the specific family member
                        await _send_json(ws, {"type": "typing", "sender": family_sender})

                        interjection_payload: dict = {
                            "type": "npc_message",
                            "sender": family_sender,
                            "content": interjection_text,
                            "message_id": interjection_id,
                            "elapsed_seconds": elapsed,
                            "is_interjection": True,
                        }
                        if interjection_audio:
                            interjection_payload["audio_base64"] = interjection_audio

                        await _send_json(ws, interjection_payload)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await _send_json(ws, {"type": "error", "content": f"Unexpected error: {exc}"})
        except Exception:
            pass
    finally:
        timer.cancel()
        idle_monitor.cancel()
        _session_locks.pop(session_id, None)
