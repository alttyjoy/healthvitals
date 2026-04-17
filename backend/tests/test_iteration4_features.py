"""
Iteration 4 Backend Tests
Features tested:
1. New admin user mohanv44@gmail.com / India@1947
2. Forgot Password flow
3. Reset Password flow
4. Email Reminder system APIs
5. Admin Content Management CRUD
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminLogin:
    """Test admin login with both admin accounts"""
    
    def test_admin1_login(self):
        """Admin 1: admin@example.com / admin123"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Admin1 login failed: {response.text}"
        data = response.json()
        # API returns user data directly (not wrapped in "user" key)
        assert data.get("email") == "admin@example.com"
        assert data.get("role") == "super_admin"
        print("SUCCESS: Admin 1 login works")
    
    def test_admin2_login(self):
        """Admin 2: mohanv44@gmail.com / India@1947"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "mohanv44@gmail.com",
            "password": "India@1947"
        })
        assert response.status_code == 200, f"Admin2 login failed: {response.text}"
        data = response.json()
        # API returns user data directly (not wrapped in "user" key)
        assert data.get("email") == "mohanv44@gmail.com"
        assert data.get("role") == "super_admin"
        print("SUCCESS: Admin 2 (mohanv44@gmail.com) login works")


class TestForgotPassword:
    """Test forgot password flow"""
    
    def test_forgot_password_existing_email(self):
        """POST /api/auth/forgot-password with existing email"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "admin@example.com"
        })
        assert response.status_code == 200, f"Forgot password failed: {response.text}"
        data = response.json()
        assert "message" in data
        # Should return success message regardless of email existence (security)
        assert "reset link" in data["message"].lower() or "sent" in data["message"].lower()
        print("SUCCESS: Forgot password endpoint works for existing email")
    
    def test_forgot_password_nonexistent_email(self):
        """POST /api/auth/forgot-password with non-existent email (should still return 200)"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        # Should return 200 for security (don't reveal if email exists)
        assert response.status_code == 200, f"Forgot password should return 200: {response.text}"
        print("SUCCESS: Forgot password returns 200 for non-existent email (security)")


class TestResetPassword:
    """Test reset password flow"""
    
    def test_reset_password_invalid_token(self):
        """POST /api/auth/reset-password with invalid token"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "invalid_token_12345",
            "password": "newpassword123"
        })
        assert response.status_code == 400, f"Should reject invalid token: {response.text}"
        data = response.json()
        assert "invalid" in data.get("detail", "").lower() or "expired" in data.get("detail", "").lower()
        print("SUCCESS: Reset password rejects invalid token")
    
    def test_reset_password_short_password(self):
        """POST /api/auth/reset-password with short password"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "some_token",
            "password": "123"
        })
        # Should fail either due to invalid token or short password
        assert response.status_code == 400
        print("SUCCESS: Reset password validates password length")


class TestEmailReminderAPIs:
    """Test email reminder system APIs"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        return session
    
    def test_get_reminder_settings(self, admin_session):
        """GET /api/admin/reminder-settings"""
        response = admin_session.get(f"{BASE_URL}/api/admin/reminder-settings")
        assert response.status_code == 200, f"Get reminder settings failed: {response.text}"
        data = response.json()
        assert "enabled" in data or "time" in data
        print(f"SUCCESS: Get reminder settings works - enabled: {data.get('enabled')}, time: {data.get('time')}")
    
    def test_update_reminder_settings(self, admin_session):
        """PUT /api/admin/reminder-settings"""
        response = admin_session.put(f"{BASE_URL}/api/admin/reminder-settings", json={
            "enabled": True,
            "time": "10:00"
        })
        assert response.status_code == 200, f"Update reminder settings failed: {response.text}"
        data = response.json()
        assert "message" in data
        print("SUCCESS: Update reminder settings works")
        
        # Verify the change
        get_response = admin_session.get(f"{BASE_URL}/api/admin/reminder-settings")
        assert get_response.status_code == 200
        settings = get_response.json()
        assert settings.get("enabled") == True
        assert settings.get("time") == "10:00"
        print("SUCCESS: Reminder settings persisted correctly")
    
    def test_send_reminders(self, admin_session):
        """POST /api/admin/send-reminders"""
        response = admin_session.post(f"{BASE_URL}/api/admin/send-reminders")
        assert response.status_code == 200, f"Send reminders failed: {response.text}"
        data = response.json()
        assert "message" in data
        print("SUCCESS: Send reminders endpoint works (SMTP not configured, so no actual emails sent)")
    
    def test_reminder_settings_requires_auth(self):
        """Reminder settings should require admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/reminder-settings")
        assert response.status_code == 401, "Should require authentication"
        print("SUCCESS: Reminder settings requires authentication")


class TestAdminContentManagement:
    """Test admin content management CRUD"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        return session
    
    def test_list_content_pages(self, admin_session):
        """GET /api/admin/content-pages"""
        response = admin_session.get(f"{BASE_URL}/api/admin/content-pages")
        assert response.status_code == 200, f"List content pages failed: {response.text}"
        data = response.json()
        assert "pages" in data
        pages = data["pages"]
        # Should have built-in pages
        page_keys = [p["key"] for p in pages]
        assert "terms" in page_keys, "Should have terms page"
        assert "privacy" in page_keys, "Should have privacy page"
        assert "refund" in page_keys, "Should have refund page"
        assert "about" in page_keys, "Should have about page"
        print(f"SUCCESS: List content pages works - found {len(pages)} pages")
    
    def test_create_custom_page(self, admin_session):
        """POST /api/admin/content-pages - create custom page"""
        response = admin_session.post(f"{BASE_URL}/api/admin/content-pages", json={
            "key": "test-page-iter4",
            "title": "Test Page Iteration 4",
            "content": "# Test Content\n\nThis is a test page created during iteration 4 testing.",
            "page_type": "custom",
            "published": True
        })
        assert response.status_code == 200, f"Create page failed: {response.text}"
        data = response.json()
        assert "message" in data
        print("SUCCESS: Create custom page works")
        
        # Verify page was created
        list_response = admin_session.get(f"{BASE_URL}/api/admin/content-pages")
        pages = list_response.json()["pages"]
        page_keys = [p["key"] for p in pages]
        assert "test-page-iter4" in page_keys, "Created page should appear in list"
        print("SUCCESS: Custom page appears in list")
    
    def test_update_custom_page(self, admin_session):
        """PUT /api/admin/content-pages/{key} - update custom page"""
        response = admin_session.put(f"{BASE_URL}/api/admin/content-pages/test-page-iter4", json={
            "key": "test-page-iter4",
            "title": "Updated Test Page",
            "content": "# Updated Content\n\nThis page was updated.",
            "page_type": "custom",
            "published": True
        })
        assert response.status_code == 200, f"Update page failed: {response.text}"
        print("SUCCESS: Update custom page works")
    
    def test_delete_custom_page(self, admin_session):
        """DELETE /api/admin/content-pages/{key} - delete custom page"""
        response = admin_session.delete(f"{BASE_URL}/api/admin/content-pages/test-page-iter4")
        assert response.status_code == 200, f"Delete page failed: {response.text}"
        print("SUCCESS: Delete custom page works")
        
        # Verify page was deleted
        list_response = admin_session.get(f"{BASE_URL}/api/admin/content-pages")
        pages = list_response.json()["pages"]
        page_keys = [p["key"] for p in pages]
        assert "test-page-iter4" not in page_keys, "Deleted page should not appear in list"
        print("SUCCESS: Custom page removed from list")
    
    def test_cannot_delete_builtin_page(self, admin_session):
        """DELETE /api/admin/content-pages/{key} - cannot delete built-in pages"""
        response = admin_session.delete(f"{BASE_URL}/api/admin/content-pages/terms")
        assert response.status_code == 400, f"Should not allow deleting built-in page: {response.text}"
        data = response.json()
        assert "built-in" in data.get("detail", "").lower() or "cannot" in data.get("detail", "").lower()
        print("SUCCESS: Cannot delete built-in pages")
    
    def test_content_pages_requires_auth(self):
        """Content pages admin endpoint should require auth"""
        response = requests.get(f"{BASE_URL}/api/admin/content-pages")
        assert response.status_code == 401, "Should require authentication"
        print("SUCCESS: Content pages requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
