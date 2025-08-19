#!/usr/bin/env python3
"""
Test script for authentication API endpoints
Tests signup, login, profile, and token-protected endpoints
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Base URL for the API
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8892")

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def make_request(method, endpoint, data=None, headers=None, expected_status=None):
    """Make HTTP request and handle response"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n--- {method.upper()} {url} ---")
    
    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response (text): {response.text}")
            response_data = {"error": "Invalid JSON response"}
        
        if expected_status and response.status_code != expected_status:
            print(f"⚠️ WARNING: Expected status {expected_status}, got {response.status_code}")
        
        return response.status_code, response_data
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None, {"error": str(e)}

def test_authentication_flow():
    """Test complete authentication flow"""
    print_section("AUTHENTICATION API TEST")
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Test started at: {datetime.now()}")
    
    # Test data
    test_user = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    auth_token = None
    
    print_section("1. HEALTH CHECK")
    status, response = make_request("GET", "/health", expected_status=200)
    if status != 200:
        print("❌ Health check failed! API may not be running.")
        return
    
    print_section("2. USER SIGNUP")
    status, response = make_request("POST", "/auth/signup", test_user, expected_status=201)
    
    if status == 201 and "access_token" in response:
        auth_token = response["access_token"]
        print(f"✅ Signup successful! Token: {auth_token[:20]}...")
        print(f"User ID: {response.get('user', {}).get('id')}")
        print(f"Username: {response.get('user', {}).get('username')}")
    else:
        print("❌ Signup failed!")
        if status == 400:
            print("This might be because the user already exists. Trying login...")
        else:
            return
    
    print_section("3. USER LOGIN")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    status, response = make_request("POST", "/auth/login", login_data, expected_status=200)
    
    if status == 200 and "access_token" in response:
        auth_token = response["access_token"]
        print(f"✅ Login successful! Token: {auth_token[:20]}...")
        user_data = response.get('user', {})
        print(f"User ID: {user_data.get('id')}")
        print(f"Username: {user_data.get('username')}")
        print(f"Email: {user_data.get('email')}")
        print(f"Active: {user_data.get('is_active')}")
    else:
        print("❌ Login failed!")
        return
    
    print_section("4. GET PROFILE (Protected Endpoint)")
    headers = {"Authorization": f"Bearer {auth_token}"}
    status, response = make_request("GET", "/auth/profile", headers=headers, expected_status=200)
    
    if status == 200:
        print("✅ Profile retrieval successful!")
        print(f"Username: {response.get('username')}")
        print(f"Email: {response.get('email')}")
        print(f"Full Name: {response.get('first_name')} {response.get('last_name')}")
    else:
        print("❌ Profile retrieval failed!")
    
    print_section("5. UPDATE PROFILE")
    update_data = {
        "first_name": "Updated",
        "last_name": "TestUser"
    }
    status, response = make_request("PUT", "/auth/profile", update_data, headers, expected_status=200)
    
    if status == 200:
        print("✅ Profile update successful!")
        print(f"Updated Name: {response.get('first_name')} {response.get('last_name')}")
    else:
        print("❌ Profile update failed!")
    
    print_section("6. CHANGE PASSWORD")
    password_data = {
        "current_password": test_user["password"],
        "new_password": "newpassword123"
    }
    status, response = make_request("POST", "/auth/change-password", password_data, headers, expected_status=200)
    
    if status == 200:
        print("✅ Password change successful!")
        print(f"Message: {response.get('message')}")
    else:
        print("❌ Password change failed!")
    
    print_section("7. LOGIN WITH NEW PASSWORD")
    new_login_data = {
        "username": test_user["username"],
        "password": "newpassword123"
    }
    status, response = make_request("POST", "/auth/login", new_login_data, expected_status=200)
    
    if status == 200:
        print("✅ Login with new password successful!")
        new_token = response["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}
    else:
        print("❌ Login with new password failed!")
    
    print_section("8. REFRESH TOKEN")
    status, response = make_request("POST", "/auth/refresh-token", headers=headers, expected_status=200)
    
    if status == 200:
        print("✅ Token refresh successful!")
        print(f"New Token: {response.get('access_token', '')[:20]}...")
    else:
        print("❌ Token refresh failed!")
    
    print_section("9. UNAUTHORIZED ACCESS TEST")
    print("Testing endpoint without token...")
    status, response = make_request("GET", "/auth/profile", expected_status=401)
    
    if status == 401:
        print("✅ Unauthorized access properly blocked!")
    else:
        print("❌ Unauthorized access should have been blocked!")
    
    print_section("10. INVALID TOKEN TEST")
    print("Testing endpoint with invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    status, response = make_request("GET", "/auth/profile", headers=invalid_headers, expected_status=401)
    
    if status == 401:
        print("✅ Invalid token properly rejected!")
    else:
        print("❌ Invalid token should have been rejected!")
    
    print_section("TEST SUMMARY")
    print("✅ Authentication API test completed!")
    print(f"Test finished at: {datetime.now()}")
    print("\n📝 Available endpoints:")
    print("   POST /auth/signup       - User registration")
    print("   POST /auth/login        - User login")
    print("   GET  /auth/profile      - Get user profile (protected)")
    print("   PUT  /auth/profile      - Update user profile (protected)")
    print("   POST /auth/change-password - Change password (protected)")
    print("   POST /auth/refresh-token   - Refresh access token (protected)")
    print("\n🔐 All endpoints use JWT Bearer token authentication")
    print("🛡️ Protected endpoints require Authorization: Bearer <token> header")

if __name__ == "__main__":
    test_authentication_flow()