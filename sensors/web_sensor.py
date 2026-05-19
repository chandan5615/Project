"""
Sentinel Agent - Web Access Log Sensor
Monitors web server access logs (Apache/Nginx) for suspicious activity.
"""

import re
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Optional, Dict
import logging
import sys
import os
from collections import defaultdict
import time as time_module
from datetime import datetime

# Add defense module to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from defense.attack_detector import AttackDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebLogHandler(FileSystemEventHandler):
    """Handler for monitoring web access log file changes."""
    
    def __init__(self, callback: Callable[[str, str, dict], None], log_path: Optional[str] = None):
        """
        Initialize the web log handler.
        
        Args:
            callback: Function to call when suspicious activity is detected
                     Signature: callback(ip_address, log_line, attack_info)
            log_path: Path to the access log file (Apache or Nginx)
        """
        super().__init__()
        if not log_path or log_path.isspace():
            log_path = os.getenv("WEB_LOG_PATH", "/var/log/apache2/access.log")
        self.callback = callback
        self.log_path = Path(log_path)
        self.last_position = 0
        self._last_inode = None  # Track file inode for rotation detection
        self.attack_detector = AttackDetector()
        
        # Rate tracking for DDoS detection
        self._ip_request_times = defaultdict(list)  # ip -> list of timestamps
        self._ddos_threshold = int(os.getenv("DDOS_THRESHOLD", "50"))   # requests
        self._ddos_window = int(os.getenv("DDOS_WINDOW", "10"))         # seconds
        self._port_scan_threshold = int(os.getenv("PORT_SCAN_THRESHOLD", "20"))
        
        # Initialize last position if file exists
        if self.log_path.exists():
            self.last_position = self.log_path.stat().st_size
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.src_path == str(self.log_path):
            self._process_new_lines()
    
    def _process_new_lines(self):
        """Read and process new lines from the log file."""
        try:
            if not self.log_path.exists():
                logger.warning(f"Log file {self.log_path} does not exist")
                return
            
            # Check if file was rotated (inode changed)
            current_stat = self.log_path.stat()
            current_inode = current_stat.st_ino
            
            if self._last_inode is not None and current_inode != self._last_inode:
                # File was rotated, reset position
                logger.info(f"Log file rotated. Starting from beginning.")
                self.last_position = 0
            
            self._last_inode = current_inode
            
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to last known position
                f.seek(self.last_position)
                
                # Read new lines
                new_lines = f.readlines()
                self.last_position = f.tell()
                
                # Process each new line
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    ip = self._extract_ip(line)
                    if ip:
                        # Check rate-based attacks first (DDoS)
                        rate_attack = self._check_rate_based_attacks(ip, line)
                        
                        # Check pattern-based attacks
                        pattern_attack = self.attack_detector.detect_attack(line, source="web")
                        
                        # Use highest severity attack
                        attack_info = None
                        if rate_attack and pattern_attack:
                            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                            if severity_order.get(rate_attack["severity"], 0) >= severity_order.get(pattern_attack["severity"], 0):
                                attack_info = rate_attack
                            else:
                                attack_info = pattern_attack
                        else:
                            attack_info = rate_attack or pattern_attack
                        
                        if attack_info:
                            logger.debug(f"Attack detected: {attack_info['description']} from IP: {ip}")
                            self.callback(ip, line, attack_info)
                            
        except PermissionError:
            logger.error(f"Permission denied reading {self.log_path}. Run with appropriate permissions.")
        except Exception as e:
            logger.error(f"Error processing log file: {e}")
    
    def _extract_ip(self, log_line: str) -> Optional[str]:
        """
        Extract IP address from a log line.
        
        Args:
            log_line: Log line to parse
            
        Returns:
            IP address if found, None otherwise
        """
        # Common web log formats:
        # Apache: IP - - [timestamp] "method path protocol" status size
        # Nginx: IP - - [timestamp] "method path protocol" status size "referer" "user-agent"
        
        ip_patterns = [
            r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # IP at start of line
            r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b',  # Any IPv4
        ]
        
        for pattern in ip_patterns:
            match = re.search(pattern, log_line)
            if match:
                ip = match.group(1) if match.groups() else match.group(0)
                # Validate IP format
                try:
                    parts = ip.split('.')
                    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                        return ip
                except ValueError:
                    continue
        
        return None
    
    def _check_rate_based_attacks(self, ip: str, log_line: str) -> Optional[Dict]:
        """Detect DDoS and rate-based attacks by tracking request frequency."""
        now = time_module.time()
        window = self._ddos_window
        threshold = self._ddos_threshold
        
        # Add current request timestamp
        self._ip_request_times[ip].append(now)
        
        # Keep only requests within the window
        self._ip_request_times[ip] = [
            t for t in self._ip_request_times[ip]
            if now - t <= window
        ]
        
        request_count = len(self._ip_request_times[ip])
        
        # DDoS detection: too many requests in window
        if request_count >= threshold:
            return {
                "attack_type": "ddos",
                "severity": "critical",
                "description": f"DDoS attack detected -- {request_count} requests in {window}s",
                "pattern_matched": f"{request_count}_requests_in_{window}s",
                "timestamp": datetime.now().isoformat(),
                "source": "web",
                "request_count": request_count,
                "time_window": window
            }
        
        # High rate warning: 20+ requests in window
        if request_count >= 20:
            return {
                "attack_type": "high_request_rate",
                "severity": "medium",
                "description": f"High request rate -- {request_count} requests in {window}s",
                "pattern_matched": f"{request_count}_requests_in_{window}s",
                "timestamp": datetime.now().isoformat(),
                "source": "web",
                "request_count": request_count
            }
        
        return None


class WebSensor:
    """Sensor for monitoring web access logs."""
    
    def __init__(self, callback: Callable[[str, str, dict], None], log_path: Optional[str] = None):
        """
        Initialize the web access log sensor.
        
        Args:
            callback: Function to call when suspicious activity is detected
                     Signature: callback(ip_address, log_line, attack_info)
            log_path: Path to the access log file
        """
        if not log_path or log_path.isspace():
            log_path = os.getenv("WEB_LOG_PATH", "/var/log/apache2/access.log")
        self.callback = callback
        self.log_path = log_path
        self.observer = None
        self.handler = None
    
    def start(self):
        """Start monitoring the log file."""
        log_file = Path(self.log_path)
        log_dir = log_file.parent
        
        if not log_dir.exists():
            logger.warning(f"Log directory {log_dir} does not exist. Creating it for testing.")
            log_dir.mkdir(parents=True, exist_ok=True)
            # Create empty log file if it doesn't exist
            if not log_file.exists():
                log_file.touch()
        
        self.handler = WebLogHandler(self.callback, self.log_path)
        self.observer = Observer()
        self.observer.schedule(self.handler, path=str(log_dir), recursive=False)
        self.observer.start()
        
        logger.info(f"Web sensor started. Monitoring {self.log_path}")
        
        # Process existing file content on startup
        self.handler._process_new_lines()
    
    def stop(self):
        """Stop monitoring the log file."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Web sensor stopped")
    
    def is_alive(self) -> bool:
        """Check if the sensor is running."""
        return self.observer is not None and self.observer.is_alive()
