"""
Sentinel Agent - Main Entry Point
Autonomous multi-agent AI SOC analyst for Linux.
"""

import json
import sys
import subprocess
import re
from typing import Dict, Any
from crewai import Crew, Process
from sensors.auth_sensor import AuthSensor
from sensors.web_sensor import WebSensor
from tasks import create_security_incident_tasks, parse_agent_response
from defense.attack_logger import AttackLogger
from defense.attack_detector import AttackDetector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentinelAgent:
    """Main Sentinel Agent orchestrator with multi-vector ingestion."""
    
    def __init__(self, auth_log_path: str = "/var/log/auth.log", web_log_path: str = "/var/log/apache2/access.log"):
        """
        Initialize the Sentinel Agent with multi-vector sensors.
        
        Args:
            auth_log_path: Path to the authentication log file
            web_log_path: Path to the web access log file (Apache/Nginx)
        """
        self.auth_log_path = auth_log_path
        self.web_log_path = web_log_path
        self.auth_sensor = None
        self.web_sensor = None
        self.incident_history = []
        self.ip_tracking = {}  # Track IPs across multiple vectors
        self.attack_logger = AttackLogger()
        self.attack_detector = AttackDetector()
    
    def handle_security_event(self, ip_address: str, log_line: str, attack_info: dict = None, source: str = "auth"):
        """
        Handle a security event by orchestrating the AI crew.
        
        Args:
            ip_address: The suspicious IP address
            log_line: The log line that triggered the alert
            attack_info: Attack detection information dictionary
            source: Source of the event ("auth" or "web")
        """
        # Detect attack type if not provided
        if not attack_info:
            attack_info = self.attack_detector.detect_attack(log_line, source=source)
            if not attack_info:
                attack_info = {
                    "attack_type": "unknown",
                    "severity": "medium",
                    "description": "Suspicious activity detected",
                    "source": source
                }
        
        # Log the attack
        attack_record = self.attack_logger.log_attack(
            ip_address=ip_address,
            attack_type=attack_info.get("attack_type", "unknown"),
            log_line=log_line,
            source=source,
            severity=attack_info.get("severity", "medium"),
            description=attack_info.get("description", "Suspicious activity")
        )
        
        logger.info(f"🚨 {attack_info.get('description', 'Security event')}: IP {ip_address} (Source: {source})")
        logger.info(f"   Attack Type: {attack_info.get('attack_type', 'unknown')}")
        logger.info(f"   Severity: {attack_info.get('severity', 'medium')}")
        logger.info(f"   Log line: {log_line}")
        
        # Track IP across multiple vectors
        if ip_address not in self.ip_tracking:
            self.ip_tracking[ip_address] = {
                "auth_events": [],
                "web_events": [],
                "first_seen": None,
                "last_seen": None,
                "attack_types": []
            }
        
        if source == "auth":
            self.ip_tracking[ip_address]["auth_events"].append(log_line)
        else:
            self.ip_tracking[ip_address]["web_events"].append(log_line)
        
        # Track attack types
        attack_type = attack_info.get("attack_type", "unknown")
        if attack_type not in self.ip_tracking[ip_address]["attack_types"]:
            self.ip_tracking[ip_address]["attack_types"].append(attack_type)
        
        try:
            # Create tasks for the crew with attack information
            tasks = create_security_incident_tasks(
                ip_address, 
                log_line, 
                attack_type=attack_info.get("attack_type", "unknown"),
                severity=attack_info.get("severity", "medium")
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[task.agent for task in tasks],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            logger.info("🤖 Starting AI crew analysis...")
            result = crew.kickoff()
            
            # Parse and display results
            logger.info("\n" + "="*80)
            logger.info("📊 ANALYSIS RESULTS")
            logger.info("="*80)
            
            # Try to extract structured data from the result
            final_report = self._extract_final_report(result, ip_address, log_line)
            
            # Store incident
            incident_record = {
                "ip": ip_address,
                "log_line": log_line,
                "report": final_report,
                "timestamp": self._get_timestamp(),
                "attack_type": attack_info.get("attack_type", "unknown"),
                "severity": attack_info.get("severity", "medium"),
                "attack_record_id": attack_record.get("id")
            }
            self.incident_history.append(incident_record)
            
            # Update attack record with actions taken
            if attack_record.get("id") and final_report.get("action_required"):
                action_details = f"Firewall rule: {final_report.get('firewall_rule', 'N/A')}"
                self.attack_logger.add_action(
                    attack_id=attack_record["id"],
                    action_type="firewall_block",
                    action_details=action_details,
                    success=final_report.get("firewall_rule_verified", False)
                )
            
            # Check if action is required
            if final_report.get("action_required", False):
                self._handle_remediation(final_report, ip_address)
            else:
                logger.info("ℹ️  No immediate action required. Monitoring recommended.")
            
            logger.info("="*80 + "\n")
            
        except Exception as e:
            logger.error(f"Error processing security event: {e}", exc_info=True)
    
    def _extract_final_report(self, result: Any, ip_address: str, log_line: str) -> Dict[str, Any]:
        """
        Extract the final report from crew results.
        
        Args:
            result: Crew execution result
            ip_address: IP address involved
            log_line: Original log line
            
        Returns:
            Structured report dictionary
        """
        report = {
            "ip_address": ip_address,
            "log_line": log_line,
            "action_required": False,
            "firewall_rule": None,
            "severity": "unknown",
            "threat_level": "unknown"
        }
        
        # Try to parse the result
        if hasattr(result, 'raw'):
            result_str = str(result.raw)
        else:
            result_str = str(result)
        
        # Look for JSON in the result
        try:
            # Find the last task's output (incident responder)
            json_match = re.search(r'\{[^{}]*"action_required"[^{}]*\}', result_str, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                report.update(parsed)
            else:
                # Try to find any JSON
                json_start = result_str.find('{')
                json_end = result_str.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(result_str[json_start:json_end])
                    report.update(parsed)
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Could not parse structured JSON from agent response")
            report["raw_response"] = result_str
        
        # Extract firewall rule if present
        if "firewall_rule" not in report or not report["firewall_rule"]:
            # Try to find iptables command in the response
            iptables_match = re.search(r'iptables\s+[^\n]+', result_str)
            if iptables_match:
                report["firewall_rule"] = iptables_match.group(0)
        
        return report
    
    def _handle_remediation(self, report: Dict[str, Any], ip_address: str):
        """
        Handle remediation actions with human-in-the-loop approval.
        
        Args:
            report: The security report
            ip_address: IP address to block
        """
        firewall_rule = report.get("firewall_rule")
        
        if not firewall_rule:
            logger.warning("No firewall rule found in report")
            return
        
        logger.info(f"\n⚠️  REMEDIATION REQUIRED")
        logger.info(f"IP Address: {ip_address}")
        logger.info(f"Severity: {report.get('severity', 'unknown')}")
        logger.info(f"Threat Level: {report.get('threat_level', 'unknown')}")
        logger.info(f"\nProposed Firewall Rule:")
        logger.info(f"  {firewall_rule}")
        
        # Human-in-the-loop approval
        print("\n" + "="*80)
        print("🛡️  SECURITY ACTION REQUIRES APPROVAL")
        print("="*80)
        print(f"IP to block: {ip_address}")
        print(f"Command: {firewall_rule}")
        print("\nThis action will block the IP address using iptables.")
        print("="*80)
        
        response = input("\nDo you want to execute this firewall rule? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            self._execute_firewall_rule(firewall_rule, ip_address)
        else:
            logger.info("❌ Action cancelled by user")
    
    def _execute_firewall_rule(self, rule: str, ip_address: str):
        """
        Execute firewall rule with additional human confirmation.
        
        Args:
            rule: The iptables command to execute
            ip_address: IP address being blocked
        """
        # Extract just the iptables command (safety check)
        if not rule.startswith("iptables"):
            logger.error(f"Invalid firewall rule format: {rule}")
            return
        
        # Final confirmation
        print(f"\n⚠️  FINAL CONFIRMATION")
        print(f"About to execute: {rule}")
        final_confirm = input("Type 'EXECUTE' to proceed, or anything else to cancel: ").strip()
        
        if final_confirm != "EXECUTE":
            logger.info("❌ Execution cancelled")
            return
        
        try:
            logger.info(f"🔒 Executing firewall rule: {rule}")
            
            # Execute the command
            result = subprocess.run(
                rule.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully blocked IP: {ip_address}")
                logger.info(f"Command output: {result.stdout}")
            else:
                logger.error(f"❌ Failed to execute firewall rule")
                logger.error(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Command execution timeout")
        except FileNotFoundError:
            logger.error("❌ iptables command not found. Ensure you're on a Linux system with iptables installed.")
        except PermissionError:
            logger.error("❌ Permission denied. Run with sudo privileges.")
        except Exception as e:
            logger.error(f"❌ Error executing firewall rule: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def start(self):
        """Start the Sentinel Defense Module with multi-vector monitoring."""
        logger.info("🚀 Starting Sentinel Defense Module...")
        logger.info(f"📁 Monitoring auth log: {self.auth_log_path}")
        logger.info(f"📁 Monitoring web log: {self.web_log_path}")
        logger.info("🤖 AI Crew ready with Ollama Local LLM")
        logger.info("🛡️  Multi-Vector Ingestion: Active")
        logger.info("="*80)
        
        # Initialize and start both sensors
        self.auth_sensor = AuthSensor(
            callback=lambda ip, line, attack_info: self.handle_security_event(ip, line, attack_info, "auth"),
            log_path=self.auth_log_path
        )
        
        self.web_sensor = WebSensor(
            callback=lambda ip, line, attack_info: self.handle_security_event(ip, line, attack_info, "web"),
            log_path=self.web_log_path
        )
        
        try:
            # Start both sensors
            self.auth_sensor.start()
            self.web_sensor.start()
            
            logger.info("✅ Sentinel Defense Module is now monitoring for security events...")
            logger.info("   - Auth log monitoring: ACTIVE")
            logger.info("   - Web log monitoring: ACTIVE")
            logger.info("   - Cross-correlation: ENABLED")
            logger.info("   - Resilience loop: ENABLED")
            logger.info("Press Ctrl+C to stop\n")
            
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down Sentinel Defense Module...")
            if self.auth_sensor:
                self.auth_sensor.stop()
            if self.web_sensor:
                self.web_sensor.stop()
            logger.info("✅ Shutdown complete")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
            if self.auth_sensor:
                self.auth_sensor.stop()
            if self.web_sensor:
                self.web_sensor.stop()
            sys.exit(1)


def check_environment():
    """Check if running in a virtual environment and verify dependencies."""
    import sys
    import importlib.util
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        logger.warning("⚠️  Not running in a virtual environment!")
        logger.warning("   It's recommended to use a virtual environment for isolation.")
        logger.warning("   Run: python -m venv venv && source venv/bin/activate")
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            logger.info("Exiting. Please activate your virtual environment first.")
            sys.exit(1)
    
    # Check critical dependencies
    required_modules = ['crewai', 'langchain_community', 'watchdog']
    missing = []
    
    for module in required_modules:
        if importlib.util.find_spec(module) is None:
            missing.append(module)
    
    if missing:
        logger.error(f"❌ Missing required modules: {', '.join(missing)}")
        logger.error("   Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("✅ Environment check passed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sentinel Defense Module - Multi-Vector AI SOC Analyst")
    parser.add_argument(
        "--auth-log",
        default="/var/log/auth.log",
        help="Path to the authentication log file (default: /var/log/auth.log)"
    )
    parser.add_argument(
        "--web-log",
        default="/var/log/apache2/access.log",
        help="Path to the web access log file (default: /var/log/apache2/access.log)"
    )
    parser.add_argument(
        "--skip-env-check",
        action="store_true",
        help="Skip environment validation check"
    )
    
    args = parser.parse_args()
    
    # Check environment unless skipped
    if not args.skip_env_check:
        check_environment()
    
    # Create and start the agent with multi-vector sensors
    agent = SentinelAgent(auth_log_path=args.auth_log, web_log_path=args.web_log)
    agent.start()


if __name__ == "__main__":
    main()
