## ADDED Requirements

### Requirement: Security headers on SPA responses

The nginx-served single-page app SHALL return the following HTTP response headers on every response (using `always` so they are emitted on error responses too): `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy: same-origin`, and `Strict-Transport-Security`. The `Content-Security-Policy` MUST NOT permit `unsafe-inline` or `unsafe-eval` for `script-src`, and MUST set a `frame-ancestors` directive. The `Strict-Transport-Security` `max-age` MUST be at least 31536000 (one year) and include `includeSubDomains`. (AppScan #3, #4, #5, #8, #9, #10, #11)

#### Scenario: Static HTML response carries all baseline headers
- **WHEN** a client requests the SPA entry document (`/`) from nginx
- **THEN** the response includes `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy`, and `Strict-Transport-Security`

#### Scenario: CSP forbids unsafe script sources
- **WHEN** the `Content-Security-Policy` header value is inspected
- **THEN** its `script-src` directive contains neither `unsafe-inline` nor `unsafe-eval`, and a `frame-ancestors` directive is present

#### Scenario: HSTS max-age is at least one year
- **WHEN** the `Strict-Transport-Security` header is inspected
- **THEN** `max-age` is ≥ 31536000 and the value includes `includeSubDomains`

### Requirement: Security headers on API responses

The FastAPI application SHALL attach the same baseline security headers (`Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy`, `Strict-Transport-Security`) to every `/api/*` response via middleware, including error responses, without breaking the existing CORS behaviour. (AppScan #3, #4, #5, #8, #9, #10, #11)

#### Scenario: API JSON response carries baseline headers
- **WHEN** a client requests `GET /api/health`
- **THEN** the JSON response includes all baseline security headers listed above

#### Scenario: Headers present on error responses
- **WHEN** a client requests a non-existent `/api/*` route and receives a 404
- **THEN** the error response still includes the baseline security headers

#### Scenario: CORS preflight still succeeds
- **WHEN** a browser sends a CORS preflight from an allowed origin
- **THEN** the existing CORS allow-origin/credentials behaviour is unchanged by the new middleware

### Requirement: Subresource Integrity for third-party assets

Every third-party (cross-origin) `<script>` or stylesheet `<link>` referenced by the SPA entry document SHALL carry an `integrity` attribute and a `crossorigin` attribute, so the browser refuses tampered CDN assets. (AppScan #2)

#### Scenario: Google Fonts stylesheet is integrity-pinned
- **WHEN** the SPA `index.html` is inspected
- **THEN** the `https://fonts.googleapis.com` stylesheet `<link>` has both an `integrity` (sha384) attribute and `crossorigin`

#### Scenario: No unpinned cross-origin asset
- **WHEN** the SPA `index.html` is inspected for cross-origin `<script>`/`<link rel="stylesheet">` elements
- **THEN** none of them lack an `integrity` attribute

### Requirement: Sensitive responses are non-cacheable

API responses that carry credentials, tokens, personal data, or other confidential content SHALL set `Cache-Control: no-store` and `Pragma: no-cache` so browsers and proxies do not retain them. (AppScan #7)

#### Scenario: Sensitive API response is marked no-store
- **WHEN** a client requests an API endpoint that returns confidential data
- **THEN** the response includes `Cache-Control: no-store` and `Pragma: no-cache`
