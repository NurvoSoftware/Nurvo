## Context

The auth/credits system reads/writes Postgres via `asyncpg` (`db.py`); `init_pool()` only opens a pool — it does **not** create the schema, so the schema must be pre-loaded. The repo already ships schema SQL at the root: `nurvo_schema.sql` (175 lines, `CREATE TABLE IF NOT EXISTS`, includes the `uuid-ossp` extension and `credits` default 80) is the cleanest, but it lacks the `password_hash` column that `routers/auth.py` email login requires (the RUNBOOK records this as a manual `ALTER`). The frontend `LoginView` already has a working email/password form (`loginWithEmail` → `/api/auth/login`). The base `infra/docker-compose.yml` runs only `backend` + `frontend`.

## Goals / Non-Goals

**Goals:**
- `docker compose … up` (one documented command) brings up frontend + backend + Postgres, schema auto-loaded, backend connected.
- Log in locally with a seeded email/password account — no Google/cloud setup.
- Keep the base compose deployment-clean (no dev DB/seed/secret leaks into a real deploy).

**Non-Goals:**
- Production DB or secret management.
- Registering a Google OAuth localhost redirect (documented as optional).
- Any change to auth/credits/application logic.

## Decisions

### D1 — Dev DB lives in a compose override, not the base file
Add `infra/docker-compose.dev.yml` that defines the `db` (Postgres) service, the backend's dev env, and the init-SQL mounts. Local dev runs `docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up`.
- **Why:** the base compose is also the deploy artifact; a dev Postgres with a **seeded known-password account** must never ship. An override keeps the seed/secret strictly local.
- **Alternative considered:** add `db` to the base compose — rejected: risks seeding a known dev account into any environment that uses this compose.
- **Cost:** the dev run command needs two `-f` flags (documented in RUNBOOK).

### D2 — Schema + migration + seed as ordered init scripts
Mount three files into the Postgres `/docker-entrypoint-initdb.d/` (runs in alphabetical order on first init of an empty volume), under `infra/db-init/`:
1. `01-schema.sql` — the repo's `nurvo_schema.sql` (tables + `uuid-ossp` + indexes).
2. `02-password-hash.sql` — `ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);` (the gap email login needs).
3. `03-seed-dev-user.sql` — insert one dev user (see D3).
- **Why mount, not `psql` by hand:** zero manual steps; idempotent on a fresh volume.
- **Note:** init scripts only run when the data volume is empty. Re-seeding requires `docker compose … down -v`.

### D3 — One seeded dev account with a real bcrypt hash
`03-seed-dev-user.sql` inserts `dev@nurvo.local` with `credits = 80` and a **bcrypt** `password_hash` (passlib `bcrypt` scheme, matching `auth.py`'s `CryptContext(schemes=["bcrypt"])`). The hash is generated during implementation with the project's passlib and pasted into the SQL; the plaintext dev password is recorded only in the RUNBOOK.
- **Why bcrypt via the same scheme:** `email_login` verifies with `_pwd_context.verify`; the seed must use a compatible hash.
- **Alternative considered:** a register endpoint / runtime seed script — rejected: more moving parts than a one-line INSERT for a dev account.

### D4 — Env supplied by the override; template updated
The override sets on the backend: `DATABASE_URL=postgresql://nurvo:nurvo@db:5432/nurvo`, `JWT_SECRET_KEY=<dev-only value>`, `FRONTEND_URL=http://localhost:8080`. `nurvobackend/.env.example` gains these three keys with safe placeholders + comments so non-Docker runs know what to set.
- **Why in the override (not committed `.env`):** `.env` is gitignored; the override is the shared, reviewable source of the dev values, and they're clearly non-production.
- The Postgres service uses `POSTGRES_USER/PASSWORD/DB = nurvo` to match the DSN.

### D5 — Google OAuth stays optional for local dev
Email/password is the supported local path. RUNBOOK documents how to set `GOOGLE_CLIENT_ID/SECRET` + add `http://localhost:8000/api/auth/google/callback` to a Google OAuth client if a developer wants to exercise the Google flow.

## Risks / Trade-offs

- **Dev secret/seed leaking to prod** → Mitigation: everything dev lives in the override (D1); base compose unchanged; RUNBOOK marks them local-only.
- **`password_hash` already present in some DBs** → Mitigation: `ADD COLUMN IF NOT EXISTS` is idempotent.
- **bcrypt hash mismatch** → Mitigation: generate with the project's own passlib; verify by logging in during the smoke (the now-unblocked tasks).
- **`uuid-ossp` unavailable** → the official `postgres` image supports `CREATE EXTENSION "uuid-ossp"`; the schema already calls it.
- **Init scripts don't re-run on an existing volume** → documented: `down -v` to reset.

## Migration Plan

Additive + local-only. Bring up with the two-file compose command; on first run the volume initializes (schema + migration + seed). Roll back by removing the override (base stack is unchanged). To re-seed: `docker compose … down -v && up`.

## Open Questions

- Consolidate the three repo-root SQL dumps (`nurvo.sql`, `nurvo_schema.sql`, `nurvo_example.sql`) into one canonical `infra/db-init/` source later? (Out of scope here — we reuse `nurvo_schema.sql`.)
