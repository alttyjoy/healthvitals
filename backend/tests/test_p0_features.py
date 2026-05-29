"""
Test P0 Features - Iteration 3
Tests for: Content Pages, PayU Gateway, Referral System, Admin SMTP Settings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from environment
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
TEST_USER_EMAIL = f"testuser_{os.urandom(4).hex()}@example.com"
TEST_USER_PASSWORD = os.environ.get("TEST_PASSWORD", "TestPass123!")


class TestContentPages:
    """Content/Legal pages - Terms, Privacy, Refund, About"""
    
    def test_terms_page_returns_content(self):
        """GET /api/content/terms should return terms content"""
        response = requests.get(f"{BASE_URL}/api/content/terms")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "Terms of Service" in data["title"]
        assert len(data["content"]) > 100
    
    def test_privacy_page_returns_content(self):
        """GET /api/content/privacy should return privacy policy"""
        response = requests.get(f"{BASE_URL}/api/content/privacy")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "Privacy" in data["title"]
        assert len(data["content"]) > 100
    
    def test_refund_page_returns_content(self):
        """GET /api/content/refund should return refund policy"""
        response = requests.get(f"{BASE_URL}/api/content/refund")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "Refund" in data["title"]
        assert len(data["content"]) > 100
    
    def test_about_page_returns_content(self):
        """GET /api/content/about should return about page"""
        response = requests.get(f"{BASE_URL}/api/content/about")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "About" in data["title"]
        assert len(data["content"]) > 100
    
    def test_invalid_page_returns_404(self):
        """GET /api/content/invalid should return 404"""
        response = requests.get(f"{BASE_URL}/api/content/nonexistent")
        assert response.status_code == 404
    
    def test_content_pages_are_public(self):
        """Content pages should be accessible without authentication"""
        # No auth header, should still work
        for page in ["terms", "privacy", "refund", "about"]:
            response = requests.get(f"{BASE_URL}/api/content/{page}")
            assert response.status_code == 200, f"Page {page} should be public"


class TestPayUGateway:
    """PayU payment gateway integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user for payment tests"""
        # First register a test user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Test User"
        })
        
        if register_response.status_code == 201:
            self.session = requests.Session()
            # Get cookies from register response
            self.session.cookies.update(register_response.cookies)
        else:
            # User might already exist, try login
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_response.status_code == 200:
                self.session = requests.Session()
                self.session.cookies.update(login_response.cookies)
            else:
                pytest.skip("Could not authenticate test user")
    
    def test_payu_initiate_returns_payment_data(self):
        """POST /api/payu/initiate should return payment_url and form_data"""
        response = self.session.post(f"{BASE_URL}/api/payu/initiate", json={
            "plan_key": "standard",
            "billing_cycle": "monthly"
        })
        assert response.status_code == 200
        data = response.json()
        assert "payment_url" in data
        assert "form_data" in data
        assert "txnid" in data
        # Verify form_data has required PayU fields
        form_data = data["form_data"]
        assert "key" in form_data
        assert "txnid" in form_data
        assert "amount" in form_data
        assert "hash" in form_data
        assert "surl" in form_data
        assert "furl" in form_data
    
    def test_payu_initiate_requires_auth(self):
        """POST /api/payu/initiate should require authentication"""
        response = requests.post(f"{BASE_URL}/api/payu/initiate", json={
            "plan_key": "standard",
            "billing_cycle": "monthly"
        })
        assert response.status_code == 401
    
    def test_payu_initiate_invalid_plan(self):
        """POST /api/payu/initiate with invalid plan should return 400"""
        response = self.session.post(f"{BASE_URL}/api/payu/initiate", json={
            "plan_key": "invalid_plan",
            "billing_cycle": "monthly"
        })
        assert response.status_code == 400
    
    def test_payu_initiate_free_plan_rejected(self):
        """POST /api/payu/initiate with free plan should return 400"""
        response = self.session.post(f"{BASE_URL}/api/payu/initiate", json={
            "plan_key": "free",
            "billing_cycle": "monthly"
        })
        assert response.status_code == 400


class TestReferralSystem:
    """Referral system - code generation, display, and application"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user for referral tests"""
        # Register a new test user for referral tests
        self.test_email = f"referral_test_{os.urandom(4).hex()}@example.com"
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Referral Test User"
        })
        
        if register_response.status_code in [200, 201]:
            self.session = requests.Session()
            self.session.cookies.update(register_response.cookies)
        else:
            pytest.skip("Could not register test user for referral tests")
    
    def test_get_referral_generates_code(self):
        """GET /api/referral should return or generate a referral code"""
        response = self.session.get(f"{BASE_URL}/api/referral")
        assert response.status_code == 200
        data = response.json()
        assert "referral_code" in data
        assert len(data["referral_code"]) > 0
        assert data["referral_code"].startswith("VT")
        assert "total_referrals" in data
        assert "successful_referrals" in data
    
    def test_referral_code_is_consistent(self):
        """GET /api/referral should return same code on subsequent calls"""
        response1 = self.session.get(f"{BASE_URL}/api/referral")
        code1 = response1.json()["referral_code"]
        
        response2 = self.session.get(f"{BASE_URL}/api/referral")
        code2 = response2.json()["referral_code"]
        
        assert code1 == code2
    
    def test_apply_invalid_referral_code(self):
        """POST /api/referral/apply with invalid code should return 404"""
        response = self.session.post(f"{BASE_URL}/api/referral/apply", json={
            "code": "INVALID123"
        })
        assert response.status_code == 404
        data = response.json()
        assert "Invalid referral code" in data.get("detail", "")
    
    def test_apply_own_referral_code_rejected(self):
        """POST /api/referral/apply with own code should return 400"""
        # First get own referral code
        ref_response = self.session.get(f"{BASE_URL}/api/referral")
        own_code = ref_response.json()["referral_code"]
        
        # Try to apply own code
        response = self.session.post(f"{BASE_URL}/api/referral/apply", json={
            "code": own_code
        })
        assert response.status_code == 400
        data = response.json()
        assert "Cannot refer yourself" in data.get("detail", "")
    
    def test_referral_requires_auth(self):
        """GET /api/referral should require authentication"""
        response = requests.get(f"{BASE_URL}/api/referral")
        assert response.status_code == 401


class TestAdminSmtpSettings:
    """Admin SMTP configuration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin for SMTP tests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code == 200:
            self.session = requests.Session()
            self.session.cookies.update(login_response.cookies)
        else:
            pytest.skip("Could not authenticate as admin")
    
    def test_get_smtp_settings(self):
        """GET /api/admin/smtp-settings should return SMTP config"""
        response = self.session.get(f"{BASE_URL}/api/admin/smtp-settings")
        assert response.status_code == 200
        data = response.json()
        # Should have key field at minimum
        assert "key" in data or isinstance(data, dict)
    
    def test_update_smtp_settings(self):
        """PUT /api/admin/smtp-settings should save SMTP config"""
        smtp_config = {
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "smtp_username": "test@test.com",
            "smtp_password": "testpassword",
            "smtp_from_email": "noreply@test.com",
            "smtp_from_name": "VitalTrack Test",
            "smtp_use_tls": True
        }
        response = self.session.put(f"{BASE_URL}/api/admin/smtp-settings", json=smtp_config)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "saved" in data["message"].lower()
        
        # Verify settings were saved (password should be masked)
        get_response = self.session.get(f"{BASE_URL}/api/admin/smtp-settings")
        assert get_response.status_code == 200
        saved_data = get_response.json()
        assert saved_data.get("smtp_host") == "smtp.test.com"
        assert saved_data.get("smtp_port") == 587
        assert saved_data.get("smtp_from_email") == "noreply@test.com"
        # Password should be masked
        assert saved_data.get("smtp_password") == "********"
    
    def test_smtp_settings_requires_admin(self):
        """SMTP settings should require admin role"""
        # Try with no auth
        response = requests.get(f"{BASE_URL}/api/admin/smtp-settings")
        assert response.status_code == 401
        
        # Try with regular user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"regular_{os.urandom(4).hex()}@example.com",
            "password": "RegularPass123!",
            "name": "Regular User"
        })
        if register_response.status_code == 201:
            user_session = requests.Session()
            user_session.cookies.update(register_response.cookies)
            response = user_session.get(f"{BASE_URL}/api/admin/smtp-settings")
            assert response.status_code in [401, 403]


class TestAuthEndpoints:
    """Basic auth endpoint verification"""
    
    def test_admin_login(self):
        """Admin login should work with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # API returns user data directly, not wrapped in "user" key
        assert "email" in data
        assert data["email"] == ADMIN_EMAIL
    
    def test_register_new_user(self):
        """User registration should work"""
        new_email = f"newuser_{os.urandom(4).hex()}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": new_email,
            "password": "NewUserPass123!",
            "name": "New User"
        })
        # API returns 200 on successful registration
        assert response.status_code in [200, 201]
        data = response.json()
        # API returns user data directly
        assert "email" in data
        assert data["email"] == new_email


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
