import os
from types import SimpleNamespace
import pytest

# Ensure agents does not do network checks at import time
os.environ['SENTINEL_SKIP_OLLAMA_CHECK'] = '1'

from main import SentinelAgent


def test_remediation_cancelled(monkeypatch):
    sa = SentinelAgent()

    calls = []
    def fake_insert_action(incident_id, action_type, details, success):
        calls.append((incident_id, action_type, details, success))

    monkeypatch.setattr('main.data_engine.insert_action', fake_insert_action)
    # Simulate user saying 'no' to execution
    monkeypatch.setattr('builtins.input', lambda prompt='': 'no')

    report = {"firewall_rule": "iptables -A INPUT -s 1.2.3.4 -j DROP", "severity": "high"}
    sa._handle_remediation(report, '1.2.3.4', incident_id=42)

    assert (42, 'proposed_firewall', report['firewall_rule'], False) in calls
    assert (42, 'firewall_cancelled', 'User cancelled execution', False) in calls


def test_remediation_execute_success(monkeypatch):
    sa = SentinelAgent()

    calls = []
    def fake_insert_action(incident_id, action_type, details, success):
        calls.append((incident_id, action_type, details, success))

    monkeypatch.setattr('main.data_engine.insert_action', fake_insert_action)

    # Simulate user approving and then confirming execution
    inputs = iter(['yes', 'EXECUTE'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))

    # Mock subprocess.run to simulate a successful iptables command
    def fake_run(args, capture_output, text, timeout):
        return SimpleNamespace(returncode=0, stderr='')

    monkeypatch.setattr('main.subprocess.run', fake_run)

    report = {"firewall_rule": "iptables -A INPUT -s 1.2.3.4 -j DROP", "severity": "high"}
    sa._handle_remediation(report, '1.2.3.4', incident_id=99)

    assert (99, 'proposed_firewall', report['firewall_rule'], False) in calls
    assert any(c[1] == 'firewall_execute' and c[3] is True for c in calls)
