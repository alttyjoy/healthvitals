"""
Iteration 7 Tests - Backend refactor & new features
Tests:
- Auth (admin1 / admin2)
- Exports: CSV & PDF
- Device sync: register-device, pull, push, devices list
- Push: vapid-key, status
- Admin panel endpoints reachable (overview/users/analytics/coupons)
"""
import os
import io
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"

ADMIN1 = {"email": "admin@example.com", "password": "admin123"}
ADMIN2 = {"email": "mohanv44@gmail.com", "password": "India@1947"}


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json=ADMIN1)
    assert r.status_code == 200, f"Admin1 login failed: {r.text}"
    return s


# ===== Auth =====
class TestAuth:
    def test_admin1_login(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN1)
        assert r.status_code == 200
        d = r.json()
        assert d.get("email") == ADMIN1["email"]
        assert d.get("role") == "super_admin"

    def test_admin2_login(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN2)
        assert r.status_code == 200
        assert r.json().get("role") == "super_admin"

    def test_unauth_me(self):
        r = requests.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401


# ===== Push =====
class TestPush:
    def test_vapid_key_public(self):
        r = requests.get(f"{BASE_URL}/api/push/vapid-key")
        assert r.status_code == 200
        d = r.json()
        assert "public_key" in d
        assert isinstance(d["public_key"], str)
        assert len(d["public_key"]) > 20

    def test_push_status_auth(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/push/status")
        assert r.status_code == 200
        d = r.json()
        assert "subscribed" in d
        assert "subscription_count" in d
        assert isinstance(d["subscribed"], bool)

    def test_push_status_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/push/status")
        assert r.status_code == 401


# ===== Exports =====
class TestExports:
    def _seed_entry(self, sess):
        # Seed a vitals entry so export has data
        r = sess.post(f"{BASE_URL}/api/entries", json={
            "vital_key": "weight", "date": "2025-01-15", "value": 70.5, "notes": "TEST_iter7"
        })
        # accept 200 or 201
        assert r.status_code in (200, 201), f"seed entry failed: {r.status_code} {r.text}"

    def test_csv_export(self, admin_session):
        self._seed_entry(admin_session)
        r = admin_session.post(f"{BASE_URL}/api/exports/generate", json={
            "format": "csv",
            "vital_keys": ["weight"],
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        })
        assert r.status_code == 200, f"CSV export failed: {r.text}"
        assert "text/csv" in r.headers.get("content-type", "")
        assert "attachment" in r.headers.get("content-disposition", "")
        body = r.content.decode()
        assert "Date" in body and "Vital" in body
        assert "Summary Statistics" in body

    def test_pdf_export_admin(self, admin_session):
        # Admin has premium plan, PDF should work
        r = admin_session.post(f"{BASE_URL}/api/exports/generate", json={
            "format": "pdf",
            "vital_keys": ["weight"],
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        })
        assert r.status_code == 200, f"PDF export failed: {r.text}"
        assert "application/pdf" in r.headers.get("content-type", "")
        # PDF should start with %PDF
        assert r.content[:4] == b"%PDF", "Response is not a valid PDF"

    def test_invalid_format(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/exports/generate", json={
            "format": "xml",
            "vital_keys": ["weight"],
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        })
        # pydantic validation or 400
        assert r.status_code in (400, 422)

    def test_export_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/exports/generate", json={
            "format": "csv", "vital_keys": ["weight"],
            "start_date": "2025-01-01", "end_date": "2025-12-31"
        })
        assert r.status_code == 401


# ===== Device Sync =====
class TestSync:
    DEVICE_ID = "TEST_device_iter7_abc"

    def test_register_device(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/sync/register-device", json={
            "device_id": self.DEVICE_ID,
            "device_type": "ios",
            "device_name": "TEST iPhone"
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("device_id") == self.DEVICE_ID

    def test_register_device_missing_id(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/sync/register-device", json={
            "device_type": "android"
        })
        assert r.status_code == 400

    def test_list_devices(self, admin_session):
        # Ensure registered
        admin_session.post(f"{BASE_URL}/api/sync/register-device", json={
            "device_id": self.DEVICE_ID, "device_type": "ios", "device_name": "TEST iPhone"
        })
        r = admin_session.get(f"{BASE_URL}/api/sync/devices")
        assert r.status_code == 200, r.text
        d = r.json()
        assert "devices" in d
        ids = [dev.get("device_id") for dev in d["devices"]]
        assert self.DEVICE_ID in ids

    def test_sync_pull_full(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/sync/pull")
        assert r.status_code == 200, r.text
        d = r.json()
        assert "entries" in d
        assert "user_data" in d
        assert "sync_timestamp" in d
        assert "entry_count" in d
        assert isinstance(d["entries"], list)
        assert d["entry_count"] == len(d["entries"])

    def test_sync_pull_since(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/sync/pull", params={"since": "2099-01-01T00:00:00"})
        assert r.status_code == 200
        d = r.json()
        assert d["entry_count"] == 0  # no entries after future date

    def test_sync_push(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/sync/push", json={
            "device_id": self.DEVICE_ID,
            "entries": [
                {"vital_key": "weight", "date": "2025-01-20", "value": 71.0, "notes": "TEST_push"},
                {"vital_key": "weight", "date": "2025-01-21", "value": 71.5},
                # Invalid - missing value
                {"vital_key": "weight", "date": "2025-01-22"},
            ]
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("synced") == 2
        assert d.get("skipped") == 1

    def test_sync_push_pull_roundtrip(self, admin_session):
        admin_session.post(f"{BASE_URL}/api/sync/push", json={
            "device_id": self.DEVICE_ID,
            "entries": [{"vital_key": "weight", "date": "2025-01-23", "value": 72.0}]
        })
        r = admin_session.get(f"{BASE_URL}/api/sync/pull")
        entries = r.json()["entries"]
        # find the pushed entry
        found = any(e.get("date") == "2025-01-23" and e.get("vital_key") == "weight" for e in entries)
        assert found, "Pushed entry not retrievable via pull"

    def test_sync_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/sync/pull")
        assert r.status_code == 401
        r = requests.post(f"{BASE_URL}/api/sync/push", json={"entries": []})
        assert r.status_code == 401
        r = requests.get(f"{BASE_URL}/api/sync/devices")
        assert r.status_code == 401

    def test_delete_device_cleanup(self, admin_session):
        r = admin_session.delete(f"{BASE_URL}/api/sync/devices/{self.DEVICE_ID}")
        assert r.status_code == 200

    def test_delete_nonexistent_device(self, admin_session):
        r = admin_session.delete(f"{BASE_URL}/api/sync/devices/NONEXISTENT_xyz")
        assert r.status_code == 404


# ===== Admin Panel Endpoints =====
class TestAdminEndpoints:
    def test_admin_stats(self, admin_session):
        # Overview tab (admin dashboard)
        r = admin_session.get(f"{BASE_URL}/api/admin/dashboard")
        assert r.status_code == 200, r.text

    def test_admin_users_list(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert r.status_code == 200, r.text
        d = r.json()
        assert "users" in d or isinstance(d, list)

    def test_admin_coupons_list(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/coupons")
        assert r.status_code == 200, r.text

    def test_admin_content_pages(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/content-pages")
        assert r.status_code == 200, r.text

    def test_admin_requires_admin_role(self):
        # Register a user, login, try to access admin endpoint -> 403
        import uuid
        email = f"TEST_user_{uuid.uuid4().hex[:8]}@example.com"
        s = requests.Session()
        reg = s.post(f"{BASE_URL}/api/auth/register", json={
            "email": email, "password": "userpass123", "name": "Test User"
        })
        if reg.status_code not in (200, 201):
            pytest.skip(f"Register failed: {reg.status_code} {reg.text}")
        r = s.get(f"{BASE_URL}/api/admin/dashboard")
        assert r.status_code in (401, 403)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
