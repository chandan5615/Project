"""
Sentinel Agent - Attack Detection Module
Detects various types of attacks from log patterns.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class AttackDetector:
    """Detects various types of attacks from log patterns."""
    
    def __init__(self):
        """Initialize attack detection patterns."""
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize attack detection patterns."""
        return {
            "sql_injection": {
                "patterns": [
                    r"union\s+select",
                    r"select\s+.*\s+from",
                    r"insert\s+into",
                    r"drop\s+table",
                    r"delete\s+from",
                    r"update\s+.*\s+set",
                    r"exec\s*\(",
                    r"';?\s*(--|#|/\*)",
                    r"or\s+1\s*=\s*1",
                    r"and\s+1\s*=\s*1",
                    r"'(\s*or\s*|\s*and\s*)",
                    r"(\||%7C).*(\||%7C)",
                ],
                "severity": "high",
                "description": "SQL Injection attempt detected"
            },
            "command_injection": {
                "patterns": [
                    r";\s*(ls|cat|pwd|whoami|id|uname)",
                    r"\|\s*(nc|netcat|bash|sh|python|perl)",
                    r"`.*`",
                    r"\$\(.*\)",
                    r"exec\(|system\(|passthru\(",
                    r"cmd\s*=|command\s*=",
                    r"eval\s*\(",
                    r"shell_exec\s*\(",
                ],
                "severity": "critical",
                "description": "Command Injection attempt detected"
            },
            "xss_stored": {
                "patterns": [
                    r"<script[^>]*>.*</script>",
                    r"javascript:",
                    r"onerror\s*=",
                    r"onload\s*=",
                    r"onclick\s*=",
                    r"onmouseover\s*=",
                    r"<iframe[^>]*>",
                    r"<img[^>]*onerror",
                    r"alert\s*\(",
                    r"document\.cookie",
                ],
                "severity": "high",
                "description": "Stored XSS attempt detected"
            },
            "xss_reflected": {
                "patterns": [
                    r"<script[^>]*>.*</script>",
                    r"javascript:",
                    r"onerror\s*=",
                    r"onload\s*=",
                    r"onclick\s*=",
                    r"alert\s*\(",
                    r"document\.cookie",
                    r"eval\s*\(",
                ],
                "severity": "medium",
                "description": "Reflected XSS attempt detected"
            },
            "brute_force": {
                "patterns": [
                    r"Failed password",
                    r"authentication failure",
                    r"invalid user",
                    r"login failed",
                ],
                "severity": "medium",
                "description": "Brute force attack detected"
            },
            "credential_stuffing": {
                "patterns": [
                    r"multiple.*failed.*login",
                    r"invalid.*credentials",
                    r"authentication.*failed",
                ],
                "severity": "medium",
                "description": "Credential stuffing attempt detected"
            },
            "session_hijacking": {
                "patterns": [
                    r"session.*expired",
                    r"invalid.*session",
                    r"session.*hijack",
                    r"cookie.*manipulation",
                ],
                "severity": "high",
                "description": "Session hijacking attempt detected"
            },
            "idor": {
                "patterns": [
                    r"/user/\d+",
                    r"/admin/\d+",
                    r"/api/\d+",
                    r"id=\d+",
                    r"user_id=\d+",
                ],
                "severity": "medium",
                "description": "IDOR (Insecure Direct Object Reference) attempt detected"
            },
            "directory_traversal": {
                "patterns": [
                    r"\.\./",
                    r"\.\.\\",
                    r"%2e%2e%2f",
                    r"%2e%2e%5c",
                    r"\.\.%2f",
                    r"\.\.%5c",
                    r"/etc/passwd",
                    r"/etc/shadow",
                    r"windows/system32",
                    r"proc/self",
                ],
                "severity": "high",
                "description": "Directory traversal attempt detected"
            },
            "csrf": {
                "patterns": [
                    r"referer.*null",
                    r"origin.*null",
                    r"cross.*site.*request",
                ],
                "severity": "medium",
                "description": "CSRF attempt detected"
            },
            "clickjacking": {
                "patterns": [
                    r"x-frame-options.*none",
                    r"frame.*ancestors.*none",
                ],
                "severity": "low",
                "description": "Clickjacking vulnerability detected"
            },
            "dos": {
                "patterns": [
                    r"connection.*reset",
                    r"timeout",
                    r"too.*many.*requests",
                ],
                "severity": "high",
                "description": "DoS attack detected"
            },
            "mitm": {
                "patterns": [
                    r"certificate.*error",
                    r"ssl.*error",
                    r"tls.*error",
                    r"invalid.*certificate",
                ],
                "severity": "high",
                "description": "Man-in-the-Middle attack detected"
            },
            "ssrf": {
                "patterns": [
                    r"localhost",
                    r"127\.0\.0\.1",
                    r"0\.0\.0\.0",
                    r"file://",
                    r"gopher://",
                    r"dict://",
                    r"internal.*ip",
                ],
                "severity": "critical",
                "description": "SSRF (Server-Side Request Forgery) attempt detected"
            },
        }
    
    def detect_attack(self, log_line: str, source: str = "web") -> Optional[Dict]:
        """
        Detect attack type from log line.
        
        Args:
            log_line: Log line to analyze
            source: Source of the log ("web" or "auth")
            
        Returns:
            Attack detection result or None
        """
        log_lower = log_line.lower()
        detected_attacks = []
        
        for attack_type, config in self.patterns.items():
            # Skip auth-specific attacks for web logs and vice versa
            if source == "web" and attack_type == "brute_force":
                continue
            if source == "auth" and attack_type in ["xss_stored", "xss_reflected", "csrf", "clickjacking"]:
                continue
            
            for pattern in config["patterns"]:
                if re.search(pattern, log_lower, re.IGNORECASE):
                    detected_attacks.append({
                        "attack_type": attack_type,
                        "severity": config["severity"],
                        "description": config["description"],
                        "pattern_matched": pattern,
                        "timestamp": datetime.now().isoformat(),
                        "source": source
                    })
                    break  # Only report each attack type once per log line
        
        if detected_attacks:
            # Return the highest severity attack
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            detected_attacks.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
            return detected_attacks[0]
        
        return None
    
    def get_attack_defense_strategy(self, attack_type: str) -> Dict:
        """
        Get defense strategy for a specific attack type.
        
        Args:
            attack_type: Type of attack detected
            
        Returns:
            Defense strategy dictionary
        """
        strategies = {
            "sql_injection": {
                "immediate_actions": [
                    "Block IP address",
                    "Review and sanitize database queries",
                    "Enable parameterized queries",
                    "Review application code for SQL injection vulnerabilities"
                ],
                "long_term": [
                    "Implement input validation",
                    "Use prepared statements",
                    "Implement least privilege database access",
                    "Regular security audits"
                ],
                "tools": ["iptables", "waf"]
            },
            "command_injection": {
                "immediate_actions": [
                    "Block IP address immediately",
                    "Kill any suspicious processes",
                    "Review system logs for executed commands",
                    "Check for unauthorized file modifications"
                ],
                "long_term": [
                    "Sanitize all user inputs",
                    "Use whitelist for allowed commands",
                    "Implement command execution restrictions",
                    "Regular security monitoring"
                ],
                "tools": ["iptables", "kill_process", "chmod"]
            },
            "xss_stored": {
                "immediate_actions": [
                    "Block IP address",
                    "Review and sanitize stored content",
                    "Remove malicious scripts from database",
                    "Notify affected users"
                ],
                "long_term": [
                    "Implement Content Security Policy (CSP)",
                    "Sanitize all user inputs",
                    "Use output encoding",
                    "Regular content audits"
                ],
                "tools": ["iptables", "waf"]
            },
            "xss_reflected": {
                "immediate_actions": [
                    "Block IP address",
                    "Review input validation",
                    "Sanitize reflected outputs"
                ],
                "long_term": [
                    "Implement Content Security Policy",
                    "Use output encoding",
                    "Input validation"
                ],
                "tools": ["iptables", "waf"]
            },
            "brute_force": {
                "immediate_actions": [
                    "Block IP address",
                    "Enable account lockout",
                    "Implement rate limiting",
                    "Review authentication logs"
                ],
                "long_term": [
                    "Implement CAPTCHA",
                    "Enable two-factor authentication",
                    "Monitor for credential stuffing",
                    "Regular password policy review"
                ],
                "tools": ["iptables", "fail2ban"]
            },
            "directory_traversal": {
                "immediate_actions": [
                    "Block IP address",
                    "Review file access controls",
                    "Check for unauthorized file access",
                    "Restrict file system access"
                ],
                "long_term": [
                    "Implement proper path validation",
                    "Use chroot or containerization",
                    "Restrict file permissions",
                    "Regular access audits"
                ],
                "tools": ["iptables", "chmod"]
            },
            "ssrf": {
                "immediate_actions": [
                    "Block IP address immediately",
                    "Review server-side request handlers",
                    "Check for unauthorized internal access",
                    "Monitor network connections"
                ],
                "long_term": [
                    "Implement URL validation",
                    "Use allowlist for allowed domains",
                    "Disable internal network access",
                    "Network segmentation"
                ],
                "tools": ["iptables", "network_firewall"]
            },
            "dos": {
                "immediate_actions": [
                    "Block attacking IPs",
                    "Enable rate limiting",
                    "Scale resources if needed",
                    "Monitor traffic patterns"
                ],
                "long_term": [
                    "Implement DDoS protection",
                    "Use CDN for traffic distribution",
                    "Implement auto-scaling",
                    "Regular capacity planning"
                ],
                "tools": ["iptables", "rate_limiting"]
            },
        }
        
        return strategies.get(attack_type, {
            "immediate_actions": ["Block IP address", "Review logs", "Monitor system"],
            "long_term": ["Implement security controls", "Regular audits"],
            "tools": ["iptables"]
        })
