"""
Sentinel Agent v2.2 - Main Entry Point
Autonomous multi-agent AI SOC analyst for Linux systems.
Production-ready enterprise security operations center.

Features:
- Feature 2: Offline threat intelligence with IP reputation
- Feature 3: JWT token-based authentication & API keys
- Feature 4: IP/pattern whitelist and blacklist management
- Feature 7: Real-time performance metrics tracking
- Feature 8: 20+ REST API endpoints for external integration
- Feature 10: 4-factor ML-based anomaly scoring algorithm

Author: Sentinel Security Team
Version: 2.2.0
GitHub: https://github.com/[your-username]/sentinel-agent
"""

import json
import sys
import subprocess
import re
from typing import Dict, Any, Optional
import os
from crewai import Crew, Process
from sensors.auth_sensor import AuthSensor
from sensors.web_sensor import WebSensor
from tasks import create_security_incident_tasks, parse_agent_response
from defense.attack_logger import AttackLogger
from defense.attack_detector import AttackDetector
from output_formatter import OutputFormatter, print_alert, print_report, print_success, print_error
from data_engine import get_engine
import logging

# Import new feature modules
from threat_intelligence import get_threat_intelligence
from auth import get_authenticator
from list_manager import get_list_manager
from metrics import get_metrics
from anomaly_scorer import get_anomaly_scorer
from environment_detector import EnvironmentDetector

# Initialize data engine (SQLite)
data_engine = get_engine()

# Configure logging: quiet console (WARNING+) and rotating file for INFO/DEBUG
LOG_DIR = os.getenv('SENTINEL_LOG_DIR', '/app/logs')
LOG_FILE = os.path.join(LOG_DIR, 'sentinel.log')
os.makedirs(LOG_DIR, exist_ok=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Rotating file handler captures INFO and DEBUG
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# Console handler set to WARNING to keep terminal quiet
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)


def _resolve_log_path(preferred_path: Optional[str], default_path: str, docker_fallback: str) -> str:
    """Resolve log path with Docker-aware fallback when unreadable."""
    path = preferred_path if preferred_path and not preferred_path.isspace() else default_path

    if EnvironmentDetector.is_docker():
        if not os.path.exists(path) or not os.access(path, os.R_OK):
            logger.warning(
                "Log path not readable in container, falling back: %s -> %s",
                path,
                docker_fallback,
            )
            return docker_fallback

    return path


class SentinelAgent:
    """Main Sentinel Agent orchestrator with multi-vector ingestion."""
    
    def __init__(self, auth_log_path: str = "/var/log/auth.log", web_log_path: str = "/var/log/apache2/access.log"):
        """
        Initialize the Sentinel Agent with multi-vector sensors.
        
        Args:
            auth_log_path: Path to the authentication log file
            web_log_path: Path to the web access log file (Apache/Nginx)
        """
        auth_env = os.getenv("AUTH_LOG_PATH")
        web_env = os.getenv("WEB_LOG_PATH")

        self.auth_log_path = _resolve_log_path(
            auth_env or auth_log_path,
            "/var/log/auth.log",
            "/app/logs/auth.log",
        )
        self.web_log_path = _resolve_log_path(
            web_env or web_log_path,
            "/var/log/apache2/access.log",
            "/app/logs/access.log",
        )
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
        # Initialize feature modules
        threat_intel = get_threat_intelligence()
        list_mgr = get_list_manager()
        perf_metrics = get_metrics()
        anomaly_scorer = get_anomaly_scorer()
        
        # FEATURE 4: Check whitelist before processing
        if list_mgr.is_ip_whitelisted(ip_address):
            logger.info(f"IP {ip_address} is whitelisted - skipping analysis")
            return
        
        # Record detection start for metrics
        detection_start_time = perf_metrics.get_current_timestamp()
        
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
        
        # FEATURE 2: Check threat intelligence
        threat_result = threat_intel.check_ip_reputation(ip_address)
        if threat_result.get('is_malicious'):
            logger.warning(f"IP {ip_address} is in threat database: {threat_result.get('threat_level')}")
            attack_info['threat_level'] = threat_result.get('threat_level')
        
        # FEATURE 10: Calculate anomaly score
        incident_data = {
            "ip": ip_address,
            "attack_type": attack_info.get("attack_type", "unknown"),
            "severity": attack_info.get("severity", "medium"),
            "source": source
        }
        
        anomaly_result = anomaly_scorer.calculate_anomaly_score(incident_data)
        anomaly_score = anomaly_result.get('anomaly_score', 0)
        logger.info(f"Anomaly score for {ip_address}: {anomaly_score:.2f} ({anomaly_result.get('recommendation')})")
        
        # Log the attack
        attack_record = self.attack_logger.log_attack(
            ip_address=ip_address,
            attack_type=attack_info.get("attack_type", "unknown"),
            log_line=log_line,
            source=source,
            severity=attack_info.get("severity", "medium"),
            description=attack_info.get("description", "Suspicious activity")
        )
        
        # Display professional alert (logged to rotating file) and persist incident
        logger.info(OutputFormatter.alert_event(
            ip_address=ip_address,
            attack_type=attack_info.get("attack_type", "unknown"),
            severity=attack_info.get("severity", "medium"),
            source=source,
            log_line=log_line
        ))

        # Persist incident to SQLite
        try:
            incident_id = data_engine.insert_incident(
                source_ip=ip_address,
                attack_type=attack_info.get("attack_type", "unknown"),
                raw_log=log_line,
                severity=attack_info.get("severity", "medium"),
                threat_type=attack_info.get("attack_type", "unknown"),
                action="blocked",
                details=attack_info.get("details", "")
            )
        except Exception as e:
            logger.error(f"Error inserting incident into DB: {e}")
            incident_id = None
        
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
            
            # Extract unique agents from tasks (CrewAI Task objects may not expose .agent directly)
            # For now, import agents directly
            from agents import triage_analyst, threat_intel_researcher, incident_responder, enforcer_agent
            agents = [triage_analyst, threat_intel_researcher, incident_responder, enforcer_agent]
            
            # Create and run the crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            logger.info(OutputFormatter.crew_kickoff())
            logger.info(OutputFormatter.analysis_started(ip_address, attack_info.get("attack_type", "unknown")))

            # Record analysis kickoff action
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "analysis_start", "AI crew kickoff", True)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")

            result = crew.kickoff()
            
            # Record AI response completion time
            ai_response_time = perf_metrics.get_current_timestamp() - detection_start_time
            
            # Parse and display results
            final_report = self._extract_final_report(result, ip_address, log_line)
            
            # FEATURE 7: Record detection metrics
            if incident_id:
                perf_metrics.record_detection(
                    incident_id=incident_id,
                    attack_type=attack_info.get("attack_type", "unknown"),
                    detection_time_ms=detection_start_time,
                    ai_response_time_ms=ai_response_time,
                    confidence=anomaly_result.get('anomaly_score', 0)
                )
            
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
                self._handle_remediation(final_report, ip_address, incident_id)
            else:
                logger.info(OutputFormatter.info_message(
                    "MONITORING MODE ACTIVE",
                    ["No immediate action required.", "System is monitoring for additional indicators."]
                ))
                if incident_id:
                    try:
                        data_engine.insert_action(incident_id, "monitoring", "No action required - monitoring", True)
                    except Exception as e:
                        logger.error(f"Error inserting action: {e}")
            
            # Update IP profile for anomaly scoring
            anomaly_scorer.update_ip_profile(ip_address, attack_info.get("severity", "medium"))
            
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
        
        # Look for JSON in the result using proper brace counting
        try:
            json_start = result_str.find('{')
            if json_start == -1:
                # No JSON found, use raw response
                report["raw_response"] = result_str
            else:
                # Count braces to find the matching closing brace
                brace_count = 0
                json_end = json_start
                for i in range(json_start, len(result_str)):
                    if result_str[i] == '{':
                        brace_count += 1
                    elif result_str[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if json_end > json_start:
                    json_str = result_str[json_start:json_end]
                    parsed = json.loads(json_str)
                    report.update(parsed)
                else:
                    report["raw_response"] = result_str
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse JSON from agent response: {e}")
            report["raw_response"] = result_str
        
        # Extract firewall rule if present
        if "firewall_rule" not in report or not report["firewall_rule"]:
            # Try to find iptables command in the response
            iptables_match = re.search(r'iptables\s+[^\n]+', result_str)
            if iptables_match:
                report["firewall_rule"] = iptables_match.group(0)
        
        return report
    
    def _handle_remediation(self, report: Dict[str, Any], ip_address: str, incident_id: Optional[int] = None):
        """
        Handle remediation actions with human-in-the-loop approval.
        
        Args:
            report: The security report
            ip_address: IP address to block
            incident_id: Optional DB incident id for logging actions
        """
        firewall_rule = report.get("firewall_rule")
        
        if not firewall_rule:
            logger.warning("No firewall rule found in report")
            return
        
        logger.warning("REMEDIATION REQUIRED")
        logger.warning(f"IP Address: {ip_address}")
        logger.warning(f"Severity: {report.get('severity', 'unknown')}")
        logger.warning(f"Threat Level: {report.get('threat_level', 'unknown')}")
        logger.warning("Proposed Firewall Rule:")
        logger.warning(f"  {firewall_rule}")

        # Log approval request and persist proposed action
        logger.warning(OutputFormatter.subheader("SECURITY ACTION REQUIRES APPROVAL"))
        logger.warning(f"  Target IP Address    : {ip_address}")
        logger.warning(f"  Firewall Command     : {firewall_rule}")
        logger.warning(f"\n  This action will block the IP address using iptables rules.")
        logger.warning(f"\n{OutputFormatter.SEPARATOR_MAIN}\n")

        if incident_id:
            try:
                data_engine.insert_action(incident_id, "proposed_firewall", firewall_rule, False)
            except Exception as e:
                logger.error(f"Error inserting action: {e}")

        response = input("  Execute this firewall rule? (yes/no): ").strip().lower()

        if response in ['yes', 'y']:
            self._execute_firewall_rule(firewall_rule, ip_address, incident_id)
        else:
            logger.info(OutputFormatter.info_message(
                "ACTION CANCELLED",
                ["The firewall rule has been cancelled by user.", "System continues monitoring."]
            ))
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_cancelled", "User cancelled execution", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
    
    def _execute_firewall_rule(self, rule: str, ip_address: str, incident_id: Optional[int] = None):
        """
        Execute firewall rule with additional human confirmation.
        
        Args:
            rule: The iptables command to execute
            ip_address: IP address being blocked
            incident_id: Optional DB incident id for logging actions
        """
        # Extract just the iptables command (safety check)
        if not rule.startswith("iptables"):
            logger.error(OutputFormatter.error_message(
                "INVALID FIREWALL RULE",
                "The firewall rule format is invalid. Operation cancelled."
            ))
            return
        
        # Final confirmation
        logger.warning(OutputFormatter.subheader("FINAL CONFIRMATION REQUIRED"))
        logger.warning(f"  Firewall Command: {rule}\n")
        final_confirm = input("  Type 'EXECUTE' to proceed, or anything else to cancel: ").strip()
        
        if final_confirm != "EXECUTE":
            logger.info(OutputFormatter.info_message(
                "EXECUTION CANCELLED",
                ["Operation was cancelled by user."]
            ))
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "execution_cancelled", "User cancelled execution", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
            return
        
        try:
            logger.info(OutputFormatter.section("EXECUTING FIREWALL RULE"))
            logger.info(f"  Status: Processing...\n")

            perf_metrics = get_metrics()
            
            # Record response start time for metrics
            response_start = perf_metrics.get_current_timestamp()
            
            # Execute the command
            result = subprocess.run(
                rule.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            response_time = perf_metrics.get_current_timestamp() - response_start
            success = False
            
            if result.returncode == 0:
                logger.info(OutputFormatter.success_message(
                    "FIREWALL RULE SUCCESSFULLY APPLIED",
                    [
                        f"Blocked IP Address: {ip_address}",
                        f"Rule Command: {rule}",
                        f"Status: Active and Verified"
                    ]
                ))
                success = True
            else:
                logger.error(OutputFormatter.error_message(
                    "FIREWALL RULE EXECUTION FAILED",
                    f"Error output: {result.stderr}"
                ))
            
            # FEATURE 7: Record response metrics
            if incident_id:
                perf_metrics.record_response(
                    incident_id=incident_id,
                    action_type="firewall_block",
                    execution_time_ms=response_time,
                    success=success
                )
                
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_execute", rule, success)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
                
        except subprocess.TimeoutExpired:
            logger.error(OutputFormatter.error_message(
                "COMMAND EXECUTION TIMEOUT",
                "The firewall command timed out after 10 seconds."
            ))
            
            # Record failed response
            if incident_id:
                perf_metrics.record_response(
                    incident_id=incident_id,
                    action_type="firewall_block",
                    execution_time_ms=-1,
                    success=False
                )
            
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_execute", "timeout", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
        except FileNotFoundError:
            logger.error(OutputFormatter.error_message(
                "IPTABLES NOT FOUND",
                "Ensure you are on a Linux system with iptables installed and available in PATH."
            ))
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_execute", "iptables_not_found", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
        except PermissionError:
            logger.error(OutputFormatter.error_message(
                "PERMISSION DENIED",
                "This operation requires sudo privileges. Please run with: sudo python main.py"
            ))
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_execute", "permission_denied", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
        except Exception as e:
            logger.error(OutputFormatter.error_message(
                "UNEXPECTED ERROR",
                f"Error executing firewall rule: {str(e)}"
            ))
            if incident_id:
                try:
                    data_engine.insert_action(incident_id, "firewall_execute", f"exception: {str(e)}", False)
                except Exception as e:
                    logger.error(f"Error inserting action: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def start(self):
        """Start the Sentinel Defense Module with multi-vector monitoring."""
        logger.info(OutputFormatter.header("SENTINEL AGENT v2.0 INITIALIZATION"))
        logger.info(OutputFormatter.section("SYSTEM CONFIGURATION"))
        logger.info(f"  Authentication Log   : {self.auth_log_path}")
        logger.info(f"  Web Access Log       : {self.web_log_path}")
        logger.info(f"  AI Engine            : Ollama Local LLM (llama3:8b)")
        logger.info(f"  Analysis Mode        : Multi-Agent AI Investigation")
        logger.info(f"  Multi-Vector Support : Enabled")
        logger.info(f"  Human-in-Loop        : Enabled")
        logger.info("")
        
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
            
            # Keep the main thread alive with periodic polling fallback
            poll_interval = 2.0
            last_poll_time = 0.0
            while True:
                import time
                now = time.time()
                if now - last_poll_time >= poll_interval:
                    if self.auth_sensor and self.auth_sensor.handler:
                        self.auth_sensor.handler._process_new_lines()
                    if self.web_sensor and self.web_sensor.handler:
                        self.web_sensor.handler._process_new_lines()
                    last_poll_time = now
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
