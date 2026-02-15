import logging
import sys
import os

# Add parent directory to path to import root-level modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import view_attacks
from defense.attack_logger import AttackLogger


def test_view_attacks_no_records(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    class DummyLogger:
        records = []

    monkeypatch.setattr('view_attacks.AttackLogger', lambda *args, **kwargs: DummyLogger())
    view_attacks.main()

    # Should have logged an info message that no records exist
    assert any('NO ATTACK RECORDS' in rec.message for rec in caplog.records)
