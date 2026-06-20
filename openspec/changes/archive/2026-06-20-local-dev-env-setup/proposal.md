## Why

A rebased merge added a full **auth + Postgres + credits** system (`routers/auth.py`, `db.py`, `scenario.py` now requires `Depends(get_current_user)` and deducts DB credits), but nothing wired it up for local development: `infra/docker-compose.yml` has no Postgres, `DATABASE_URL`/`JWT_SECRET_KEY` are empty, and there is no login account. The result is that **the app can no longer run end-to-end locally** — login fails ("Missing client_id" for Google, 401 for email since there's no user/DB), and even with a token, scenario generation fails on the missing DB. This blocks the two deferred manual-smoke tasks (`chat-mention-chips` 5.2 and `harden-web-security` 4.1) and all local testing.

## What Changes

- **Add a Postgres service for local dev** via a compose override `infra/docker-compose.dev.yml` (keeps the base compose deployment-clean — the dev DB and seed account never ship). The backend `depends_on` the DB being healthy.
- **Auto-load the schema on first DB start** by mounting init SQL into the Postgres `/docker-entrypoint-initdb.d/`: the existing `nurvo_schema.sql` (tables, `uuid-ossp`, `credits` default), plus the `password_hash` column migration that email login needs.
- **Seed one dev login account** (email + bcrypt `password_hash` + credits) so the developer can log in via the existing email/password form — no Google Cloud setup required for local dev.
- **Provide the required env** for local dev: `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_URL` (set in the override and added to `nurvobackend/.env.example` with safe placeholders).
- **Document the local-dev run** in `sysdoc/RUNBOOK.md` (the two-file compose command, the seed credentials, where to set Google OAuth if wanted).

No application code changes; this is environment/infra + docs. **Not for production** — the dev DB, seed account, and dev secrets are local-only.

## Capabilities

### New Capabilities
- `local-dev-environment`: A developer SHALL be able to bring up the full stack locally (frontend + backend + Postgres) with one documented command, log in with a seeded dev account, and run a scenario end-to-end, without any external (Google/cloud) setup.

### Modified Capabilities
<!-- None — no existing spec covers the dev environment. -->

## Impact

- **Infra:** new `infra/docker-compose.dev.yml` (Postgres service + backend dev env + init-SQL mounts); base `infra/docker-compose.yml` stays unchanged.
- **DB init:** new SQL under `infra/db-init/` (or reuse repo-root `nurvo_schema.sql`) + a `password_hash` migration + a dev seed.
- **Config:** `nurvobackend/.env.example` gains `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_URL`.
- **Docs:** `sysdoc/RUNBOOK.md` local-dev section.
- **Unblocks:** `chat-mention-chips` task 5.2 and `harden-web-security` task 4.1 (interactive smoke).
- **Out of scope:** production DB/secret management; Google OAuth localhost registration (documented as optional); any change to auth/credits application logic.
