"""
Sentinel Agent Setup Verification Script
Verifies all components are properly initialized and working
"""

import os
import sqlite3
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SetupVerifier:
    """Verifies Sentinel Agent setup"""
    
    def __init__(self):
        self.data_dir = os.getenv("SENTINEL_DATA_DIR", "/app/data")
        self.issues = []
        self.successes = []
    
    def verify_data_directory(self):
        """Verify data directory exists and is writable"""
        logger.info("Checking data directory...")
        
        try:
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)
            test_file = Path(self.data_dir) / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            self.successes.append(f"✓ Data directory exists and is writable: {self.data_dir}")
        except Exception as e:
            self.issues.append(f"✗ Data directory issue: {e}")
    
    def verify_database(self, db_path: str, expected_tables: list):
        """Verify database and its tables"""
        logger.info(f"Checking database: {db_path}")
        
        db_name = Path(db_path).name
        
        if not Path(db_path).exists():
            self.issues.append(f"✗ Database not found: {db_name}")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get existing tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            # Check for expected tables
            missing_tables = set(expected_tables) - existing_tables
            if missing_tables:
                self.issues.append(f"✗ {db_name}: Missing tables: {missing_tables}")
                conn.close()
                return False
            
            # Verify incidents table schema (if it exists)
            if "incidents" in existing_tables:
                cursor.execute("PRAGMA table_info(incidents)")
                columns = {row[1] for row in cursor.fetchall()}
                required_cols = {"id", "timestamp", "source_ip", "attack_type", "severity", "raw_log"}
                missing_cols = required_cols - columns
                
                if missing_cols:
                    self.issues.append(f"✗ incidents table missing columns: {missing_cols}")
                    conn.close()
                    return False
                
                # Check for new optional columns
                optional_cols = {"threat_type", "action", "details"}
                has_optional = optional_cols & columns
                if has_optional:
                    self.successes.append(f"✓ {db_name} has enhanced incident fields")
                else:
                    logger.warning(f"  Optional columns not found in incidents table")
            
            # Get record count
            cursor.execute("SELECT COUNT(*) FROM incidents" if "incidents" in existing_tables else "SELECT 0")
            record_count = cursor.fetchone()[0] if "incidents" in existing_tables else 0
            
            conn.close()
            
            self.successes.append(f"✓ {db_name}: OK ({len(existing_tables)} tables, {record_count} incidents)")
            return True
            
        except Exception as e:
            self.issues.append(f"✗ Error reading {db_name}: {e}")
            return False
    
    def verify_all_databases(self):
        """Verify all Sentinel databases"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("DATABASE VERIFICATION")
        logger.info("=" * 60)
        
        databases = [
            (os.path.join(self.data_dir, "sentinel_intel.db"), ["incidents", "actions", "threat_intel"]),
            (os.path.join(self.data_dir, "auth.db"), ["users", "sessions", "api_keys"]),
            (os.path.join(self.data_dir, "threat_intel.db"), ["malicious_ips", "malicious_patterns", "safe_ips", "ip_reputation_cache"]),
            (os.path.join(self.data_dir, "lists.db"), ["ip_whitelist", "ip_blacklist", "pattern_whitelist", "pattern_blacklist"]),
            (os.path.join(self.data_dir, "metrics.db"), ["detection_metrics", "response_metrics", "hourly_stats", "system_health"]),
            (os.path.join(self.data_dir, "anomalies.db"), ["baseline_patterns", "anomaly_scores", "ip_profiles"]),
        ]
        
        for db_path, expected_tables in databases:
            self.verify_database(db_path, expected_tables)
    
    def verify_log_files(self):
        """Verify log files exist"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("LOG FILE VERIFICATION")
        logger.info("=" * 60)
        
        log_files = [
            ("/var/log/auth.log", "Auth log"),
            ("/var/log/apache2/access.log", "Web access log"),
        ]
        
        for log_path, description in log_files:
            if Path(log_path).exists():
                size = Path(log_path).stat().st_size
                self.successes.append(f"✓ {description} exists ({size} bytes)")
            else:
                logger.warning(f"  {description} not found: {log_path}")
    
    def verify_python_modules(self):
        """Verify required Python modules"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("PYTHON MODULES VERIFICATION")
        logger.info("=" * 60)
        
        required_modules = [
            "fastapi",
            "uvicorn",
            "crewai",
            "streamlit",
            "pandas",
            "sqlite3",
            "requests",
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
                self.successes.append(f"✓ {module_name} is installed")
            except ImportError:
                self.issues.append(f"✗ {module_name} is NOT installed")
    
    def run_verification(self):
        """Run all verifications"""
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " SENTINEL AGENT SETUP VERIFICATION ".center(58) + "║")
        logger.info("╚" + "=" * 58 + "╝")
        logger.info("")
        
        self.verify_data_directory()
        self.verify_all_databases()
        self.verify_log_files()
        self.verify_python_modules()
        
        # Print results
        logger.info("")
        logger.info("=" * 60)
        logger.info("VERIFICATION RESULTS")
        logger.info("=" * 60)
        
        for msg in self.successes:
            logger.info(msg)
        
        for msg in self.issues:
            logger.error(msg)
        
        logger.info("")
        if self.issues:
            logger.error(f"✗ VERIFICATION FAILED: {len(self.issues)} issues found")
            return False
        else:
            logger.info("✓ ALL CHECKS PASSED - SYSTEM IS READY")
            return True


def main():
    """Main entry point"""
    verifier = SetupVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
