"""
Offline Threat Intelligence Module
Local database for IP reputation and threat scoring without internet dependency.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
import logging
import hashlib

logger = logging.getLogger(__name__)


class OfflineThreatIntelligence:
    """Local threat intelligence database management."""
    
    def __init__(self, db_path: str = "/app/data/threat_intel.db"):
        """Initialize offline threat intelligence system."""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_default_threats()
    
    def _init_db(self):
        """Initialize threat intelligence database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Known malicious IPs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS malicious_ips (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                threat_level TEXT,  -- critical, high, medium, low
                reason TEXT,
                last_seen TEXT,
                confidence INTEGER,  -- 0-100
                sources TEXT  -- comma-separated list
            )
        """)
        
        # Known malicious patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS malicious_patterns (
                id INTEGER PRIMARY KEY,
                pattern TEXT UNIQUE,
                pattern_type TEXT,  -- signature, behavioral
                threat_category TEXT,  -- malware, botnet, scanner, etc
                severity TEXT,
                description TEXT
            )
        """)
        
        # Known safe IPs (whitelist)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS safe_ips (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                reason TEXT,
                added_date TEXT
            )
        """)
        
        # IP reputation cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_reputation_cache (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                threat_score INTEGER,  -- 0-100
                is_malicious INTEGER,
                last_checked TEXT,
                cache_age_hours INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_default_threats(self):
        """Load default threat data into database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already loaded
        cursor.execute("SELECT COUNT(*) FROM malicious_patterns")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Default malicious patterns
        default_patterns = [
            ("admin' OR '1'='1", "signature", "sql_injection", "critical", "Classic SQL injection"),
            ("union select", "signature", "sql_injection", "high", "SQL UNION-based injection"),
            ("../", "signature", "directory_traversal", "high", "Directory traversal attempt"),
            ("../../", "signature", "directory_traversal", "high", "Multi-level directory traversal"),
            ("<script>", "signature", "xss", "high", "XSS script injection"),
            ("onclick=", "signature", "xss", "medium", "XSS event handler"),
            ("/etc/passwd", "signature", "path_disclosure", "high", "Unix file access attempt"),
            ("/etc/shadow", "signature", "sensitive_file", "critical", "Shadow file access"),
            ("cmd.exe", "signature", "command_execution", "critical", "Windows command execution"),
            ("/bin/bash", "signature", "command_execution", "critical", "Unix shell access"),
        ]
        
        for pattern, ptype, category, severity, desc in default_patterns:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO malicious_patterns 
                    (pattern, pattern_type, threat_category, severity, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (pattern, ptype, category, severity, desc))
            except sqlite3.IntegrityError:
                pass
        
        # Default malicious IPs (public known botnets/scanners)
        default_ips = [
            ("192.241.238.166", "critical", "Known botnet C2 server", 95, "AbuseIPDB, Team Cymru"),
            ("91.199.77.50", "high", "Known SSH scanner", 85, "Shodan, AbuseIPDB"),
            ("103.145.45.97", "high", "Known vulnerability scanner", 80, "Censys"),
        ]
        
        for ip, level, reason, confidence, sources in default_ips:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO malicious_ips 
                    (ip, threat_level, reason, last_seen, confidence, sources)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ip, level, reason, datetime.now().isoformat(), confidence, sources))
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        conn.close()
        logger.info("Loaded default threat intelligence data")
    
    def check_ip_reputation(self, ip: str) -> Dict:
        """
        Check reputation of an IP address locally.
        
        Args:
            ip: IP address to check
            
        Returns:
            Dictionary with threat assessment
        """
        result = {
            "ip": ip,
            "threat_score": 0,
            "is_malicious": False,
            "threat_level": "safe",
            "reason": "No known threat",
            "sources": ["Local Database"],
            "confidence": 50
        }
        
        # Check if IP is whitelisted
        if self._is_whitelisted(ip):
            result["threat_score"] = 0
            result["threat_level"] = "safe"
            result["reason"] = "IP is whitelisted"
            result["is_malicious"] = False
            return result
        
        # Check malicious IPs database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT threat_level, reason, confidence, sources FROM malicious_ips WHERE ip = ?
        """, (ip,))
        
        row = cursor.fetchone()
        if row:
            threat_level, reason, confidence, sources = row
            result["threat_level"] = threat_level
            result["reason"] = reason
            result["confidence"] = confidence
            result["sources"] = sources.split(",") if sources else []
            
            # Map threat level to score
            level_map = {"critical": 100, "high": 75, "medium": 50, "low": 25}
            result["threat_score"] = level_map.get(threat_level, 0)
            result["is_malicious"] = result["threat_score"] >= 50
        
        # Check reputation cache
        cursor.execute("""
            SELECT threat_score, is_malicious FROM ip_reputation_cache WHERE ip = ?
        """, (ip,))
        
        cached = cursor.fetchone()
        if cached:
            threat_score, is_malicious = cached
            result["threat_score"] = threat_score
            result["is_malicious"] = bool(is_malicious)
            result["threat_level"] = "malicious" if is_malicious else "safe"
        
        conn.close()
        return result
    
    def add_malicious_ip(self, ip: str, threat_level: str, reason: str, confidence: int = 80):
        """Add IP to malicious list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO malicious_ips 
                (ip, threat_level, reason, last_seen, confidence, sources)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ip, threat_level, reason, datetime.now().isoformat(), confidence, "Local Detection"))
            conn.commit()
            logger.info(f"Added malicious IP: {ip} ({threat_level})")
        except Exception as e:
            logger.error(f"Error adding malicious IP: {e}")
        finally:
            conn.close()
    
    def add_safe_ip(self, ip: str, reason: str = ""):
        """Whitelist an IP address."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO safe_ips (ip, reason, added_date)
                VALUES (?, ?, ?)
            """, (ip, reason, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Whitelisted IP: {ip}")
        except Exception as e:
            logger.error(f"Error whitelisting IP: {e}")
        finally:
            conn.close()
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM safe_ips WHERE ip = ?", (ip,))
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def get_malicious_patterns(self) -> List[Dict]:
        """Get all known malicious patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT pattern, threat_category, severity, description FROM malicious_patterns")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "pattern": row[0],
                "category": row[1],
                "severity": row[2],
                "description": row[3]
            }
            for row in rows
        ]
    
    def cache_reputation(self, ip: str, threat_score: int, is_malicious: bool):
        """Cache IP reputation for fast lookup."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ip_reputation_cache 
                (ip, threat_score, is_malicious, last_checked, cache_age_hours)
                VALUES (?, ?, ?, ?, 24)
            """, (ip, threat_score, 1 if is_malicious else 0, datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error caching reputation: {e}")
        finally:
            conn.close()


# Convenience singleton
_threat_intel_instance = None

def get_threat_intelligence() -> OfflineThreatIntelligence:
    """Get threat intelligence instance."""
    global _threat_intel_instance
    if _threat_intel_instance is None:
        _threat_intel_instance = OfflineThreatIntelligence()
    return _threat_intel_instance
