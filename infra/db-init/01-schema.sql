-- ============================================================
-- Nurvo schema — local-dev Docker init (runs once on an empty volume).
-- Source: repo-root nurvo_schema.sql, minus `CREATE DATABASE` (Docker's
-- POSTGRES_DB already created the `nurvo` database and connected to it).
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id            UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    name          VARCHAR(255),
    picture_url   VARCHAR(512),
    google_id     VARCHAR(255) UNIQUE,
    credits       INT          NOT NULL DEFAULT 80,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_users_email     ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);

-- 2. game_sessions
CREATE TABLE IF NOT EXISTS game_sessions (
    id                 UUID        PRIMARY KEY,
    user_id            UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    difficulty         VARCHAR(10) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    status             VARCHAR(20) NOT NULL DEFAULT 'briefing'
                           CHECK (status IN ('briefing','playing','recording','scoring','completed')),
    time_limit_seconds INT         NOT NULL DEFAULT 480,
    started_at         TIMESTAMPTZ,
    completed_at       TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_game_sessions_user    ON game_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_status  ON game_sessions (status);
CREATE INDEX IF NOT EXISTS idx_game_sessions_created ON game_sessions (created_at);

-- 3. scenarios
CREATE TABLE IF NOT EXISTS scenarios (
    id                        UUID  PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id                UUID  NOT NULL UNIQUE REFERENCES game_sessions(id) ON DELETE CASCADE,
    patient_name              VARCHAR(100) NOT NULL,
    patient_age               INT          NOT NULL,
    patient_gender            VARCHAR(10)  NOT NULL,
    patient_diagnosis         TEXT         NOT NULL,
    patient_medications       JSONB        NOT NULL DEFAULT '[]',
    patient_medical_history   JSONB        NOT NULL DEFAULT '[]',
    patient_allergies         JSONB        NOT NULL DEFAULT '[]',
    pain_location             TEXT  NOT NULL,
    pain_severity             INT   NOT NULL,
    pain_type                 VARCHAR(100) NOT NULL,
    pain_duration             VARCHAR(100) NOT NULL,
    pain_onset                TEXT  NOT NULL,
    pain_aggravating_factors  JSONB NOT NULL DEFAULT '[]',
    pain_relieving_factors    JSONB NOT NULL DEFAULT '[]',
    pain_associated_symptoms  JSONB NOT NULL DEFAULT '[]',
    communication_challenges  JSONB NOT NULL DEFAULT '[]',
    correct_answers           JSONB NOT NULL DEFAULT '{}',
    background_image_url      TEXT,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. family_members
CREATE TABLE IF NOT EXISTS family_members (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id           UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    member_index          INT  NOT NULL CHECK (member_index IN (0, 1, 2)),
    name                  VARCHAR(100) NOT NULL,
    gender                VARCHAR(10)  NOT NULL,
    relationship          VARCHAR(100) NOT NULL,
    personality           TEXT NOT NULL,
    emotional_state       TEXT NOT NULL,
    interjection_triggers JSONB NOT NULL DEFAULT '[]',
    UNIQUE (scenario_id, member_index)
);

-- 5. chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id               VARCHAR(255) PRIMARY KEY,
    session_id       UUID         NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    sender           VARCHAR(50)  NOT NULL,
    content          TEXT         NOT NULL,
    elapsed_seconds  FLOAT        NOT NULL DEFAULT 0,
    is_interjection  BOOLEAN      NOT NULL DEFAULT FALSE,
    is_proactive     BOOLEAN      NOT NULL DEFAULT FALSE,
    sent_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages (session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender  ON chat_messages (session_id, sender);

-- 6. patient_records
CREATE TABLE IF NOT EXISTS patient_records (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id             UUID NOT NULL UNIQUE REFERENCES game_sessions(id) ON DELETE CASCADE,
    content                TEXT NOT NULL,
    submitted_at           TIMESTAMPTZ NOT NULL,
    time_remaining_seconds INT  NOT NULL
);

-- 7. score_results
CREATE TABLE IF NOT EXISTS score_results (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id               UUID NOT NULL UNIQUE REFERENCES game_sessions(id) ON DELETE CASCADE,
    overall_score            INT         NOT NULL,
    level_label              VARCHAR(50) NOT NULL,
    score_empathy            INT NOT NULL,
    score_guided_questioning INT NOT NULL,
    score_family_calming     INT NOT NULL,
    score_info_gathering     INT NOT NULL,
    score_response_fluency   INT NOT NULL,
    strengths                JSONB NOT NULL DEFAULT '[]',
    improvements             JSONB NOT NULL DEFAULT '[]',
    key_moments              JSONB NOT NULL DEFAULT '[]',
    evaluated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_score_results_session ON score_results (session_id);
CREATE INDEX IF NOT EXISTS idx_score_results_score   ON score_results (overall_score);
