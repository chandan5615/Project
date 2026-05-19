#!/usr/bin/env python
"""Test DDoS detection functionality"""

from sensors.web_sensor import WebLogHandler
import tempfile

results = []
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
    test_log = f.name

handler = WebLogHandler(lambda ip, line, info: results.append(info), test_log)
handler._ddos_threshold = 5
handler._ddos_window = 10

fake_line = '203.0.113.1 - - [19/May/2026:10:00:00 +0000] GET / HTTP/1.1 200 1234'
for i in range(6):
    result = handler._check_rate_based_attacks('203.0.113.1', fake_line)
    if result:
        print(f'Request {i+1}: {result["attack_type"]} -- {result["description"]}')
        break
    else:
        print(f'Request {i+1}: no alert yet')
