## 1. Backend — security-headers middleware (TDD)

- [x] 1.1 RED: add `nurvobackend/tests/test_security_headers.py` — assert the baseline headers (CSP, X-Content-Type-Options, Referrer-Policy, COOP, COEP, CORP, HSTS) + `Cache-Control: no-store` + `Pragma: no-cache` on `GET /api/health`; assert they are present on a 404 `/api/*`; assert each header is single-valued (no duplicates). Run → fails.
- [x] 1.2 GREEN: add `nurvobackend/middleware/security_headers.py` (a `BaseHTTPMiddleware` subclass) emitting the design §D3 header values + `no-store`/`Pragma` on every response.
- [x] 1.3 Register the middleware in `nurvobackend/main.py`, keeping `CORSMiddleware` added last (outermost) so OPTIONS preflight still short-circuits. Run → green.
- [x] 1.4 RED→GREEN: add a test asserting a CORS preflight from an allowed origin still returns the CORS allow-origin/credentials headers; confirm unaffected.
- [x] 1.5 Run the full backend suite (`pytest`) — confirm the existing 22 tests still pass.

## 2. Frontend — self-host the Inter font (TDD)  [revised: see design §D5]

- [x] 2.1 Confirmed SRI on the Google Fonts stylesheet is UA-fragile (two UAs → two different sha384 hashes) → self-host instead. Install `@fontsource/inter`.
- [x] 2.2 RED: add a vitest that reads `index.html` and asserts it contains **no** `fonts.googleapis.com` / `fonts.gstatic.com` reference. Run → fails.
- [x] 2.3 GREEN: remove the Google Fonts `<link>` + `preconnect`s from `index.html`; `import '@fontsource/inter/{400,500,600,700,800}.css'` in `main.ts`; drop the Google font domains from the CSP (`style-src`/`font-src`) in `security_headers.py`. Run → green.

## 3. Frontend — nginx security headers (static SPA)

- [x] 3.1 In `nurvofronted/nginx.conf`, add the design §D3 headers as `add_header … always` inside the `location /` block **only** (not at `server` level, not in the `/api/` or `/api/chat/` blocks — see design §D1 to avoid duplicate headers on proxied responses).
- [x] 3.2 Validate: `docker compose -f infra/docker-compose.yml build frontend` succeeds (implies `nginx -t` passes); `curl -I http://localhost:8080/` shows each header exactly once.

## 4. Verify the SPA still works under the new policy

- [x] 4.1 Interactive SPA load DONE (2026-06-21, after `local-dev-env-setup`). Headers re-verified by curl against the docker nginx build (`:8080`): all 7 baseline headers present on `/` and `/api/*`, CSP `script-src 'self'` (no `unsafe-inline`), `/api/*` carries `Cache-Control: no-store`. Served `index.html` has zero Google-Fonts references; the self-hosted Inter woff2 is served (`font/woff2`, 200). App driven live through login → scenario → chat with a clean browser console (no errors); the font renders and the gpt-image background loads (`img-src` data:/https: covers it). No CSP/COEP violation is possible since the app loads only `self` + `data:`/`https:` images + `ws:` — all permitted by the policy.
- [x] 4.2 COEP resolved to `credentialless` (design Open Questions) so cross-origin DALL·E images won't be blocked; full scenario/chat smoke DEFERRED behind the auth/DB wall.
- [x] 4.3 `curl -I` `/` and `/api/health`: confirm all baseline headers present + single-valued, and `/api/*` carries `Cache-Control: no-store`.

## 5. Documentation

- [x] 5.1 Add an ADR to `sysdoc/ARCHITECTURE.md`: the security-header policy + per-layer ownership (nginx = static, FastAPI = API), and the chosen CSP/COEP values with rationale.
- [x] 5.2 Add an operator remediation note to `sysdoc/RUNBOOK.md` for the infra-only findings: IIS/ARR force HTTP→HTTPS + HSTS preload (#1), securing/removing the production Spring Boot Actuator / digiRunner (#6), and the SRI re-hash / self-host-font follow-up.

## 6. Close out

- [x] 6.1 Trace each in-repo AppScan finding (#2, #3, #4, #5, #7, #8, #9, #10, #11) to the task that implements it; confirm all nine are covered.
- [x] 6.2 Ran `openspec validate harden-web-security` (valid). Commit pending user go-ahead.
