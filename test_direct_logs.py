#!/usr/bin/env python3
"""
Direct Log Writer for Sentinel Agent Testing
Writes attack logs directly to files monitored by Sentinel Agent
Designed to work both inside and outside Docker

Usage:
    python3 test_direct_logs.py              # Auto-detect environment
    python3 test_direct_logs.py --local      # Force local logs
    python3 test_direct_logs.py --docker     # Force Docker logs
"""

import os
import sys
import time
import random
import argparse
from datetime import datetime
from pathlib import Path

# Attack scenarios
ATTACKING_IPS = [
    "203.0.113.45",
    "198.51.100.12", 
    "192.0.2.88",
    "10.76.250.150",
    "10.76.250.151",
    "10.76.250.152",
]

def is_docker():
    """Detect if running in Docker."""
    return os.path.exists("/.dockerenv")

def get_log_target(force_env=None):
    """Determine where to write logs."""
    if force_env == "docker":
        return "/app/logs"
    elif force_env == "local":
        return "./logs"
    
    # Auto-detect
    if is_docker():
        return "/app/logs"
    return "./logs"

def generate_auth_attack_log(target_dir, count=10):
    """Generate simulated auth log attacks."""
    log_path = Path(target_dir) / "auth.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    auth_patterns = [
        "Failed password for root from {ip} port 22 ssh2",
        "Invalid user admin from {ip} port 22",
        "Failed password for invalid user test from {ip} port 22 ssh2",
        "authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost={ip}  user=root",
    ]
    
    print(f"\n📝 Writing {count} auth log entries to {log_path}")
    
    with open(log_path, 'a') as f:
        for i in range(count):
            ip = random.choice(ATTACKING_IPS)
            timestamp = datetime.now().strftime("%b %d %H:%M:%S")
            pattern = random.choice(auth_patterns)
            
            log_entry = f"{timestamp} sentinel-agent sshd[{1000+i}]: {pattern.format(ip=ip)}\n"
            f.write(log_entry)
            
            print(f"  [{i+1}/{count}] {ip} - auth attempt")
            time.sleep(0.1)
    
    print(f"✅ Wrote {count} auth log entries")
    return count

def generate_web_attack_log(target_dir, count=10):
    """Generate simulated web log attacks."""
    log_path = Path(target_dir) / "access.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    web_patterns = [
        '{ip} - - [{timestamp}] "GET /admin HTTP/1.1" 401',
        '{ip} - - [{timestamp}] "POST /api/login HTTP/1.1" 400',
        '{ip} - - [{timestamp}] "GET /../../etc/passwd HTTP/1.1" 400',
        "{ip} - - [{timestamp}] 'GET /?id=1' UNION SELECT" ,
        '{ip} - - [{timestamp}] "GET /<script>alert(1)</script> HTTP/1.1" 400',
    ]
    
    print(f"\n📝 Writing {count} web log entries to {log_path}")
    
    with open(log_path, 'a') as f:
        for i in range(count):
            ip = random.choice(ATTACKING_IPS)
            timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
            pattern = random.choice(web_patterns)
            
            log_entry = pattern.format(ip=ip, timestamp=timestamp) + "\n"
            f.write(log_entry)
            
            print(f"  [{i+1}/{count}] {ip} - web attack")
            time.sleep(0.1)
    
    print(f"✅ Wrote {count} web log entries")
    return count

def main():
    parser = argparse.ArgumentParser(description="Generate attack logs for Sentinel testing")
    parser.add_argument("--local", action="store_true", help="Force write to local ./logs")
    parser.add_argument("--docker", action="store_true", help="Force write to /app/logs")
    parser.add_argument("--auth-count", type=int, default=10, help="Number of auth attacks")
    parser.add_argument("--web-count", type=int, default=10, help="Number of web attacks")
    
    args = parser.parse_args()
    
    # Determine environment
    force_env = None
    if args.docker:
        force_env = "docker"
    elif args.local:
        force_env = "local"
    
    target_dir = get_log_target(force_env)
    
    print("=" * 70)
    print("  SENTINEL AGENT - DIRECT LOG GENERATOR")
    print("=" * 70)
    print(f"\n📍 Environment: {'Docker' if force_env == 'docker' else 'Local' if force_env == 'local' else 'Auto-detected'}")
    print(f"📁 Log target: {target_dir}")
    print(f"🎯 Attacking IPs: {ATTACKING_IPS}")
    
    try:
        auth_count = generate_auth_attack_log(target_dir, args.auth_count)
        web_count = generate_web_attack_log(target_dir, args.web_count)
        
        total = auth_count + web_count
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS! Generated {total} total attack logs")
        print(f"{'='*70}\n")
        
        print("📊 Next steps:")
        print(f"  1. Monitor Sentinel Agent logs:")
        print(f"     docker-compose logs -f sentinel-agent | grep -E 'detected|blocked'")
        print(f"  2. Check incidents database:")
        print(f"     docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \\")
        print(f'       "SELECT COUNT(*) FROM incidents;"')
        print(f"  3. Check blocked IPs:")
        print(f"     docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \\")
        print(f'       "SELECT ip, banned_until FROM blocked_ips WHERE status=\'active\';"')
        print(f"  4. Check whitelisted IPs:")
        print(f"     docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \\")
        print(f'       "SELECT ip, reason FROM safe_ips LIMIT 5;"')
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
