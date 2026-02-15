import tempfile
import os
import sys

# Add parent directory to path to import root-level modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_engine import DataEngine


def test_insert_and_query_incident():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    de = DataEngine(db_path=path)
    try:
        inc_id = de.insert_incident('1.2.3.4', 'ssh_bruteforce', 'raw log line', 'high')
        assert isinstance(inc_id, int)

        records = de.query_incidents(limit=10)
        assert any(r['id'] == inc_id for r in records)
    finally:
        de.close()
        os.remove(path)


def test_insert_action_and_query():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    de = DataEngine(db_path=path)
    try:
        inc_id = de.insert_incident('2.2.2.2', 'web_attack', 'line', 'medium')
        act_id = de.insert_action(inc_id, 'proposed_firewall', 'iptables -A INPUT -s 2.2.2.2 -j DROP', False)
        assert isinstance(act_id, int)

        actions = de.query_actions(incident_id=inc_id)
        assert any(a['id'] == act_id for a in actions)
    finally:
        de.close()
        os.remove(path)
