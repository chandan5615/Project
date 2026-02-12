"""
Whitelist and Blacklist Management Module
Manage IPs and patterns to include or exclude from blocking.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ListManager:
    """Manages whitelist and blacklist for security controls."""
    
    def __init__(self, db_path: str = "/app/data/lists.db"):
        """Initialize list manager."""
        # Ensure db_path is valid
        if not db_path or db_path.isspace():
            db_path = "/app/data/lists.db"
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize lists database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # IP Whitelist - IPs never to block
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_whitelist (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                reason TEXT,
                added_by TEXT,
                added_date TEXT,
                expires_date TEXT
            )
        """)
        
        # IP Blacklist - IPs to always block
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_blacklist (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                reason TEXT,
                severity TEXT,  -- critical, high, medium
                added_by TEXT,
                added_date TEXT,
                expires_date TEXT
            )
        """)
        
        # Pattern Whitelist - Attack patterns to ignore
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_whitelist (
                id INTEGER PRIMARY KEY,
                pattern TEXT UNIQUE,
                pattern_type TEXT,
                reason TEXT,
                added_by TEXT,
                added_date TEXT
            )
        """)
        
        # Pattern Blacklist - Attack patterns to always flag
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_blacklist (
                id INTEGER PRIMARY KEY,
                pattern TEXT UNIQUE,
                pattern_type TEXT,
                reason TEXT,
                added_by TEXT,
                added_date TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    # IP WHITELIST OPERATIONS
    
    def whitelist_ip(self, ip: str, reason: str = "", added_by: str = "system") -> bool:
        """Add IP to whitelist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ip_whitelist (ip, reason, added_by, added_date)
                VALUES (?, ?, ?, ?)
            """, (ip, reason, added_by, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Whitelisted IP: {ip}")
            return True
        except Exception as e:
            logger.error(f"Error whitelisting IP: {e}")
            return False
        finally:
            conn.close()
    
    def remove_whitelist_ip(self, ip: str) -> bool:
        """Remove IP from whitelist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM ip_whitelist WHERE ip = ?", (ip,))
            conn.commit()
            logger.info(f"Removed IP from whitelist: {ip}")
            return True
        except Exception as e:
            logger.error(f"Error removing from whitelist: {e}")
            return False
        finally:
            conn.close()
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM ip_whitelist 
            WHERE ip = ? AND (expires_date IS NULL OR expires_date > ?)
        """, (ip, datetime.now().isoformat()))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def get_whitelisted_ips(self) -> List[Dict]:
        """Get all whitelisted IPs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip, reason, added_by, added_date FROM ip_whitelist
            WHERE expires_date IS NULL OR expires_date > ?
            ORDER BY added_date DESC
        """, (datetime.now().isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "ip": row[0],
                "reason": row[1],
                "added_by": row[2],
                "added_date": row[3]
            }
            for row in rows
        ]
    
    # IP BLACKLIST OPERATIONS
    
    def blacklist_ip(self, ip: str, reason: str = "", severity: str = "high", 
                    added_by: str = "system") -> bool:
        """Add IP to blacklist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ip_blacklist 
                (ip, reason, severity, added_by, added_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ip, reason, severity, added_by, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Blacklisted IP: {ip} ({severity})")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting IP: {e}")
            return False
        finally:
            conn.close()
    
    def remove_blacklist_ip(self, ip: str) -> bool:
        """Remove IP from blacklist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM ip_blacklist WHERE ip = ?", (ip,))
            conn.commit()
            logger.info(f"Removed IP from blacklist: {ip}")
            return True
        except Exception as e:
            logger.error(f"Error removing from blacklist: {e}")
            return False
        finally:
            conn.close()
    
    def is_ip_blacklisted(self, ip: str) -> bool:
        """Check if IP is blacklisted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM ip_blacklist 
            WHERE ip = ? AND (expires_date IS NULL OR expires_date > ?)
        """, (ip, datetime.now().isoformat()))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def get_blacklisted_ips(self) -> List[Dict]:
        """Get all blacklisted IPs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ip, reason, severity, added_by, added_date FROM ip_blacklist
            WHERE expires_date IS NULL OR expires_date > ?
            ORDER BY added_date DESC
        """, (datetime.now().isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "ip": row[0],
                "reason": row[1],
                "severity": row[2],
                "added_by": row[3],
                "added_date": row[4]
            }
            for row in rows
        ]
    
    # PATTERN WHITELIST OPERATIONS
    
    def whitelist_pattern(self, pattern: str, pattern_type: str, reason: str = "",
                         added_by: str = "system") -> bool:
        """Add pattern to whitelist (ignore these patterns)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO pattern_whitelist 
                (pattern, pattern_type, reason, added_by, added_date)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern, pattern_type, reason, added_by, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Whitelisted pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Error whitelisting pattern: {e}")
            return False
        finally:
            conn.close()
    
    def is_pattern_whitelisted(self, pattern: str) -> bool:
        """Check if pattern is whitelisted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pattern_whitelist WHERE pattern = ?", (pattern,))
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    # PATTERN BLACKLIST OPERATIONS
    
    def blacklist_pattern(self, pattern: str, pattern_type: str, reason: str = "",
                         added_by: str = "system") -> bool:
        """Add pattern to blacklist (always alert)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO pattern_blacklist 
                (pattern, pattern_type, reason, added_by, added_date)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern, pattern_type, reason, added_by, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Blacklisted pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting pattern: {e}")
            return False
        finally:
            conn.close()
    
    def is_pattern_blacklisted(self, pattern: str) -> bool:
        """Check if pattern is blacklisted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pattern_blacklist WHERE pattern = ?", (pattern,))
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    # SUMMARY OPERATIONS
    
    def get_summary(self) -> Dict:
        """Get summary of all lists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ip_whitelist")
        whitelist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ip_blacklist")
        blacklist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pattern_whitelist")
        pattern_whitelist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pattern_blacklist")
        pattern_blacklist_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "ip_whitelist_count": whitelist_count,
            "ip_blacklist_count": blacklist_count,
            "pattern_whitelist_count": pattern_whitelist_count,
            "pattern_blacklist_count": pattern_blacklist_count
        }


# Convenience singleton
_list_manager_instance = None

def get_list_manager() -> ListManager:
    """Get list manager instance."""
    global _list_manager_instance
    if _list_manager_instance is None:
        _list_manager_instance = ListManager()
    return _list_manager_instance
