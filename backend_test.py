#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta

class VitalTrackAPITester:
    def __init__(self, base_url="https://wellness-log-105.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name} - {details}")
            self.failed_tests.append({"test": test_name, "error": details})

    def api_call(self, method, endpoint, data=None, expected_status=200):
        """Make API call and return response"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            return success, response
        except Exception as e:
            return False, str(e)

    def test_admin_login(self):
        """Test admin login with credentials from test_credentials.md"""
        success, response = self.api_call('POST', 'auth/login', {
            'email': 'admin@example.com',
            'password': 'admin123'
        })
        
        if success and hasattr(response, 'json'):
            try:
                data = response.json()
                # Extract token from cookies or response
                if 'access_token' in response.cookies:
                    self.token = response.cookies['access_token']
                elif 'token' in data:
                    self.token = data['token']
                self.log_result("Admin Login", True)
                return True
            except:
                pass
        
        self.log_result("Admin Login", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")
        return False

    def test_plans_endpoint(self):
        """Test GET /api/plans returns premium at ₹499"""
        success, response = self.api_call('GET', 'plans')
        
        if success:
            try:
                plans = response.json()
                premium_plan = next((p for p in plans if p['key'] == 'premium'), None)
                if premium_plan and premium_plan['price'] == 499:
                    self.log_result("Premium Plan Price ₹499", True)
                    return True
                else:
                    self.log_result("Premium Plan Price ₹499", False, f"Found price: {premium_plan['price'] if premium_plan else 'Plan not found'}")
            except Exception as e:
                self.log_result("Premium Plan Price ₹499", False, str(e))
        else:
            self.log_result("Premium Plan Price ₹499", False, f"API call failed: {response}")
        return False

    def test_translations_endpoints(self):
        """Test translation endpoints for Hindi and Telugu"""
        # Test Hindi translations
        success, response = self.api_call('GET', 'translations/hi')
        if success:
            try:
                translations = response.json()
                if 'app_name' in translations and 'dashboard' in translations:
                    self.log_result("Hindi Translations", True)
                else:
                    self.log_result("Hindi Translations", False, "Missing expected keys")
            except:
                self.log_result("Hindi Translations", False, "Invalid JSON response")
        else:
            self.log_result("Hindi Translations", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")

        # Test Telugu translations
        success, response = self.api_call('GET', 'translations/te')
        if success:
            try:
                translations = response.json()
                if 'app_name' in translations and 'dashboard' in translations:
                    self.log_result("Telugu Translations", True)
                else:
                    self.log_result("Telugu Translations", False, "Missing expected keys")
            except:
                self.log_result("Telugu Translations", False, "Invalid JSON response")
        else:
            self.log_result("Telugu Translations", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")

    def test_razorpay_create_order(self):
        """Test Razorpay order creation for standard plan"""
        if not self.token:
            self.log_result("Razorpay Create Order", False, "No auth token")
            return False

        success, response = self.api_call('POST', 'razorpay/create-order', {
            'plan_key': 'standard',
            'billing_cycle': 'monthly'
        })
        
        if success:
            try:
                data = response.json()
                if 'order_id' in data and 'amount' in data and data['amount'] == 29900:  # ₹299 * 100 paise
                    self.log_result("Razorpay Create Order", True)
                    return True
                else:
                    self.log_result("Razorpay Create Order", False, f"Missing fields or wrong amount: {data}")
            except Exception as e:
                self.log_result("Razorpay Create Order", False, str(e))
        else:
            self.log_result("Razorpay Create Order", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")
        return False

    def test_shared_reports_creation(self):
        """Test shared reports creation with password"""
        if not self.token:
            self.log_result("Shared Reports Creation", False, "No auth token")
            return False

        # First enable some vitals for the admin user
        self.api_call('POST', 'vitals/toggle', {'vital_key': 'heart_rate', 'enabled': True})
        
        success, response = self.api_call('POST', 'shared-reports', {
            'vital_keys': ['heart_rate'],
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'expires_days': 7,
            'password': 'test123'
        })
        
        if success:
            try:
                data = response.json()
                if 'token' in data and 'has_password' in data and data['has_password']:
                    self.shared_token = data['token']
                    self.log_result("Shared Reports Creation", True)
                    return True
                else:
                    self.log_result("Shared Reports Creation", False, f"Missing fields: {data}")
            except Exception as e:
                self.log_result("Shared Reports Creation", False, str(e))
        else:
            self.log_result("Shared Reports Creation", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")
        return False

    def test_shared_reports_view_password(self):
        """Test shared reports view with password protection"""
        if not hasattr(self, 'shared_token'):
            self.log_result("Shared Reports View Password", False, "No shared token available")
            return False

        # Test without password (should require password)
        success, response = self.api_call('GET', f'shared-reports/view/{self.shared_token}')
        if success:
            try:
                data = response.json()
                if data.get('requires_password'):
                    self.log_result("Shared Reports Password Protection", True)
                else:
                    self.log_result("Shared Reports Password Protection", False, "Should require password")
            except:
                self.log_result("Shared Reports Password Protection", False, "Invalid response")
        else:
            self.log_result("Shared Reports Password Protection", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")

        # Test with correct password
        success, response = self.api_call('POST', f'shared-reports/view/{self.shared_token}', {
            'password': 'test123'
        })
        if success:
            try:
                data = response.json()
                if 'entries' in data and 'vital_keys' in data:
                    self.log_result("Shared Reports View with Password", True)
                    return True
                else:
                    self.log_result("Shared Reports View with Password", False, f"Missing fields: {data}")
            except Exception as e:
                self.log_result("Shared Reports View with Password", False, str(e))
        else:
            self.log_result("Shared Reports View with Password", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")
        return False

    def test_subscription_change_to_free(self):
        """Test downgrade to free plan (should work without payment)"""
        if not self.token:
            self.log_result("Subscription Change to Free", False, "No auth token")
            return False

        success, response = self.api_call('POST', 'subscription/change', {
            'plan_key': 'free'
        })
        
        if success:
            try:
                data = response.json()
                if 'plan' in data and data['plan']['key'] == 'free':
                    self.log_result("Subscription Change to Free", True)
                    return True
                else:
                    self.log_result("Subscription Change to Free", False, f"Plan not changed: {data}")
            except Exception as e:
                self.log_result("Subscription Change to Free", False, str(e))
        else:
            self.log_result("Subscription Change to Free", False, f"Status: {response.status_code if hasattr(response, 'status_code') else 'Error'}")
        return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting VitalTrack API Tests...")
        print(f"Backend URL: {self.base_url}")
        print("-" * 50)

        # Authentication
        if not self.test_admin_login():
            print("❌ Cannot proceed without authentication")
            return False

        # Core API tests
        self.test_plans_endpoint()
        self.test_translations_endpoints()
        self.test_razorpay_create_order()
        self.test_shared_reports_creation()
        self.test_shared_reports_view_password()
        self.test_subscription_change_to_free()

        # Summary
        print("-" * 50)
        print(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed tests:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VitalTrackAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())