## 1. Backend — security-headers middleware (TDD)

- [ ] 1.1 RED: add `nurvobackend/tests/test_security_headers.py` — assert the baseline headers (CSP, X-Content-Type-Options, Referrer-Policy, COOP, COEP, CORP, HSTS) + `Cache-Control: no-store` + `Pragma: no-cache` on `GET /api/health`; assert they are present on a 404 `/api/*`; assert each header is single-valued (no duplicates). Run → fails.
- [ ] 1.2 GREEN: add `nurvobackend/middleware/security_headers.py` (a `BaseHTTPMiddleware` subclass) emitting the design §D3 header values + `no-store`/`Pragma` on every response.
- [ ] 1.3 Register the middleware in `nurvobackend/main.py`, keeping `CORSMiddleware` added last (outermost) so OPTIONS preflight still short-circuits. Run → green.
- [ ] 1.4 RED→GREEN: add a test asserting a CORS preflight from an allowed origin still returns the CORS allow-origin/credentials headers; confirm unaffected.
- [ ] 1.5 Run the full backend suite (`pytest`) — confirm the existing 22 tests still pass.

## 2. Frontend — Subresource Integrity (TDD)

- [ ] 2.1 Generate the sha384 integrity hash of the current Google Fonts stylesheet (`curl -s 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' | openssl dgst -sha384 -binary | openssl base64 -A`, or srihash.org).
- [ ] 2.2 RED: add a vitest in `nurvofronted/src/__tests__/` that reads `index.html` and asserts the `fonts.googleapis.com` `<link>` has an `integrity="sha384-…"` and a `crossorigin` attribute. Run → fails.
- [ ] 2.3 GREEN: add `integrity="sha384-…"` + `crossorigin="anonymous"` to the Google Fonts `<link>` in `nurvofronted/index.html`. Run → green.

## 3. Frontend — nginx security headers (static SPA)

- [ ] 3.1 In `nurvofronted/nginx.conf`, add the design §D3 headers as `add_header … always` inside the `location /` block **only** (not at `server` level, not in the `/api/` or `/api/chat/` blocks — see design §D1 to avoid duplicate headers on proxied responses).
- [ ] 3.2 Validate: `docker compose -f infra/docker-compose.yml build frontend` succeeds (implies `nginx -t` passes); `curl -I http://localhost:8080/` shows each header exactly once.

## 4. Verify the SPA still works under the new policy

- [ ] 4.1 Run the stack (`docker compose -f infra/docker-compose.yml up --build`); load the SPA and confirm the Inter font renders and the browser console shows **no** CSP / COEP violations.
- [ ] 4.2 Smoke a full flow: generate a scenario (background image loads), start a chat session (WebSocket connects). Resolve the design Open Questions — finalize the COEP value (`require-corp` vs `credentialless`) and the `img-src` directive based on what actually loads.
- [ ] 4.3 `curl -I` `/` and `/api/health`: confirm all baseline headers present + single-valued, and `/api/*` carries `Cache-Control: no-store`.

## 5. Documentation

- [ ] 5.1 Add an ADR to `sysdoc/ARCHITECTURE.md`: the security-header policy + per-layer ownership (nginx = static, FastAPI = API), and the chosen CSP/COEP values with rationale.
- [ ] 5.2 Add an operator remediation note to `sysdoc/RUNBOOK.md` for the infra-only findings: IIS/ARR force HTTP→HTTPS + HSTS preload (#1), securing/removing the production Spring Boot Actuator / digiRunner (#6), and the SRI re-hash / self-host-font follow-up.

## 6. Close out

- [ ] 6.1 Trace each in-repo AppScan finding (#2, #3, #4, #5, #7, #8, #9, #10, #11) to the task that implements it; confirm all nine are covered.
- [ ] 6.2 Run `openspec validate harden-web-security`; then commit (await user go-ahead per repo git workflow).
