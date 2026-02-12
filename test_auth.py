#!/usr/bin/env python3
"""
Test Authentication Directly
Quick script to debug authentication issues
"""

import requests
import sys
import subprocess

API_URL = "http://localhost:8000"

def get_password_from_logs():
    """Extract password from container logs"""
    try:
        result = subprocess.run(
            ["docker-compose", "logs", "sentinel-agent"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if "DEFAULT ADMIN CREDENTIALS" in line:
                for j in range(i, min(i+5, len(lines))):
                    if "Password:" in lines[j]:
                        password = lines[j].split("Password:")[-1].strip()
                        return password
        return None
    except Exception as e:
        print(f"Error extracting password: {e}")
        return None

def test_health():
    """Test API health"""
    print("=" * 60)
    print("Testing API Health...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login(username, password):
    """Test login endpoint"""
    print("\n" + "=" * 60)
    print("Testing Login...")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print()
    
    # Method 1: Form data
    print("Method 1: Form Data")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            data={"username": username, "password": password},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✓ Form data authentication SUCCESSFUL!")
            token = response.json().get("token")
            print(f"Token: {token[:30]}...")
            return token
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 2: JSON data
    print("\nMethod 2: JSON Data")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login-json",
            json={"username": username, "password": password},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✓ JSON authentication SUCCESSFUL!")
            token = response.json().get("token")
            print(f"Token: {token[:30]}...")
            return token
    except Exception as e:
        print(f"Error: {e}")
    
    # Method 3: Query parameters
    print("\nMethod 3: Query Parameters")
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login?username={username}&password={password}",
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✓ Query param authentication SUCCESSFUL!")
            token = response.json().get("token")
            print(f"Token: {token[:30]}...")
            return token
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_api_with_token(token):
    """Test API call with token"""
    print("\n" + "=" * 60)
    print("Testing API with Token...")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_URL}/api/info",
            headers={"X-API-Key": token},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    # Test 1: Health check
    if not test_health():
        print("\n✗ API is not healthy! Make sure container is running.")
        print("Run: docker-compose ps")
        sys.exit(1)
    
    # Test 2: Extract password
    print("\n" + "=" * 60)
    print("Extracting Password from Logs...")
    print("=" * 60)
    
    password = get_password_from_logs()
    if not password:
        print("✗ Could not extract password from logs")
        print("\nManually check logs:")
        print("  docker-compose logs sentinel-agent | grep -A 3 'DEFAULT ADMIN CREDENTIALS'")
        sys.exit(1)
    
    print(f"✓ Password extracted: {password}")
    
    # Test 3: Login
    token = test_login("admin", password)
    
    if not token:
        print("\n" + "=" * 60)
        print("✗ Authentication FAILED")
        print("=" * 60)
        print("\nTroubleshooting steps:")
        print("1. Check container logs:")
        print("   docker-compose logs sentinel-agent")
        print("2. Verify database was initialized:")
        print("   docker exec sentinel-agent ls -la /app/data/")
        print("3. Try restarting container:")
        print("   docker-compose restart sentinel-agent")
        sys.exit(1)
    
    # Test 4: Use token
    if test_api_with_token(token):
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\nYour API token: {token}")
        print(f"\nSave this token to .sentinel_token file:")
        print(f"  echo '{token}' > .sentinel_token")
    else:
        print("\n✗ Token authentication failed")

if __name__ == "__main__":
    main()
