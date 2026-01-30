import os
import re
import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
import dashboard.app as app_mod

# Set fake credentials for tests
os.environ['DASHBOARD_USER'] = 'test'
os.environ['DASHBOARD_PASS'] = 'test'

client = TestClient(app_mod.app)


def test_api_summary_unauthorized():
    r = client.get('/api/summary')
    assert r.status_code == 401


def test_api_summary_authorized():
    r = client.get('/api/summary', auth=('test', 'test'))
    assert r.status_code == 200
    data = r.json()
    assert 'severity_counts' in data


def test_index_and_websocket_token():
    r = client.get('/', auth=('test', 'test'))
    assert r.status_code == 200
    html = r.text
    # Token is embedded in page as WS_TOKEN
    m = re.search(r"const WS_TOKEN = '([0-9a-fA-F\-]+)';", html)
    assert m, 'WS token not found in page'
    token = m.group(1)

    # Now connect to websocket using the token
    with client.websocket_connect(f"/ws/summary?token={token}") as ws:
        msg = ws.receive_text()
        assert 'severity_counts' in msg
