"""
Sentinel Agent - Attack Logging System
Records attacks with date, time, attack type, and actions taken.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AttackLogger:
    """Logs security attacks and defensive actions."""
    
    def __init__(self, log_file: str = "attack_records.json"):
        """
        Initialize the attack logger.
        
        Args:
            log_file: Path to the JSON file storing attack records
        """
        self.log_file = Path(log_file)
        self.records = []
        self._load_existing_records()
    
    def _load_existing_records(self):
        """Load existing attack records from file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                logger.info(f"Loaded {len(self.records)} existing attack records")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load existing records: {e}")
                self.records = []
        else:
            self.records = []
    
    def _save_records(self):
        """Save attack records to file."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Could not save attack records: {e}")

    def _next_id(self) -> int:
        """Generate next unique record ID."""
        if not self.records:
            return 1
        return max(r.get("id", 0) for r in self.records) + 1
    
    def log_attack(
        self,
        ip_address: str,
        attack_type: str,
        log_line: str,
        source: str = "web",
        severity: str = "medium",
        description: str = ""
    ) -> Dict:
        """
        Log a detected attack.
        
        Args:
            ip_address: Attacking IP address
            attack_type: Type of attack detected
            log_line: Original log line
            source: Source of the log ("web" or "auth")
            severity: Severity level (critical, high, medium, low)
            description: Description of the attack
            
        Returns:
            Attack record dictionary
        """
        record = {
            "id": self._next_id(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip_address,
            "attack_type": attack_type,
            "severity": severity,
            "description": description,
            "source": source,
            "log_line": log_line,
            "actions_taken": [],
            "status": "detected"
        }
        
        self.records.append(record)
        self._save_records()
        
        logger.info(f"Logged attack: {attack_type} from {ip_address}")
        
        return record
    
    def add_action(
        self,
        attack_id: int,
        action_type: str,
        action_details: str,
        success: bool = True
    ):
        """
        Add an action taken in response to an attack.
        
        Args:
            attack_id: ID of the attack record
            action_type: Type of action (e.g., "firewall_block", "process_kill")
            action_details: Details of the action
            success: Whether the action was successful
        """
        action = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": action_details,
            "success": success
        }
        
        # Find the attack record
        for record in self.records:
            if record["id"] == attack_id:
                record["actions_taken"].append(action)
                record["status"] = "mitigated" if success else "action_failed"
                break
        
        self._save_records()
        logger.info(f"Added action to attack #{attack_id}: {action_type}")
    
    def get_attacks_by_ip(self, ip_address: str) -> List[Dict]:
        """
        Get all attacks from a specific IP address.
        
        Args:
            ip_address: IP address to search for
            
        Returns:
            List of attack records
        """
        return [r for r in self.records if r["ip_address"] == ip_address]
    
    def get_attacks_by_type(self, attack_type: str) -> List[Dict]:
        """
        Get all attacks of a specific type.
        
        Args:
            attack_type: Type of attack to search for
            
        Returns:
            List of attack records
        """
        return [r for r in self.records if r["attack_type"] == attack_type]
    
    def get_recent_attacks(self, limit: int = 10) -> List[Dict]:
        """
        Get recent attacks.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent attack records
        """
        return sorted(self.records, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def generate_report(self) -> str:
        """
        Generate a summary report of all attacks.
        
        Returns:
            Formatted report string
        """
        if not self.records:
            return "No attacks recorded."
        
        total_attacks = len(self.records)
        by_type = {}
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_ip = {}
        
        for record in self.records:
            # Count by type
            attack_type = record["attack_type"]
            by_type[attack_type] = by_type.get(attack_type, 0) + 1
            
            # Count by severity
            severity = record["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by IP
            ip = record["ip_address"]
            by_ip[ip] = by_ip.get(ip, 0) + 1
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           ATTACK RECORDS SUMMARY REPORT                  ║
╠══════════════════════════════════════════════════════════╣
║ Total Attacks Recorded: {total_attacks:<35} ║
╠══════════════════════════════════════════════════════════╣
║ Attacks by Severity:                                     ║
║   Critical: {by_severity.get('critical', 0):<45} ║
║   High:     {by_severity.get('high', 0):<45} ║
║   Medium:   {by_severity.get('medium', 0):<45} ║
║   Low:      {by_severity.get('low', 0):<45} ║
╠══════════════════════════════════════════════════════════╣
║ Attacks by Type:                                         ║
"""
        for attack_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            report += f"║   {attack_type}: {count:<42} ║\n"
        
        report += f"""╠══════════════════════════════════════════════════════════╣
║ Top Attacking IPs:                                       ║
"""
        top_ips = sorted(by_ip.items(), key=lambda x: x[1], reverse=True)[:5]
        for ip, count in top_ips:
            report += f"║   {ip}: {count:<45} ║\n"
        
        report += "╚══════════════════════════════════════════════════════╝\n"
        
        return report
