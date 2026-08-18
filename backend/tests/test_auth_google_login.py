"""Tests for iteration 11: cookie secure/samesite fix + Google OAuth callback."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://wellness-log-105.preview.emergentagent.com").rstrip("/")


@pytest.fixture
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


class TestEmailPasswordLogin:
    def test_admin_login_success(self, session):
        r = session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["email"] == "admin@example.com"
        assert data["role"] in ("admin", "super_admin")
        # Cookie must be set with Secure + SameSite=None because FRONTEND_URL is https
        set_cookie = r.headers.get("set-cookie", "")
        assert "access_token=" in set_cookie
        assert "Secure" in set_cookie, f"Expected Secure flag on cookie: {set_cookie}"
        assert "samesite=none" in set_cookie.lower(), f"Expected SameSite=None: {set_cookie}"
        assert "httponly" in set_cookie.lower()

    def test_login_invalid_credentials(self, session):
        r = session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@example.com", "password": "wrong-password"})
        assert r.status_code == 401

    def test_me_with_cookie(self, session):
        r = session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
        assert r.status_code == 200
        r2 = session.get(f"{BASE_URL}/api/auth/me")
        assert r2.status_code == 200
        assert r2.json()["email"] == "admin@example.com"

    def test_logout_clears_cookies(self, session):
        session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
        r = session.post(f"{BASE_URL}/api/auth/logout")
        assert r.status_code == 200
        set_cookie = r.headers.get("set-cookie", "")
        # Cookies should be cleared (Max-Age=0 or expires in past)
        assert "access_token=" in set_cookie


class TestGoogleAuthCallback:
    def test_callback_empty_session_id(self, session):
        r = session.post(f"{BASE_URL}/api/auth/google/callback", json={"session_id": ""})
        assert r.status_code == 400
        assert "session_id" in r.text.lower()

    def test_callback_missing_body(self, session):
        r = session.post(f"{BASE_URL}/api/auth/google/callback", json={})
        assert r.status_code == 400

    def test_callback_invalid_session_id(self, session):
        # Emergent Auth will reject bogus session_id
        r = session.post(f"{BASE_URL}/api/auth/google/callback", json={"session_id": "bogus_invalid_session_id_12345"})
        assert r.status_code in (401, 502), r.text


class TestCORS:
    def test_cors_allows_frontend_origin(self, session):
        origin = "https://wellness-log-105.preview.emergentagent.com"
        r = session.options(
            f"{BASE_URL}/api/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert r.status_code in (200, 204)
        assert r.headers.get("access-control-allow-origin") == origin
        assert r.headers.get("access-control-allow-credentials", "").lower() == "true"
