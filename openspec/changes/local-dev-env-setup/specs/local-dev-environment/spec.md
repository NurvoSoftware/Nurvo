## ADDED Requirements

### Requirement: One-command local stack with Postgres

The project SHALL provide a documented command that brings up frontend, backend, and a Postgres database together for local development, with the backend waiting until the database is ready before it serves requests.

#### Scenario: Stack starts with a database
- **WHEN** the developer runs the documented local-dev compose command
- **THEN** a Postgres service starts, the backend connects to it (no "DB unavailable" log), and the SPA is reachable at the documented URL

#### Scenario: Base compose stays deployment-clean
- **WHEN** the base `infra/docker-compose.yml` is used without the dev override
- **THEN** it contains no dev database, seed account, or dev secrets

### Requirement: Schema loaded automatically on first start

On first initialization of an empty database volume, the schema (all tables, the `uuid-ossp` extension, and the `password_hash` column required by email login) SHALL be created automatically without manual SQL steps.

#### Scenario: Tables exist after first boot
- **WHEN** the local stack is started against an empty DB volume
- **THEN** the `users` table exists with a `password_hash` column and the other application tables are present

### Requirement: Seeded dev account for email login

A single dev account SHALL be seeded with a known email, a valid bcrypt password hash, and non-zero credits, so a developer can log in through the existing email/password form without any external (Google) setup.

#### Scenario: Developer logs in and generates a scenario
- **WHEN** the developer logs in with the seeded dev credentials and starts a game
- **THEN** authentication succeeds and scenario generation proceeds (credits are deducted from the seeded balance)

### Requirement: Required environment is documented and templated

The environment variables the auth/DB system needs (`DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_URL`) SHALL be present in `nurvobackend/.env.example` and the local-dev values SHALL be supplied by the dev setup, with the run steps and seed credentials recorded in the runbook.

#### Scenario: Env template lists the auth/DB vars
- **WHEN** `nurvobackend/.env.example` is inspected
- **THEN** it includes `DATABASE_URL`, `JWT_SECRET_KEY`, and `FRONTEND_URL` with safe placeholder values and comments

#### Scenario: Runbook documents the local-dev flow
- **WHEN** a new developer reads `sysdoc/RUNBOOK.md`
- **THEN** it states the local-dev compose command, the seed login credentials, and how to optionally configure Google OAuth
