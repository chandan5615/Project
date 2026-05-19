#!/usr/bin/env python
"""Test display names functionality"""

from defense.attack_detector import AttackDetector

tests = ['sql_injection', 'xss_stored', 'ddos', 'ssh_brute_force', 'command_injection', 'unknown_thing']
for t in tests:
    result = AttackDetector.get_display_name(t)
    print(f'{t} -> {result}')
