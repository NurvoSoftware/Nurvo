# Architecture Decisions

<!-- One entry per significant architectural choice. Newest at the top.
     Purpose: explain WHY the system is shaped this way, not what it does.
     Future-you (and teammates) will thank present-you for writing this. -->

> These entries were reconstructed from the codebase and git history on 2026-06-08 as the
> initial system record, not authored at decision time — dates are approximate to the commits
> that introduced each choice. Refine when the original authors confirm details.

## 2026-06-08 — Removed digiRunner; frontend talks to FastAPI directly

**Context:** Every request used to route Browser → nginx → digiRunner → FastAPI. The gateway's
features (runtime routing, admin console, H2-persisted config) were not actually used, and the
extra hop made local dev and deployment more cumbersome — a gateway had to run on `:31080`, the
WebSocket handshake was order-dependent, and the default admin creds were a standing risk.

**Decision:** Drop the digiRunner service entirely. The frontend nginx now reverse-proxies
`/api/*` (REST) and `/api/chat/{session_id}` (WebSocket) straight to FastAPI at `backend:8000`.
Chat uses the existing path-based WebSocket endpoint (`session_id` in the URL); the gateway-only
`/api/chat/ws` endpoint and its `session_join` handshake were deleted.

**Alternatives considered:**
- Keep digiRunner but simplify its config — rejected: still an unused moving part plus dev/ops overhead.
- Minimal repoint (keep `/website` naming pointed at the backend) — rejected: leaves confusing
  gateway-shaped leftovers in code and docs.

**Consequences:**
- Simpler dev (just backend + Vite) and deploy (two containers, no H2 volume, no admin console).
- Lost gateway capabilities (edge rate-limiting, runtime route edits) — none were in use.
- Revisit if: a real edge need returns (auth at the gateway, multi-service routing) — reintroduce one then.

## ~2026 — In-memory session store (MVP)

**Context:** The MVP needed to ship the game loop fast without committing to a schema.

**Decision:** Store `GameSession` objects in a plain in-process dict
(`nurvobackend/session_store.py`). No database, no ORM, no migrations.

**Alternatives considered:**
- Postgres/Supabase from day one — rejected for MVP: schema churn cost while the model is
  still moving.
- Redis — rejected: adds an operational dependency before persistence is actually required.

**Consequences:**
- Makes iteration trivial; zero DB ops.
- Sessions are **lost on backend restart** and **cannot scale horizontally** (state is per
  process). Acceptable only for single-instance MVP.
- Revisit when: auth/accounts, progress history, or multi-instance deploy is needed — that's
  where the planned Supabase integration lands.

## ~2026 — Async DALL·E background generation with client polling

**Context:** DALL·E 3 image generation is slow (tens of seconds) and would block scenario
generation if done inline.

**Decision:** Generate the scenario immediately and return it; kick off the ward background
image as a separate async task. The frontend polls `GET /api/scenario/{id}/background` until
status flips from `pending` to `ready`.

**Alternatives considered:**
- Inline/blocking generation — rejected: long request, timeout risk, blank screen.
- Push via WebSocket — rejected: the WS channel is for the chat session; polling is simpler
  for a one-shot asset.

**Consequences:**
- Briefing renders fast; the background fills in shortly after.
- Adds a small polling loop on the client; the image may be briefly absent.
- Revisit if: more async assets appear (then a generic job/notification channel beats per-asset
  polling).

## ~2026 — Gender-aware ElevenLabs voice selection with fallback chain

**Context:** Patient and the three family members should sound distinct and gender-consistent
with the generated scenario, but not every voice ID is always configured.

**Decision:** Resolve each NPC's voice through a layered fallback in `config.py` +
`tts_service.py`: role+gender-specific ID → role legacy ID → patient default. TTS uses
`eleven_flash_v2_5` (low latency); audio is base64-streamed over the chat WebSocket after the
text reply.

**Alternatives considered:**
- A single shared voice — rejected: NPCs indistinguishable, breaks immersion.
- Hard-failing when a specific voice ID is missing — rejected: brittle; graceful degradation
  preferred.

**Consequences:**
- Robust to partial voice configuration; never crashes on a missing ID.
- Many env vars (patient male/female + 3 families × male/female + legacy defaults).
- Revisit if: voice catalog or roles change, or a different TTS provider is adopted.

## ~2026 — Proactive (idle-triggered) NPC speech

**Context:** Silence when the nurse hesitates feels unnatural and gives no training pressure.

**Decision:** When the nurse is idle past a threshold, an NPC speaks unprompted. Thresholds
shorten with a "streak" (`PROACTIVE_IDLE_THRESHOLDS=25,20,15`), gated by a cooldown
(`PROACTIVE_COOLDOWN_SECONDS`) and suppressed near the end of the game
(`PROACTIVE_ENDGAME_GUARD_SECONDS`). Toggleable via `PROACTIVE_ENABLED`. Activity signals
(typing/audio/reconnect) reset idle tracking; `RECONNECT_GRACE_SECONDS` tolerates brief drops.

**Alternatives considered:**
- No proactive speech — rejected: static, less realistic.
- Fixed-interval prompts — rejected: ignores nurse activity and game phase; feels robotic.

**Consequences:**
- More lifelike, pressure-aware NPCs; fully tunable via env.
- More conversation-engine state (idle timers, streak, cooldown, endgame guard) to reason about.
- Revisit if: pacing complaints arise, or the timing logic needs per-difficulty tuning.
