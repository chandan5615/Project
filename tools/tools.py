"""
Sentinel Agent - Security Tools Module
Provides CrewAI tools for threat intelligence, system context, and firewall management.
"""

import subprocess
import re
import ipaddress
from typing import Optional
from pathlib import Path
import shutil
try:
    from crewai_tools import tool
except Exception:
    # Fallback for different CrewAI versions
    try:
        from crewai.tools import tool
    except Exception:
        tool = None

# Ensure 'tool' is a decorator; if not available, provide a no-op decorator
if not callable(tool):
    def tool(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
import requests
import json


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Check IP Threat")
    _decor_check_ip_threat = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_check_ip_threat = (lambda f: f)
@_decor_check_ip_threat
def check_ip_threat(ip: str) -> str:
    """
    Check the reputation of an IP address using threat intelligence APIs.
    
    Args:
        ip: IP address to check
        
    Returns:
        JSON string with threat intelligence data
    """
    result = {
        "ip": ip,
        "threat_level": "unknown",
        "details": {},
        "sources": []
    }
    
    # Try AbuseIPDB API (requires API key in environment)
    # For demo purposes, we'll simulate the check
    try:
        # In production, you would use: requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}")
        # For now, we'll do a basic check
        result["details"]["checked"] = True
        result["sources"].append("AbuseIPDB (simulated)")
        
        # Simulate threat check - in production, parse actual API response
        # For demo: assume private IPs are low risk
        if ip.startswith(("10.", "172.16.", "192.168.", "127.")):
            result["threat_level"] = "low"
            result["details"]["reason"] = "Private IP address"
        else:
            result["threat_level"] = "medium"
            result["details"]["reason"] = "Public IP - requires further investigation"
            
    except Exception as e:
        result["details"]["error"] = str(e)
        result["threat_level"] = "unknown"
    
    return json.dumps(result, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Get System Context")
    _decor_get_system_context = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_get_system_context = (lambda f: f)
@_decor_get_system_context
def get_system_context() -> str:
    """
    Gather current system context including logged-in users and recent login history.
    
    Returns:
        JSON string with system context information
    """
    context = {
        "current_users": [],
        "recent_logins": [],
        "system_info": {}
    }
    
    try:
        # Get current logged-in users
        if shutil.which("who"):
            who_result = subprocess.run(
                ["who"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if who_result.returncode == 0 and who_result.stdout.strip():
                context["current_users"] = who_result.stdout.strip().split("\n")
        
        # Get recent login history
        if shutil.which("last"):
            last_result = subprocess.run(
                ["last", "-n", "5"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if last_result.returncode == 0 and last_result.stdout.strip():
                context["recent_logins"] = last_result.stdout.strip().split("\n")[:5]
        
        # Get system uptime
        if shutil.which("uptime"):
            uptime_result = subprocess.run(
                ["uptime"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if uptime_result.returncode == 0 and uptime_result.stdout.strip():
                context["system_info"]["uptime"] = uptime_result.stdout.strip()
            
    except subprocess.TimeoutExpired:
        context["error"] = "Command timeout"
    except Exception as e:
        context["error"] = str(e)
    
    return json.dumps(context, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Generate Firewall Rule")
    _decor_generate_firewall_rule = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_generate_firewall_rule = (lambda f: f)
@_decor_generate_firewall_rule
def generate_firewall_rule(ip: str, protocol: str = "tcp", port: str = "all") -> str:
    """
    Generate the exact iptables command string needed to block an IP address.
    
    Args:
        ip: IP address to block
        protocol: Protocol to block (tcp, udp, or all)
        port: Port to block (specific port number or "all")
        
    Returns:
        JSON string with firewall rule details
    """
    rule = {
        "ip": ip,
        "protocol": protocol,
        "port": port,
        "iptables_command": "",
        "ufw_command": "",
        "description": f"Block IP {ip} for security incident"
    }
    
    # Generate iptables command
    if port == "all":
        rule["iptables_command"] = f"iptables -A INPUT -s {ip} -j DROP"
    else:
        rule["iptables_command"] = f"iptables -A INPUT -s {ip} -p {protocol} --dport {port} -j DROP"
    
    # Generate ufw command (alternative)
    rule["ufw_command"] = f"ufw deny from {ip}"
    
    # Add comment for tracking
    rule["iptables_command"] += f" -m comment --comment \"Sentinel Agent: Blocked {ip}\""
    
    return json.dumps(rule, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Extract IP from Log Line")
    _decor_extract_ip_from_log = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_extract_ip_from_log = (lambda f: f)
@_decor_extract_ip_from_log
def extract_ip_from_log(log_line: str) -> Optional[str]:
    """
    Extract IP address from a log line using regex patterns.
    
    Args:
        log_line: Log line to parse
        
    Returns:
        IP address if found, None otherwise
    """
    # Common IP patterns in auth.log
    ip_patterns = [
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # Standard IPv4
        r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # "from IP" pattern
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # Any IPv4
    ]
    
    for pattern in ip_patterns:
        match = re.search(pattern, log_line)
        if match:
            ip = match.group(1) if match.groups() else match.group(0)
            # Validate IP format
            parts = ip.split('.')
            if len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts if p.isdigit()):
                return ip
    
    return None


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Check Web Logs for IP")
    _decor_check_web_logs_for_ip = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_check_web_logs_for_ip = (lambda f: f)
@_decor_check_web_logs_for_ip
def check_web_logs_for_ip(ip: str, log_path: str = "/var/log/apache2/access.log") -> str:
    """
    Check if an IP address appears in web access logs (cross-correlation).
    
    Args:
        ip: IP address to search for
        log_path: Path to web access log file (Apache or Nginx)
        
    Returns:
        JSON string with search results
    """
    result = {
        "ip": ip,
        "found": False,
        "occurrences": 0,
        "recent_entries": [],
        "log_path": log_path
    }
    
    try:
        log_file = Path(log_path)
        if not log_file.exists():
            result["error"] = f"Log file {log_path} does not exist"
            return json.dumps(result, indent=2)
        
        # Read last 1000 lines for performance
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Check last 1000 lines
            recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            
            for line in recent_lines:
                if ip in line:
                    result["found"] = True
                    result["occurrences"] += 1
                    if len(result["recent_entries"]) < 10:  # Keep last 10 entries
                        result["recent_entries"].append(line.strip())
        
    except PermissionError:
        result["error"] = "Permission denied reading log file"
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Verify Firewall Rule")
    _decor_verify_firewall_rule = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_verify_firewall_rule = (lambda f: f)
@_decor_verify_firewall_rule
def verify_firewall_rule(ip: str) -> str:
    """
    Verify if a firewall rule exists for blocking an IP address.
    
    Args:
        ip: IP address to check
        
    Returns:
        JSON string with verification results
    """
    result = {
        "ip": ip,
        "rule_exists": False,
        "rule_details": None,
        "method": "iptables"
    }
    
    try:
        # Check iptables rules
        check_cmd = ["iptables", "-L", "INPUT", "-n", "-v"]
        check_result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=5
        )
        
        if check_result.returncode == 0:
            # Look for the IP in the output
            for line in check_result.stdout.split('\n'):
                if ip in line and "DROP" in line:
                    result["rule_exists"] = True
                    result["rule_details"] = line.strip()
                    break
        
        # If iptables not found, try ufw
        if not result["rule_exists"]:
            ufw_check = subprocess.run(
                ["ufw", "status", "numbered"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ufw_check.returncode == 0 and ip in ufw_check.stdout:
                result["rule_exists"] = True
                result["method"] = "ufw"
                result["rule_details"] = "Found in ufw rules"
                
    except FileNotFoundError:
        result["error"] = "iptables/ufw command not found"
    except subprocess.TimeoutExpired:
        result["error"] = "Command timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Execute Iptables Rule with Resilience")
    _decor_execute_iptables_rule = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_execute_iptables_rule = (lambda f: f)
@_decor_execute_iptables_rule
def execute_iptables_rule(ip: str, max_attempts: int = 3) -> str:
    """
    Execute an iptables rule to block an IP with resilience loop.
    Verifies the rule was added and retries if necessary.
    
    Args:
        ip: IP address to block
        max_attempts: Maximum number of attempts (default: 3)
        
    Returns:
        JSON string with execution results
    """
    result = {
        "ip": ip,
        "success": False,
        "attempts": 0,
        "final_rule": None,
        "errors": []
    }

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        result["errors"].append("Invalid IP address format")
        return json.dumps(result, indent=2)
    
    # Different command variations to try
    commands = [
        ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP", "-m", "comment", "--comment", f"Sentinel Agent: Blocked {ip}"],
        ["iptables", "-I", "INPUT", "1", "-s", ip, "-j", "DROP", "-m", "comment", "--comment", f"Sentinel Agent: Blocked {ip}"],
        ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
    ]
    
    for attempt in range(max_attempts):
        result["attempts"] = attempt + 1
        cmd = commands[attempt % len(commands)]
        
        try:
            # Execute the command
            exec_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=False,
                timeout=10
            )
            
            if exec_result.returncode == 0:
                # Verify the rule was added
                verify_result = verify_firewall_rule(ip)
                verify_data = json.loads(verify_result)
                
                if verify_data.get("rule_exists"):
                    result["success"] = True
                    result["final_rule"] = " ".join(cmd)
                    break
                else:
                    result["errors"].append(f"Attempt {attempt + 1}: Rule executed but not found in firewall table")
            else:
                result["errors"].append(f"Attempt {attempt + 1}: {exec_result.stderr}")
                
        except subprocess.TimeoutExpired:
            result["errors"].append(f"Attempt {attempt + 1}: Command timeout")
        except Exception as e:
            result["errors"].append(f"Attempt {attempt + 1}: {str(e)}")
    
    return json.dumps(result, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Kill Process by Name or PID")
    _decor_kill_process = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_kill_process = (lambda f: f)
@_decor_kill_process
def kill_process(process_name: str = None, pid: int = None, signal: str = "TERM") -> str:
    """
    Kill a process using systemctl or kill command.
    
    Args:
        process_name: Name of the process/service to kill
        pid: Process ID to kill
        signal: Signal to send (TERM, KILL, etc.)
        
    Returns:
        JSON string with execution results
    """
    result = {
        "success": False,
        "method": None,
        "output": None,
        "error": None
    }
    
    try:
        if process_name:
            # Try systemctl first (for services)
            systemctl_result = subprocess.run(
                ["systemctl", "kill", f"--signal={signal}", process_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if systemctl_result.returncode == 0:
                result["success"] = True
                result["method"] = "systemctl"
                result["output"] = systemctl_result.stdout
            else:
                # Fallback to pkill
                pkill_result = subprocess.run(
                    ["pkill", f"-{signal}", process_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if pkill_result.returncode == 0:
                    result["success"] = True
                    result["method"] = "pkill"
                    result["output"] = pkill_result.stdout
                else:
                    result["error"] = pkill_result.stderr
                    
        elif pid:
            # Use kill command
            kill_result = subprocess.run(
                ["kill", f"-{signal}", str(pid)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if kill_result.returncode == 0:
                result["success"] = True
                result["method"] = "kill"
                result["output"] = kill_result.stdout
            else:
                result["error"] = kill_result.stderr
        else:
            result["error"] = "Either process_name or pid must be provided"
            
    except FileNotFoundError:
        result["error"] = "Command not found (may not be on Linux system)"
    except subprocess.TimeoutExpired:
        result["error"] = "Command timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, indent=2)


# Use crewai 'tool' decorator when available; otherwise use a no-op decorator
if callable(tool):
    _tmp = tool("Change File Permissions")
    _decor_change_permissions = _tmp if callable(_tmp) else (lambda f: f)
else:
    _decor_change_permissions = (lambda f: f)
@_decor_change_permissions
def change_permissions(file_path: str, permissions: str, recursive: bool = False) -> str:
    """
    Change file or directory permissions using chmod.
    
    Args:
        file_path: Path to file or directory
        permissions: Permissions in octal (e.g., "755") or symbolic (e.g., "u+x")
        recursive: If True, apply recursively (for directories)
        
    Returns:
        JSON string with execution results
    """
    result = {
        "file_path": file_path,
        "permissions": permissions,
        "success": False,
        "error": None
    }
    
    try:
        cmd = ["chmod"]
        if recursive:
            cmd.append("-R")
        cmd.extend([permissions, file_path])
        
        chmod_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=5
        )
        
        if chmod_result.returncode == 0:
            result["success"] = True
        else:
            result["error"] = chmod_result.stderr
            
    except FileNotFoundError:
        result["error"] = "chmod command not found"
    except subprocess.TimeoutExpired:
        result["error"] = "Command timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, indent=2)


# =========================================================================
# FEATURE: Whitelist Protection - Local IP Detection
# =========================================================================

def get_local_ip() -> Optional[str]:
    """
    Automatically detect the server's primary IP address.
    Used to add the admin/server IP to the whitelist on startup.
    
    Returns:
        Primary IP address or None if detection fails
    """
    import socket
    try:
        # Connect to external DNS server (doesn't actually send data)
        # This gets the IP used for outbound connections
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        # Fallback: try to get hostname IP
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return None


def get_local_network() -> Optional[str]:
    """
    Detect the local network CIDR (e.g., 192.168.1.0/24).
    Used to whitelist the entire local network.
    
    Returns:
        Network CIDR string or None
    """
    local_ip = get_local_ip()
    if not local_ip:
        return None
    
    try:
        # For most home/office networks, assume /24 subnet
        ip_obj = ipaddress.ip_address(local_ip)
        
        # Determine network based on IP class
        if local_ip.startswith("192.168."):
            # Class C private network - /24
            network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
        elif local_ip.startswith("10."):
            # Class A private network - /16 for safety
            network = ipaddress.ip_network(f"{local_ip}/16", strict=False)
        elif local_ip.startswith("172."):
            # Class B private network - /16
            network = ipaddress.ip_network(f"{local_ip}/16", strict=False)
        else:
            # Public IP or unknown - just whitelist the single IP
            return f"{local_ip}/32"
        
        return str(network)
    except Exception:
        return None


def get_admin_ips() -> list:
    """
    Get list of IPs that should be automatically whitelisted.
    Includes: localhost, local IP, local network, common private ranges.
    
    Returns:
        List of IP addresses/networks to whitelist
    """
    safe_ips = [
        "127.0.0.1",      # Localhost IPv4
        "::1",            # Localhost IPv6
        "localhost"       # Hostname
    ]
    
    # Add detected local IP
    local_ip = get_local_ip()
    if local_ip:
        safe_ips.append(local_ip)
    
    # Add local network
    local_network = get_local_network()
    if local_network:
        safe_ips.append(local_network)
    
    return safe_ips

