## Context

Nurvo serves a Vite-built Vue SPA through nginx, which also reverse-proxies `/api/*` and the chat WebSocket to FastAPI (`backend:8000`). An AppScan report (see `proposal.md`) lists 11 findings; 9 are fixable in this repo and are all about HTTP response hygiene: missing security headers, missing SRI on the Google Fonts link, and a cacheable sensitive response. There is no auth in this repo today, so the "sensitive response" requirement is satisfied generically rather than on a specific login endpoint. The scanned production deployment runs behind IIS/ARR and is not built from this repo, so the two infrastructure findings (force-HTTPS, Spring Actuator) are documented for the operator, not coded here.

## Goals / Non-Goals

**Goals:**
- Every response from a deployment *of this repo* carries the baseline security headers (CSP, X-Content-Type-Options, Referrer-Policy, COOP, COEP, CORP, HSTS).
- Third-party assets are integrity-pinned (SRI).
- Sensitive/dynamic API responses are non-cacheable.
- The SPA keeps working (fonts render, images load, chat WebSocket connects).
- Regression tests lock the headers/SRI in place.

**Non-Goals:**
- IIS/ARR edge config, HTTP→HTTPS redirect, HSTS preload submission (infra, operator-side).
- Securing/removing the production Spring Boot Actuator / digiRunner (infra; already removed from this repo).
- Adding authentication or changing any API contract.
- Self-hosting fonts (noted as a recommended follow-up, not done here).

## Decisions

### D1 — Headers set per-layer by response owner (no server-level duplication)
nginx sets the headers on the **static SPA** (`location /`); FastAPI middleware sets them on **`/api/*`**. We deliberately do **not** add a `server`-level `add_header`, because that would also apply to proxied `/api/` responses *and* FastAPI would set them too → duplicate headers (e.g. two `Content-Security-Policy`). Each layer owns exactly the responses it generates.
- **Why:** app-layer headers are portable — they survive whatever edge sits in front (our nginx, the production IIS/ARR, or Vite in dev). nginx covers the static files FastAPI never sees.
- **Alternative considered:** set everything in nginx only — rejected: static-only deployments differ per environment (IIS in prod), and dev (Vite `:5173`) has no nginx, so the API would ship unprotected there.
- **Alternative considered:** one shared `server`-level block — rejected: causes duplicate headers on proxied API responses.

### D2 — FastAPI: a `BaseHTTPMiddleware` class in its own file
Add `nurvobackend/middleware/security_headers.py` (a `BaseHTTPMiddleware` subclass) registered in `main.py`, rather than an inline `@app.middleware("http")` in `main.py`.
- **Why:** isolated + unit-testable + matches the repo's "many small files" rule.
- **Ordering:** keep `CORSMiddleware` outermost (added last) so it still short-circuits OPTIONS preflight; the security-headers middleware wraps normal responses. A spec scenario asserts CORS preflight is unaffected.
- **Alternative considered:** inline decorator — rejected: harder to test in isolation.

### D3 — The exact header values
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: blob: https:;
  connect-src 'self' ws: wss:;
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'none';
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
- `script-src 'self'` (no `unsafe-inline`/`unsafe-eval`) satisfies the strict CSP sub-tests; `object-src 'none'` + `frame-ancestors 'none'` cover the other two.
- `style-src 'unsafe-inline'` is kept because Vue/PrimeVue inject runtime inline styles — script injection (the dangerous vector) stays blocked.
- `connect-src ws: wss:` is required for the chat WebSocket; `img-src data: blob: https:` covers generated images / TTS blobs.
- **Why these are decisions, not spec:** the spec mandates *behavior* (no unsafe script-src, frame-ancestors present, HSTS ≥ 1yr); these concrete values are the implementation that satisfies it.

### D4 — `Cache-Control: no-store` on all API responses
The middleware sets `Cache-Control: no-store` + `Pragma: no-cache` on every `/api/*` response; static hashed assets served by nginx keep their normal (cacheable) behaviour.
- **Why:** no API response in this app benefits from caching, and a blanket rule can't be forgotten when a future sensitive endpoint (e.g. the OAuth flow seen in prod) is added — directly pre-empts finding #7.
- **Alternative considered:** per-endpoint `no-store` — rejected: fragile, easy to miss a new endpoint.

### D5 — Self-host the Inter font via `@fontsource/inter` (revised during apply)
Remove the third-party Google Fonts `<link>` (and its `preconnect`s) from `index.html`; install `@fontsource/inter` and `import` the needed weights (400/500/600/700/800) in `main.ts` so Vite bundles the CSS and serves the woff2 files from our own origin.
- **Why:** SRI on the Google Fonts *stylesheet* is unreliable — the CSS Google returns **varies by User-Agent** (proven during apply: two UAs → two different sha384 hashes), so a pinned `integrity` would block the stylesheet for any browser whose UA differs from the one hashed, and it can't be verified locally while the auth/DB wall is up. Self-hosting removes the third-party dependency entirely (the strongest fix for a supply-chain finding), is not UA-fragile, and makes the font same-origin so it no longer interacts with CSP `font-src`/COEP/CORP.
- **Alternative considered — pin an SRI hash on the Google link (original D5):** rejected for the UA-variance fragility above.
- **CSP impact:** drop `https://fonts.googleapis.com` from `style-src` and `https://fonts.gstatic.com` from `font-src`; `style-src 'self' 'unsafe-inline'` + `font-src 'self'` now suffice (bundled CSS + same-origin woff2).

## Risks / Trade-offs

- **CSP breaks the SPA (inline styles, images, WebSocket)** → Mitigation: the D3 policy explicitly allows `style-src 'unsafe-inline'`, `img-src data: blob: https:`, `connect-src ws: wss:`. Validate by loading the app and watching the console for CSP violations before declaring done. Optionally ship as `Content-Security-Policy-Report-Only` first, then flip to enforcing.
- **`COEP: require-corp` blocks Google Fonts** → Mitigation: keep the `<link crossorigin>`; if gstatic/fonts fail to load, downgrade to `Cross-Origin-Embedder-Policy: credentialless` or self-host. Tracked in Open Questions.
- **Duplicate headers** → Mitigation: strict per-layer ownership (D1); a test asserts single-valued headers.
- **HSTS sent over http in dev** → No effect: browsers ignore HSTS received over a non-secure transport, so emitting it from FastAPI on `http://localhost` is harmless.
- **Pinned SRI hash drifts when Google updates the CSS** → Mitigation: documented re-hash step; self-hosting removes the risk entirely.

## Migration Plan

1. Additive change — deploy frontend (nginx + `index.html`) and backend (middleware) together. No data migration.
2. Verify: `curl -I` the SPA and `/api/health` show the headers; load the SPA and confirm fonts render, a scenario generates, and a chat session connects with no CSP/COEP console errors.
3. **Rollback:** revert the three edits (nginx, index.html, middleware registration) — no state to undo.
4. **Operator follow-up (separate, infra):** at IIS/ARR — force HTTP→HTTPS redirect + add HSTS `preload`; restrict or remove the exposed Spring Boot Actuator (digiRunner). Record in `sysdoc/RUNBOOK.md`.

## Open Questions

- **COEP value:** RESOLVED → `credentialless`. `require-corp` would block cross-origin subresources lacking a CORP header (e.g. remote DALL·E background images); `credentialless` still satisfies AppScan #3 and won't break them. Chosen conservatively because the live smoke test is blocked by the auth/DB wall — re-confirm `require-corp` is viable once the app runs locally.
- **`img-src` precision:** does the frontend load generated images by remote URL (needs `https:`) or as base64/blob (needs `data:`/`blob:`)? Confirm against `scenarioStore`/`SceneView` to tighten the directive.
- **Self-host Inter font** as the durable fix for #2 + COEP/CORP — schedule as a follow-up change?
