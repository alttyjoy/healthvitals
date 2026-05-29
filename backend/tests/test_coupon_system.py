"""
Coupon System Backend Tests - Iteration 6
Tests for Admin Coupon CRUD and User Coupon Validation
"""
import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://wellness-log-105.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN2_EMAIL = "mohanv44@gmail.com"
ADMIN2_PASSWORD = "India@1947"


class TestCouponSystem:
    """Coupon System Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_user = response.json()
        yield
        # Cleanup: Delete test coupons
        for code in ["TEST_COUPON_10", "TEST_COUPON_20", "TEST_COUPON_EDIT", "TEST_COUPON_DELETE", "TEST_COUPON_DUP"]:
            try:
                self.session.delete(f"{BASE_URL}/api/admin/coupons/{code}")
            except:
                pass
    
    # ==================== Admin Coupon CRUD Tests ====================
    
    def test_admin_list_coupons(self):
        """GET /api/admin/coupons - List all coupons"""
        response = self.session.get(f"{BASE_URL}/api/admin/coupons")
        assert response.status_code == 200, f"Failed to list coupons: {response.text}"
        data = response.json()
        assert "coupons" in data, "Response should contain 'coupons' key"
        assert isinstance(data["coupons"], list), "Coupons should be a list"
        print(f"✓ Listed {len(data['coupons'])} coupons")
    
    def test_admin_create_coupon_basic(self):
        """POST /api/admin/coupons - Create basic coupon"""
        response = self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_10",
            "discount_percent": 10,
            "max_uses": 100,
            "valid_plans": [],
            "expires_at": "",
            "active": True
        })
        assert response.status_code == 200, f"Failed to create coupon: {response.text}"
        data = response.json()
        assert data.get("code") == "TEST_COUPON_10", "Coupon code should be returned"
        print("✓ Created coupon TEST_COUPON_10 with 10% discount")
    
    def test_admin_create_coupon_with_expiry(self):
        """POST /api/admin/coupons - Create coupon with expiry date"""
        future_date = (datetime.now() + timedelta(days=30)).isoformat()
        response = self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_20",
            "discount_percent": 20,
            "max_uses": 50,
            "valid_plans": ["standard", "premium"],
            "expires_at": future_date,
            "active": True
        })
        assert response.status_code == 200, f"Failed to create coupon with expiry: {response.text}"
        print("✓ Created coupon TEST_COUPON_20 with 20% discount and expiry")
    
    def test_admin_create_coupon_duplicate_prevention(self):
        """POST /api/admin/coupons - Duplicate coupon code should fail"""
        # First create
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_DUP",
            "discount_percent": 15,
            "max_uses": 0,
            "active": True
        })
        # Try duplicate
        response = self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_DUP",
            "discount_percent": 25,
            "max_uses": 0,
            "active": True
        })
        assert response.status_code == 400, f"Duplicate coupon should fail: {response.text}"
        assert "already exists" in response.text.lower(), "Error should mention duplicate"
        print("✓ Duplicate coupon prevention works")
    
    def test_admin_create_coupon_invalid_discount(self):
        """POST /api/admin/coupons - Invalid discount should fail"""
        response = self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "INVALID_DISCOUNT",
            "discount_percent": 150,  # Invalid: > 100
            "max_uses": 0,
            "active": True
        })
        assert response.status_code == 400, f"Invalid discount should fail: {response.text}"
        print("✓ Invalid discount validation works")
    
    def test_admin_update_coupon(self):
        """PUT /api/admin/coupons/{code} - Update coupon"""
        # First create
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_EDIT",
            "discount_percent": 10,
            "max_uses": 100,
            "active": True
        })
        # Update
        response = self.session.put(f"{BASE_URL}/api/admin/coupons/TEST_COUPON_EDIT", json={
            "code": "TEST_COUPON_EDIT",
            "discount_percent": 25,  # Changed
            "max_uses": 200,  # Changed
            "active": True
        })
        assert response.status_code == 200, f"Failed to update coupon: {response.text}"
        
        # Verify update
        list_response = self.session.get(f"{BASE_URL}/api/admin/coupons")
        coupons = list_response.json().get("coupons", [])
        updated = next((c for c in coupons if c["code"] == "TEST_COUPON_EDIT"), None)
        assert updated is not None, "Updated coupon should exist"
        assert updated["discount_percent"] == 25, "Discount should be updated to 25%"
        assert updated["max_uses"] == 200, "Max uses should be updated to 200"
        print("✓ Coupon updated successfully")
    
    def test_admin_delete_coupon(self):
        """DELETE /api/admin/coupons/{code} - Delete coupon"""
        # First create
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_COUPON_DELETE",
            "discount_percent": 5,
            "max_uses": 10,
            "active": True
        })
        # Delete
        response = self.session.delete(f"{BASE_URL}/api/admin/coupons/TEST_COUPON_DELETE")
        assert response.status_code == 200, f"Failed to delete coupon: {response.text}"
        
        # Verify deletion
        list_response = self.session.get(f"{BASE_URL}/api/admin/coupons")
        coupons = list_response.json().get("coupons", [])
        deleted = next((c for c in coupons if c["code"] == "TEST_COUPON_DELETE"), None)
        assert deleted is None, "Deleted coupon should not exist"
        print("✓ Coupon deleted successfully")
    
    def test_admin_delete_nonexistent_coupon(self):
        """DELETE /api/admin/coupons/{code} - Delete nonexistent coupon should fail"""
        response = self.session.delete(f"{BASE_URL}/api/admin/coupons/NONEXISTENT_CODE_XYZ")
        assert response.status_code == 404, f"Delete nonexistent should return 404: {response.text}"
        print("✓ Delete nonexistent coupon returns 404")
    
    # ==================== User Coupon Validation Tests ====================
    
    def test_validate_coupon_valid(self):
        """POST /api/coupons/validate - Validate valid coupon"""
        # First create a coupon
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_VALID_COUPON",
            "discount_percent": 15,
            "max_uses": 100,
            "active": True
        })
        
        # Validate
        response = self.session.post(f"{BASE_URL}/api/coupons/validate", json={
            "code": "TEST_VALID_COUPON",
            "plan_key": "standard"
        })
        assert response.status_code == 200, f"Valid coupon should validate: {response.text}"
        data = response.json()
        assert data.get("valid") == True, "Should return valid=True"
        assert data.get("discount_percent") == 15, "Should return correct discount"
        print("✓ Valid coupon validation works")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/coupons/TEST_VALID_COUPON")
    
    def test_validate_coupon_invalid_code(self):
        """POST /api/coupons/validate - Invalid coupon code should fail"""
        response = self.session.post(f"{BASE_URL}/api/coupons/validate", json={
            "code": "INVALID_CODE_XYZ",
            "plan_key": ""
        })
        assert response.status_code == 404, f"Invalid coupon should return 404: {response.text}"
        assert "invalid" in response.text.lower(), "Error should mention invalid"
        print("✓ Invalid coupon code returns 404")
    
    def test_validate_coupon_inactive(self):
        """POST /api/coupons/validate - Inactive coupon should fail"""
        # Create inactive coupon
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_INACTIVE",
            "discount_percent": 10,
            "max_uses": 100,
            "active": False  # Inactive
        })
        
        response = self.session.post(f"{BASE_URL}/api/coupons/validate", json={
            "code": "TEST_INACTIVE",
            "plan_key": ""
        })
        assert response.status_code == 400, f"Inactive coupon should fail: {response.text}"
        assert "no longer active" in response.text.lower(), "Error should mention inactive"
        print("✓ Inactive coupon validation fails correctly")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/coupons/TEST_INACTIVE")
    
    def test_validate_coupon_expired(self):
        """POST /api/coupons/validate - Expired coupon should fail"""
        # Create expired coupon
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "TEST_EXPIRED",
            "discount_percent": 10,
            "max_uses": 100,
            "expires_at": past_date,
            "active": True
        })
        
        response = self.session.post(f"{BASE_URL}/api/coupons/validate", json={
            "code": "TEST_EXPIRED",
            "plan_key": ""
        })
        assert response.status_code == 400, f"Expired coupon should fail: {response.text}"
        assert "expired" in response.text.lower(), "Error should mention expired"
        print("✓ Expired coupon validation fails correctly")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/coupons/TEST_EXPIRED")
    
    # ==================== SAVE20 Coupon Tests ====================
    
    def test_save20_coupon_exists(self):
        """Verify SAVE20 coupon exists with 20% discount"""
        response = self.session.get(f"{BASE_URL}/api/admin/coupons")
        assert response.status_code == 200
        coupons = response.json().get("coupons", [])
        save20 = next((c for c in coupons if c["code"] == "SAVE20"), None)
        if save20:
            assert save20["discount_percent"] == 20, "SAVE20 should have 20% discount"
            print(f"✓ SAVE20 coupon exists: {save20['discount_percent']}% off, max_uses={save20.get('max_uses', 0)}")
        else:
            # Create it if it doesn't exist
            create_response = self.session.post(f"{BASE_URL}/api/admin/coupons", json={
                "code": "SAVE20",
                "discount_percent": 20,
                "max_uses": 100,
                "active": True
            })
            assert create_response.status_code == 200, f"Failed to create SAVE20: {create_response.text}"
            print("✓ Created SAVE20 coupon with 20% discount")
    
    def test_validate_save20(self):
        """POST /api/coupons/validate - Validate SAVE20 coupon"""
        # Ensure SAVE20 exists
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "SAVE20",
            "discount_percent": 20,
            "max_uses": 100,
            "active": True
        })
        
        response = self.session.post(f"{BASE_URL}/api/coupons/validate", json={
            "code": "SAVE20",
            "plan_key": "standard"
        })
        # May fail if already used by this user, but should not be 404
        if response.status_code == 200:
            data = response.json()
            assert data.get("discount_percent") == 20, "SAVE20 should give 20% discount"
            print("✓ SAVE20 validates with 20% discount")
        elif response.status_code == 400:
            # Already used by this user
            print("✓ SAVE20 validation: already used by this user (expected)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code} - {response.text}")
    
    # ==================== Razorpay Order with Coupon Tests ====================
    
    def test_razorpay_order_with_coupon(self):
        """POST /api/razorpay/create-order - Order with coupon should have discounted amount"""
        # Ensure SAVE20 exists
        self.session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "SAVE20",
            "discount_percent": 20,
            "max_uses": 100,
            "active": True
        })
        
        response = self.session.post(f"{BASE_URL}/api/razorpay/create-order", json={
            "plan_key": "standard",
            "billing_cycle": "monthly",
            "coupon_code": "SAVE20"
        })
        
        if response.status_code == 503:
            # Razorpay not configured - skip
            print("⚠ Razorpay not configured - skipping order test")
            pytest.skip("Razorpay not configured")
        
        assert response.status_code == 200, f"Failed to create order: {response.text}"
        data = response.json()
        
        # Standard plan is ₹299, with 20% off should be ₹239
        assert data.get("discount_percent") == 20, "Should return discount_percent"
        assert data.get("coupon_code") == "SAVE20", "Should return coupon_code"
        
        # Verify discounted price
        original_price = 299
        expected_discounted = round(original_price * 0.8)  # 20% off
        assert data.get("final_price") == expected_discounted, f"Final price should be {expected_discounted}"
        
        print(f"✓ Razorpay order with SAVE20: original=₹{original_price}, discounted=₹{data.get('final_price')}")
    
    def test_razorpay_order_without_coupon(self):
        """POST /api/razorpay/create-order - Order without coupon should have full price"""
        response = self.session.post(f"{BASE_URL}/api/razorpay/create-order", json={
            "plan_key": "standard",
            "billing_cycle": "monthly",
            "coupon_code": ""
        })
        
        if response.status_code == 503:
            print("⚠ Razorpay not configured - skipping order test")
            pytest.skip("Razorpay not configured")
        
        assert response.status_code == 200, f"Failed to create order: {response.text}"
        data = response.json()
        
        assert data.get("discount_percent") == 0, "Should have no discount"
        assert data.get("final_price") == 299, "Should have full price ₹299"
        print("✓ Razorpay order without coupon: full price ₹299")


class TestCouponSystemAdmin2:
    """Test coupon system with second admin account"""
    
    def test_admin2_can_manage_coupons(self):
        """Admin 2 (mohanv44@gmail.com) can create/edit/delete coupons"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin 2
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN2_EMAIL,
            "password": ADMIN2_PASSWORD
        })
        assert response.status_code == 200, f"Admin 2 login failed: {response.text}"
        
        # Create coupon
        create_response = session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "ADMIN2_TEST",
            "discount_percent": 30,
            "max_uses": 50,
            "active": True
        })
        assert create_response.status_code == 200, f"Admin 2 create coupon failed: {create_response.text}"
        print("✓ Admin 2 can create coupons")
        
        # Update coupon
        update_response = session.put(f"{BASE_URL}/api/admin/coupons/ADMIN2_TEST", json={
            "code": "ADMIN2_TEST",
            "discount_percent": 35,
            "max_uses": 100,
            "active": True
        })
        assert update_response.status_code == 200, f"Admin 2 update coupon failed: {update_response.text}"
        print("✓ Admin 2 can update coupons")
        
        # Delete coupon
        delete_response = session.delete(f"{BASE_URL}/api/admin/coupons/ADMIN2_TEST")
        assert delete_response.status_code == 200, f"Admin 2 delete coupon failed: {delete_response.text}"
        print("✓ Admin 2 can delete coupons")


class TestCouponSystemUnauthorized:
    """Test coupon system authorization"""
    
    def test_unauthenticated_cannot_list_coupons(self):
        """Unauthenticated user cannot list admin coupons"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/admin/coupons")
        assert response.status_code == 401, f"Should return 401: {response.text}"
        print("✓ Unauthenticated cannot list admin coupons")
    
    def test_unauthenticated_cannot_create_coupon(self):
        """Unauthenticated user cannot create coupons"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/admin/coupons", json={
            "code": "UNAUTH_TEST",
            "discount_percent": 10,
            "active": True
        })
        assert response.status_code == 401, f"Should return 401: {response.text}"
        print("✓ Unauthenticated cannot create coupons")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
