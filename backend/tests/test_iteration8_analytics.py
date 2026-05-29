"""Iteration 8: Tests for enhanced /insights and /charts analytics with period comparison."""
import os
import pytest
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    assert r.status_code == 200, r.text
    return s


def test_login_works(admin_session):
    r = admin_session.get(f"{API}/auth/me")
    assert r.status_code == 200
    assert r.json().get("email") == "admin@example.com"


# Insights: ensure expected new fields exist for each vital
def test_insights_enhanced_fields(admin_session):
    r = admin_session.get(f"{API}/insights")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if not data:
        pytest.skip("No insights present - seed data missing")
    for ins in data:
        for field in ["vital_key", "vital_name", "status", "trend",
                      "latest", "average", "previous_average",
                      "change_percent", "min", "max", "entry_count"]:
            assert field in ins, f"Missing {field} in {ins.get('vital_key')}"
        assert ins["trend"] in ("rising", "falling", "stable")
        # min/max sanity
        if ins["entry_count"] > 0:
            assert ins["min"] <= ins["max"]


def test_insights_weight_and_heart_rate_have_change(admin_session):
    """Per problem statement, 14 days of weight + heart_rate seeded; previous_average + change_percent should be numeric."""
    r = admin_session.get(f"{API}/insights")
    assert r.status_code == 200
    data = {i["vital_key"]: i for i in r.json()}
    for vk in ("weight", "heart_rate"):
        if vk not in data:
            pytest.skip(f"{vk} not enabled or no data")
        ins = data[vk]
        assert ins["previous_average"] is not None, f"{vk} missing previous_average"
        assert ins["change_percent"] is not None, f"{vk} missing change_percent"
        assert isinstance(ins["change_percent"], (int, float))


# Charts: stats / previous_stats / change_percent / trend
def _date_range(days=14):
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def test_charts_weight_has_stats_and_prev_stats(admin_session):
    start, end = _date_range(14)
    r = admin_session.get(f"{API}/charts/weight", params={"start_date": start, "end_date": end})
    assert r.status_code == 200, r.text
    j = r.json()
    for key in ("entries", "vital_key", "stats", "previous_stats", "change_percent", "trend"):
        assert key in j, f"Missing {key}"
    assert j["vital_key"] == "weight"
    s = j["stats"]
    for f in ("min", "max", "avg", "count"):
        assert f in s
    ps = j["previous_stats"]
    for f in ("min", "max", "avg", "count"):
        assert f in ps
    assert j["trend"] in ("rising", "falling", "stable")
    # No previous_entries unless compare=true
    assert "previous_entries" not in j


def test_charts_weight_compare_true_returns_previous_entries(admin_session):
    start, end = _date_range(14)
    r = admin_session.get(f"{API}/charts/weight",
                          params={"start_date": start, "end_date": end, "compare": "true"})
    assert r.status_code == 200, r.text
    j = r.json()
    assert "previous_entries" in j
    assert isinstance(j["previous_entries"], list)


def test_charts_heart_rate_stats(admin_session):
    start, end = _date_range(14)
    r = admin_session.get(f"{API}/charts/heart_rate", params={"start_date": start, "end_date": end})
    assert r.status_code == 200
    j = r.json()
    assert "stats" in j and "previous_stats" in j
    if j["stats"]["count"] > 0:
        assert j["stats"]["min"] <= j["stats"]["max"]


def test_charts_change_percent_math(admin_session):
    """change_percent should equal ((avg - prev_avg)/prev_avg)*100 (rounded to 1)."""
    start, end = _date_range(14)
    r = admin_session.get(f"{API}/charts/weight", params={"start_date": start, "end_date": end})
    j = r.json()
    cur = j["stats"]["avg"]
    prev = j["previous_stats"]["avg"]
    if cur is None or prev is None or prev == 0:
        pytest.skip("Insufficient data for change_percent math")
    expected = round(((cur - prev) / prev) * 100, 1)
    assert j["change_percent"] == expected


def test_charts_unauth_returns_401():
    start, end = _date_range(7)
    r = requests.get(f"{API}/charts/weight", params={"start_date": start, "end_date": end})
    assert r.status_code in (401, 403)


def test_insights_unauth_returns_401():
    r = requests.get(f"{API}/insights")
    assert r.status_code in (401, 403)
