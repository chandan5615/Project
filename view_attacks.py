"""
Sentinel Agent - Attack Records Viewer
View and analyze recorded attacks.
"""

import json
import sys
from defense.attack_logger import AttackLogger
from pathlib import Path


def main():
    """Main function to view attack records."""
    logger = AttackLogger()
    
    if not logger.records:
        print("No attacks recorded yet.")
        return
    
    # Generate and display report
    print(logger.generate_report())
    
    # Show recent attacks
    print("\n" + "="*80)
    print("RECENT ATTACKS (Last 10)")
    print("="*80)
    
    recent = logger.get_recent_attacks(limit=10)
    for record in recent:
        print(f"\n[#{record['id']}] {record['date']} {record['time']}")
        print(f"  IP: {record['ip_address']}")
        print(f"  Attack Type: {record['attack_type']}")
        print(f"  Severity: {record['severity']}")
        print(f"  Description: {record['description']}")
        print(f"  Source: {record['source']}")
        if record['actions_taken']:
            print(f"  Actions Taken: {len(record['actions_taken'])}")
            for action in record['actions_taken']:
                status = "[SUCCESS]" if action['success'] else "[FAILED]"
                print(f"    {status} {action['action_type']}: {action['details']}")
        print()


if __name__ == "__main__":
    main()
