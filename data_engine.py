"""
Quiet Data Engine for Sentinel Agent
- Creates SQLite DB at configurable path (default: ./data/sentinel_intel.db or /app/data/sentinel_intel.db)
- Tables: incidents, actions, threat_intel
- Simple insert/query helpers
"""
import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# CHANGE TRACKING (2026-02-23): Fixed default data directory detection
# Auto-detect if running in Docker or local environment
def _detect_default_data_dir():
    """Detect appropriate data directory based on environment."""
    # Check if running in Docker
    if os.path.exists("/.dockerenv") or os.path.exists("/proc/self/cgroup"):
        try:
            with open("/proc/self/cgroup", "r") as f:
                if "docker" in f.read():
                    return "/app/data"
        except:
            pass
        return "/app/data"
    # Local development
    return "./data"

DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR") or _detect_default_data_dir()
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH") or os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db")

logger.info(f"Data Engine initialized with DB path: {DEFAULT_DB_PATH}")

class DataEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        # Ensure db_path is valid and not empty
        if not self.db_path or self.db_path.isspace():
            self.db_path = DEFAULT_DB_PATH
        
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if path has a directory component
            os.makedirs(db_dir, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        try:
            with self._conn:
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        source_ip TEXT,
                        attack_type TEXT,
                        severity TEXT,
                        raw_log TEXT,
                        threat_type TEXT,
                        action TEXT,
                        details TEXT
                    )
                    """
                )
                logger.info(f"[OK] incidents table created/verified in {self.db_path}")
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incident_id INTEGER,
                        action_type TEXT,
                        details TEXT,
                        success INTEGER,
                        timestamp TEXT
                    )
                    """
                )
                logger.info(f"[OK] actions table created/verified in {self.db_path}")
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS threat_intel (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT UNIQUE,
                        reputation_score INTEGER,
                        details TEXT,
                        last_checked TEXT
                    )
                    """
                )
                logger.info(f"[OK] threat_intel table created/verified in {self.db_path}")
                
                # FEATURE: Temporary Ban Logic (Auto-Expiry)
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS blocked_ips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT UNIQUE,
                        blocked_at TEXT,
                        banned_until TEXT,
                        offense_count INTEGER DEFAULT 1,
                        ban_duration_minutes INTEGER,
                        reason TEXT,
                        status TEXT DEFAULT 'active'
                    )
                    """
                )
                logger.info(f"[OK] blocked_ips table created/verified in {self.db_path}")
                
                # FEATURE: Whitelist Protection (Admin God-Mode)
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS safe_ips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT UNIQUE,
                        reason TEXT,
                        added_at TEXT,
                        auto_detected INTEGER DEFAULT 0
                    )
                    """
                )
                logger.info(f"[OK] safe_ips (whitelist) table created/verified in {self.db_path}")
        except Exception as e:
            logger.error(f"Error creating tables in {self.db_path}: {e}")
            raise

    def insert_incident(self, source_ip: str, attack_type: str, raw_log: str, severity: str = "unknown", threat_type: str = None, action: str = None, details: str = None) -> int:
        ts = datetime.utcnow().isoformat()
        try:
            with self._conn:
                cur = self._conn.execute(
                    "INSERT INTO incidents (timestamp, source_ip, attack_type, severity, raw_log, threat_type, action, details) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (ts, source_ip, attack_type, severity, raw_log, threat_type or attack_type, action or "blocked", details or "")
                )
                incident_id = cur.lastrowid
                logger.info(f"[OK] Incident #{incident_id} inserted for {source_ip} ({attack_type})")
                return incident_id
        except Exception as e:
            logger.error(f"Failed to insert incident for {source_ip}: {e}")
            raise

    def insert_action(self, incident_id: int, action_type: str, details: str, success: bool = True) -> int:
        ts = datetime.utcnow().isoformat()
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO actions (incident_id, action_type, details, success, timestamp) VALUES (?, ?, ?, ?, ?)",
                (incident_id, action_type, details, 1 if success else 0, ts)
            )
            return cur.lastrowid

    def upsert_threat_intel(self, ip: str, score: Optional[int], details: Optional[str]):
        ts = datetime.utcnow().isoformat()
        with self._conn:
            # Try update
            self._conn.execute(
                "INSERT INTO threat_intel (ip, reputation_score, details, last_checked) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(ip) DO UPDATE SET reputation_score=excluded.reputation_score, details=excluded.details, last_checked=excluded.last_checked",
                (ip, score if score is not None else -1, details or "", ts)
            )

    def query_incidents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        cur = self._conn.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def query_actions(self, incident_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if incident_id:
            cur = self._conn.execute("SELECT * FROM actions WHERE incident_id = ? ORDER BY timestamp DESC", (incident_id,))
        else:
            cur = self._conn.execute("SELECT * FROM actions ORDER BY timestamp DESC")
        return [dict(r) for r in cur.fetchall()]

    def query_threat_intel(self, ip: Optional[str] = None) -> List[Dict[str, Any]]:
        if ip:
            cur = self._conn.execute("SELECT * FROM threat_intel WHERE ip = ?", (ip,))
        else:
            cur = self._conn.execute("SELECT * FROM threat_intel")
        return [dict(r) for r in cur.fetchall()]
    
    # =========================================================================
    # FEATURE: Temporary Ban Logic with Progressive Punishment
    # =========================================================================
    
    def block_ip(self, ip: str, ban_duration_minutes: int, reason: str = "Security incident") -> int:
        """
        Block an IP with automatic expiry.
        Implements progressive punishment based on offense count.
        
        Args:
            ip: IP address to block
            ban_duration_minutes: How long to ban (15, 120, or 1440 minutes)
            reason: Reason for blocking
            
        Returns:
            ID of blocked_ips record
        """
        from datetime import timedelta
        
        blocked_at = datetime.utcnow()
        banned_until = blocked_at + timedelta(minutes=ban_duration_minutes)
        
        with self._conn:
            # Check if IP was previously blocked
            cur = self._conn.execute("SELECT offense_count FROM blocked_ips WHERE ip = ?", (ip,))
            existing = cur.fetchone()
            
            if existing:
                # Increment offense count
                new_count = existing['offense_count'] + 1
                self._conn.execute(
                    """UPDATE blocked_ips 
                       SET offense_count = ?, blocked_at = ?, banned_until = ?, 
                           ban_duration_minutes = ?, status = 'active', reason = ?
                       WHERE ip = ?""",
                    (new_count, blocked_at.isoformat(), banned_until.isoformat(), 
                     ban_duration_minutes, reason, ip)
                )
                logger.info(f"[OK] IP {ip} re-blocked (offense #{new_count}) until {banned_until.isoformat()}")
            else:
                # First offense
                cur = self._conn.execute(
                    """INSERT INTO blocked_ips 
                       (ip, blocked_at, banned_until, offense_count, ban_duration_minutes, reason, status)
                       VALUES (?, ?, ?, 1, ?, ?, 'active')""",
                    (ip, blocked_at.isoformat(), banned_until.isoformat(), ban_duration_minutes, reason)
                )
                logger.info(f"[OK] IP {ip} blocked (1st offense) until {banned_until.isoformat()}")
            
            return cur.lastrowid
    
    def get_expired_ips(self) -> List[Dict[str, Any]]:
        """
        Get all IPs whose ban time has expired.
        
        Returns:
            List of expired blocked IP records
        """
        now = datetime.utcnow().isoformat()
        cur = self._conn.execute(
            "SELECT * FROM blocked_ips WHERE status = 'active' AND banned_until < ?",
            (now,)
        )
        return [dict(r) for r in cur.fetchall()]
    
    def mark_ip_unblocked(self, ip: str) -> bool:
        """
        Mark an IP as unblocked (status='expired').
        
        Args:
            ip: IP address to mark as unblocked
            
        Returns:
            True if successful
        """
        with self._conn:
            self._conn.execute(
                "UPDATE blocked_ips SET status = 'expired' WHERE ip = ? AND status = 'active'",
                (ip,)
            )
            logger.info(f"[OK] IP {ip} marked as expired/unblocked")
            return True
    
    def get_offense_count(self, ip: str) -> int:
        """
        Get the current offense count for an IP.
        
        Args:
            ip: IP address to check
            
        Returns:
            Offense count (0 if never seen)
        """
        cur = self._conn.execute("SELECT offense_count FROM blocked_ips WHERE ip = ?", (ip,))
        row = cur.fetchone()
        return row['offense_count'] if row else 0
    
    def unblock_ip_globally(self, ip: str) -> Dict[str, Any]:
        """
        GLOBAL IP CLEARANCE: Completely remove an IP from the system.
        
        This performs a complete wipe of the IP:
        - Deletes ALL incidents for this IP (not just one)
        - Removes IP from blocked_ips table
        - Returns count of deleted records
        
        Args:
            ip: IP address to completely clear
            
        Returns:
            Dict with counts of deleted records
        """
        try:
            # Count incidents before deletion
            cur = self._conn.execute("SELECT COUNT(*) FROM incidents WHERE source_ip = ?", (ip,))
            incident_count = cur.fetchone()[0]
            
            # Count blocked_ips entries before deletion
            cur = self._conn.execute("SELECT COUNT(*) FROM blocked_ips WHERE ip = ?", (ip,))
            blocked_count = cur.fetchone()[0]
            
            # Perform global wipe
            with self._conn:
                # Delete ALL incidents for this IP
                self._conn.execute("DELETE FROM incidents WHERE source_ip = ?", (ip,))
                
                # Delete ALL blocked_ips entries for this IP
                self._conn.execute("DELETE FROM blocked_ips WHERE ip = ?", (ip,))
            
            logger.info(f"[OK] GLOBAL WIPE for {ip}: Deleted {incident_count} incidents, {blocked_count} block records")
            
            return {
                "success": True,
                "ip": ip,
                "incidents_deleted": incident_count,
                "blocks_deleted": blocked_count,
                "total_deleted": incident_count + blocked_count
            }
        except Exception as e:
            logger.error(f"❌ Failed to globally unblock {ip}: {e}")
            return {
                "success": False,
                "ip": ip,
                "error": str(e),
                "incidents_deleted": 0,
                "blocks_deleted": 0
            }
    
    # =========================================================================
    # FEATURE: Whitelist Protection (Admin God-Mode)
    # =========================================================================
    
    def add_safe_ip(self, ip: str, reason: str, auto_detected: bool = False) -> int:
        """
        Add an IP to the whitelist (safe_ips).
        
        Args:
            ip: IP address to whitelist
            reason: Reason for whitelisting
            auto_detected: Whether this was auto-detected (local network, etc.)
            
        Returns:
            ID of safe_ips record
        """
        added_at = datetime.utcnow().isoformat()
        try:
            with self._conn:
                cur = self._conn.execute(
                    """INSERT INTO safe_ips (ip, reason, added_at, auto_detected)
                       VALUES (?, ?, ?, ?)""",
                    (ip, reason, added_at, 1 if auto_detected else 0)
                )
                logger.info(f"[OK] IP {ip} added to whitelist: {reason}")
                return cur.lastrowid
        except sqlite3.IntegrityError:
            # Already whitelisted
            logger.info(f"IP {ip} already in whitelist")
            return -1
    
    def is_whitelisted(self, ip: str) -> bool:
        """
        Check if an IP is in the whitelist.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is whitelisted
        """
        cur = self._conn.execute("SELECT COUNT(*) FROM safe_ips WHERE ip = ?", (ip,))
        count = cur.fetchone()[0]
        return count > 0
    
    def get_all_whitelisted_ips(self) -> List[Dict[str, Any]]:
        """Get all whitelisted IPs."""
        cur = self._conn.execute("SELECT * FROM safe_ips ORDER BY added_at DESC")
        return [dict(r) for r in cur.fetchall()]
    
    def remove_from_whitelist(self, ip: str) -> bool:
        """
        Remove an IP from the whitelist.
        
        Args:
            ip: IP address to remove
            
        Returns:
            True if removed
        """
        with self._conn:
            self._conn.execute("DELETE FROM safe_ips WHERE ip = ?", (ip,))
            logger.info(f"[OK] IP {ip} removed from whitelist")
            return True

    def close(self):
        """Close the underlying DB connection."""
        try:
            self._conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

# Convenience single instance
_default_engine: Optional[DataEngine] = None

def get_engine() -> DataEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = DataEngine()
    return _default_engine
