## Why

An HCL AppScan Standard scan (2026/6/4, target `https://meqa.ncu.edu.tw/nurvo/`) found **11 issues** — 5 medium, 5 low, 1 informational. **8 of the 11 are missing HTTP security response headers**; the rest are missing Subresource Integrity (SRI) on third-party assets and a cacheable sensitive response. Left unaddressed, these expose users to XSS / clickjacking (no CSP), MIME-sniffing drive-by downloads (no `nosniff`), cross-origin side-channel leakage (no COOP/COEP/CORP), HTTPS-downgrade MITM (no HSTS), referrer URL leakage (no Referrer-Policy), and a compromised-CDN supply-chain attack (no SRI). These are cheap, well-understood, standards-based fixes that belong at the application's HTTP boundary.

> **Scan-target caveat (production ≠ this repo).** The scanned deployment is **not built from this repository**: it serves a Google-OAuth login (`/api/auth/google`, `LoginView`, `AuthCallbackView`) that exists on no branch here, runs behind **IIS 10.0 + ARR/3.0** under a `/nurvo/` path prefix (not the repo's nginx+Docker topology), and AppScan flagged a **Spring Boot Actuator** endpoint — almost certainly the legacy **digiRunner** gateway still live in production (removed from this repo on 2026/6/8). Therefore hardening this repo will **not** by itself clear the live `meqa` scan; it makes any deployment *of this codebase* pass. The two production-only / infrastructure findings (#1 force-HTTPS, #6 Spring Actuator) are tracked here as a remediation note for the NCU/IIS operator, not implemented in this change.

## What Changes

- **Add a single source of truth for HTTP security headers**, emitted in two layers so every response is covered:
  - **nginx** (`nurvofronted/nginx.conf`) — for the static SPA (HTML/JS/CSS).
  - **FastAPI middleware** (`nurvobackend/`) — for all `/api/*` responses.
  - Headers added: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy`, `Strict-Transport-Security`.
- **Add Subresource Integrity** (`integrity` + `crossorigin`) to the third-party Google Fonts `<link>` in `nurvofronted/index.html` (finding #2).
- **Add `Cache-Control: no-store` + `Pragma: no-cache`** to sensitive (non-static, credential/PII-bearing) API responses, so secrets are never browser-cached (finding #7).
- **Add tests** asserting the headers/SRI are present (regression lock), and **update `sysdoc/`**.
- **Document (not implement) the two infra findings** in this proposal for the production operator: force HTTP→HTTPS redirect + HSTS preload at the edge (#1), and secure/remove the exposed Spring Boot Actuator / digiRunner (#6).

No API contract changes; no breaking changes to request/response *bodies*. (CSP/COEP interaction with Google Fonts is a real configuration risk handled in `design.md`.)

## Capabilities

### New Capabilities
- `web-security`: The application's HTTP responses MUST carry a baseline set of security headers (CSP, X-Content-Type-Options, Referrer-Policy, COOP, COEP, CORP, HSTS), third-party subresources MUST be integrity-pinned (SRI), and sensitive responses MUST be marked non-cacheable. Covers both the nginx-served SPA and the FastAPI API surface.

### Modified Capabilities
<!-- None — openspec/specs/ is empty; this is the first capability. -->

## Impact

- **Code:**
  - `nurvofronted/nginx.conf` — `add_header` directives (with `always`) on the static + API-proxy location blocks.
  - `nurvofronted/index.html` — `integrity` + `crossorigin` on the Google Fonts stylesheet link.
  - `nurvobackend/main.py` + new `nurvobackend/middleware/security_headers.py` — a security-headers middleware registered on the app.
- **Tests:** new backend test (header presence on a sample route) + frontend test (SRI attributes present in `index.html`).
- **Docs:** `sysdoc/ARCHITECTURE.md` (ADR for the header policy) + `sysdoc/RUNBOOK.md` (the infra remediation note).
- **Dependencies:** none added.
- **Out of scope (infra, tracked only):** IIS/ARR force-HTTPS + HSTS preload; securing/removing the production Spring Boot Actuator (digiRunner).
- **Compatibility risk:** an over-strict CSP or `COEP: require-corp` can block Google Fonts / inline styles — resolved by the exact policy values chosen in `design.md`.
