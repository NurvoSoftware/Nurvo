-- SBAR review of the nurse's patient record (scoring_engine → persist.py).
-- NULL for sessions scored before this column existed. Idempotent: also the
-- migration to run once against an existing / production database.
ALTER TABLE score_results ADD COLUMN IF NOT EXISTS sbar_analysis JSONB;
