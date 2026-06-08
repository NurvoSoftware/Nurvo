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

# Frontend:        http://localhost:8080
# API gateway:     http://localhost:31080
# digiRunner admin: http://localhost:31080/dgrv4/login   (default manager / manager123)

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

> The Vite dev server proxies `/api` and `/website` → `http://localhost:31080`, so it expects
> **digiRunner** on `:31080` (e.g. run only `digirunner` + `backend` from the compose file).
> To bypass the gateway, point `nurvofronted/vite.config.ts` at `http://localhost:8000`, or set
> `VITE_USE_MOCK_API=true` in `nurvofronted/.env.development` to run with no backend at all.

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
| `DIGIRUNNER_DB_PASSWORD` | no | empty | digiRunner H2 datasource password (root/infra `.env`) |

Frontend vars (`nurvofronted/.env.development`): `VITE_USE_MOCK_API`, `VITE_DIGIRUNNER_WS_SITE`
(default `nurvo-chat`, must match the digiRunner site name).

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
Production nginx already routes `/api/` and `/website/` to digiRunner; port `8000` is for
internal upstream only — do not expose it. Change the digiRunner admin password before any
non-local deployment.

## Troubleshooting

### digiRunner fails / logs errors on repeated startup (H2 schema init)
**Cause:** The bundled `schema.sql` replays on every boot, but the persisted file-based H2
already has the seed rows after the first start.
**Fix:** `SPRING_SQL_INIT_CONTINUE_ON_ERROR=true` is set in `infra/docker-compose.yml` to
tolerate the repeated init. If you wipe `digirunner_data`, the first boot re-seeds cleanly.

### Game sessions vanish after a backend restart
**Cause:** Sessions are stored **in memory only** (`session_store.py`); there is no database.
**Fix:** Expected for MVP — re-generate the scenario. Durable sessions require the planned
Supabase work; don't rely on session continuity across restarts.

### WebSocket won't connect / "session not found"
**Cause:** Wrong path or missing handshake. Through the gateway the client must connect to
`/website/<site>` (site = `VITE_DIGIRUNNER_WS_SITE`, default `nurvo-chat`) and send
`{"type":"session_join","session_id":"..."}` as the **first** frame.
**Fix:** Verify the site name matches digiRunner's config; for gateway-free debugging connect
directly to `ws://localhost:8000/api/chat/{session_id}`.

### Background image never appears
**Cause:** DALL·E generation is async; the client polls until ready.
**Fix:** Confirm `GET /api/scenario/{id}/background` returns `ready` with a URL; check
`OPENAI_API_KEY` quota and `DALLE_TIMEOUT`.
