"""WebSocket chat router for real-time nurse-NPC conversation."""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import GAME_TIME_LIMIT
from models.chat import ChatMessage, SessionStatus
from services.conversation_engine import get_npc_response, maybe_family_interjection
from session_store import get_session, update_session

router = APIRouter(prefix="/chat", tags=["chat"])


def _elapsed_seconds(start_time: datetime) -> float:
    """Calculate elapsed seconds from session start to now."""
    now = datetime.now(timezone.utc)
    return round((now - start_time).total_seconds(), 1)


async def _send_json(ws: WebSocket, data: dict) -> None:
    """Send a JSON message over the WebSocket."""
    await ws.send_text(json.dumps(data, ensure_ascii=False))


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

    # Start session timer on first connection if not already started
    if session.start_time is None:
        session.start_time = datetime.now(timezone.utc)
        session.status = SessionStatus.PLAYING
        update_session(session)

    # Send initial timer state
    initial_elapsed = _elapsed_seconds(session.start_time)
    initial_remaining = max(0, GAME_TIME_LIMIT - int(initial_elapsed))
    await _send_json(ws, {
        "type": "timer_update",
        "remaining_seconds": initial_remaining,
    })

    # Start background timer task
    timer = asyncio.create_task(_timer_task(ws, session_id, session.start_time))

    try:
        while True:
            raw = await ws.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await _send_json(ws, {"type": "error", "content": "Invalid JSON"})
                continue

            msg_type = data.get("type")
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
