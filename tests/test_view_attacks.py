import logging
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
