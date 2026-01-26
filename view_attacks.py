"""
Sentinel Agent - Attack Records Viewer
Professional display of recorded attacks with fancy formatting.
"""

import json
import sys
from defense.attack_logger import AttackLogger
from output_formatter import OutputFormatter
from pathlib import Path


def main():
    """Main function to view attack records."""
    logger = AttackLogger()
    
    if not logger.records:
        print(OutputFormatter.info_message(
            "NO ATTACK RECORDS",
            ["The attack records database is empty."]
        ))
        return
    
    # Display header
    print(OutputFormatter.header("ATTACK RECORDS ANALYSIS"))
    
    # Generate and display report
    report_text = logger.generate_report()
    print(report_text)
    
    # Show recent attacks in professional table format
    print(OutputFormatter.section("RECENT ATTACKS DETAILED"))
    
    recent = logger.get_recent_attacks(limit=10)
    print(OutputFormatter.attack_record_table(recent))
    
    # Display statistics
    print(OutputFormatter.section("STATISTICS"))
    
    total = len(logger.records)
    by_severity = {}
    by_type = {}
    
    for record in logger.records:
        severity = record.get('severity', 'unknown')
        attack_type = record.get('attack_type', 'unknown')
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[attack_type] = by_type.get(attack_type, 0) + 1
    
    print(OutputFormatter.system_statistics(total, by_type, by_severity))
    
    # Interactive mode
    while True:
        print(OutputFormatter.section("INTERACTIVE VIEWER OPTIONS"))
        print("  1. View full details of a record")
        print("  2. Search by IP address")
        print("  3. Filter by attack type")
        print("  4. Filter by severity")
        print("  5. Exit")
        print("")
        
        choice = input("  Select option (1-5): ").strip()
        
        if choice == '1':
            try:
                record_id = int(input("\n  Enter record ID: ").strip())
                for record in logger.records:
                    if record.get('id') == record_id:
                        print(OutputFormatter.attack_record_detail(record))
                        break
                else:
                    print(OutputFormatter.error_message("RECORD NOT FOUND", f"No record found with ID {record_id}"))
            except ValueError:
                print(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid record ID number."))
        
        elif choice == '2':
            ip = input("\n  Enter IP address to search: ").strip()
            matches = [r for r in logger.records if r.get('ip_address') == ip]
            if matches:
                print(OutputFormatter.subheader(f"SEARCH RESULTS FOR IP: {ip}"))
                print(OutputFormatter.attack_record_table(matches))
            else:
                print(OutputFormatter.info_message("NO MATCHES", [f"No attacks found for IP: {ip}"]))
        
        elif choice == '3':
            print("\n  Available attack types:")
            unique_types = sorted(set(r.get('attack_type', 'unknown') for r in logger.records))
            for i, attack_type in enumerate(unique_types, 1):
                print(f"    {i}. {attack_type.replace('_', ' ').title()}")
            
            try:
                type_choice = int(input("\n  Select attack type number: ").strip())
                if 1 <= type_choice <= len(unique_types):
                    selected_type = unique_types[type_choice - 1]
                    matches = [r for r in logger.records if r.get('attack_type') == selected_type]
                    print(OutputFormatter.subheader(f"ATTACKS: {selected_type.upper()}"))
                    print(OutputFormatter.attack_record_table(matches))
            except ValueError:
                print(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid selection number."))
        
        elif choice == '4':
            print("\n  Available severity levels:")
            unique_severity = sorted(set(r.get('severity', 'unknown') for r in logger.records))
            for i, severity in enumerate(unique_severity, 1):
                print(f"    {i}. {severity.upper()}")
            
            try:
                sev_choice = int(input("\n  Select severity level number: ").strip())
                if 1 <= sev_choice <= len(unique_severity):
                    selected_severity = unique_severity[sev_choice - 1]
                    matches = [r for r in logger.records if r.get('severity') == selected_severity]
                    print(OutputFormatter.subheader(f"ATTACKS WITH SEVERITY: {selected_severity.upper()}"))
                    print(OutputFormatter.attack_record_table(matches))
            except ValueError:
                print(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid selection number."))
        
        elif choice == '5':
            print(OutputFormatter.info_message("VIEWER CLOSED", ["Thank you for using Sentinel Attack Viewer."]))
            break
        
        else:
            print(OutputFormatter.error_message("INVALID OPTION", "Please select a valid option (1-5)."))


if __name__ == "__main__":
    main()

