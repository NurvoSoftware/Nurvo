# Architecture Decisions

<!-- One entry per significant architectural choice. Newest at the top.
     Purpose: explain WHY the system is shaped this way, not what it does.
     Future-you (and teammates) will thank present-you for writing this. -->

> These entries were reconstructed from the codebase and git history on 2026-06-08 as the
> initial system record, not authored at decision time — dates are approximate to the commits
> that introduced each choice. Refine when the original authors confirm details.

## ~2026 — digiRunner gateway in front of FastAPI

**Context:** The frontend needs one stable entry point for both REST and WebSocket traffic,
and the team wanted to avoid exposing the FastAPI backend directly or scattering proxy rules
across nginx and app code.

**Decision:** Run TPIsoftware digiRunner OSS v4.7.3 as an API gateway. Browser → nginx →
digiRunner → FastAPI. REST goes through `/api/*`; WebSocket connects to `/website/<site>`
(default site `nurvo-chat`) which digiRunner proxies to the backend's fixed `/api/chat/ws`.
The gateway also persists its proxy/site config in a **file-based H2** database at
`/app/data/dgrdb` so configuration survives container restarts. It binds **loopback-only**
(`127.0.0.1:31080`) to avoid LAN exposure.

**Alternatives considered:**
- nginx-only reverse proxy — rejected: no admin console / runtime-editable routing, weaker
  WebSocket proxy story.
- Expose FastAPI directly — rejected: larger attack surface, no gateway-level controls.

**Consequences:**
- Makes routing/observability/runtime config easier (admin console at `/dgrv4/login`).
- Makes local dev heavier: the Vite proxy points at `:31080`, so digiRunner must be running
  locally (or you edit `vite.config.ts` to hit `:8000`).
- The WebSocket handshake is order-dependent: the **first** frame must be `session_join`.
- Operational risk: default admin creds (`manager / manager123`) must be changed before any
  non-local deployment.
- Revisit if: the gateway becomes a bottleneck, or routing needs outgrow what nginx could do.

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
