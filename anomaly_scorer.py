"""
Machine Learning - Anomaly Scoring Module
Simple ML-based scoring for attack anomalies and pattern recognition.
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import logging
import math

logger = logging.getLogger(__name__)


class AnomalyScorer:
    """ML-based anomaly detection and scoring."""
    
    def __init__(self, db_path: str = "/app/data/anomalies.db"):
        """Initialize anomaly scorer."""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Thresholds
        self.ANOMALY_THRESHOLD = 0.6  # 0-1 scale
        self.CRITICAL_THRESHOLD = 0.85
    
    def _init_db(self):
        """Initialize anomaly database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Baseline patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS baseline_patterns (
                id INTEGER PRIMARY KEY,
                pattern TEXT UNIQUE,
                attack_type TEXT,
                frequency_count INTEGER,
                avg_severity REAL,
                last_seen TEXT
            )
        """)
        
        # Anomaly scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_scores (
                id INTEGER PRIMARY KEY,
                incident_id INTEGER,
                base_score REAL,  -- 0-1
                frequency_score REAL,  -- 0-1
                behavior_score REAL,  -- 0-1
                temporal_score REAL,  -- 0-1
                final_score REAL,  -- 0-1
                is_anomaly INTEGER,  -- 0 or 1
                timestamp TEXT
            )
        """)
        
        # IP behavior profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_profiles (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                total_incidents INTEGER,
                avg_severity REAL,
                attack_types TEXT,  -- JSON list
                last_seen TEXT,
                behavior_pattern TEXT  -- consistent, variable, escalating
            )
        """)
        
        conn.commit()
        conn.close()
    
    def calculate_anomaly_score(self, incident: Dict) -> Dict:
        """
        Calculate anomaly score for an incident.
        
        Args:
            incident: Incident dictionary with attack info
            
        Returns:
            Dictionary with anomaly analysis
        """
        # Component scores
        base_score = self._calculate_base_score(incident)
        frequency_score = self._calculate_frequency_score(incident)
        behavior_score = self._calculate_behavior_score(incident)
        temporal_score = self._calculate_temporal_score(incident)
        
        # Weighted final score
        final_score = (
            base_score * 0.3 +
            frequency_score * 0.25 +
            behavior_score * 0.25 +
            temporal_score * 0.2
        )
        
        # Determine if anomalous
        is_anomaly = final_score >= self.ANOMALY_THRESHOLD
        severity_level = "critical" if final_score >= self.CRITICAL_THRESHOLD else \
                        "high" if is_anomaly else "normal"
        
        result = {
            "base_score": round(base_score, 3),
            "frequency_score": round(frequency_score, 3),
            "behavior_score": round(behavior_score, 3),
            "temporal_score": round(temporal_score, 3),
            "final_score": round(final_score, 3),
            "is_anomaly": is_anomaly,
            "severity_level": severity_level,
            "recommendation": self._get_recommendation(final_score)
        }
        
        # Record score
        if "incident_id" in incident:
            self._record_anomaly_score(
                incident["incident_id"],
                base_score, frequency_score, behavior_score, temporal_score,
                final_score, is_anomaly
            )
        
        return result
    
    def _calculate_base_score(self, incident: Dict) -> float:
        """
        Calculate base score from attack characteristics.
        
        Base score depends on:
        - Attack type severity
        - Pattern complexity
        - Payload size/complexity
        """
        severity_map = {
            "critical": 0.95,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        severity = incident.get("severity", "medium").lower()
        base_score = severity_map.get(severity, 0.5)
        
        # Adjust for attack type
        attack_type = incident.get("attack_type", "unknown").lower()
        type_multipliers = {
            "sql_injection": 1.0,
            "command_injection": 1.0,
            "directory_traversal": 0.9,
            "xss": 0.8,
            "brute_force": 0.7,
            "dos": 0.85
        }
        
        multiplier = type_multipliers.get(attack_type, 0.8)
        return min(base_score * multiplier, 1.0)
    
    def _calculate_frequency_score(self, incident: Dict) -> float:
        """
        Calculate frequency score based on IP attack history.
        
        Frequency score depends on:
        - How many times this IP attacked before
        - Attack pattern frequency
        """
        ip = incident.get("source_ip", "unknown")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check IP profile
        cursor.execute("""
            SELECT total_incidents FROM ip_profiles WHERE ip = ?
        """, (ip,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            incident_count = result[0]
            # Logarithmic scaling: more frequent = higher anomaly score
            frequency_score = min(math.log(incident_count + 1) / 5.0, 1.0)
        else:
            # New IP = higher anomaly score
            frequency_score = 0.7
        
        return frequency_score
    
    def _calculate_behavior_score(self, incident: Dict) -> float:
        """
        Calculate behavior score based on pattern deviations.
        
        Behavior score depends on:
        - Change in attack type from baseline
        - Unusual combinations
        - Multi-vector attacks
        """
        ip = incident.get("source_ip", "unknown")
        attack_type = incident.get("attack_type", "unknown")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check IP profile
        cursor.execute("""
            SELECT attack_types, behavior_pattern FROM ip_profiles WHERE ip = ?
        """, (ip,))
        
        result = cursor.fetchone()
        conn.close()
        
        behavior_score = 0.5  # Default
        
        if result:
            previous_attacks_json, pattern = result
            try:
                previous_attacks = json.loads(previous_attacks_json)
                
                if attack_type not in previous_attacks:
                    # New attack type from this IP = anomalous
                    behavior_score = 0.8
                elif pattern == "escalating":
                    # Escalating behavior = anomalous
                    behavior_score = 0.9
                else:
                    # Consistent pattern = less anomalous
                    behavior_score = 0.3
            except:
                behavior_score = 0.5
        else:
            # New IP = moderately anomalous behavior
            behavior_score = 0.6
        
        return behavior_score
    
    def _calculate_temporal_score(self, incident: Dict) -> float:
        """
        Calculate temporal score based on timing patterns.
        
        Temporal score depends on:
        - Time of day (off-hours = more anomalous)
        - Inter-arrival time (rapid succession = anomalous)
        - Deviation from baseline timing
        """
        now = datetime.now()
        hour = now.hour
        
        # Off-hours detection (0-6 AM, 10 PM-midnight)
        off_hours = hour < 6 or hour >= 22
        time_score = 0.7 if off_hours else 0.3
        
        # Check rapid succession (within 5 minutes of last attack)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ip = incident.get("source_ip", "unknown")
        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
        
        cursor.execute("""
            SELECT COUNT(*) FROM anomaly_scores 
            WHERE incident_id IN (
                SELECT id FROM incidents WHERE source_ip = ? AND timestamp > ?
            )
        """, (ip, cutoff))
        
        recent_count = cursor.fetchone()[0] or 0
        conn.close()
        
        if recent_count > 2:
            # Rapid succession = anomalous
            time_score = min(time_score + 0.4, 1.0)
        
        return time_score
    
    def update_ip_profile(self, ip: str, attack_type: str, severity: str) -> Dict:
        """
        Update IP behavior profile.
        
        Args:
            ip: IP address
            attack_type: Type of attack
            severity: Attack severity
            
        Returns:
            Updated profile
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing profile
        cursor.execute("""
            SELECT total_incidents, avg_severity, attack_types, behavior_pattern 
            FROM ip_profiles WHERE ip = ?
        """, (ip,))
        
        row = cursor.fetchone()
        
        if row:
            total, avg_severity, attacks_json, pattern = row
            
            # Update counts
            new_total = total + 1
            severity_val = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(severity, 2)
            new_avg = (avg_severity * total + severity_val) / new_total
            
            # Update attack types
            try:
                attacks = json.loads(attacks_json)
            except:
                attacks = []
            
            if attack_type not in attacks:
                attacks.append(attack_type)
            
            # Determine behavior pattern
            if len(attacks) > 3:
                behavior_pattern = "escalating"
            elif len(attacks) > 1:
                behavior_pattern = "variable"
            else:
                behavior_pattern = "consistent"
        else:
            new_total = 1
            new_avg = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(severity, 2)
            attacks = [attack_type]
            behavior_pattern = "consistent"
        
        # Update profile
        attacks_json = json.dumps(attacks)
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ip_profiles 
                (ip, total_incidents, avg_severity, attack_types, 
                 last_seen, behavior_pattern)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ip, new_total, new_avg, attacks_json, 
                  datetime.now().isoformat(), behavior_pattern))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating IP profile: {e}")
        finally:
            conn.close()
        
        return {
            "ip": ip,
            "total_incidents": new_total,
            "avg_severity": round(new_avg, 2),
            "attack_types": attacks,
            "behavior_pattern": behavior_pattern
        }
    
    def _record_anomaly_score(self, incident_id: int, base: float, freq: float,
                             behavior: float, temporal: float, final: float,
                             is_anomaly: bool):
        """Record anomaly score to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO anomaly_scores 
                (incident_id, base_score, frequency_score, behavior_score,
                 temporal_score, final_score, is_anomaly, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (incident_id, base, freq, behavior, temporal, final,
                  1 if is_anomaly else 0, datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error recording anomaly score: {e}")
        finally:
            conn.close()
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on anomaly score."""
        if score >= self.CRITICAL_THRESHOLD:
            return "IMMEDIATE_BLOCK: Critical anomaly detected - block IP immediately"
        elif score >= self.ANOMALY_THRESHOLD:
            return "ESCALATE: High anomaly score - escalate to human analyst"
        else:
            return "MONITOR: Normal behavior - continue monitoring"


# Convenience singleton
_scorer_instance = None

def get_anomaly_scorer() -> AnomalyScorer:
    """Get anomaly scorer instance."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = AnomalyScorer()
    return _scorer_instance
