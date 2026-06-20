"""Tests for the baseline HTTP security headers (AppScan harden-web-security).

Locks in that every API response carries the security headers from design §D3
plus no-store caching, including on error responses, single-valued, without
breaking CORS.
"""

import unittest

from fastapi.testclient import TestClient

from main import app

_BASELINE = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "cross-origin-embedder-policy": "credentialless",
}


class SecurityHeadersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_baseline_headers_on_api_response(self) -> None:
        resp = self.client.get("/api/health")
        for name, value in _BASELINE.items():
            self.assertEqual(resp.headers.get(name), value, f"{name} mismatch")
        self.assertIn("content-security-policy", resp.headers)
        self.assertIn("strict-transport-security", resp.headers)

    def test_hsts_has_long_max_age(self) -> None:
        resp = self.client.get("/api/health")
        hsts = resp.headers.get("strict-transport-security", "")
        self.assertIn("max-age=31536000", hsts)
        self.assertIn("includeSubDomains", hsts)

    def test_csp_forbids_unsafe_script_and_sets_frame_ancestors(self) -> None:
        resp = self.client.get("/api/health")
        csp = resp.headers.get("content-security-policy", "")
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("object-src 'none'", csp)
        # script-src must not allow unsafe execution
        script_src = next(
            (d for d in csp.split(";") if d.strip().startswith("script-src")), ""
        )
        self.assertNotIn("unsafe-inline", script_src)
        self.assertNotIn("unsafe-eval", script_src)

    def test_sensitive_responses_are_no_store(self) -> None:
        resp = self.client.get("/api/health")
        self.assertEqual(resp.headers.get("cache-control"), "no-store")
        self.assertEqual(resp.headers.get("pragma"), "no-cache")

    def test_headers_present_on_error_response(self) -> None:
        resp = self.client.get("/api/this-route-does-not-exist")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertIn("content-security-policy", resp.headers)

    def test_headers_are_single_valued(self) -> None:
        resp = self.client.get("/api/health")
        for name in ("content-security-policy", "strict-transport-security",
                     "cross-origin-opener-policy"):
            self.assertEqual(
                len(resp.headers.get_list(name)), 1, f"{name} duplicated"
            )

    def test_cors_preflight_still_succeeds(self) -> None:
        resp = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(resp.headers.get("access-control-allow-origin"), "http://localhost:8080")


if __name__ == "__main__":
    unittest.main()
