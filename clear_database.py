#!/usr/bin/env python3
"""
Clear Database Utility
Safely clears IP records and incidents from Sentinel database

Usage:
    python3 clear_database.py --all           # Clear everything
    python3 clear_database.py --incidents     # Clear incidents only
    python3 clear_database.py --threat-intel  # Clear threat Intel Data only
    python3 clear_database.py --ip 10.0.0.1   # Clear specific IP
    python3 clear_database.py --dry-run       # Preview what would be deleted
"""

import sqlite3
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH", "/app/data/sentinel_intel.db")
if not os.path.exists(os.path.dirname(DEFAULT_DB_PATH) or "."):
    DEFAULT_DB_PATH = "./data/sentinel_intel.db"

class DatabaseCleaner:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.dry_run = False
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at: {self.db_path}")
            sys.exit(1)
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_stats(self):
        """Get database statistics before clearing"""
        self.cursor.execute("SELECT COUNT(*) FROM incidents")
        incidents_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM threat_intel")
        threat_intel_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM actions")
        actions_count = self.cursor.fetchone()[0]
        
        return {
            "incidents": incidents_count,
            "threat_intel": threat_intel_count,
            "actions": actions_count
        }
    
    def get_incidents_by_ip(self, ip: str):
        """Get incident count for specific IP"""
        self.cursor.execute("SELECT COUNT(*) FROM incidents WHERE source_ip = ?", (ip,))
        return self.cursor.fetchone()[0]
    
    def clear_all(self):
        """Clear all data from all tables"""
        stats = self.get_stats()
        
        print(f"\n{'='*60}")
        print("CURRENT DATABASE STATISTICS")
        print(f"{'='*60}")
        print(f"  Incidents: {stats['incidents']}")
        print(f"  Threat Intel IPs: {stats['threat_intel']}")
        print(f"  Actions: {stats['actions']}")
        print(f"  Database: {self.db_path}\n")
        
        if sum(stats.values()) == 0:
            print("✓ Database is already empty")
            return
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete:")
            print(f"  - {stats['incidents']} incident records")
            print(f"  - {stats['threat_intel']} threat intelligence records")
            print(f"  - {stats['actions']} action records")
            return
        
        # Confirm action
        response = input(f"⚠️  Delete ALL data? (yes/no): ").strip().lower()
        if response != "yes":
            print("❌ Cancelled")
            return
        
        try:
            self.cursor.execute("DELETE FROM actions")
            self.cursor.execute("DELETE FROM incidents")
            self.cursor.execute("DELETE FROM threat_intel")
            self.conn.commit()
            
            print(f"✓ Deleted {stats['incidents']} incidents")
            print(f"✓ Deleted {stats['threat_intel']} threat intel records")
            print(f"✓ Deleted {stats['actions']} action records")
            print("✓ Database cleared successfully\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
    
    def clear_incidents(self):
        """Clear incidents table only"""
        stats = self.get_stats()
        
        print(f"\n{'='*60}")
        print("INCIDENT RECORDS")
        print(f"{'='*60}")
        print(f"  Total incidents: {stats['incidents']}\n")
        
        if stats['incidents'] == 0:
            print("✓ No incidents to clear")
            return
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete {stats['incidents']} incident records")
            return
        
        response = input(f"⚠️  Delete ALL {stats['incidents']} incidents? (yes/no): ").strip().lower()
        if response != "yes":
            print("❌ Cancelled")
            return
        
        try:
            # First delete associated actions
            self.cursor.execute("DELETE FROM actions")
            self.cursor.execute("DELETE FROM incidents")
            self.conn.commit()
            
            print(f"✓ Deleted {stats['incidents']} incident records")
            print("✓ Incidents cleared successfully\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
    
    def clear_threat_intel(self):
        """Clear threat intelligence (IP reputation) data"""
        stats = self.get_stats()
        
        print(f"\n{'='*60}")
        print("THREAT INTELLIGENCE DATA")
        print(f"{'='*60}")
        print(f"  Total IPs in threat database: {stats['threat_intel']}\n")
        
        if stats['threat_intel'] == 0:
            print("✓ Threat intelligence database is empty")
            return
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete {stats['threat_intel']} threat intelligence records")
            return
        
        response = input(f"⚠️  Delete ALL {stats['threat_intel']} threat intel records? (yes/no): ").strip().lower()
        if response != "yes":
            print("❌ Cancelled")
            return
        
        try:
            self.cursor.execute("DELETE FROM threat_intel")
            self.conn.commit()
            
            print(f"✓ Deleted {stats['threat_intel']} threat intelligence records")
            print("✓ Threat intelligence cleared successfully\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
    
    def clear_ip(self, ip: str):
        """Clear all records for a specific IP"""
        incident_count = self.get_incidents_by_ip(ip)
        
        print(f"\n{'='*60}")
        print(f"IP: {ip}")
        print(f"{'='*60}")
        print(f"  Incidents: {incident_count}\n")
        
        if incident_count == 0:
            print("  No records found for this IP")
            return
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete {incident_count} incidents for IP {ip}")
            return
        
        response = input(f"⚠️  Delete ALL {incident_count} incidents for IP {ip}? (yes/no): ").strip().lower()
        if response != "yes":
            print("❌ Cancelled")
            return
        
        try:
            # Get incident IDs
            self.cursor.execute("SELECT id FROM incidents WHERE source_ip = ?", (ip,))
            incident_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Delete actions for these incidents
            for incident_id in incident_ids:
                self.cursor.execute("DELETE FROM actions WHERE incident_id = ?", (incident_id,))
            
            # Delete incidents
            self.cursor.execute("DELETE FROM incidents WHERE source_ip = ?", (ip,))
            
            # Delete threat intel entry
            self.cursor.execute("DELETE FROM threat_intel WHERE ip = ?", (ip,))
            
            self.conn.commit()
            
            print(f"✓ Deleted {incident_count} incidents for IP {ip}")
            print("✓ IP cleared successfully\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
    
    def list_top_ips(self, limit: int = 10):
        """List top IPs with most incidents"""
        print(f"\n{'='*60}")
        print("TOP IPs BY INCIDENT COUNT")
        print(f"{'='*60}\n")
        
        try:
            self.cursor.execute("""
                SELECT source_ip, COUNT(*) as count 
                FROM incidents 
                GROUP BY source_ip 
                ORDER BY count DESC 
                LIMIT ?
            """, (limit,))
            
            results = self.cursor.fetchall()
            if not results:
                print("  No incidents found\n")
                return
            
            for ip, count in results:
                print(f"  {ip:20} → {count:3} incidents")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Clear IP records and incidents from Sentinel database",
        epilog="Examples:\n"
               "  python3 clear_database.py --all\n"
               "  python3 clear_database.py --incidents\n"
               "  python3 clear_database.py --ip 10.0.0.1\n"
               "  python3 clear_database.py --list",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--all", action="store_true", help="Clear everything")
    parser.add_argument("--incidents", action="store_true", help="Clear incidents only")
    parser.add_argument("--threat-intel", action="store_true", help="Clear threat intelligence data")
    parser.add_argument("--ip", type=str, help="Clear records for specific IP")
    parser.add_argument("--list", action="store_true", help="List top IPs")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_PATH, help=f"Database path (default: {DEFAULT_DB_PATH})")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be deleted")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.incidents, args.threat_intel, args.ip, args.list]):
        parser.print_help()
        print("\n⚠️  Please specify an action (--all, --incidents, --threat-intel, --ip, or --list)")
        return 1
    
    # Initialize cleaner
    cleaner = DatabaseCleaner(args.db)
    cleaner.dry_run = args.dry_run
    
    if not cleaner.connect():
        return 1
    
    try:
        if args.list:
            cleaner.list_top_ips()
        elif args.all:
            cleaner.clear_all()
        elif args.incidents:
            cleaner.clear_incidents()
        elif args.threat_intel:
            cleaner.clear_threat_intel()
        elif args.ip:
            cleaner.clear_ip(args.ip)
    finally:
        cleaner.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
