"""
Sentinel Agent - Adaptive Reporting System Integration Example
Shows how to integrate environment detection, logging, and dashboards
"""

import sys
import logging
import time
from pathlib import Path

# Import adaptive components
from environment_detector import EnvironmentDetector
from logging_adapter import create_adaptive_logger, create_adaptive_printer
from dashboard_controller import create_dashboard_controller


class SentinelAgentAdaptive:
    """Main Sentinel Agent with adaptive reporting system"""
    
    def __init__(self):
        """Initialize Sentinel Agent with adaptive reporting"""
        # Step 1: Detect environment
        self.detector = EnvironmentDetector()
        self.env_config = self.detector.get_environment_config()
        
        print(f"\n[INFO] Environment Detection:")
        print(f"  Mode: {self.env_config['mode']}")
        print(f"  Database: {self.env_config['db_path']}")
        if self.env_config['mode'] == 'gui':
            print(f"  Dashboard: {self.env_config['dashboard_url']}")
        print()
        
        # Step 2: Setup adaptive logging
        self.logger = create_adaptive_logger(self.env_config)
        self.printer = create_adaptive_printer(self.env_config)
        
        # Step 3: Setup dashboard controller
        self.dashboard_controller = create_dashboard_controller(self.env_config)
        
        # Get the actual logger instance
        self.log = self.logger.get_logger()
    
    def initialize(self) -> bool:
        """Initialize Sentinel Agent and dashboards"""
        try:
            self.logger.log_system_status("Initializing Sentinel Agent", 
                                         f"Environment: {self.env_config['mode']}")
            
            # Start appropriate dashboard
            if not self.dashboard_controller.start_dashboard():
                self.logger.log_system_status("Dashboard disabled", 
                                             f"Mode: {self.env_config['mode']}")
            
            self.logger.log_system_status("Initialization complete", 
                                         "All sensors and dashboards ready")
            return True
        
        except Exception as e:
            self.logger.log_error("Initialization failed", e)
            return False
    
    def run_monitoring_loop(self, duration: int = 60):
        """Run monitoring loop with heartbeat
        
        Args:
            duration: How long to monitor (seconds)
        """
        self.printer.print_dashboard_header()
        
        start_time = time.time()
        heartbeat_interval = 10  # Seconds between heartbeats
        last_heartbeat = start_time
        
        try:
            while time.time() - start_time < duration:
                # Simulate threat detection and actions
                # In real scenario, this would come from sensors/agents
                
                current_time = time.time()
                
                # Send heartbeat at intervals
                if current_time - last_heartbeat >= heartbeat_interval:
                    # Get stats from database
                    threat_count = self._get_recent_threat_count()
                    blocked_ips = self._get_blocked_ip_count()
                    
                    # Send heartbeat
                    self.logger.heartbeat(threat_count, blocked_ips)
                    
                    last_heartbeat = current_time
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.log_system_status("Monitoring interrupted by user")
        except Exception as e:
            self.logger.log_error("Error in monitoring loop", e)
        finally:
            self.shutdown()
    
    def log_threat(self, threat_type: str, source_ip: str, action: str):
        """Log a detected threat
        
        Args:
            threat_type: Type of threat
            source_ip: Source IP address
            action: Action taken
        """
        self.logger.log_threat_detected(threat_type, source_ip, action)
        self.printer.print_threat_alert(threat_type, source_ip, action)
    
    def _get_recent_threat_count(self) -> int:
        """Get count of recent threats (simulated)"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.env_config['db_path'])
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE timestamp > datetime('now', '-5 minutes')
            """)
            
            count = cursor.fetchone()[0] or 0
            conn.close()
            return count
        except:
            return 0
    
    def _get_blocked_ip_count(self) -> int:
        """Get count of recently blocked IPs (simulated)"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.env_config['db_path'])
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(DISTINCT source_ip) FROM incidents 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            
            count = cursor.fetchone()[0] or 0
            conn.close()
            return count
        except:
            return 0
    
    def shutdown(self):
        """Shutdown Sentinel Agent and dashboards"""
        try:
            self.logger.log_system_status("Shutting down", "Stopping dashboards")
            self.dashboard_controller.stop_dashboard()
            self.logger.log_system_status("Shutdown complete")
        except Exception as e:
            self.logger.log_error("Error during shutdown", e)


def main():
    """Main entry point for adaptive Sentinel Agent"""
    
    print("="*60)
    print("🛡️  SENTINEL AGENT - ADAPTIVE REPORTING SYSTEM")
    print("="*60)
    
    # Create and initialize agent
    agent = SentinelAgentAdaptive()
    
    if not agent.initialize():
        print("[ERROR] Failed to initialize Sentinel Agent")
        sys.exit(1)
    
    # Run monitoring loop
    print("\n[INFO] Starting 60-second monitoring session...")
    print("Press Ctrl+C to stop\n")
    
    agent.run_monitoring_loop(duration=60)


if __name__ == "__main__":
    main()
