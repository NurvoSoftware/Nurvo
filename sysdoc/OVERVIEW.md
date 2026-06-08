# System Overview

<!-- Keep this file up to date whenever a major feature ships.
     Goal: a new team member reads this and understands the system in 5 minutes. -->

## What this system does

Nurvo (護理溝通情境遊戲) is an AI-powered training game for nursing communication skills.
A nurse plays through a procedurally generated clinical scenario, talking (voice or text, in
Traditional Chinese) with one AI patient and three AI family members to practice pain
assessment and family communication. After the session the nurse writes a nursing record and
receives an LLM-graded scorecard across five communication dimensions. Audience: nursing
students and practicing nurses. The project is at MVP stage, deployed as a single-machine
Docker Compose stack.

## Main components

| Component | Role | Location |
|-----------|------|----------|
| Frontend SPA | Vue 3 + Vite + TS game UI (6-step flow, chat, dashboard) | `nurvofronted/` (nginx, host `:8080`→`:80`) |
| Backend API | FastAPI app: scenario gen, chat loop, scoring, STT | `nurvobackend/` (host `:8000`) |
| Conversation engine | NPC replies, family interjections, idle→proactive speech | `nurvobackend/services/conversation_engine.py` |
| Session store | In-memory game state (no DB) | `nurvobackend/session_store.py` |
| External AI services | LLM, image, voice (see table below) | called from `nurvobackend/services/` |

## Data flow

End-to-end request path:

1. Browser loads the Vue SPA from nginx (`:8080`).
2. SPA calls `/api/*` (REST) and `/api/chat/{session_id}` (WebSocket); the frontend nginx
   reverse-proxies both directly to FastAPI (`backend:8000`).
3. FastAPI calls out to OpenAI, DALL·E 3, and ElevenLabs as needed.

Game lifecycle (the user journey the data follows):

1. **Generate** — `POST /api/scenario/generate {difficulty}` → GPT-4o builds the scenario;
   DALL·E 3 renders the ward background **asynchronously** (frontend polls
   `GET /api/scenario/{id}/background`). A `GameSession` is created in memory.
2. **Briefing** — frontend shows patient profile, family cards, communication challenges.
3. **Chat** — WebSocket at `/api/chat/{session_id}`: client sends `nurse_message{target}`; the
   conversation engine returns `npc_message` (+ `npc_audio` TTS), plus probabilistic family
   interjections and idle-triggered proactive speech, under a per-difficulty countdown.
4. **Record** — `POST /api/record/submit` stores the nurse's clinical note; status → SCORING.
5. **Score** — `POST /api/score/evaluate` → GPT-4o rubric returns weighted scores (empathy 20%,
   guided questioning 25%, family calming 15%, info gathering 25%, response fluency 15%),
   strengths, improvements, and key moments → Dashboard.

## Key external dependencies

| Dependency | Purpose |
|------------|---------|
| OpenAI GPT-4o | Scenario generation + scoring/evaluation |
| OpenAI gpt-4.1-mini | NPC conversation + family interjections (default, configurable) |
| OpenAI DALL·E 3 | Async ward background image generation |
| ElevenLabs TTS (`eleven_flash_v2_5`) | NPC voices, gender-aware per role |
| ElevenLabs Scribe | Nurse speech-to-text (Mandarin) |

## What is intentionally out of scope

- **Persistence & auth** — sessions live in memory only; they are lost on backend restart.
  Supabase (auth + storage) is *planned*, not built. No user accounts, no migrations.
- **Localization** — Traditional Chinese only.
- **Native mobile** — web/browser only (responsive layout); no iOS/Android/desktop client.
