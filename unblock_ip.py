#!/usr/bin/env python3
"""
Sentinel Agent - IP Unblock Utility
Removes blocked IPs from iptables, database, and adds to whitelist.
Run this when you need to unblock a development IP that was flagged as brute_force.

Usage:
    python3 unblock_ip.py --ip 192.168.31.186
    python3 unblock_ip.py --ip 192.168.31.186 --whitelist
    python3 unblock_ip.py --ip 192.168.31.186 --reason "Development machine"
"""

import sqlite3
import subprocess
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database paths
DATA_DIR = os.getenv("SENTINEL_DATA_DIR", "/app/data")
INTEL_DB = os.path.join(DATA_DIR, "sentinel_intel.db")
LISTS_DB = os.path.join(DATA_DIR, "lists.db")


def check_permissions():
    """Check if running with sudo for iptables operations."""
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        logger.warning("Some operations require root access. Use: sudo python3 unblock_ip.py")
        return False
    return True


def remove_iptables_rule(ip: str) -> bool:
    """Remove iptables DROP rule for IP."""
    try:
        logger.info(f"Attempting to remove iptables rule for {ip}...")
        
        # Check if rule exists
        result = subprocess.run(
            ["iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.info(f"No iptables rule found for {ip}")
            return True
        
        # Remove the rule
        logger.info(f"Found iptables rule, removing...")
        result = subprocess.run(
            ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully removed iptables rule for {ip}")
            return True
        else:
            logger.error(f"❌ Failed to remove iptables rule: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error removing iptables rule: {e}")
        return False


def remove_from_incidents(ip: str) -> bool:
    """Remove entries for IP from incidents table."""
    try:
        logger.info(f"Removing incidents for {ip} from database...")
        conn = sqlite3.connect(INTEL_DB)
        cursor = conn.cursor()
        
        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE source_ip = ?", (ip,))
        count_before = cursor.fetchone()[0]
        
        # Delete incidents
        cursor.execute("DELETE FROM incidents WHERE source_ip = ?", (ip,))
        conn.commit()
        
        count_deleted = count_before
        logger.info(f"✅ Deleted {count_deleted} incident(s) for {ip}")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            logger.info(f"Incidents table not found or not initialized yet")
            return True
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error removing incidents: {e}")
        return False


def add_to_whitelist(ip: str, reason: str = "") -> bool:
    """Add IP to whitelist."""
    try:
        logger.info(f"Adding {ip} to IP whitelist...")
        
        # Ensure lists database exists
        if not os.path.exists(LISTS_DB):
            logger.warning(f"Lists database not found at {LISTS_DB}, skipping whitelist add")
            return True
        
        conn = sqlite3.connect(LISTS_DB)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ip_whitelist'")
        if not cursor.fetchone():
            logger.info("ip_whitelist table not found, skipping")
            conn.close()
            return True
        
        # Add to whitelist
        default_reason = reason or f"Unblocked development IP - {datetime.now().isoformat()}"
        cursor.execute("""
            INSERT OR REPLACE INTO ip_whitelist (ip, reason, added_by, added_date)
            VALUES (?, ?, ?, ?)
        """, (ip, default_reason, "unblock_utility", datetime.now().isoformat()))
        
        conn.commit()
        logger.info(f"✅ Added {ip} to whitelist with reason: {default_reason}")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            logger.info("Whitelist table not initialized yet")
            return True
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error adding to whitelist: {e}")
        return False


def get_blocked_ips() -> list:
    """Get list of currently blocking IPs from iptables."""
    try:
        result = subprocess.run(
            ["iptables", "-L", "INPUT", "-v", "-n"],
            capture_output=True,
            text=True
        )
        
        blocked_ips = []
        for line in result.stdout.split('\n'):
            if "DROP" in line and "192.168." in line:
                # Parse IP from iptables output
                parts = line.split()
                for part in parts:
                    if "192.168." in part or "10." in part:
                        blocked_ips.append(part)
        
        return list(set(blocked_ips))  # Remove duplicates
        
    except Exception as e:
        logger.error(f"Error reading iptables: {e}")
        return []


def get_incident_ips() -> dict:
    """Get IPs from incidents table marked as brute_force."""
    try:
        conn = sqlite3.connect(INTEL_DB)
        cursor = conn.cursor()
        
        # Get brute_force incidents
        cursor.execute("""
            SELECT source_ip, COUNT(*) as count, MAX(timestamp) as last_seen
            FROM incidents
            WHERE attack_type='brute_force' OR threat_type='brute_force'
            GROUP BY source_ip
            ORDER BY count DESC
        """)
        
        results = {}
        for row in cursor.fetchall():
            ip, count, last_seen = row
            results[ip] = {"count": count, "last_seen": last_seen}
        
        conn.close()
        return results
        
    except Exception as e:
        logger.error(f"Error querying incidents: {e}")
        return {}


def show_status(ip: str):
    """Show blocking status of an IP."""
    print("\n" + "="*60)
    print("IP BLOCKING STATUS")
    print("="*60)
    
    # Check iptables
    try:
        result = subprocess.run(
            ["iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ iptables: BLOCKED (DROP rule exists)")
        else:
            print(f"✓ iptables: NOT BLOCKED")
    except Exception:
        print(f"✓ iptables: Could not verify (requires root)")
    
    # Check incidents
    incident_ips = get_incident_ips()
    if ip in incident_ips:
        info = incident_ips[ip]
        print(f"✓ incidents: BLOCKED ({info['count']} attempts, last: {info['last_seen']})")
    else:
        print(f"✓ incidents: NOT FOUND")
    
    # Check whitelist
    try:
        conn = sqlite3.connect(LISTS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT reason FROM ip_whitelist WHERE ip = ?", (ip,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"✓ whitelist: WHITELISTED ({result[0]})")
        else:
            print(f"✓ whitelist: NOT WHITELISTED")
    except Exception:
        print(f"✓ whitelist: Could not verify")
    
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Unblock IPs blocked by Sentinel Agent security system"
    )
    parser.add_argument("--ip", required=True, help="IP address to unblock (e.g., 192.168.31.186)")
    parser.add_argument("--whitelist", action="store_true", help="Add to whitelist after unblocking")
    parser.add_argument("--reason", help="Reason for whitelisting")
    parser.add_argument("--status", action="store_true", help="Show blocking status only")
    parser.add_argument("--list-blocked", action="store_true", help="List all currently blocked IPs")
    
    args = parser.parse_args()
    
    # Validate IP format
    parts = args.ip.split('.')
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        logger.error(f"Invalid IP address format: {args.ip}")
        sys.exit(1)
    
    # Show status only
    if args.status:
        show_status(args.ip)
        return
    
    # List all blocked IPs
    if args.list_blocked:
        print("\n📋 Currently Blocked IPs (iptables):")
        blocked = get_blocked_ips()
        if blocked:
            for ip in blocked:
                print(f"  - {ip}")
        else:
            print("  (None found)")
        
        print("\n📋 Brute Force Attack IPs (database):")
        incident_ips = get_incident_ips()
        if incident_ips:
            for ip, info in incident_ips.items():
                print(f"  - {ip} ({info['count']} attempts)")
        else:
            print("  (None found)")
        return
    
    # Check if we need root
    needs_root = True
    if not check_permissions() and needs_root:
        logger.info("\nTo remove iptables rules, run with sudo:")
        logger.info(f"  sudo python3 unblock_ip.py --ip {args.ip}")
        # Continue anyway - can still do database cleanup
        logger.info("Continuing with database operations...\n")
    
    print(f"\n🔓 UNBLOCKING IP: {args.ip}")
    print("="*60 + "\n")
    
    # Step 1: Show current status
    show_status(args.ip)
    
    # Step 2: Remove iptables rule
    if os.geteuid() == 0:
        remove_iptables_rule(args.ip)
    else:
        logger.warning("Skipping iptables removal (requires root)")
    
    # Step 3: Remove from incidents
    remove_from_incidents(args.ip)
    
    # Step 4: Add to whitelist
    if args.whitelist or args.reason:
        add_to_whitelist(args.ip, args.reason)
    
    # Step 5: Show final status
    print("\n✅ UNBLOCK COMPLETE\n")
    show_status(args.ip)
    
    print("ℹ️  Next steps:")
    print(f"  1. If on a systemd system: sudo systemctl restart sentinel-agent")
    print(f"  2. Or with Docker: docker-compose restart sentinel-agent")
    print(f"  3. Try accessing dashboard: http://192.168.31.91:8501")


if __name__ == "__main__":
    main()
