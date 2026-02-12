#!/usr/bin/env python3
"""
Sentinel Agent v2.2 - Automated Setup & Testing Tool
Complete automation for password extraction, token generation, and attack testing
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
PASSWORD_FILE = ".sentinel_password"
TOKEN_FILE = ".sentinel_token"
RESULTS_DIR = "test_results"

# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_status(status: str, message: str):
    """Print status message with color"""
    if status == "✓":
        color = Colors.GREEN
    elif status == "✗":
        color = Colors.RED
    elif status == "⏳":
        color = Colors.YELLOW
    else:
        color = Colors.CYAN
    
    print(f"{color}{status} {message}{Colors.RESET}")

def ensure_results_dir():
    """Create results directory if it doesn't exist"""
    Path(RESULTS_DIR).mkdir(exist_ok=True)

def wait_for_container(max_retries: int = 60) -> bool:
    """Wait for container to be healthy (up to 2 minutes)"""
    print_status("⏳", "Waiting for Sentinel Agent to be healthy...")
    print_status("ℹ️", "This may take up to 2 minutes for initial startup...")
    
    for i in range(max_retries):
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "sentinel-agent"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "healthy" in result.stdout.lower():
                print_status("✓", "Container is healthy")
                return True
            
            if (i + 1) % 10 == 0:
                print_status("⏳", f"Attempt {i+1}/{max_retries}...")
        except Exception as e:
            print_status("⏳", f"Checking... ({i+1}/{max_retries})")
        
        time.sleep(2)
    
    print_status("✗", "Container did not become healthy")
    print_status("💡", "Run './diagnose.sh' to check container logs and status")
    return False

def extract_password() -> Optional[str]:
    """Extract password from container logs"""
    print_status("🔑", "Extracting admin password from logs...")
    
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
                # Look for Password line
                for j in range(i, min(i+5, len(lines))):
                    if "Password:" in lines[j]:
                        password = lines[j].split("Password:")[-1].strip()
                        if password:
                            with open(PASSWORD_FILE, 'w') as f:
                                f.write(password)
                            masked = password[:8] + "..." + password[-4:]
                            print_status("✓", f"Password extracted: {masked}")
                            return password
        
        print_status("✗", "Could not find password in logs")
        return None
    
    except Exception as e:
        print_status("✗", f"Error extracting password: {e}")
        return None

def get_api_token(password: str) -> Optional[str]:
    """Authenticate and get API token"""
    print_status("🔐", "Getting API token...")
    
    try:
        for attempt in range(10):
            try:
                # Try form data first (standard method)
                response = requests.post(
                    f"{API_URL}/api/auth/login",
                    data={"username": "admin", "password": password},
                    timeout=5
                )
                
                if response.status_code == 200:
                    token = response.json().get("token")
                    if token:
                        with open(TOKEN_FILE, 'w') as f:
                            f.write(token)
                        masked = token[:20] + "..." if len(token) > 20 else token
                        print_status("✓", f"API token obtained: {masked}")
                        return token
                elif response.status_code == 401:
                    print_status("✗", f"Authentication failed: Invalid credentials")
                    print_status("ℹ️", f"Username: admin, Password: {password[:8]}...{password[-4:]}")
                    return None
                else:
                    print_status("⚠", f"Status {response.status_code}: {response.text[:100]}")
            except requests.exceptions.ConnectionError as e:
                if attempt < 9:
                    print_status("⏳", f"Connection attempt {attempt+1}/10... (API may still be starting)")
                    time.sleep(2)
                    continue
                else:
                    print_status("✗", f"Connection failed: {e}")
            except Exception as e:
                if attempt < 9:
                    print_status("⏳", f"Attempt {attempt+1}/10... ({e})")
                    time.sleep(2)
                    continue
        
        print_status("✗", "Failed to authenticate after all attempts")
        return None
    
    except Exception as e:
        print_status("✗", f"Error getting token: {e}")
        return None

def test_api() -> bool:
    """Test API connectivity"""
    print_status("🧪", "Testing API connectivity...")
    
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status("✓", f"API is healthy (v{data.get('version', '?')})")
            return True
        else:
            print_status("✗", f"API returned status {response.status_code}")
            return False
    except Exception as e:
        print_status("✗", f"API connectivity failed: {e}")
        return False

def get_baseline(token: str) -> Dict[str, Any]:
    """Get baseline metrics"""
    print_status("📊", "Getting baseline metrics...")
    
    try:
        response = requests.get(
            f"{API_URL}/api/metrics/detection",
            headers={"X-API-Key": token},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_events_analyzed", 0)
            threats = data.get("threats_detected", 0)
            print_status("✓", f"Baseline captured ({total} events, {threats} threats)")
            
            # Save to file
            with open(f"{RESULTS_DIR}/baseline_metrics.json", 'w') as f:
                json.dump(data, f, indent=2)
            
            return data
    except Exception as e:
        print_status("✗", f"Error getting baseline: {e}")
    
    return {}

def test_ssh_brute_force(attempts: int = 20) -> bool:
    """Simulate SSH brute force attack"""
    print_status("🚀", f"Running SSH brute force test ({attempts} attempts)...")
    
    try:
        for i in range(attempts):
            subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=1",
                 f"wrong_user_{i}@localhost"],
                capture_output=True,
                timeout=3
            )
            if (i + 1) % 5 == 0:
                print(f"  {i+1}/{attempts} attempts...", end='\r')
        
        print_status("✓", f"SSH brute force test completed ({attempts} attempts)")
        return True
    
    except Exception as e:
        print_status("⚠", f"SSH test error (may be expected): {e}")
        return True

def test_sql_injection() -> bool:
    """Simulate SQL injection attacks"""
    print_status("🚀", "Running SQL injection test...")
    
    try:
        # Check if web server is running
        try:
            requests.get("http://localhost/", timeout=2)
        except Exception:
            print_status("⚠", "Web server not running on localhost:80 (skipping)")
            return False
        
        payloads = [
            "1' OR '1'='1",
            "admin'--",
            "1 UNION SELECT NULL--",
            "' OR 1=1--"
        ]
        
        print_status("ℹ", f"Testing {len(payloads)} SQL injection payloads...")
        
        for payload in payloads:
            try:
                requests.get(
                    f"http://localhost/search?q={payload}",
                    timeout=2
                )
            except Exception:
                pass
        
        print_status("✓", "SQL injection test completed")
        return True
    
    except Exception as e:
        print_status("⚠", f"SQL test error: {e}")
        return False

def test_ddos(requests_count: int = 100) -> bool:
    """Simulate DDoS/rate limit attack"""
    print_status("🚀", f"Running DDoS test ({requests_count} requests)...")
    
    try:
        import concurrent.futures
        
        def make_request(_):
            try:
                requests.get("http://localhost/", timeout=2)
            except Exception:
                pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(make_request, range(requests_count)))
        
        print_status("✓", f"DDoS test completed ({requests_count} requests)")
        return True
    
    except Exception as e:
        print_status("⚠", f"DDoS test error: {e}")
        return False

def check_results(token: str) -> Dict[str, Any]:
    """Check for detected incidents"""
    print_status("📋", "Checking for detected incidents...")
    print_status("⏳", "Waiting 30 seconds for analysis...")
    
    time.sleep(30)
    
    try:
        response = requests.get(
            f"{API_URL}/api/incidents/recent",
            headers={"X-API-Key": token},
            timeout=5
        )
        
        if response.status_code == 200:
            incidents = response.json()
            count = len(incidents) if isinstance(incidents, list) else 0
            
            if count > 0:
                print_status("✓", f"Found {count} incidents")
                
                # Display first 5
                for incident in incidents[:5]:
                    incident_type = incident.get("type", "Unknown")
                    severity = incident.get("severity", "?")
                    source_ip = incident.get("source_ip", "?")
                    print(f"  • {incident_type} ({severity}) from {source_ip}")
                
                # Save results
                with open(f"{RESULTS_DIR}/incidents.json", 'w') as f:
                    json.dump(incidents, f, indent=2)
                
                return {"count": count, "incidents": incidents}
            else:
                print_status("⚠", "No incidents detected yet")
        else:
            print_status("✗", f"API returned status {response.status_code}")
    
    except Exception as e:
        print_status("✗", f"Error checking incidents: {e}")
    
    return {}

def show_dashboard(token: str):
    """Display status dashboard"""
    print_header("Sentinel Agent Status Dashboard")
    
    try:
        # Health
        print(f"{Colors.YELLOW}System Health:{Colors.RESET}")
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"  Status: {health.get('status', '?')}")
            print(f"  Version: {health.get('version', '?')}")
            print(f"  Uptime: {health.get('uptime_seconds', 0)}s")
        
        # Metrics
        print(f"\n{Colors.YELLOW}Detection Metrics:{Colors.RESET}")
        response = requests.get(
            f"{API_URL}/api/metrics/detection",
            headers={"X-API-Key": token},
            timeout=5
        )
        if response.status_code == 200:
            metrics = response.json()
            print(f"  Total Events: {metrics.get('total_events_analyzed', 0)}")
            print(f"  Threats Detected: {metrics.get('threats_detected', 0)}")
            print(f"  Detection Rate: {metrics.get('detection_rate', 0):.1%}")
        
        # Recent Incidents
        print(f"\n{Colors.YELLOW}Recent Incidents:{Colors.RESET}")
        response = requests.get(
            f"{API_URL}/api/incidents/recent",
            headers={"X-API-Key": token},
            timeout=5
        )
        if response.status_code == 200:
            incidents = response.json()
            if incidents:
                for incident in incidents[:3]:
                    print(f"  • {incident.get('type')} ({incident.get('severity')})")
            else:
                print("  No incidents")
        
        # IP Lists
        print(f"\n{Colors.YELLOW}IP Lists:{Colors.RESET}")
        response = requests.get(
            f"{API_URL}/api/lists/summary",
            headers={"X-API-Key": token},
            timeout=5
        )
        if response.status_code == 200:
            lists = response.json()
            print(f"  Whitelisted: {lists.get('whitelisted_count', 0)}")
            print(f"  Blacklisted: {lists.get('blacklisted_count', 0)}")
    
    except Exception as e:
        print_status("✗", f"Error loading dashboard: {e}")

def run_setup():
    """Run complete setup"""
    print_header("Sentinel Agent - Complete Setup")
    
    ensure_results_dir()
    
    if not wait_for_container():
        return False
    
    if not test_api():
        return False
    
    password = extract_password()
    if not password:
        return False
    
    token = get_api_token(password)
    if not token:
        return False
    
    get_baseline(token)
    
    print_status("✓", "Setup complete!")
    print(f"\n{Colors.CYAN}Next: python3 sentinel_auto.py demo{Colors.RESET}\n")
    return True

def run_demo(token: str):
    """Run automated demo with all tests"""
    print_header("Run Automated Detection Demo")
    
    ensure_results_dir()
    
    print_status("ℹ", "Getting baseline metrics...")
    get_baseline(token)
    
    print_status("ℹ", "Running attacks (this will take a few minutes)...")
    test_ssh_brute_force(15)
    test_sql_injection()
    test_ddos(50)
    
    print_status("ℹ", "Waiting for analysis and checking results...")
    results = check_results(token)
    
    if results:
        print_status("✓", f"Demo complete! Detected {results.get('count', 0)} incidents")
    else:
        print_status("⚠", "Demo complete but no incidents detected")
    
    print(f"\n{Colors.CYAN}View dashboard: python3 sentinel_auto.py status{Colors.RESET}\n")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        command = "help"
    else:
        command = sys.argv[1]
    
    # Commands that don't need token
    if command == "setup":
        return run_setup()
    
    elif command == "password":
        extract_password()
        return True
    
    elif command == "test-api":
        return test_api()
    
    elif command == "help":
        print(f"""
{Colors.BLUE}{Colors.BOLD}Sentinel Agent v2.2 - Automated Setup & Testing{Colors.RESET}

{Colors.YELLOW}USAGE:{Colors.RESET}
  python3 sentinel_auto.py [COMMAND]

{Colors.YELLOW}COMMANDS:{Colors.RESET}
  setup              Complete setup (password + token)
  password           Extract admin password
  test-api           Test API connectivity
  demo               Run full detection demo
  status             Show system dashboard
  test-ssh           Run SSH brute force test
  test-sql           Run SQL injection test
  test-ddos          Run DDoS test
  check              Check for incidents
  help               Show this message

{Colors.YELLOW}QUICK START:{Colors.RESET}
  1. python3 sentinel_auto.py setup
  2. python3 sentinel_auto.py demo
  3. python3 sentinel_auto.py status

{Colors.YELLOW}FILES CREATED:{Colors.RESET}
  .sentinel_password       - Admin password
  .sentinel_token          - API token
  test_results/            - All test results and metrics

{Colors.YELLOW}REQUIREMENTS:{Colors.RESET}
  - Sentinel Agent running (docker-compose up -d)
  - Python 3.7+
  - requests library (pip install requests)

{Colors.CYAN}Home: http://localhost:8000
Docs: http://localhost:8000/docs{Colors.RESET}
""")
        return True
    
    # Commands that need token
    token_file = TOKEN_FILE
    if not os.path.exists(token_file):
        print_status("✗", f"Token file not found. Run: python3 sentinel_auto.py setup")
        return False
    
    with open(token_file, 'r') as f:
        token = f.read().strip()
    
    if command == "demo":
        run_demo(token)
    elif command == "status":
        show_dashboard(token)
    elif command == "test-ssh":
        test_ssh_brute_force()
        print(f"\n{Colors.CYAN}Check results: python3 sentinel_auto.py check{Colors.RESET}\n")
    elif command == "test-sql":
        test_sql_injection()
        print(f"\n{Colors.CYAN}Check results: python3 sentinel_auto.py check{Colors.RESET}\n")
    elif command == "test-ddos":
        test_ddos()
        print(f"\n{Colors.CYAN}Check results: python3 sentinel_auto.py check{Colors.RESET}\n")
    elif command == "check":
        check_results(token)
    else:
        print_status("✗", f"Unknown command: {command}")
        print(f"{Colors.CYAN}Run: python3 sentinel_auto.py help{Colors.RESET}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
