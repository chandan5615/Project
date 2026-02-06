"""
Performance Metrics Tracking Module
Tracks detection performance, response times, and accuracy metrics.
"""

import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Tracks Sentinel Agent performance metrics."""
    
    def __init__(self, db_path: str = "/app/data/metrics.db"):
        """Initialize metrics tracker."""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize metrics database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Detection metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_metrics (
                id INTEGER PRIMARY KEY,
                incident_id INTEGER,
                attack_type TEXT,
                detection_time_ms INTEGER,
                processing_time_ms INTEGER,
                ai_response_time_ms INTEGER,
                accuracy_confidence REAL,
                timestamp TEXT
            )
        """)
        
        # Response metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_metrics (
                id INTEGER PRIMARY KEY,
                incident_id INTEGER,
                action_type TEXT,  -- firewall_block, process_kill, etc
                execution_time_ms INTEGER,
                success INTEGER,  -- 0 or 1
                timestamp TEXT
            )
        """)
        
        # Hourly statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hourly_stats (
                id INTEGER PRIMARY KEY,
                hour_start TEXT,
                total_incidents INTEGER,
                attacks_detected INTEGER,
                attacks_blocked INTEGER,
                false_positives INTEGER,
                avg_detection_time_ms INTEGER,
                avg_response_time_ms INTEGER
            )
        """)
        
        # System health
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY,
                check_time TEXT,
                cpu_usage_percent REAL,
                memory_usage_mb INTEGER,
                disk_free_mb INTEGER,
                active_connections INTEGER,
                db_size_mb INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_detection(self, incident_id: int, attack_type: str, 
                        detection_time_ms: int, processing_time_ms: int,
                        ai_response_time_ms: int, confidence: float) -> bool:
        """
        Record detection metrics.
        
        Args:
            incident_id: ID of detected incident
            attack_type: Type of attack detected
            detection_time_ms: Time from log to detection (milliseconds)
            processing_time_ms: Log processing time
            ai_response_time_ms: AI crew response time
            confidence: Detection confidence (0-1)
            
        Returns:
            Success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO detection_metrics 
                (incident_id, attack_type, detection_time_ms, processing_time_ms,
                 ai_response_time_ms, accuracy_confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (incident_id, attack_type, detection_time_ms, processing_time_ms,
                  ai_response_time_ms, confidence, datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording detection metrics: {e}")
            return False
        finally:
            conn.close()
    
    def record_response(self, incident_id: int, action_type: str,
                       execution_time_ms: int, success: bool) -> bool:
        """
        Record response action metrics.
        
        Args:
            incident_id: ID of incident
            action_type: Type of action taken
            execution_time_ms: Time to execute action
            success: Whether action succeeded
            
        Returns:
            Success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO response_metrics 
                (incident_id, action_type, execution_time_ms, success, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (incident_id, action_type, execution_time_ms, 1 if success else 0,
                  datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording response metrics: {e}")
            return False
        finally:
            conn.close()
    
    def get_detection_stats(self, hours: int = 24) -> Dict:
        """
        Get detection statistics for last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Total detections
        cursor.execute("""
            SELECT COUNT(*) FROM detection_metrics WHERE timestamp > ?
        """, (cutoff_time,))
        total_detections = cursor.fetchone()[0] or 0
        
        # Average detection time
        cursor.execute("""
            SELECT AVG(detection_time_ms) FROM detection_metrics WHERE timestamp > ?
        """, (cutoff_time,))
        avg_detection_time = cursor.fetchone()[0] or 0
        
        # Average confidence
        cursor.execute("""
            SELECT AVG(accuracy_confidence) FROM detection_metrics WHERE timestamp > ?
        """, (cutoff_time,))
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Detections by type
        cursor.execute("""
            SELECT attack_type, COUNT(*) as count 
            FROM detection_metrics WHERE timestamp > ?
            GROUP BY attack_type ORDER BY count DESC
        """, (cutoff_time,))
        
        attacks_by_type = [
            {"type": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_detections": total_detections,
            "avg_detection_time_ms": round(avg_detection_time, 2),
            "avg_confidence": round(avg_confidence, 4),
            "attacks_by_type": attacks_by_type
        }
    
    def get_response_stats(self, hours: int = 24) -> Dict:
        """
        Get response action statistics for last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Total actions
        cursor.execute("""
            SELECT COUNT(*) FROM response_metrics WHERE timestamp > ?
        """, (cutoff_time,))
        total_actions = cursor.fetchone()[0] or 0
        
        # Successful actions
        cursor.execute("""
            SELECT COUNT(*) FROM response_metrics WHERE timestamp > ? AND success = 1
        """, (cutoff_time,))
        successful_actions = cursor.fetchone()[0] or 0
        
        # Average execution time
        cursor.execute("""
            SELECT AVG(execution_time_ms) FROM response_metrics WHERE timestamp > ?
        """, (cutoff_time,))
        avg_execution_time = cursor.fetchone()[0] or 0
        
        # Success rate
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        conn.close()
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": total_actions - successful_actions,
            "success_rate_percent": round(success_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2)
        }
    
    def get_health_status(self) -> Dict:
        """Get current system health status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get latest health check
        cursor.execute("""
            SELECT cpu_usage_percent, memory_usage_mb, disk_free_mb, 
                   active_connections, db_size_mb, check_time
            FROM system_health ORDER BY check_time DESC LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "cpu_usage_percent": row[0],
                "memory_usage_mb": row[1],
                "disk_free_mb": row[2],
                "active_connections": row[3],
                "db_size_mb": row[4],
                "last_check": row[5],
                "status": "healthy" if row[0] < 80 else "warning"
            }
        
        return {
            "status": "no_data",
            "last_check": None
        }
    
    def record_health_check(self, cpu_percent: float, memory_mb: int,
                           disk_free_mb: int, connections: int, db_size_mb: int) -> bool:
        """Record system health metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO system_health 
                (cpu_usage_percent, memory_usage_mb, disk_free_mb, 
                 active_connections, db_size_mb, check_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cpu_percent, memory_mb, disk_free_mb, connections, 
                  db_size_mb, datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording health check: {e}")
            return False
        finally:
            conn.close()
    
    def get_dashboard_metrics(self) -> Dict:
        """Get all metrics for dashboard display."""
        detection_stats = self.get_detection_stats(24)
        response_stats = self.get_response_stats(24)
        health_status = self.get_health_status()
        
        return {
            "detection": detection_stats,
            "response": response_stats,
            "health": health_status,
            "timestamp": datetime.now().isoformat()
        }


# Convenience singleton
_metrics_instance = None

def get_metrics() -> PerformanceMetrics:
    """Get metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()
    return _metrics_instance
