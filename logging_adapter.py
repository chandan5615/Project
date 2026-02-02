"""
Sentinel Agent Adaptive Logging Layer
Adjusts logging and output behavior based on environment detection
- GUI mode: Heartbeat messages to console, detailed logs to file
- CLI mode: Rich terminal dashboard
- Docker/systemd mode: Logging only (no interactive UI)
"""

import logging
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path


class AdaptiveLogger:
    """Adaptive logger that changes behavior based on environment"""
    
    def __init__(self, 
                 mode: str = "cli",
                 log_file: str = "app/logs/sentinel.log",
                 console_level: int = logging.WARNING,
                 file_level: int = logging.DEBUG):
        """
        Initialize adaptive logger
        
        Args:
            mode: Environment mode ("gui", "cli", "docker", "systemd")
            log_file: Path to log file
            console_level: Console logging level
            file_level: File logging level
        """
        self.mode = mode
        self.log_file = log_file
        self.console_level = console_level
        self.file_level = file_level
        self.logger = logging.getLogger("sentinel")
        self.heartbeat_count = 0
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging handlers based on mode"""
        # Clear existing handlers
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler (always present)
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (conditional based on mode)
        if self.mode in ["gui", "cli"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.console_level)
            
            if self.mode == "gui":
                # Simple format for GUI heartbeat
                console_formatter = logging.Formatter(
                    '[%(asctime)s] %(message)s',
                    datefmt='%H:%M'
                )
            else:
                # Standard format for CLI
                console_formatter = logging.Formatter(
                    '%(levelname)-8s | %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def heartbeat(self, threat_count: int = 0, blocked_ips: int = 0):
        """Log heartbeat message (for GUI mode)
        
        Args:
            threat_count: Number of threats in last interval
            blocked_ips: Number of unique blocked IPs
        """
        self.heartbeat_count += 1
        
        if self.mode == "gui":
            # Minimal output for GUI mode
            msg = f"Monitoring Active"
            if threat_count > 0:
                msg += f" - {threat_count} Threat{'s' if threat_count != 1 else ''}"
            if blocked_ips > 0:
                msg += f" - {blocked_ips} Blocked IP{'s' if blocked_ips != 1 else ''}"
            
            self.logger.info(msg)
        elif self.mode == "cli":
            # More detailed output for CLI mode
            msg = f"Checkpoint {self.heartbeat_count}: "
            msg += f"Threats={threat_count}, Blocked_IPs={blocked_ips}"
            self.logger.info(msg)
        # Docker/systemd modes log silently (only file)
    
    def log_threat_detected(self, threat_type: str, source_ip: str, action: str):
        """Log threat detection
        
        Args:
            threat_type: Type of threat detected
            source_ip: Source IP of threat
            action: Action taken (block, quarantine, etc.)
        """
        msg = f"[THREAT] {threat_type} from {source_ip} - Action: {action}"
        
        if self.mode in ["gui", "cli"]:
            self.logger.warning(msg)
        else:
            self.logger.info(msg)
    
    def log_system_status(self, status: str, details: str = ""):
        """Log system status message
        
        Args:
            status: Status type (started, stopped, error, etc.)
            details: Additional details
        """
        msg = f"[STATUS] {status}"
        if details:
            msg += f" - {details}"
        
        self.logger.info(msg)
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log error message
        
        Args:
            error_msg: Error message
            exception: Optional exception object
        """
        if exception:
            self.logger.error(f"{error_msg}: {exception}", exc_info=True)
        else:
            self.logger.error(error_msg)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger object"""
        return self.logger


class AdaptivePrinter:
    """Adaptive print function that respects environment"""
    
    def __init__(self, mode: str = "cli"):
        """
        Initialize adaptive printer
        
        Args:
            mode: Environment mode ("gui", "cli", "docker", "systemd")
        """
        self.mode = mode
    
    def print_dashboard_header(self):
        """Print dashboard header (CLI mode only)"""
        if self.mode == "cli":
            print("\n" + "="*60)
            print("🛡️  SENTINEL AGENT - SECURITY DASHBOARD")
            print("="*60 + "\n")
    
    def print_threat_alert(self, threat_type: str, source_ip: str, action: str):
        """Print threat alert
        
        Args:
            threat_type: Type of threat
            source_ip: Source IP
            action: Action taken
        """
        if self.mode == "cli":
            print(f"⚠️  THREAT: {threat_type} from {source_ip}")
            print(f"   Action: {action}\n")
        elif self.mode == "gui":
            # GUI mode keeps alerts silent (shown in dashboard)
            pass
    
    def print_status_message(self, message: str):
        """Print status message
        
        Args:
            message: Status message to print
        """
        if self.mode in ["cli"]:
            print(f"ℹ️  {message}")
        elif self.mode == "gui":
            # GUI mode suppresses non-critical messages
            if "error" in message.lower():
                print(f"⚠️  {message}")
    
    def print_network_summary(self, total_threats: int, blocked_ips: int, 
                             security_score: int):
        """Print network summary (CLI mode only)
        
        Args:
            total_threats: Total threats detected
            blocked_ips: Number of blocked IPs
            security_score: Security score 0-100
        """
        if self.mode == "cli":
            print(f"\n📊 Network Summary:")
            print(f"   Threats Detected: {total_threats}")
            print(f"   Blocked IPs: {blocked_ips}")
            print(f"   Security Score: {security_score}%")
            print()


def create_adaptive_logger(environment_config: dict) -> AdaptiveLogger:
    """Factory function to create adaptive logger from environment config
    
    Args:
        environment_config: Config dict from environment_detector
        
    Returns:
        AdaptiveLogger instance configured for environment
    """
    mode = environment_config.get("mode", "cli")
    log_file = environment_config.get("log_path", "app/logs/sentinel.log")
    
    return AdaptiveLogger(
        mode=mode,
        log_file=log_file,
        console_level=logging.WARNING,
        file_level=logging.DEBUG
    )


def create_adaptive_printer(environment_config: dict) -> AdaptivePrinter:
    """Factory function to create adaptive printer from environment config
    
    Args:
        environment_config: Config dict from environment_detector
        
    Returns:
        AdaptivePrinter instance configured for environment
    """
    mode = environment_config.get("mode", "cli")
    return AdaptivePrinter(mode=mode)


if __name__ == "__main__":
    # Example usage
    config = {
        "mode": "cli",
        "log_path": "sentinel.log"
    }
    
    logger = create_adaptive_logger(config)
    printer = create_adaptive_printer(config)
    
    # Test various logging functions
    printer.print_dashboard_header()
    printer.print_status_message("System initialized successfully")
    
    logger.heartbeat(threat_count=3, blocked_ips=2)
    logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
    logger.log_system_status("Monitoring", "All sensors active")
    
    printer.print_network_summary(15, 5, 78)
