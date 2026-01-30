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

DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR", "/app/data")
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH", os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db"))

class DataEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source_ip TEXT,
                    attack_type TEXT,
                    severity TEXT,
                    raw_log TEXT
                )
                """
            )
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

    def insert_incident(self, source_ip: str, attack_type: str, raw_log: str, severity: str = "unknown") -> int:
        ts = datetime.utcnow().isoformat()
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO incidents (timestamp, source_ip, attack_type, severity, raw_log) VALUES (?, ?, ?, ?, ?)",
                (ts, source_ip, attack_type, severity, raw_log)
            )
            return cur.lastrowid

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
