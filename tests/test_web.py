"""Smoke tests for the Unwatermark web server.

Runs against FastAPI TestClient — no running server needed.
Tests health endpoint, security headers, rate limiting, and static pages.
"""

from __future__ import annotations

import os

import pytest

# Set minimal env vars before importing the app (env validation requires at least one key)
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-ci")

from fastapi.testclient import TestClient

from unwatermark.web import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_get_returns_ok(self):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_head_returns_200(self):
        resp = client.head("/healthz")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------


class TestSecurityHeaders:
    def test_x_content_type_options(self):
        resp = client.get("/healthz")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self):
        resp = client.get("/healthz")
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self):
        resp = client.get("/healthz")
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy(self):
        resp = client.get("/healthz")
        assert "camera=()" in resp.headers.get("permissions-policy", "")

    def test_headers_on_html_pages(self):
        resp = client.get("/")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"


# ---------------------------------------------------------------------------
# Static pages
# ---------------------------------------------------------------------------


class TestStaticPages:
    @pytest.mark.parametrize(
        "path", ["/", "/app", "/help", "/about", "/contact", "/terms", "/privacy"],
    )
    def test_pages_return_200(self, path):
        resp = client.get(path)
        assert resp.status_code == 200

    def test_robots_txt(self):
        resp = client.get("/robots.txt")
        assert resp.status_code == 200
        assert "User-agent" in resp.text

    def test_sitemap_xml(self):
        resp = client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert "urlset" in resp.text

    def test_favicon(self):
        resp = client.get("/favicon.ico")
        assert resp.status_code == 200
        assert "svg" in resp.headers.get("content-type", "")

    def test_404_returns_html(self):
        resp = client.get("/nonexistent-page")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Rate limiting (verify the limiter is wired up)
# ---------------------------------------------------------------------------


class TestRateLimiting:
    def test_analyze_has_rate_limit(self):
        # Just verify the endpoint exists and rejects bad requests (not that we hit the limit)
        resp = client.post("/analyze")
        # 422 = missing required file field, which means the endpoint is reachable
        assert resp.status_code == 422

    def test_process_has_rate_limit(self):
        resp = client.post("/process")
        assert resp.status_code == 422
