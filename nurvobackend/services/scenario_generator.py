"""Scenario generation service using OpenAI GPT-4o."""

import json
import uuid

from fastapi import HTTPException
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT
from models.scenario import Scenario
from prompts.scenario_generation import SCENARIO_GENERATION_PROMPT


_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_scenario() -> tuple[str, Scenario]:
    """Generate a unique nursing scenario via OpenAI and return (session_id, Scenario)."""
    try:
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

        # Strip markdown code fences if present
        cleaned = content.strip()
        if cleaned.startswith("```"):
            # Remove opening fence (possibly ```json)
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        scenario_data = json.loads(cleaned)
        scenario = Scenario(**scenario_data)

        session_id = str(uuid.uuid4())
        return session_id, scenario

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to parse scenario JSON from OpenAI: {exc}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI scenario generation failed: {exc}",
        )
