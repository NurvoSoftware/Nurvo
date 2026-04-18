"""Scenario generation service using OpenAI GPT-4o and DALL-E 3."""

import asyncio
import json
import logging
import uuid

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from config import (
    DALLE_MODEL,
    DALLE_QUALITY,
    DALLE_SIZE,
    DALLE_TIMEOUT,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TIMEOUT,
)
from models.scenario import Scenario
from prompts.scenario_generation import SCENARIO_GENERATION_PROMPT

_MAX_SCENARIO_ATTEMPTS = 2


_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
_logger = logging.getLogger(__name__)

_BACKGROUND_PROMPT = (
    "A realistic, warm hospital ward interior scene. "
    "An elderly patient is resting peacefully in a hospital bed, "
    "wearing a light hospital gown, with medical equipment visible nearby. "
    "Three family members are gathered around the bedside showing care and concern, "
    "some standing and some seated. "
    "Soft natural lighting comes through a large window, creating a calm supportive atmosphere. "
    "Pale blue walls, clean tiled floor, curtains partially drawn. "
    "Taiwanese hospital setting. Photorealistic cinematic wide-angle shot. "
    "No text, no labels, no watermarks, no on-screen captions."
)


async def _call_openai_for_scenario() -> Scenario:
    """Issue a single GPT-4o call and parse the response into a Scenario.

    Raises HTTPException for empty/malformed responses and ValidationError
    when the returned JSON violates Scenario model constraints (family
    relationships, surname rules, etc.).
    """
    response = await _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a nursing education scenario generator. Respond only with valid JSON."},
            {"role": "user", "content": SCENARIO_GENERATION_PROMPT},
        ],
        temperature=0.9,
        timeout=OPENAI_TIMEOUT,
    )

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(status_code=502, detail="OpenAI returned empty response")

    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    try:
        scenario_data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to parse scenario JSON from OpenAI: {exc}",
        )

    return Scenario(**scenario_data)


async def _generate_scenario_text() -> Scenario:
    """Generate scenario text via GPT-4o with one retry on validation failure.

    Validation failures (e.g. LLM returns "主治醫師" as a family relationship
    or gives every family member a different surname from the patient) are
    transient and often resolved by a second sampling. Non-validation errors
    (JSON parse, OpenAI network/timeout) are surfaced immediately without retry.
    """
    last_validation_error: ValidationError | None = None

    for attempt in range(1, _MAX_SCENARIO_ATTEMPTS + 1):
        try:
            return await _call_openai_for_scenario()
        except ValidationError as exc:
            last_validation_error = exc
            _logger.warning(
                "Scenario validation failed on attempt %d/%d: %s",
                attempt,
                _MAX_SCENARIO_ATTEMPTS,
                exc.errors(),
            )

    raise HTTPException(
        status_code=502,
        detail=f"Scenario validation failed after retry: {last_validation_error}",
    )


async def _generate_background_image() -> str | None:
    """Call DALL-E 3 to generate a hospital ward background image.

    Returns the image URL on success, or None on failure. Never raises —
    image generation is best-effort, frontend falls back to the static
    hospital_bg.jpg when this returns None.
    """
    try:
        response = await _client.images.generate(
            model=DALLE_MODEL,
            prompt=_BACKGROUND_PROMPT,
            size=DALLE_SIZE,
            quality=DALLE_QUALITY,
            n=1,
            timeout=DALLE_TIMEOUT,
        )
        return response.data[0].url
    except Exception as exc:
        _logger.warning("DALL-E 3 image generation failed: %s", exc)
        return None


async def generate_scenario() -> tuple[str, Scenario]:
    """Generate scenario text (GPT-4o) and background image (DALL-E 3) in parallel."""
    try:
        scenario, image_url = await asyncio.gather(
            _generate_scenario_text(),
            _generate_background_image(),
        )

        scenario.background_image_url = image_url
        session_id = str(uuid.uuid4())
        return session_id, scenario

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI scenario generation failed: {exc}",
        )
