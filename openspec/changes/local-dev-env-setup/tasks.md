## 1. DB init scripts

- [x] 1.1 Create `infra/db-init/01-schema.sql` from the repo's `nurvo_schema.sql` (tables + `uuid-ossp` + indexes).
- [x] 1.2 Create `infra/db-init/02-password-hash.sql`: `ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);`
- [x] 1.3 Generate a bcrypt hash for the dev password with the project's passlib (`.venv/bin/python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('<dev-pw>'))"`); create `infra/db-init/03-seed-dev-user.sql` inserting `dev@nurvo.local` with that hash and `credits = 80`.

## 2. Compose override

- [x] 2.1 Create `infra/docker-compose.dev.yml`: a `db` (postgres) service with `POSTGRES_USER/PASSWORD/DB=nurvo`, a named volume, a healthcheck (`pg_isready`), and the `infra/db-init/` mount into `/docker-entrypoint-initdb.d/`.
- [x] 2.2 In the override, set the backend's dev env (`DATABASE_URL=postgresql://nurvo:nurvo@db:5432/nurvo`, `JWT_SECRET_KEY=<dev>`, `FRONTEND_URL=http://localhost:8080`) and `depends_on: db: condition: service_healthy`.

## 3. Env template

- [x] 3.1 Add `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_URL` (placeholders + comments) to `nurvobackend/.env.example`.

## 4. Bring up & verify (unblocks the deferred smokes)

- [x] 4.1 `docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build`; confirm Postgres starts healthy and the backend logs the pool initialized (no "DB unavailable").
- [x] 4.2 Log in at `http://localhost:8080` with the seeded dev account; confirm `/api/auth/me` returns the user and a scenario generates (credits deducted).
- [x] 4.3 Now-unblocked smokes DONE (2026-06-21). `chat-mention-chips` 5.2: @ dropdown → chip + text strip, tab toggle, `×` remove, send clean content (no `@`), targeted NPC reply over WS, IME guard — all verified live. `harden-web-security` 4.1: headers re-confirmed by curl on `:8080`, app driven live with a clean console, font + background render. (See each change's task notes for detail.)

## 5. Docs

- [x] 5.1 Update `sysdoc/RUNBOOK.md`: the two-file local-dev compose command, seed credentials (`dev@nurvo.local` / `<dev-pw>`), `down -v` to re-seed, and the optional Google OAuth localhost setup.

## 6. Close out

- [x] 6.1 Marked the two deferred tasks complete in their changes (`chat-mention-chips` 5.2, `harden-web-security` 4.1) with the smoke results.
- [x] 6.2 `openspec validate local-dev-env-setup` passed; change committed (165fde8) and pushed to main.
