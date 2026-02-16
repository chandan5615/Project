"""
Test Attack Generator for Sentinel Agent
Generates simulated attack logs to test the detection system
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _is_docker() -> bool:
    """Detect if running inside a Docker container."""
    if os.path.exists("/.dockerenv"):
        return True
    try:
        with open("/proc/self/cgroup", "r", encoding="utf-8") as f:
            return "docker" in f.read()
    except OSError:
        return False


def _resolve_writable_log_path(path: str, docker_fallback: str) -> str:
    """Resolve a writable log path, falling back inside Docker if needed."""
    if not path or path.isspace():
        path = docker_fallback

    if _is_docker():
        target_dir = os.path.dirname(path) or "."
        if os.path.exists(path):
            if not os.access(path, os.W_OK):
                logger.warning("Log file not writable in container, using %s", docker_fallback)
                return docker_fallback
        elif not os.access(target_dir, os.W_OK):
            logger.warning("Log directory not writable in container, using %s", docker_fallback)
            return docker_fallback

    return path


class TestAttackGenerator:
    """Generates simulated attacks for testing the Sentinel Agent"""

    __test__ = False
    
    # Common attacking IPs to use
    ATTACKING_IPS = [
        "192.168.1.100",
        "10.0.0.50",
        "172.16.0.25",
        "203.0.113.42",
        "198.51.100.88",
        "192.0.2.12",
        "198.51.100.199",
        "203.0.113.75",
    ]
    
    # Auth log attack patterns
    AUTH_LOG_ATTACKS = [
        "Failed password for root from {ip} port 22 ssh2",
        "Invalid user admin from {ip} port 22",
        "Failed password for invalid user test from {ip} port 22 ssh2",
        "authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost={ip}  user=root",
        "authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost={ip}  user=admin",
        "Failed password for {ip} port 22 ssh2 [preauth]",
    ]
    
    # Web log attack patterns
    WEB_LOG_ATTACKS = [
        '{ip} - - [{timestamp}] "GET /admin HTTP/1.1" 401 1234 "-" "Mozilla/5.0 (scanning)"',
        '{ip} - - [{timestamp}] "POST /login HTTP/1.1" 200 5678 "-" "python-requests/2.28.0"',
        '{ip} - - [{timestamp}] "GET /index.php?id=1\' OR \'1\'=\'1 HTTP/1.1" 200 1234',
        '{ip} - - [{timestamp}] "GET / HTTP/1.1" 403 0 "-" "-"',
        '{ip} - - [{timestamp}] "POST /api/users HTTP/1.1" 401 1234',
        '{ip} - - [{timestamp}] "GET /../../../etc/passwd HTTP/1.1" 400 0',
    ]
    
    def __init__(self,
                 auth_log_path: str = "/var/log/auth.log",
                 web_log_path: str = "/var/log/apache2/access.log"):
        resolved_auth = _resolve_writable_log_path(auth_log_path, "/app/logs/auth.log")
        resolved_web = _resolve_writable_log_path(web_log_path, "/app/logs/access.log")
        self.auth_log_path = Path(resolved_auth)
        self.web_log_path = Path(resolved_web)
        self.attack_count = 0
    
    def generate_auth_log_attacks(self, count: int = 10):
        """Generate simulated auth log attacks"""
        logger.info(f"Generating {count} auth log attacks...")
        
        # Ensure log file exists
        self.auth_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.auth_log_path, 'a', encoding='utf-8') as f:
                for i in range(count):
                    ip = random.choice(self.ATTACKING_IPS)
                    pattern = random.choice(self.AUTH_LOG_ATTACKS)
                    timestamp = (datetime.now() - timedelta(seconds=random.randint(0, 3600))).strftime("%b %d %H:%M:%S")
                    
                    # Format the log entry
                    log_entry = pattern.format(ip=ip, timestamp=timestamp)
                    if not log_entry.startswith(timestamp):
                        log_entry = f"{timestamp} ubuntu {log_entry}"
                    
                    f.write(log_entry + "\n")
                    logger.info(f"  [{i+1}/{count}] {ip} - brute force")
                    self.attack_count += 1
                    time.sleep(0.1)  # Small delay between entries
            
            logger.info(f"✓ Generated {count} auth log attacks")
        except Exception as e:
            logger.error(f"✗ Error writing to auth.log: {e}")
    
    def generate_web_log_attacks(self, count: int = 10):
        """Generate simulated web log attacks"""
        logger.info(f"Generating {count} web log attacks...")
        
        # Ensure log file exists
        self.web_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.web_log_path, 'a', encoding='utf-8') as f:
                for i in range(count):
                    ip = random.choice(self.ATTACKING_IPS)
                    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
                    pattern = random.choice(self.WEB_LOG_ATTACKS)
                    
                    log_entry = pattern.format(ip=ip, timestamp=timestamp)
                    
                    f.write(log_entry + "\n")
                    logger.info(f"  [{i+1}/{count}] {ip} - web attack")
                    self.attack_count += 1
                    time.sleep(0.1)
            
            logger.info(f"✓ Generated {count} web log attacks")
        except Exception as e:
            logger.error(f"✗ Error writing to web log: {e}")
    
    def generate_all_attacks(self, auth_count: int = 15, web_count: int = 15):
        """Generate all test attacks"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("SENTINEL AGENT TEST ATTACK GENERATOR")
        logger.info("=" * 60)
        logger.info("")
        
        self.generate_auth_log_attacks(auth_count)
        logger.info("")
        self.generate_web_log_attacks(web_count)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✓ GENERATED {self.attack_count} TOTAL ATTACKS")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. The Sentinel Agent will detect these attacks")
        logger.info("2. Check the dashboard for detected incidents")
        logger.info("3. Monitor /app/logs/sentinel.log for results")
        logger.info("")

        if _is_docker() and ("/app/logs" in str(self.auth_log_path) or "/app/logs" in str(self.web_log_path)):
            logger.info("NOTE: Using /app/logs for test data. Ensure sensors read the same paths:")
            logger.info("  AUTH_LOG_PATH=/app/logs/auth.log")
            logger.info("  WEB_LOG_PATH=/app/logs/access.log")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test attacks for Sentinel Agent")
    parser.add_argument("--auth-count", type=int, default=15, help="Number of auth log attacks to generate")
    parser.add_argument("--web-count", type=int, default=15, help="Number of web log attacks to generate")
    parser.add_argument("--auth-log", default=os.getenv("AUTH_LOG_PATH", "/var/log/auth.log"), help="Path to auth.log")
    parser.add_argument("--web-log", default=os.getenv("WEB_LOG_PATH", "/var/log/apache2/access.log"), help="Path to web access log")
    
    args = parser.parse_args()
    
    generator = TestAttackGenerator(
        auth_log_path=args.auth_log,
        web_log_path=args.web_log
    )
    
    generator.generate_all_attacks(
        auth_count=args.auth_count,
        web_count=args.web_count
    )


if __name__ == "__main__":
    main()
