#!/usr/bin/env python3
"""
IP Manager CLI - Command-line tool for blocking/unblocking IPs on Linux
Simple and fast IP management without web interface

USAGE:
------
# Block an IP
python3 ip_manager_cli.py block 1.2.3.4

# Block multiple IPs
python3 ip_manager_cli.py block 1.2.3.4 5.6.7.8 9.10.11.12

# Unblock an IP
python3 ip_manager_cli.py unblock 1.2.3.4

# Unblock multiple IPs
python3 ip_manager_cli.py unblock 1.2.3.4 5.6.7.8

# List all blocked IPs
python3 ip_manager_cli.py list

# List blocked IPs with details
python3 ip_manager_cli.py list --details

# Check if an IP is blocked
python3 ip_manager_cli.py check 1.2.3.4

# Block with comment/reason
python3 ip_manager_cli.py block 1.2.3.4 --reason "Brute force attack"

# Interactive mode
python3 ip_manager_cli.py

# Flush all blocks (DANGEROUS!)
python3 ip_manager_cli.py flush

FEATURES:
---------
✓ Works with both UFW and iptables
✓ Validates IP addresses
✓ Color-coded output
✓ Interactive mode available
✓ Batch operations supported
✓ Fast and lightweight
✓ No web interface needed
"""

import subprocess
import sys
import re
import argparse
from typing import List, Tuple, Optional
from datetime import datetime

# Color codes for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header():
    """Print tool header"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║          SENTINEL IP MANAGER - CLI TOOL                ║")
    print("║        Block/Unblock IPs from Command Line             ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(Colors.RESET)

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def validate_ip(ip: str) -> bool:
    """Validate IP address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    # Check each octet is 0-255
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True

def run_command(command: List[str], require_sudo: bool = True) -> Tuple[bool, str]:
    """Run shell command and return success status and output"""
    try:
        if require_sudo and command[0] != 'sudo':
            command = ['sudo'] + command
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timeout"
    except Exception as e:
        return False, str(e)

def check_firewall_available() -> Tuple[bool, bool]:
    """Check which firewall is available (UFW, iptables)"""
    # Check UFW
    ufw_available, _ = run_command(['which', 'ufw'], require_sudo=False)
    
    # Check iptables
    iptables_available, _ = run_command(['which', 'iptables'], require_sudo=False)
    
    return ufw_available, iptables_available

def block_ip_ufw(ip: str, reason: Optional[str] = None) -> bool:
    """Block IP using UFW"""
    comment = f" comment '{reason}'" if reason else ""
    success, output = run_command(['ufw', 'deny', 'from', ip, 'to', 'any'])
    
    if success:
        print_success(f"Blocked {ip} using UFW{f' (Reason: {reason})' if reason else ''}")
        return True
    else:
        print_error(f"Failed to block {ip} with UFW: {output}")
        return False

def block_ip_iptables(ip: str, reason: Optional[str] = None) -> bool:
    """Block IP using iptables"""
    comment_args = ['-m', 'comment', '--comment', reason] if reason else []
    command = ['iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP'] + comment_args
    
    success, output = run_command(command)
    
    if success:
        print_success(f"Blocked {ip} using iptables{f' (Reason: {reason})' if reason else ''}")
        return True
    else:
        print_error(f"Failed to block {ip} with iptables: {output}")
        return False

def unblock_ip_ufw(ip: str) -> bool:
    """Unblock IP using UFW"""
    success, output = run_command(['ufw', 'delete', 'deny', 'from', ip, 'to', 'any'])
    
    if success:
        print_success(f"Unblocked {ip} using UFW")
        return True
    else:
        print_error(f"Failed to unblock {ip} with UFW: {output}")
        return False

def unblock_ip_iptables(ip: str) -> bool:
    """Unblock IP using iptables"""
    success, output = run_command(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])
    
    if success:
        print_success(f"Unblocked {ip} using iptables")
        return True
    else:
        print_error(f"Failed to unblock {ip} with iptables: {output}")
        return False

def list_blocked_ufw(show_details: bool = False) -> List[str]:
    """List blocked IPs from UFW"""
    success, output = run_command(['ufw', 'status', 'numbered'])
    
    if not success:
        print_error("Failed to get UFW status")
        return []
    
    blocked_ips = []
    for line in output.split('\n'):
        if 'DENY' in line:
            # Extract IP from UFW status line
            match = re.search(r'DENY\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if match:
                blocked_ips.append(match.group(1))
    
    if blocked_ips:
        print_info(f"Found {len(blocked_ips)} blocked IPs in UFW:")
        for i, ip in enumerate(blocked_ips, 1):
            print(f"  {i}. {Colors.RED}{ip}{Colors.RESET}")
    else:
        print_warning("No IPs currently blocked in UFW")
    
    return blocked_ips

def list_blocked_iptables(show_details: bool = False) -> List[str]:
    """List blocked IPs from iptables"""
    success, output = run_command(['iptables', '-L', 'INPUT', '-n', '-v'])
    
    if not success:
        print_error("Failed to get iptables rules")
        return []
    
    blocked_ips = []
    for line in output.split('\n'):
        if 'DROP' in line:
            # Extract IP from iptables rule
            match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if match:
                ip = match.group(1)
                if ip not in blocked_ips:  # Avoid duplicates
                    blocked_ips.append(ip)
    
    if blocked_ips:
        print_info(f"Found {len(blocked_ips)} blocked IPs in iptables:")
        for i, ip in enumerate(blocked_ips, 1):
            print(f"  {i}. {Colors.RED}{ip}{Colors.RESET}")
    else:
        print_warning("No IPs currently blocked in iptables")
    
    return blocked_ips

def check_ip_blocked(ip: str) -> Tuple[bool, str]:
    """Check if an IP is blocked"""
    # Check UFW
    ufw_available, iptables_available = check_firewall_available()
    
    blocked_by = []
    
    if ufw_available:
        success, output = run_command(['ufw', 'status'])
        if success and ip in output:
            blocked_by.append("UFW")
    
    if iptables_available:
        success, output = run_command(['iptables', '-L', 'INPUT', '-n'])
        if success and ip in output:
            blocked_by.append("iptables")
    
    if blocked_by:
        return True, ", ".join(blocked_by)
    else:
        return False, ""

def block_ips(ips: List[str], reason: Optional[str] = None):
    """Block one or more IPs"""
    print_header()
    print_info(f"Attempting to block {len(ips)} IP(s)...\n")
    
    # Check available firewalls
    ufw_available, iptables_available = check_firewall_available()
    
    if not ufw_available and not iptables_available:
        print_error("No firewall available (UFW or iptables not found)")
        return
    
    success_count = 0
    fail_count = 0
    
    for ip in ips:
        # Validate IP
        if not validate_ip(ip):
            print_error(f"Invalid IP address: {ip}")
            fail_count += 1
            continue
        
        # Check if already blocked
        is_blocked, blocked_by = check_ip_blocked(ip)
        if is_blocked:
            print_warning(f"{ip} is already blocked by {blocked_by}")
            continue
        
        # Try to block with available firewall
        if ufw_available:
            if block_ip_ufw(ip, reason):
                success_count += 1
            else:
                fail_count += 1
        elif iptables_available:
            if block_ip_iptables(ip, reason):
                success_count += 1
            else:
                fail_count += 1
    
    print()
    print_info(f"Results: {Colors.GREEN}{success_count} blocked{Colors.RESET}, {Colors.RED}{fail_count} failed{Colors.RESET}")

def unblock_ips(ips: List[str]):
    """Unblock one or more IPs"""
    print_header()
    print_info(f"Attempting to unblock {len(ips)} IP(s)...\n")
    
    # Check available firewalls
    ufw_available, iptables_available = check_firewall_available()
    
    if not ufw_available and not iptables_available:
        print_error("No firewall available (UFW or iptables not found)")
        return
    
    success_count = 0
    fail_count = 0
    
    for ip in ips:
        # Validate IP
        if not validate_ip(ip):
            print_error(f"Invalid IP address: {ip}")
            fail_count += 1
            continue
        
        # Try to unblock with both firewalls
        unblocked = False
        
        if ufw_available:
            if unblock_ip_ufw(ip):
                unblocked = True
        
        if iptables_available:
            if unblock_ip_iptables(ip):
                unblocked = True
        
        if unblocked:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print_info(f"Results: {Colors.GREEN}{success_count} unblocked{Colors.RESET}, {Colors.RED}{fail_count} failed{Colors.RESET}")

def list_blocked(show_details: bool = False):
    """List all blocked IPs"""
    print_header()
    
    # Check available firewalls
    ufw_available, iptables_available = check_firewall_available()
    
    if not ufw_available and not iptables_available:
        print_error("No firewall available (UFW or iptables not found)")
        return
    
    if ufw_available:
        print(f"\n{Colors.BOLD}=== UFW BLOCKED IPs ==={Colors.RESET}")
        list_blocked_ufw(show_details)
    
    if iptables_available:
        print(f"\n{Colors.BOLD}=== IPTABLES BLOCKED IPs ==={Colors.RESET}")
        list_blocked_iptables(show_details)

def check_ip(ip: str):
    """Check if an IP is blocked"""
    print_header()
    
    if not validate_ip(ip):
        print_error(f"Invalid IP address: {ip}")
        return
    
    is_blocked, blocked_by = check_ip_blocked(ip)
    
    if is_blocked:
        print_info(f"IP {Colors.RED}{ip}{Colors.RESET} is {Colors.RED}BLOCKED{Colors.RESET} by: {blocked_by}")
    else:
        print_info(f"IP {Colors.GREEN}{ip}{Colors.RESET} is {Colors.GREEN}NOT BLOCKED{Colors.RESET}")

def flush_all_blocks():
    """Remove all blocks (DANGEROUS!)"""
    print_header()
    print_warning("⚠️  WARNING: This will remove ALL IP blocks!")
    
    try:
        confirm = input(f"{Colors.YELLOW}Type 'YES' to confirm: {Colors.RESET}")
        if confirm.strip() != 'YES':
            print_info("Operation cancelled")
            return
    except KeyboardInterrupt:
        print("\n" + Colors.RESET)
        print_info("Operation cancelled")
        return
    
    print()
    
    # Check available firewalls
    ufw_available, iptables_available = check_firewall_available()
    
    if ufw_available:
        print_info("Resetting UFW...")
        run_command(['ufw', 'reset'])
        run_command(['ufw', 'enable'])
        print_success("UFW reset complete")
    
    if iptables_available:
        print_info("Flushing iptables INPUT chain...")
        run_command(['iptables', '-F', 'INPUT'])
        print_success("iptables flushed")

def interactive_mode():
    """Interactive mode for IP management"""
    print_header()
    
    print(f"{Colors.CYAN}Interactive Mode - Type 'help' for commands{Colors.RESET}\n")
    
    while True:
        try:
            command = input(f"{Colors.BOLD}sentinel-ip> {Colors.RESET}").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd in ['exit', 'quit', 'q']:
                print_info("Goodbye!")
                break
            
            elif cmd == 'help':
                print(f"""
{Colors.CYAN}Available Commands:{Colors.RESET}
  block <ip> [<ip2> ...]     - Block one or more IPs
  unblock <ip> [<ip2> ...]   - Unblock one or more IPs
  list                       - List all blocked IPs
  check <ip>                 - Check if an IP is blocked
  flush                      - Remove all blocks (dangerous!)
  help                       - Show this help
  exit / quit / q            - Exit interactive mode
                """)
            
            elif cmd == 'block':
                if len(parts) < 2:
                    print_error("Usage: block <ip> [<ip2> ...]")
                else:
                    block_ips(parts[1:])
            
            elif cmd == 'unblock':
                if len(parts) < 2:
                    print_error("Usage: unblock <ip> [<ip2> ...]")
                else:
                    unblock_ips(parts[1:])
            
            elif cmd == 'list':
                list_blocked()
            
            elif cmd == 'check':
                if len(parts) < 2:
                    print_error("Usage: check <ip>")
                else:
                    check_ip(parts[1])
            
            elif cmd == 'flush':
                flush_all_blocks()
            
            else:
                print_error(f"Unknown command: {cmd}")
                print_info("Type 'help' for available commands")
            
            print()  # Blank line for readability
            
        except KeyboardInterrupt:
            print("\n" + Colors.RESET)
            print_info("Use 'exit' to quit")
        except EOFError:
            print("\n" + Colors.RESET)
            break

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='IP Manager CLI - Block/Unblock IPs from command line',
        epilog='Run without arguments for interactive mode'
    )
    
    parser.add_argument(
        'action',
        nargs='?',
        choices=['block', 'unblock', 'list', 'check', 'flush'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'ips',
        nargs='*',
        help='IP address(es) to block/unblock/check'
    )
    
    parser.add_argument(
        '--reason',
        '-r',
        help='Reason for blocking (optional)'
    )
    
    parser.add_argument(
        '--details',
        '-d',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # If no action specified, enter interactive mode
    if args.action is None:
        interactive_mode()
        return
    
    # Execute specified action
    if args.action == 'block':
        if not args.ips:
            print_error("Please specify at least one IP to block")
            sys.exit(1)
        block_ips(args.ips, args.reason)
    
    elif args.action == 'unblock':
        if not args.ips:
            print_error("Please specify at least one IP to unblock")
            sys.exit(1)
        unblock_ips(args.ips)
    
    elif args.action == 'list':
        list_blocked(args.details)
    
    elif args.action == 'check':
        if not args.ips:
            print_error("Please specify an IP to check")
            sys.exit(1)
        check_ip(args.ips[0])
    
    elif args.action == 'flush':
        flush_all_blocks()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Colors.RESET)
        print_info("Operation cancelled")
        sys.exit(0)
