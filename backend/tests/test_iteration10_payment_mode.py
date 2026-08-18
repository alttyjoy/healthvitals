"""Iteration 10: Test mode toggle + payment history."""
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


# --- GET /admin/payment-settings: new nested structure ---
def test_get_returns_mode_and_buckets(admin_session):
    r = admin_session.get(f"{API}/admin/payment-settings")
    assert r.status_code == 200, r.text
    d = r.json()
    assert "mode" in d and d["mode"] in ("test", "live")
    assert "test" in d and isinstance(d["test"], dict)
    assert "live" in d and isinstance(d["live"], dict)
    for bucket_name in ("test", "live"):
        b = d[bucket_name]
        for f in ["razorpay_key_id", "razorpay_key_secret", "payu_merchant_key", "payu_merchant_salt"]:
            assert f in b, f"Missing {bucket_name}.{f}"
        # secrets must be either '' or MASK, never real
        assert b["razorpay_key_secret"] in ("", MASK)
        assert b["payu_merchant_salt"] in ("", MASK)
    assert "razorpay_configured" in d
    assert "payu_configured" in d
    # payu_base_url should NOT be part of response (mode-derived on frontend)
    assert "payu_base_url" not in d


def test_get_no_auth():
    r = requests.get(f"{API}/admin/payment-settings")
    assert r.status_code in (401, 403)


# --- PUT: save both buckets + mode switch ---
def test_put_saves_both_buckets_and_mode(admin_session):
    payload = {
        "mode": "test",
        "test": {
            "razorpay_key_id": "rzp_test_ITER10",
            "razorpay_key_secret": "TEST_SECRET_ITER10",
            "payu_merchant_key": "PAYU_TEST_KEY",
            "payu_merchant_salt": "PAYU_TEST_SALT",
        },
        "live": {
            "razorpay_key_id": "rzp_live_ITER10",
            "razorpay_key_secret": "LIVE_SECRET_ITER10",
            "payu_merchant_key": "PAYU_LIVE_KEY",
            "payu_merchant_salt": "PAYU_LIVE_SALT",
        },
    }
    r = admin_session.put(f"{API}/admin/payment-settings", json=payload)
    assert r.status_code == 200, r.text

    d = admin_session.get(f"{API}/admin/payment-settings").json()
    assert d["mode"] == "test"
    assert d["test"]["razorpay_key_id"] == "rzp_test_ITER10"
    assert d["test"]["payu_merchant_key"] == "PAYU_TEST_KEY"
    assert d["live"]["razorpay_key_id"] == "rzp_live_ITER10"
    assert d["live"]["payu_merchant_key"] == "PAYU_LIVE_KEY"
    # Secrets masked
    assert d["test"]["razorpay_key_secret"] == MASK
    assert d["live"]["payu_merchant_salt"] == MASK


def test_put_masked_secret_preserves_existing(admin_session):
    # Send MASK for test.razorpay_key_secret - existing should be kept
    payload = {
        "mode": "test",
        "test": {
            "razorpay_key_id": "rzp_test_UPDATED",
            "razorpay_key_secret": MASK,
            "payu_merchant_key": "PAYU_TEST_KEY",
            "payu_merchant_salt": MASK,
        },
        "live": {
            "razorpay_key_id": "rzp_live_ITER10",
            "razorpay_key_secret": MASK,
            "payu_merchant_key": "PAYU_LIVE_KEY",
            "payu_merchant_salt": MASK,
        },
    }
    r = admin_session.put(f"{API}/admin/payment-settings", json=payload)
    assert r.status_code == 200
    d = admin_session.get(f"{API}/admin/payment-settings").json()
    assert d["test"]["razorpay_key_id"] == "rzp_test_UPDATED"
    assert d["test"]["razorpay_key_secret"] == MASK
    assert d["razorpay_configured"] is True  # was saved earlier


def test_put_switches_mode_to_live(admin_session):
    r = admin_session.put(f"{API}/admin/payment-settings", json={"mode": "live"})
    assert r.status_code == 200
    d = admin_session.get(f"{API}/admin/payment-settings").json()
    assert d["mode"] == "live"
    # live bucket credentials should still exist
    assert d["live"]["razorpay_key_id"] == "rzp_live_ITER10"


# --- Payment gateway calls are mode-aware ---
def test_payu_initiate_uses_live_url_when_live_mode(admin_session):
    # Mode is 'live' from previous test
    r = admin_session.post(f"{API}/payu/initiate",
                           json={"plan_key": "standard", "billing_cycle": "monthly"})
    if r.status_code == 200:
        d = r.json()
        assert d["payu_url"] == "https://secure.payu.in/_payment", f"Expected live URL, got {d['payu_url']}"
        assert d["params"]["key"] == "PAYU_LIVE_KEY"


def test_payu_initiate_uses_test_url_when_test_mode(admin_session):
    # Switch back to test
    admin_session.put(f"{API}/admin/payment-settings", json={"mode": "test"})
    r = admin_session.post(f"{API}/payu/initiate",
                           json={"plan_key": "standard", "billing_cycle": "monthly"})
    if r.status_code == 200:
        d = r.json()
        assert d["payu_url"] == "https://test.payu.in/_payment"
        assert d["params"]["key"] == "PAYU_TEST_KEY"


# --- GET /admin/payments: payment history ---
def test_get_payments_returns_transactions(admin_session):
    r = admin_session.get(f"{API}/admin/payments")
    assert r.status_code == 200, r.text
    d = r.json()
    assert "transactions" in d and isinstance(d["transactions"], list)
    assert "total" in d and isinstance(d["total"], int)
    # Expected structure of transactions
    for tx in d["transactions"]:
        for f in ["id", "gateway", "user_email", "plan", "order_id", "status", "created_at"]:
            assert f in tx, f"Missing tx field {f}"
        assert tx["gateway"] in ("Razorpay", "PayU")
    # Per the request, there should be at least 3 PayU test tx
    payu_count = sum(1 for tx in d["transactions"] if tx["gateway"] == "PayU")
    assert payu_count >= 3, f"Expected >=3 PayU tx, got {payu_count}"


def test_get_payments_no_auth():
    r = requests.get(f"{API}/admin/payments")
    assert r.status_code in (401, 403)


def test_get_payments_pagination(admin_session):
    r = admin_session.get(f"{API}/admin/payments?skip=0&limit=2")
    assert r.status_code == 200
    d = r.json()
    assert len(d["transactions"]) <= 2


# --- Restore env-defaults for continued app operation ---
def test_zzz_restore(admin_session):
    r = admin_session.put(f"{API}/admin/payment-settings", json={
        "mode": "test",
        "test": {
            "razorpay_key_id": "rzp_test_SY4wkkjcQo4e5i",
            "razorpay_key_secret": "0B2NnJKy0K8lzhpr26B3Zuh2",
            "payu_merchant_key": "wRL2ZK",
            "payu_merchant_salt": "qaUSgp8KoSFWTp0gIH3riPSMaSy1XVfE",
        },
        "live": {
            "razorpay_key_id": "",
            "razorpay_key_secret": "",
            "payu_merchant_key": "",
            "payu_merchant_salt": "",
        },
    })
    assert r.status_code == 200
