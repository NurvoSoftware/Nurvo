"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_PATIENT_VOICE_ID: str = os.getenv("ELEVENLABS_PATIENT_VOICE_ID", "")
ELEVENLABS_FAMILY_VOICE_ID_0: str = os.getenv("ELEVENLABS_FAMILY_VOICE_ID_0", os.getenv("ELEVENLABS_FAMILY_VOICE_ID", ""))
ELEVENLABS_FAMILY_VOICE_ID_1: str = os.getenv("ELEVENLABS_FAMILY_VOICE_ID_1", os.getenv("ELEVENLABS_FAMILY_VOICE_ID", ""))
ELEVENLABS_FAMILY_VOICE_ID_2: str = os.getenv("ELEVENLABS_FAMILY_VOICE_ID_2", os.getenv("ELEVENLABS_FAMILY_VOICE_ID", ""))

OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
GAME_TIME_LIMIT: int = int(os.getenv("GAME_TIME_LIMIT", "480"))
