"""
Sentinel Agent - Attack Records Viewer
Professional display of recorded attacks with fancy formatting.
"""

import json
import sys
import logging
from defense.attack_logger import AttackLogger
from output_formatter import OutputFormatter
from pathlib import Path

# Module logger
log = logging.getLogger(__name__) 


def main():
    """Main function to view attack records."""
    attack_logger = AttackLogger()
    
    if not attack_logger.records:
        log.info(OutputFormatter.info_message(
            "NO ATTACK RECORDS",
            ["The attack records database is empty."]
        ))
        return
    
    # Display header
    log.info(OutputFormatter.header("ATTACK RECORDS ANALYSIS"))
    
    # Generate and display report
    report_text = attack_logger.generate_report()
    log.info(report_text)
    
    # Show recent attacks in professional table format
    log.info(OutputFormatter.section("RECENT ATTACKS DETAILED"))
    
    recent = attack_logger.get_recent_attacks(limit=10)
    log.info(OutputFormatter.attack_record_table(recent))
    
    # Display statistics
    log.info(OutputFormatter.section("STATISTICS"))
    
    total = len(attack_logger.records)
    by_severity = {}
    by_type = {}
    
    for record in attack_logger.records:
        severity = record.get('severity', 'unknown')
        attack_type = record.get('attack_type', 'unknown')
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[attack_type] = by_type.get(attack_type, 0) + 1
    
    log.info(OutputFormatter.system_statistics(total, by_type, by_severity))
    
    # Interactive mode
    while True:
        log.info(OutputFormatter.section("INTERACTIVE VIEWER OPTIONS"))
        log.info("  1. View full details of a record")
        log.info("  2. Search by IP address")
        log.info("  3. Filter by attack type")
        log.info("  4. Filter by severity")
        log.info("  5. Exit")
        log.info("")
        
        choice = input("  Select option (1-5): ").strip()
        
        if choice == '1':
            try:
                record_id = int(input("\n  Enter record ID: ").strip())
                for record in attack_logger.records:
                    if record.get('id') == record_id:
                        log.info(OutputFormatter.attack_record_detail(record))
                        break
                else:
                    log.error(OutputFormatter.error_message("RECORD NOT FOUND", f"No record found with ID {record_id}"))
            except ValueError:
                log.error(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid record ID number."))
        
        elif choice == '2':
            ip = input("\n  Enter IP address to search: ").strip()
            matches = [r for r in attack_logger.records if r.get('ip_address') == ip]
            if matches:
                log.info(OutputFormatter.subheader(f"SEARCH RESULTS FOR IP: {ip}"))
                log.info(OutputFormatter.attack_record_table(matches))
            else:
                log.info(OutputFormatter.info_message("NO MATCHES", [f"No attacks found for IP: {ip}"]))
        
        elif choice == '3':
            log.info("\n  Available attack types:")
            unique_types = sorted(set(r.get('attack_type', 'unknown') for r in attack_logger.records))
            for i, attack_type in enumerate(unique_types, 1):
                log.info(f"    {i}. {attack_type.replace('_', ' ').title()}")
            
            try:
                type_choice = int(input("\n  Select attack type number: ").strip())
                if 1 <= type_choice <= len(unique_types):
                    selected_type = unique_types[type_choice - 1]
                    matches = [r for r in attack_logger.records if r.get('attack_type') == selected_type]
                    log.info(OutputFormatter.subheader(f"ATTACKS: {selected_type.upper()}"))
                    log.info(OutputFormatter.attack_record_table(matches))
            except ValueError:
                log.error(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid selection number."))
        
        elif choice == '4':
            log.info("\n  Available severity levels:")
            unique_severity = sorted(set(r.get('severity', 'unknown') for r in attack_logger.records))
            for i, severity in enumerate(unique_severity, 1):
                log.info(f"    {i}. {severity.upper()}")
            
            try:
                sev_choice = int(input("\n  Select severity level number: ").strip())
                if 1 <= sev_choice <= len(unique_severity):
                    selected_severity = unique_severity[sev_choice - 1]
                    matches = [r for r in attack_logger.records if r.get('severity') == selected_severity]
                    log.info(OutputFormatter.subheader(f"ATTACKS WITH SEVERITY: {selected_severity.upper()}"))
                    log.info(OutputFormatter.attack_record_table(matches))
            except ValueError:
                log.error(OutputFormatter.error_message("INVALID INPUT", "Please enter a valid selection number."))
        
        elif choice == '5':
            log.info(OutputFormatter.info_message("VIEWER CLOSED", ["Thank you for using Sentinel Attack Viewer."]))
            break
        
        else:
            log.error(OutputFormatter.error_message("INVALID OPTION", "Please select a valid option (1-5)."))


if __name__ == "__main__":
    main()

