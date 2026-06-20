-- Local-dev login account (NOT for production).
-- Credentials:  dev@nurvo.local  /  nurvodev123
-- password_hash is bcrypt (passlib scheme used by routers/auth.py).
-- High credit balance so the dev account doesn't run out during repeated testing.
INSERT INTO users (email, name, password_hash, credits)
VALUES (
    'dev@nurvo.local',
    'Dev User',
    '$2b$12$FOJqxEdB5QRabTWWYDuQRu5HSnXi/RgNHbXDVvRbcLx/KibSF4.3S',
    999999
)
ON CONFLICT (email) DO NOTHING;
