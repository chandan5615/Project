"""
Professional Output Formatter for Sentinel Agent
Provides fancy, easy-to-understand output without icons.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json


class OutputFormatter:
    """Professional output formatter for Sentinel Agent."""
    
    # Color codes for terminal output (standard ANSI)
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Styling constants
    SEPARATOR_MAIN = "=" * 100
    SEPARATOR_SUB = "-" * 100
    SEPARATOR_LIGHT = "." * 100
    
    @staticmethod
    def header(title: str, width: int = 100) -> str:
        """Create a professional header."""
        padding = (width - len(title) - 2) // 2
        line = "=" * width
        title_line = " " * padding + f"  {title}  " + " " * (width - padding - len(title) - 2)
        return f"\n{line}\n{title_line}\n{line}\n"
    
    @staticmethod
    def subheader(title: str, width: int = 100) -> str:
        """Create a professional subheader."""
        padding = (width - len(title) - 2) // 2
        line = "-" * width
        title_line = " " * padding + f"  {title}  " + " " * (width - padding - len(title) - 2)
        return f"\n{title_line}\n{line}\n"
    
    @staticmethod
    def section(title: str, width: int = 100) -> str:
        """Create a section header."""
        return f"\n{' ' * 2}{title.upper()}\n{'-' * (len(title) + 4)}\n"
    
    @staticmethod
    def alert_event(ip_address: str, attack_type: str, severity: str, source: str, 
                    log_line: str = None) -> str:
        """Format a security alert event."""
        severity_level = severity.upper()
        
        output = [
            OutputFormatter.subheader("SECURITY ALERT DETECTED"),
            f"  Threat Source        : {ip_address}",
            f"  Attack Classification: {attack_type.replace('_', ' ').title()}",
            f"  Severity Level       : {severity_level}",
            f"  Event Source         : {source.upper()}",
        ]
        
        if log_line:
            output.append(f"\n  Log Reference        :")
            output.append(f"  {log_line[:95]}")
            if len(log_line) > 95:
                output.append(f"  {log_line[95:]}")
        
        output.append("")
        return "\n".join(output)
    
    @staticmethod
    def analysis_started(ip_address: str, attack_type: str) -> str:
        """Format analysis startup message."""
        output = [
            OutputFormatter.section("INITIATING AI ANALYSIS"),
            f"  Threat Target        : {ip_address}",
            f"  Threat Category      : {attack_type.replace('_', ' ').title()}",
            f"  Analysis Type        : Multi-Agent AI Investigation",
            f"  Start Time           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        return "\n".join(output)
    
    @staticmethod
    def agent_status(agent_name: str, status: str, message: str = None) -> str:
        """Format agent status update."""
        status_display = f"[{status.upper()}]"
        output = f"    {status_display:15} {agent_name:30} ", 
        if message:
            output += f" | {message}"
        return "".join(output)
    
    @staticmethod
    def analysis_report(report: Dict[str, Any], ip_address: str) -> str:
        """Format the final analysis report."""
        output = [
            OutputFormatter.header("ANALYSIS COMPLETE - FINAL REPORT"),
            OutputFormatter.section("THREAT INTELLIGENCE"),
            f"  Target IP Address    : {ip_address}",
            f"  Threat Severity      : {report.get('severity', 'UNKNOWN').upper()}",
            f"  Threat Level         : {report.get('threat_level', 'UNKNOWN').upper()}",
            f"  Confidence Score     : {report.get('confidence', 'N/A')}",
        ]
        
        if report.get('description'):
            output.append(OutputFormatter.section("THREAT ANALYSIS"))
            output.append(f"  {report.get('description')}")
        
        if report.get('defensive_measures'):
            output.append(OutputFormatter.section("RECOMMENDED ACTIONS"))
            measures = report.get('defensive_measures', [])
            if isinstance(measures, list):
                for i, measure in enumerate(measures, 1):
                    output.append(f"  {i}. {measure}")
            else:
                output.append(f"  {measures}")
        
        if report.get('firewall_rule'):
            output.append(OutputFormatter.section("FIREWALL RULE"))
            output.append(f"  Command: {report.get('firewall_rule')}")
        
        output.append(OutputFormatter.section("DECISION"))
        action_status = "ACTION REQUIRED" if report.get('action_required') else "MONITORING MODE"
        output.append(f"  Status: {action_status}")
        output.append(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        output.append(f"\n{OutputFormatter.SEPARATOR_MAIN}\n")
        return "\n".join(output)
    
    @staticmethod
    def action_remediation(ip_address: str, firewall_rule: str = None, 
                          verified: bool = False) -> str:
        """Format remediation action display."""
        output = [
            OutputFormatter.header("EXECUTING REMEDIATION"),
            OutputFormatter.section("TARGET"),
            f"  IP Address: {ip_address}",
        ]
        
        if firewall_rule:
            output.append(OutputFormatter.section("FIREWALL RULE"))
            output.append(f"  {firewall_rule}")
        
        if verified:
            output.append(OutputFormatter.section("VERIFICATION"))
            output.append("  Status: SUCCESSFULLY APPLIED")
        
        output.append(f"\n{OutputFormatter.SEPARATOR_MAIN}\n")
        return "\n".join(output)
    
    @staticmethod
    def attack_record_table(records: List[Dict[str, Any]]) -> str:
        """Format multiple attack records as a professional table."""
        if not records:
            return "  No attack records available.\n"
        
        output = []
        
        # Table headers
        headers = ["ID", "Date & Time", "IP Address", "Attack Type", "Severity", "Source"]
        col_widths = [5, 19, 16, 20, 10, 8]
        
        # Header row
        header_row = "  "
        for header, width in zip(headers, col_widths):
            header_row += f"{header:<{width}}"
        
        output.append(header_row)
        output.append("  " + "-" * 95)
        
        # Data rows
        for record in records:
            row = "  "
            row += f"{str(record.get('id', 'N/A')):<5}"
            
            date_time = f"{record.get('date', '')} {record.get('time', '')}"[:19]
            row += f"{date_time:<19}"
            
            ip = str(record.get('ip_address', 'N/A'))[:16]
            row += f"{ip:<16}"
            
            attack_type = str(record.get('attack_type', 'unknown')).replace('_', ' ')[:20]
            row += f"{attack_type:<20}"
            
            severity = str(record.get('severity', 'N/A')).upper()[:10]
            row += f"{severity:<10}"
            
            source = str(record.get('source', 'N/A')).upper()[:8]
            row += f"{source:<8}"
            
            output.append(row)
        
        return "\n".join(output) + "\n"
    
    @staticmethod
    def attack_record_detail(record: Dict[str, Any]) -> str:
        """Format a single attack record with full details."""
        output = [
            OutputFormatter.header("ATTACK RECORD DETAILS"),
            OutputFormatter.section("INCIDENT INFORMATION"),
            f"  Record ID            : {record.get('id', 'N/A')}",
            f"  Date & Time          : {record.get('date', 'N/A')} {record.get('time', 'N/A')}",
            f"  Attacker IP          : {record.get('ip_address', 'N/A')}",
        ]
        
        output.append(OutputFormatter.section("ATTACK DETAILS"))
        output.append(f"  Attack Type          : {record.get('attack_type', 'Unknown').replace('_', ' ').title()}")
        output.append(f"  Severity Level       : {record.get('severity', 'Unknown').upper()}")
        output.append(f"  Detection Source     : {record.get('source', 'Unknown').upper()}")
        output.append(f"  Description          : {record.get('description', 'No description')}")
        
        if record.get('log_reference'):
            output.append(OutputFormatter.section("LOG REFERENCE"))
            output.append(f"  {record.get('log_reference')}")
        
        if record.get('actions_taken'):
            output.append(OutputFormatter.section("RESPONSE ACTIONS"))
            for i, action in enumerate(record['actions_taken'], 1):
                status = "[SUCCESS]" if action.get('success') else "[PENDING]"
                output.append(f"  {i}. {status} {action.get('action_type', 'Unknown').replace('_', ' ').title()}")
                if action.get('details'):
                    output.append(f"     Details: {action.get('details')}")
        
        output.append(f"\n{OutputFormatter.SEPARATOR_MAIN}\n")
        return "\n".join(output)
    
    @staticmethod
    def system_statistics(total_attacks: int, by_type: Dict[str, int], 
                         by_severity: Dict[str, int]) -> str:
        """Format system statistics."""
        output = [
            OutputFormatter.header("SYSTEM STATISTICS"),
            OutputFormatter.section("OVERVIEW"),
            f"  Total Attacks Recorded: {total_attacks}",
        ]
        
        if by_severity:
            output.append(OutputFormatter.section("ATTACKS BY SEVERITY"))
            for severity, count in sorted(by_severity.items(), key=lambda x: x[1], reverse=True):
                bar = "=" * count
                output.append(f"  {severity.upper():12}: {bar} ({count})")
        
        if by_type:
            output.append(OutputFormatter.section("TOP ATTACK TYPES"))
            sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]
            for attack_type, count in sorted_types:
                attack_name = attack_type.replace('_', ' ').title()
                output.append(f"  {attack_name:30}: {count}")
        
        output.append(f"\n{OutputFormatter.SEPARATOR_MAIN}\n")
        return "\n".join(output)
    
    @staticmethod
    def error_message(error_title: str, error_details: str = None) -> str:
        """Format error messages professionally."""
        output = [
            OutputFormatter.section("ERROR ENCOUNTERED"),
            f"  Title: {error_title}",
        ]
        if error_details:
            output.append(f"  Details: {error_details}")
        output.append("")
        return "\n".join(output)
    
    @staticmethod
    def success_message(title: str, details: List[str] = None) -> str:
        """Format success messages."""
        output = [
            OutputFormatter.section("SUCCESS"),
            f"  {title}",
        ]
        if details:
            for detail in details:
                output.append(f"  {detail}")
        output.append("")
        return "\n".join(output)
    
    @staticmethod
    def info_message(title: str, details: List[str] = None) -> str:
        """Format informational messages."""
        output = [
            OutputFormatter.section("INFORMATION"),
            f"  {title}",
        ]
        if details:
            for detail in details:
                output.append(f"  {detail}")
        output.append("")
        return "\n".join(output)
    
    @staticmethod
    def formatted_json(data: Dict[str, Any], title: str = "DATA") -> str:
        """Format JSON data professionally."""
        output = [
            OutputFormatter.section(title),
            json.dumps(data, indent=2),
            ""
        ]
        return "\n".join(output)
    
    @staticmethod
    def ip_reputation_report(ip_address: str, reputation_data: Dict[str, Any]) -> str:
        """Format IP reputation report."""
        output = [
            OutputFormatter.section("IP REPUTATION ANALYSIS"),
            f"  Target IP Address    : {ip_address}",
            f"  Reputation Score     : {reputation_data.get('score', 'N/A')}/100",
            f"  Previous Reports     : {reputation_data.get('reports', 'N/A')}",
            f"  Threat Classification: {reputation_data.get('threat_level', 'UNKNOWN')}",
        ]
        
        if reputation_data.get('threat_reasons'):
            output.append(OutputFormatter.section("THREAT INDICATORS"))
            reasons = reputation_data.get('threat_reasons', [])
            if isinstance(reasons, list):
                for reason in reasons:
                    output.append(f"  - {reason}")
        
        output.append("")
        return "\n".join(output)
    
    @staticmethod
    def crew_kickoff() -> str:
        """Format crew analysis kickoff."""
        output = [
            OutputFormatter.subheader("INITIALIZING AI INVESTIGATION CREW"),
            "  Status: All agents are being assembled and coordinated",
            "  Operation: Sequential analysis chain execution",
            "  Mode: Verbose reporting enabled",
            ""
        ]
        return "\n".join(output)


# Convenience functions
def print_header(title: str) -> None:
    """Print a professional header."""
    print(OutputFormatter.header(title))


def print_alert(ip_address: str, attack_type: str, severity: str, source: str, 
                log_line: str = None) -> None:
    """Print a security alert."""
    print(OutputFormatter.alert_event(ip_address, attack_type, severity, source, log_line))


def print_report(report: Dict[str, Any], ip_address: str) -> None:
    """Print analysis report."""
    print(OutputFormatter.analysis_report(report, ip_address))


def print_success(title: str, details: List[str] = None) -> None:
    """Print success message."""
    print(OutputFormatter.success_message(title, details))


def print_error(title: str, details: str = None) -> None:
    """Print error message."""
    print(OutputFormatter.error_message(title, details))


def print_info(title: str, details: List[str] = None) -> None:
    """Print info message."""
    print(OutputFormatter.info_message(title, details))
