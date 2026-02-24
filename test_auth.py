#!/usr/bin/env python3
"""
Test Authentication Directly
Quick script to debug authentication issues
"""

import os
import requests
import sys
import subprocess
import shutil
import pytest

# Updated (2026-02-23): Use Ubuntu server IP 10.76.250.89
API_URL = os.getenv("SENTINEL_API_URL", "http://10.76.250.89:8000")

def get_password_from_logs():
    """Extract password from container logs"""
    try:
        if not shutil.which("docker-compose"):
            return None
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
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        assert response.status_code == 200
    except Exception as e:
        pytest.skip(f"API not reachable: {e}")

def test_login(api_ready, username, password):
    """Test login endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            data={"username": username, "password": password},
            timeout=5
        )
        assert response.status_code == 200
        token = response.json().get("token")
        assert token
        return token
    except Exception as e:
        pytest.skip(f"Login failed: {e}")

def test_api_with_token(api_ready, token):
    """Test API call with token"""
    try:
        response = requests.get(
            f"{API_URL}/api/info",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        assert response.status_code == 200
        return response.json()
    except Exception as e:
        pytest.skip(f"Token auth failed: {e}")


@pytest.fixture(scope="session")
def api_ready():
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code != 200:
            pytest.skip(f"API health status {response.status_code}")
        return True
    except Exception as e:
        pytest.skip(f"API not reachable: {e}")


@pytest.fixture(scope="session")
def username():
    return os.getenv("SENTINEL_TEST_USER", "admin")


@pytest.fixture(scope="session")
def password():
    env_password = os.getenv("SENTINEL_TEST_PASS")
    if env_password:
        return env_password
    log_password = get_password_from_logs()
    if log_password:
        return log_password
    pytest.skip("No password available; set SENTINEL_TEST_PASS or run container")


@pytest.fixture(scope="session")
def token(api_ready, username, password):
    return test_login(api_ready, username, password)

def main():
    # Test 1: Health check
    try:
        test_health()
    except pytest.SkipTest as e:
        print(f"\n✗ API is not healthy: {e}")
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
    token = test_login(True, "admin", password)
    
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
    if test_api_with_token(True, token):
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
