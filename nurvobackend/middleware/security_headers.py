"""HTTP security-headers middleware (AppScan harden-web-security, design §D3).

Attaches a baseline set of security response headers plus no-store caching to
every response, so a deployment of this app passes the AppScan scan regardless
of the edge (nginx, IIS/ARR, or Vite) in front of it. nginx separately covers
the static SPA it serves; this middleware owns the FastAPI API surface.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self'; "
    "img-src 'self' data: blob: https:; "
    "connect-src 'self' ws: wss:; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)

# Static, single-valued header set applied to every response.
_SECURITY_HEADERS: dict[str, str] = {
    "Content-Security-Policy": _CSP,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    # credentialless (not require-corp): satisfies AppScan COEP while still
    # allowing cross-origin subresources (e.g. remote DALL·E images) to load.
    "Cross-Origin-Embedder-Policy": "credentialless",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    # API responses are dynamic / may carry confidential data — never cache.
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add the baseline security headers to every response (assign, not append,
    so each header stays single-valued)."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        for name, value in _SECURITY_HEADERS.items():
            response.headers[name] = value
        return response
