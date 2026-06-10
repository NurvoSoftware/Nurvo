# Runbook

<!-- Operational reference: how to run, debug, and deploy this system.
     Update whenever setup steps or deploy procedures change. -->

## Local development

### Full stack via Docker (recommended)

```bash
# 1. Create nurvobackend/.env with API keys (see .env.example).
# 2. From the repo root:
docker compose -f infra/docker-compose.yml build --no-cache && \
  docker compose -f infra/docker-compose.yml up --force-recreate

# Frontend:        http://localhost:8080  (nginx proxies /api/* and /api/chat/ to the backend)
# Backend (direct, for debugging): http://localhost:8000

# Stop:
docker compose -f infra/docker-compose.yml down
```

### Backend only (FastAPI)

```bash
cd nurvobackend
pip install -r requirements.txt
uvicorn main:app --reload    # http://localhost:8000
```

### Frontend only (Vite)

```bash
cd nurvofronted
npm install
npm run dev                  # http://localhost:5173
```

> The Vite dev server proxies `/api` (REST + WebSocket) → `http://localhost:8000`, so just run
> the backend alongside it. Set `VITE_USE_MOCK_API=true` in `nurvofronted/.env.development` to
> run the UI with no backend at all.

## Environment variables

Backend vars live in `nurvobackend/.env` (template: `nurvobackend/.env.example`).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | yes | — | OpenAI key (also used by DALL·E 3) |
| `OPENAI_MODEL` | no | `gpt-4o` | Scenario generation + scoring |
| `OPENAI_CONVERSATION_MODEL` | no | `gpt-4.1-mini` | NPC chat + interjections |
| `OPENAI_TIMEOUT` | no | `30` | OpenAI request timeout (s) |
| `DALLE_MODEL` / `DALLE_SIZE` / `DALLE_QUALITY` / `DALLE_TIMEOUT` | no | `dall-e-3` / `1792x1024` / `standard` / `60` | Background image generation |
| `ELEVENLABS_API_KEY` | yes | — | TTS + Scribe STT |
| `ELEVENLABS_TTS_MODEL` | no | `eleven_flash_v2_5` | TTS model |
| `ELEVENLABS_PATIENT_*` / `ELEVENLABS_FAMILY_{0,1,2}_*_VOICE_ID` | no | fall back to patient default | Per-role, per-gender voice IDs |
| `GAME_TIME_LIMIT` | no | `480` | Base game length (s); overridden per difficulty |
| `PROACTIVE_ENABLED` | no | `true` | Idle-triggered NPC speech on/off |
| `PROACTIVE_IDLE_THRESHOLDS` | no | `25,20,15` | Idle seconds per streak before NPC speaks |
| `PROACTIVE_COOLDOWN_SECONDS` | no | `10` | Min gap between proactive events |
| `PROACTIVE_ENDGAME_GUARD_SECONDS` | no | `30` | Suppress proactive speech near timeout |
| `RECONNECT_GRACE_SECONDS` | no | `10` | WebSocket reconnect grace window |
| `DATABASE_URL` | yes | — | asyncpg connection string, e.g. `postgresql+asyncpg://postgres:1234@localhost:5432/nurvo` |
| `GOOGLE_CLIENT_ID` | yes | — | OAuth 2.0 client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | yes | — | OAuth 2.0 client secret from Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | yes | `http://localhost:8000/api/auth/google/callback` | Must match an Authorized redirect URI in Google Cloud Console |
| `FRONTEND_URL` | yes | `http://localhost:5173` | Used to build the post-OAuth redirect back to the SPA |
| `JWT_SECRET_KEY` | yes | — | Random secret for signing JWTs — change before deploy |
| `JWT_EXPIRE_DAYS` | no | `7` | JWT lifetime in days |

Frontend vars (`nurvofronted/.env.development`): `VITE_USE_MOCK_API`.

## Google Cloud Console setup (one-time)

1. Go to **APIs & Services → Credentials** in Google Cloud Console.
2. Create or open an OAuth 2.0 Client ID (Web application).
3. Add `http://localhost:8000/api/auth/google/callback` to **Authorized redirect URIs**.
4. Copy the Client ID and Client Secret into `nurvobackend/.env`.

## Database setup (one-time)

```sql
-- Run in pgAdmin or psql against the 'nurvo' database
-- Import nurvo_example.sql to create the schema, then apply any pending migrations:
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS password_hash character varying(255);
ALTER TABLE public.game_sessions ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE public.game_sessions ADD COLUMN IF NOT EXISTS chat_messages jsonb DEFAULT '[]'::jsonb NOT NULL;
```

## Common tasks

### Run tests
```bash
cd nurvobackend && pytest          # backend unit tests (gender/voice/websocket)
cd nurvofronted && npm run test:unit   # frontend Vitest
```

### Run linter / type-check
```bash
cd nurvofronted && npm run type-check   # vue-tsc
cd nurvofronted && npm run lint         # eslint + oxlint + prettier
# Backend: ruff (per agentkit .claude/rules), e.g. `ruff check nurvobackend`
```

### Deploy
```bash
docker compose -f infra/docker-compose.yml build --no-cache && \
  docker compose -f infra/docker-compose.yml up -d --force-recreate
```
Production nginx routes `/api/` (REST) and `/api/chat/` (WebSocket) directly to the FastAPI
backend; port `8000` is for internal upstream only — do not expose it.

## Troubleshooting

### Game sessions vanish after a backend restart
**Cause:** Sessions are stored **in memory only** (`session_store.py`); there is no database.
**Fix:** Expected for MVP — re-generate the scenario. Durable sessions require the planned
Supabase work; don't rely on session continuity across restarts.

### WebSocket won't connect / "session not found"
**Cause:** Wrong path or an unknown/expired `session_id`. The client must connect to
`ws://<host>/api/chat/{session_id}` with a valid id from `POST /api/scenario/generate`.
**Fix:** Confirm the session was generated (and that the backend hasn't restarted — sessions are
in-memory). In dev, ensure Vite's `/api` proxy has `ws: true` so the upgrade reaches the backend.

### Background image never appears
**Cause:** DALL·E generation is async; the client polls until ready.
**Fix:** Confirm `GET /api/scenario/{id}/background` returns `ready` with a URL; check
`OPENAI_API_KEY` quota and `DALLE_TIMEOUT`.
