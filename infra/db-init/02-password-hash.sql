-- Email/password login (routers/auth.py) verifies against users.password_hash,
-- which the base schema does not include. Add it idempotently.
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
