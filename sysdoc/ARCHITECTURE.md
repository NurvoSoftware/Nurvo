# Architecture Decisions

<!-- One entry per significant architectural choice. Newest at the top.
     Purpose: explain WHY the system is shaped this way, not what it does.
     Future-you (and teammates) will thank present-you for writing this. -->

> These entries were reconstructed from the codebase and git history on 2026-06-08 as the
> initial system record, not authored at decision time — dates are approximate to the commits
> that introduced each choice. Refine when the original authors confirm details.

## 2026-06-20 — Baseline HTTP security headers (per-layer) + self-hosted font

**Context:** An HCL AppScan scan of the production deployment flagged 11 issues, mostly missing
HTTP security headers (CSP, X-Content-Type-Options, Referrer-Policy, COOP/COEP/CORP, HSTS), a
missing Subresource Integrity on the Google Fonts `<link>`, and a cacheable sensitive response.
(`openspec/changes/harden-web-security`.)

**Decision:** Emit the baseline headers from **two layers by response owner** — nginx adds them
on the static SPA (`location /` only), and a FastAPI `SecurityHeadersMiddleware` adds them on
every `/api/*` response (plus `Cache-Control: no-store`). Headers are deliberately *not* set at
nginx `server` level so proxied `/api/*` responses aren't double-headed. The Inter font is
**self-hosted** via `@fontsource/inter` (imported in `main.ts`) instead of the Google CDN —
because the Google Fonts CSS varies by User-Agent, a pinned SRI hash is unreliable; self-hosting
removes the third-party dependency entirely and makes the font same-origin.

**Alternatives considered:**
- Single `server`-level nginx header block — rejected: duplicates headers on proxied API responses.
- SRI hash on the Google Fonts link — rejected: UA-dependent CSS makes the hash fragile (proven:
  two UAs → two hashes).
- `COEP: require-corp` (the scanner's recommendation) — rejected for `credentialless`, which still
  satisfies the finding but doesn't block cross-origin subresources (e.g. remote DALL·E images).

**Consequences:**
- Headers are portable — they survive whatever edge fronts the app (our nginx, the production
  IIS/ARR, or Vite in dev), since the API ones live in the app itself.
- CSP keeps `style-src 'unsafe-inline'` (Vue/PrimeVue inject runtime styles); `script-src 'self'`
  (no `unsafe-inline`/`eval`) is the part that matters for XSS.
- Two infra-only findings (#1 force-HTTPS, #6 Spring Actuator) are operator tasks, not in this repo
  (see RUNBOOK). Interactive CSP/COEP smoke is pending the local auth/DB env fix.

## 2026-06-11 — JWT auth with Google OAuth + email/password; token in URL hash

**Context:** The game needs to know who is playing (for session persistence and future progress
tracking). We wanted to support Google Sign-In as the primary method but also email/password for
accounts without Google. The login page should be a dedicated route, not a direct browser
redirect to Google.

**Decision:** All auth entry points (`startGame()`, NavBar button, route guard) push to `/login`,
a dedicated page where the user chooses their method. Google OAuth uses the authorization code
flow (server-side exchange in FastAPI, never exposes the secret to the browser). The resulting
JWT is passed back to the SPA in the URL hash (`#token=...`) rather than a query param so it is
never sent to any server in a request log. `AuthCallbackView` reads the hash, moves the token to
`localStorage`, and navigates to the original destination.

**Alternatives considered:**
- HttpOnly cookie instead of localStorage JWT — better CSRF protection, but requires a
  same-origin setup; deferred to post-MVP when deployment domain is settled.
- Redirect directly to Google on first protected-route access — rejected: no room to add
  email/password or future methods without another refactor.

**Consequences:**
- Single `/login` page is the universal auth wall; adding new login methods only touches that
  one view and the backend auth router.
- JWT in `localStorage` is accessible to JavaScript (XSS risk) — acceptable for MVP, revisit
  when the security hardening spec (`openspec/changes/harden-web-security`) ships.

## 2026-06-11 — Best-effort async DB persistence for completed sessions

**Context:** Sessions are in-memory; if the backend restarts, all history is lost. We want
completed sessions written to Postgres without blocking the score API response.

**Decision:** After `POST /api/score/evaluate` finishes, `asyncio.create_task()` fires
`persist.save_completed_session()` in the background. The API returns the scorecard immediately;
the DB write happens asynchronously. `save_completed_session` wraps everything in a single
try/except — if it fails, the user's scorecard is still returned and an error is logged.

**Alternatives considered:**
- Blocking DB write before returning — rejected: adds latency to the critical score response path.
- Queue (e.g. Redis) — rejected: operational overhead before persistence is even proven useful.

**Consequences:**
- Score API stays fast; DB write failures are silent to the user.
- A crash immediately after score evaluation can lose the session record — acceptable at MVP scale.
- Revisit when: sessions must be reliably queryable (progress history, analytics).

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
