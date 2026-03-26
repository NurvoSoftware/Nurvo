"""Conversation engine service for patient and family NPC responses."""

from fastapi import HTTPException
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from models.chat import GameSession
from services.tts_service import get_family_voice, get_patient_voice


_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Minimum nurse-to-patient messages between family interjections
_MIN_INTERJECTION_GAP = 2
# Max recent messages to include in interjection decision context
_MAX_DECISION_HISTORY = 10


def _count_messages_since_last_interjection(session: GameSession) -> int:
    """Count nurse messages to patient since the last family interjection."""
    count = 0
    for msg in reversed(session.conversation_history):
        if msg.is_interjection:
            break
        if msg.sender == "nurse":
            count += 1
    return count


def _build_history(messages: list) -> list[dict[str, str]]:
    """Convert ChatMessage list to OpenAI message format with speaker labels."""
    history: list[dict[str, str]] = []
    for msg in messages:
        if msg.sender == "nurse":
            history.append({"role": "user", "content": msg.content})
        else:
            label = "[病患]" if msg.sender == "patient" else "[家屬]"
            history.append({"role": "assistant", "content": f"{label} {msg.content}"})
    return history


def _build_openai_messages(
    system_prompt: str,
    conversation_history: list[dict[str, str]],
    nurse_message: str,
) -> list[dict[str, str]]:
    """Build the OpenAI messages list from system prompt, history, and new nurse message."""
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": nurse_message})
    return messages


async def get_npc_response(
    session: GameSession,
    nurse_message: str,
    target: str,
) -> tuple[str, str, str]:
    """Get an NPC response for the nurse's message.

    Returns (npc_response_text, sender, audio_base64) where sender is
    'patient' or 'family' and audio_base64 may be empty on TTS failure.
    """
    if target == "patient":
        system_prompt = session.patient_system_prompt
        sender = "patient"
    elif target == "family":
        system_prompt = session.family_system_prompt
        sender = "family"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid target: {target}")

    history = _build_history(session.conversation_history)
    messages = _build_openai_messages(system_prompt, history, nurse_message)

    try:
        response = await _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            timeout=5,
        )

        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=502, detail="OpenAI returned empty NPC response")

        npc_text = content.strip()

        # Generate TTS audio (non-blocking; falls back to empty string)
        if sender == "patient":
            audio_base64 = await get_patient_voice(npc_text)
        else:
            audio_base64 = await get_family_voice(npc_text)

        return npc_text, sender, audio_base64

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"NPC response generation failed: {exc}",
        )


async def maybe_family_interjection(session: GameSession) -> tuple[str, bool, str]:
    """Use LLM to decide whether the family member should interject based on conversation content.

    Returns (interjection_text, did_interject, audio_base64).
    Decisions are content-driven, not counter-based.
    """
    # Enforce minimum gap between interjections
    messages_since = _count_messages_since_last_interjection(session)
    if messages_since < _MIN_INTERJECTION_GAP:
        return "", False, ""

    # Build recent history only (last N messages for performance)
    recent_messages = session.conversation_history[-_MAX_DECISION_HISTORY:]
    history = _build_history(recent_messages)

    decision_prompt = (
        "根據目前的對話，判斷你（作為家屬）是否需要在此刻插話。\n"
        "只在以下情況插話：\n"
        "- 護理師提到讓你擔心的內容（疼痛加劇、需要手術、藥物副作用等）\n"
        "- 你覺得護理師忽略了重要資訊\n"
        "- 你等太久想催促\n"
        "- 對話觸發了你的情緒（根據你的性格）\n\n"
        "回覆格式嚴格如下：\n"
        "第一行只寫 YES 或 NO\n"
        "如果 YES，第二行寫你要說的話（一到兩句，簡短自然）"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": session.family_system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": decision_prompt})

    try:
        response = await _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=100,
            timeout=5,
        )

        content = response.choices[0].message.content
        if not content:
            return "", False, ""

        lines = content.strip().split("\n", 1)
        if lines[0].strip().upper() == "YES" and len(lines) > 1:
            interjection_text = lines[1].strip()
            if not interjection_text:
                return "", False, ""
            audio_base64 = await get_family_voice(interjection_text)
            return interjection_text, True, audio_base64

        return "", False, ""

    except Exception:
        # Don't fail the main flow for an interjection error
        return "", False, ""
