"""
Test Admin User CRUD Feature - Iteration 5
Tests: Add, Edit, Delete users with role assignment (Admin/User)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://wellness-log-105.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN1_EMAIL = "admin@example.com"
ADMIN1_PASSWORD = "admin123"
ADMIN2_EMAIL = "mohanv44@gmail.com"
ADMIN2_PASSWORD = "India@1947"
ADMIN3_EMAIL = "alttyjoy@gmail.com"
ADMIN2_PASSWORD = "India@1947"


class TestAdminUserCRUD:
    """Admin User CRUD endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with admin auth"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN1_EMAIL,
            "password": ADMIN1_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_user = response.json()
        print(f"Logged in as admin: {self.admin_user.get('email')}")
        yield
        # Cleanup: delete test users created during tests
        self._cleanup_test_users()
    
    def _cleanup_test_users(self):
        """Delete any TEST_ prefixed users"""
        try:
            res = self.session.get(f"{BASE_URL}/api/admin/users?search=TEST_")
            if res.status_code == 200:
                users = res.json().get('users', [])
                for u in users:
                    self.session.delete(f"{BASE_URL}/api/admin/users/{u['id']}")
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    # ==================== POST /api/admin/users ====================
    
    def test_create_user_success(self):
        """POST /api/admin/users creates user with correct role"""
        payload = {
            "email": f"TEST_user_{int(time.time())}@example.com",
            "password": "testpass123",
            "name": "TEST User",
            "role": "user",
            "plan": "free"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 200, f"Create user failed: {response.text}"
        
        data = response.json()
        assert data["email"] == payload["email"].lower()
        assert data["name"] == payload["name"]
        assert data["role"] == "user"
        assert data["plan"] == "free"
        assert "id" in data
        print(f"Created user: {data['email']} with role {data['role']}")
    
    def test_create_admin_user(self):
        """POST /api/admin/users creates admin (super_admin role)"""
        payload = {
            "email": f"TEST_admin_{int(time.time())}@example.com",
            "password": "adminpass123",
            "name": "TEST Admin",
            "role": "super_admin",
            "plan": "premium"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 200, f"Create admin failed: {response.text}"
        
        data = response.json()
        assert data["role"] == "super_admin"
        assert data["plan"] == "premium"
        print(f"Created admin: {data['email']} with role {data['role']}")
    
    def test_create_user_with_standard_plan(self):
        """POST /api/admin/users creates user with standard plan"""
        payload = {
            "email": f"TEST_standard_{int(time.time())}@example.com",
            "password": "testpass123",
            "name": "TEST Standard User",
            "role": "user",
            "plan": "standard"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 200, f"Create user failed: {response.text}"
        
        data = response.json()
        assert data["plan"] == "standard"
        print(f"Created user with plan: {data['plan']}")
    
    def test_create_user_empty_email_rejected(self):
        """POST /api/admin/users rejects empty email"""
        payload = {
            "email": "",
            "password": "testpass123",
            "name": "No Email User",
            "role": "user",
            "plan": "free"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Empty email correctly rejected")
    
    def test_create_user_empty_password_rejected(self):
        """POST /api/admin/users rejects empty password"""
        payload = {
            "email": f"TEST_nopass_{int(time.time())}@example.com",
            "password": "",
            "name": "No Password User",
            "role": "user",
            "plan": "free"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Empty password correctly rejected")
    
    def test_create_user_short_password_rejected(self):
        """POST /api/admin/users rejects password < 6 chars"""
        payload = {
            "email": f"TEST_shortpass_{int(time.time())}@example.com",
            "password": "12345",
            "name": "Short Password User",
            "role": "user",
            "plan": "free"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Short password correctly rejected")
    
    def test_create_user_duplicate_email_rejected(self):
        """POST /api/admin/users rejects duplicate email"""
        # First create a user
        email = f"TEST_dup_{int(time.time())}@example.com"
        payload = {
            "email": email,
            "password": "testpass123",
            "name": "First User",
            "role": "user",
            "plan": "free"
        }
        response1 = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response1.status_code == 200
        
        # Try to create another with same email
        payload["name"] = "Second User"
        response2 = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        print("Duplicate email correctly rejected")
    
    def test_create_user_invalid_role_rejected(self):
        """POST /api/admin/users rejects invalid role"""
        payload = {
            "email": f"TEST_badrole_{int(time.time())}@example.com",
            "password": "testpass123",
            "name": "Bad Role User",
            "role": "invalid_role",
            "plan": "free"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/users", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid role, got {response.status_code}"
        print("Invalid role correctly rejected")
    
    # ==================== PUT /api/admin/users/{id} ====================
    
    def test_update_user_role(self):
        """PUT /api/admin/users/{id} updates user role from user to super_admin"""
        # Create a user first
        email = f"TEST_rolechange_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Role Change User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]
        
        # Update role to super_admin
        update_res = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}", json={
            "role": "super_admin"
        })
        assert update_res.status_code == 200, f"Update failed: {update_res.text}"
        
        updated = update_res.json()
        assert updated["role"] == "super_admin"
        print(f"Updated user role to: {updated['role']}")
        
        # Verify with GET
        get_res = self.session.get(f"{BASE_URL}/api/admin/users/{user_id}")
        assert get_res.status_code == 200
        assert get_res.json()["role"] == "super_admin"
        print("Role change verified via GET")
    
    def test_update_user_plan(self):
        """PUT /api/admin/users/{id} updates user plan"""
        # Create a user first
        email = f"TEST_planchange_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Plan Change User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]
        
        # Update plan to premium
        update_res = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}", json={
            "plan": "premium"
        })
        assert update_res.status_code == 200, f"Update failed: {update_res.text}"
        
        updated = update_res.json()
        assert updated["plan"] == "premium"
        print(f"Updated user plan to: {updated['plan']}")
    
    def test_update_user_name(self):
        """PUT /api/admin/users/{id} updates user name"""
        # Create a user first
        email = f"TEST_namechange_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Original Name",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]
        
        # Update name
        update_res = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}", json={
            "name": "Updated Name"
        })
        assert update_res.status_code == 200, f"Update failed: {update_res.text}"
        
        updated = update_res.json()
        assert updated["name"] == "Updated Name"
        print(f"Updated user name to: {updated['name']}")
    
    def test_update_multiple_fields(self):
        """PUT /api/admin/users/{id} updates multiple fields at once"""
        # Create a user first
        email = f"TEST_multiupdate_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Multi Update User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]
        
        # Update multiple fields
        update_res = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}", json={
            "name": "New Name",
            "role": "super_admin",
            "plan": "standard"
        })
        assert update_res.status_code == 200, f"Update failed: {update_res.text}"
        
        updated = update_res.json()
        assert updated["name"] == "New Name"
        assert updated["role"] == "super_admin"
        assert updated["plan"] == "standard"
        print("Multiple fields updated successfully")
    
    # ==================== DELETE /api/admin/users/{id} ====================
    
    def test_delete_user(self):
        """DELETE /api/admin/users/{id} deletes user"""
        # Create a user first
        email = f"TEST_delete_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Delete Me User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        user_id = create_res.json()["id"]
        
        # Delete the user
        delete_res = self.session.delete(f"{BASE_URL}/api/admin/users/{user_id}")
        assert delete_res.status_code == 200, f"Delete failed: {delete_res.text}"
        print(f"Deleted user: {email}")
        
        # Verify user no longer exists
        get_res = self.session.get(f"{BASE_URL}/api/admin/users/{user_id}")
        assert get_res.status_code == 404, f"Expected 404 after delete, got {get_res.status_code}"
        print("User deletion verified - returns 404")
    
    def test_delete_self_protection(self):
        """DELETE /api/admin/users/{id} prevents admin from deleting themselves"""
        admin_id = self.admin_user.get("id")
        assert admin_id, "Admin ID not found"
        
        delete_res = self.session.delete(f"{BASE_URL}/api/admin/users/{admin_id}")
        assert delete_res.status_code == 400, f"Expected 400 for self-delete, got {delete_res.status_code}"
        
        # Verify error message
        error_data = delete_res.json()
        assert "cannot delete yourself" in error_data.get("detail", "").lower() or "yourself" in str(error_data).lower()
        print("Self-delete protection working correctly")
    
    def test_delete_nonexistent_user(self):
        """DELETE /api/admin/users/{id} returns 404 for nonexistent user"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        delete_res = self.session.delete(f"{BASE_URL}/api/admin/users/{fake_id}")
        assert delete_res.status_code == 404, f"Expected 404, got {delete_res.status_code}"
        print("Nonexistent user delete returns 404")
    
    # ==================== GET /api/admin/users ====================
    
    def test_list_users(self):
        """GET /api/admin/users returns user list"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        print(f"Listed {len(data['users'])} users, total: {data['total']}")
    
    def test_search_users(self):
        """GET /api/admin/users?search= filters users"""
        # Create a user with unique name
        unique_name = f"TEST_SEARCHABLE_{int(time.time())}"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": f"{unique_name.lower()}@example.com",
            "password": "testpass123",
            "name": unique_name,
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        
        # Search for the user
        search_res = self.session.get(f"{BASE_URL}/api/admin/users?search={unique_name}")
        assert search_res.status_code == 200
        
        data = search_res.json()
        assert data["total"] >= 1
        found = any(u["name"] == unique_name for u in data["users"])
        assert found, f"Created user not found in search results"
        print(f"Search found user: {unique_name}")
    
    # ==================== Auth Required Tests ====================
    
    def test_create_user_requires_admin(self):
        """POST /api/admin/users requires admin authentication"""
        # Create new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        response = no_auth_session.post(f"{BASE_URL}/api/admin/users", json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test",
            "role": "user",
            "plan": "free"
        })
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("Create user requires authentication")
    
    def test_regular_user_cannot_create_users(self):
        """POST /api/admin/users rejects non-admin users"""
        # Create a regular user
        email = f"TEST_regular_{int(time.time())}@example.com"
        create_res = self.session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Regular User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200
        
        # Login as regular user
        regular_session = requests.Session()
        regular_session.headers.update({"Content-Type": "application/json"})
        login_res = regular_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": "testpass123"
        })
        assert login_res.status_code == 200
        
        # Try to create user as regular user
        response = regular_session.post(f"{BASE_URL}/api/admin/users", json={
            "email": "another@example.com",
            "password": "testpass123",
            "name": "Another User",
            "role": "user",
            "plan": "free"
        })
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("Non-admin user correctly rejected from creating users")


class TestAdminUserCRUDWithSecondAdmin:
    """Test with second admin account"""
    
    def test_second_admin_can_manage_users(self):
        """Admin 2 (mohanv44@gmail.com) can create/edit/delete users"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as second admin
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN2_EMAIL,
            "password": ADMIN2_PASSWORD
        })
        assert login_res.status_code == 200, f"Admin 2 login failed: {login_res.text}"
        admin2 = login_res.json()
        assert admin2["role"] == "super_admin"
        print(f"Logged in as Admin 2: {admin2['email']}")
        
        # Create a user
        email = f"TEST_admin2_created_{int(time.time())}@example.com"
        create_res = session.post(f"{BASE_URL}/api/admin/users", json={
            "email": email,
            "password": "testpass123",
            "name": "Admin2 Created User",
            "role": "user",
            "plan": "free"
        })
        assert create_res.status_code == 200, f"Create failed: {create_res.text}"
        user_id = create_res.json()["id"]
        print(f"Admin 2 created user: {email}")
        
        # Update the user
        update_res = session.put(f"{BASE_URL}/api/admin/users/{user_id}", json={
            "role": "super_admin"
        })
        assert update_res.status_code == 200, f"Update failed: {update_res.text}"
        print("Admin 2 updated user role")
        
        # Delete the user
        delete_res = session.delete(f"{BASE_URL}/api/admin/users/{user_id}")
        assert delete_res.status_code == 200, f"Delete failed: {delete_res.text}"
        print("Admin 2 deleted user")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
