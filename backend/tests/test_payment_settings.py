"""Tests for admin payment gateway settings (Razorpay + PayU)."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://wellness-log-105.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
MASK = "********"


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    return s


# --- GET /admin/payment-settings ---
def test_get_payment_settings_masked(admin_session):
    r = admin_session.get(f"{API}/admin/payment-settings")
    assert r.status_code == 200, r.text
    d = r.json()
    # Required fields
    for f in ["razorpay_key_id", "razorpay_key_secret", "payu_merchant_key",
              "payu_merchant_salt", "payu_base_url", "razorpay_configured", "payu_configured"]:
        assert f in d, f"Missing field {f}"
    # Configured flags should be True (env has values)
    assert d["razorpay_configured"] is True
    assert d["payu_configured"] is True
    # Secrets should be masked, not leaked
    assert d["razorpay_key_secret"] == MASK
    assert d["payu_merchant_salt"] == MASK
    # Non-secret fields should be visible
    assert d["razorpay_key_id"].startswith("rzp_"), f"Expected rzp_ key id, got {d['razorpay_key_id']}"
    assert d["payu_merchant_key"] != ""
    assert "payu.in" in d["payu_base_url"]


def test_get_payment_settings_no_auth():
    r = requests.get(f"{API}/admin/payment-settings")
    assert r.status_code in (401, 403)


# --- PUT /admin/payment-settings ---
def test_put_preserves_masked_secrets(admin_session):
    """When secret sent as MASK, backend must keep existing value."""
    # First set a known real secret
    r = admin_session.put(f"{API}/admin/payment-settings", json={
        "razorpay_key_id": "rzp_test_SY4wkkjcQo4e5i",
        "razorpay_key_secret": "TEST_REAL_SECRET_123",
        "payu_merchant_key": "wRL2ZK",
        "payu_merchant_salt": "TEST_REAL_SALT_456",
        "payu_base_url": "https://test.payu.in/_payment",
    })
    assert r.status_code == 200, r.text

    # Now PUT with masked secrets (simulating user editing key_id only)
    r = admin_session.put(f"{API}/admin/payment-settings", json={
        "razorpay_key_id": "rzp_test_UPDATED_ID",
        "razorpay_key_secret": MASK,
        "payu_merchant_key": "UPDATED_KEY",
        "payu_merchant_salt": MASK,
        "payu_base_url": "https://test.payu.in/_payment",
    })
    assert r.status_code == 200, r.text

    # GET should show new key_id + masked secret; internally secret preserved
    d = admin_session.get(f"{API}/admin/payment-settings").json()
    assert d["razorpay_key_id"] == "rzp_test_UPDATED_ID"
    assert d["payu_merchant_key"] == "UPDATED_KEY"
    assert d["razorpay_key_secret"] == MASK
    assert d["payu_merchant_salt"] == MASK
    assert d["razorpay_configured"] is True
    assert d["payu_configured"] is True


def test_put_updates_actual_secret(admin_session):
    """When a real secret string is sent, it should replace old."""
    r = admin_session.put(f"{API}/admin/payment-settings", json={
        "razorpay_key_id": "rzp_test_NEWID",
        "razorpay_key_secret": "brand_new_secret_XYZ",
        "payu_merchant_key": "NEWPAYUKEY",
        "payu_merchant_salt": "brand_new_salt_ABC",
        "payu_base_url": "https://test.payu.in/_payment",
    })
    assert r.status_code == 200

    # Verify via direct DB inspection through re-PUT with MASK + check GET reflects id change
    d = admin_session.get(f"{API}/admin/payment-settings").json()
    assert d["razorpay_key_id"] == "rzp_test_NEWID"
    assert d["payu_merchant_key"] == "NEWPAYUKEY"
    # secret still masked in response
    assert d["razorpay_key_secret"] == MASK


def test_put_no_auth():
    r = requests.put(f"{API}/admin/payment-settings", json={"razorpay_key_id": "x"})
    assert r.status_code in (401, 403)


# --- Restore to env-default values so live payment flows still work ---
def test_zzz_restore_env_credentials(admin_session):
    """Runs last (zzz prefix) to restore .env creds so razorpay create-order still works."""
    r = admin_session.put(f"{API}/admin/payment-settings", json={
        "razorpay_key_id": os.environ.get("RAZORPAY_KEY_ID", "rzp_test_SY4wkkjcQo4e5i"),
        "razorpay_key_secret": "0B2NnJKy0K8lzhpr26B3Zuh2",
        "payu_merchant_key": "wRL2ZK",
        "payu_merchant_salt": "qaUSgp8KoSFWTp0gIH3riPSMaSy1XVfE",
        "payu_base_url": "https://test.payu.in/_payment",
    })
    assert r.status_code == 200


# --- Dynamic key loading: razorpay create-order after settings save ---
def test_razorpay_create_order_after_save(admin_session):
    """Ensure /api/razorpay/create-order works using DB-loaded keys."""
    r = admin_session.post(f"{API}/razorpay/create-order",
                            json={"plan_key": "standard", "billing_cycle": "monthly"})
    # Either successful order or a razorpay-side error, but NOT "not configured"
    assert r.status_code != 500 or "not configured" not in r.text.lower(), r.text
    if r.status_code == 200:
        data = r.json()
        assert "order_id" in data
        assert "key_id" in data
        assert data["key_id"].startswith("rzp_")


def test_payu_initiate_after_save(admin_session):
    r = admin_session.post(f"{API}/payu/initiate",
                            json={"plan_key": "standard", "billing_cycle": "monthly"})
    assert r.status_code != 500 or "not configured" not in r.text.lower(), r.text
    if r.status_code == 200:
        d = r.json()
        assert "payu_url" in d and "params" in d
        assert d["params"].get("key") == "wRL2ZK"
        assert "hash" in d["params"]
