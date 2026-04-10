#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class VitalTrackAPITester:
    def __init__(self, base_url: str = "https://wellness-log-105.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        
    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, use_admin: bool = False) -> tuple[bool, Any]:
        """Make API request and validate response"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                return False, f"Unsupported method: {method}"
            
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            return success, response_data
            
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test user registration
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        register_data = {
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        }
        
        success, response = self.make_request('POST', 'auth/register', register_data, 200)
        self.log_test("User Registration", success, 
                     "" if success else f"Failed: {response}", response)
        
        if success:
            self.test_user_id = response.get('id')
        
        # Test user login
        login_data = {
            "email": test_email,
            "password": "testpass123"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, 200)
        self.log_test("User Login", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test admin login
        admin_login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        success, response = self.make_request('POST', 'auth/login', admin_login_data, 200)
        self.log_test("Admin Login", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test /auth/me endpoint
        success, response = self.make_request('GET', 'auth/me', expected_status=200)
        self.log_test("Get Current User", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test logout
        success, response = self.make_request('POST', 'auth/logout', expected_status=200)
        self.log_test("User Logout", success, 
                     "" if success else f"Failed: {response}", response)
    
    def test_vitals_endpoints(self):
        """Test vitals management endpoints"""
        print("\n💓 Testing Vitals Endpoints...")
        
        # Re-login for subsequent tests
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        self.make_request('POST', 'auth/login', login_data, 200)
        
        # Test get vital types
        success, response = self.make_request('GET', 'vitals/types', expected_status=200)
        self.log_test("Get Vital Types", success, 
                     "" if success else f"Failed: {response}", response)
        
        if success and isinstance(response, list):
            vital_count = len(response)
            self.log_test(f"Vital Types Count (Expected: 12)", vital_count == 12, 
                         f"Got {vital_count} vitals" if vital_count != 12 else "")
        
        # Test get enabled vitals
        success, response = self.make_request('GET', 'vitals/enabled', expected_status=200)
        self.log_test("Get Enabled Vitals", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test toggle vital (enable)
        toggle_data = {
            "vital_key": "blood_glucose",
            "enabled": True
        }
        success, response = self.make_request('POST', 'vitals/toggle', toggle_data, 200)
        self.log_test("Enable Vital", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test toggle vital (disable)
        toggle_data["enabled"] = False
        success, response = self.make_request('POST', 'vitals/toggle', toggle_data, 200)
        self.log_test("Disable Vital", success, 
                     "" if success else f"Failed: {response}", response)
    
    def test_entries_endpoints(self):
        """Test data entry endpoints"""
        print("\n📊 Testing Entry Endpoints...")
        
        # Enable a vital first
        toggle_data = {
            "vital_key": "blood_glucose",
            "enabled": True
        }
        self.make_request('POST', 'vitals/toggle', toggle_data, 200)
        
        # Test create entry
        today = datetime.now().strftime('%Y-%m-%d')
        entry_data = {
            "vital_key": "blood_glucose",
            "date": today,
            "value": 95.5,
            "notes": "Morning reading"
        }
        
        success, response = self.make_request('POST', 'entries', entry_data, 200)
        self.log_test("Create Entry", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test get entries
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        success, response = self.make_request('GET', f'entries?start_date={week_ago}&end_date={today}', expected_status=200)
        self.log_test("Get Entries", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test bulk entries
        bulk_data = {
            "entries": [
                {
                    "vital_key": "blood_glucose",
                    "date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    "value": 88.0
                },
                {
                    "vital_key": "blood_glucose", 
                    "date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "value": 92.5
                }
            ]
        }
        
        success, response = self.make_request('POST', 'entries/bulk', bulk_data, 200)
        self.log_test("Bulk Create Entries", success, 
                     "" if success else f"Failed: {response}", response)
    
    def test_charts_endpoints(self):
        """Test charts and analytics endpoints"""
        print("\n📈 Testing Charts Endpoints...")
        
        # Test get chart data
        today = datetime.now().strftime('%Y-%m-%d')
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        success, response = self.make_request('GET', f'charts/blood_glucose?start_date={week_ago}&end_date={today}', expected_status=200)
        self.log_test("Get Chart Data", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test insights
        success, response = self.make_request('GET', 'insights', expected_status=200)
        self.log_test("Get Insights", success, 
                     "" if success else f"Failed: {response}", response)
    
    def test_plans_endpoints(self):
        """Test subscription plans endpoints"""
        print("\n💳 Testing Plans Endpoints...")
        
        # Test get plans
        success, response = self.make_request('GET', 'plans', expected_status=200)
        self.log_test("Get Plans", success, 
                     "" if success else f"Failed: {response}", response)
        
        if success and isinstance(response, list):
            plan_count = len(response)
            self.log_test(f"Plans Count (Expected: 3)", plan_count == 3, 
                         f"Got {plan_count} plans" if plan_count != 3 else "")
        
        # Test get subscription
        success, response = self.make_request('GET', 'subscription', expected_status=200)
        self.log_test("Get Subscription", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test change subscription (mocked)
        change_data = {
            "plan_key": "standard"
        }
        success, response = self.make_request('POST', 'subscription/change', change_data, 200)
        self.log_test("Change Subscription (MOCKED)", success, 
                     "" if success else f"Failed: {response}", response)
    
    def test_exports_endpoints(self):
        """Test export functionality"""
        print("\n📄 Testing Export Endpoints...")
        
        # Test CSV export
        export_data = {
            "vital_keys": ["blood_glucose"],
            "start_date": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d'),
            "format": "csv"
        }
        
        # Note: This endpoint returns a file, so we expect different handling
        url = f"{self.base_url}/api/exports/generate"
        try:
            response = self.session.post(url, json=export_data)
            success = response.status_code == 200 and 'text/csv' in response.headers.get('content-type', '')
            self.log_test("CSV Export", success, 
                         "" if success else f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
        except Exception as e:
            self.log_test("CSV Export", False, f"Request failed: {str(e)}")
    
    def test_admin_endpoints(self):
        """Test admin panel endpoints"""
        print("\n👑 Testing Admin Endpoints...")
        
        # Test admin dashboard
        success, response = self.make_request('GET', 'admin/dashboard', expected_status=200)
        self.log_test("Admin Dashboard", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test admin users list
        success, response = self.make_request('GET', 'admin/users?limit=10', expected_status=200)
        self.log_test("Admin Users List", success, 
                     "" if success else f"Failed: {response}", response)
        
        # Test admin analytics
        success, response = self.make_request('GET', 'admin/analytics', expected_status=200)
        self.log_test("Admin Analytics", success, 
                     "" if success else f"Failed: {response}", response)
    
    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting VitalTrack API Test Suite...")
        print(f"Testing against: {self.base_url}")
        
        try:
            self.test_auth_endpoints()
            self.test_vitals_endpoints()
            self.test_entries_endpoints()
            self.test_charts_endpoints()
            self.test_plans_endpoints()
            self.test_exports_endpoints()
            self.test_admin_endpoints()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
            return False
        
        # Print summary
        print(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate < 80:
            print("⚠️  Warning: Low success rate detected")
            return False
        
        return success_rate >= 80

def main():
    tester = VitalTrackAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_api_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'test_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())