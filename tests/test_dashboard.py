import os
import sys
import re
import base64
import pytest

# Add parent directory to path to import root-level modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set fake credentials BEFORE importing app module
os.environ['DASHBOARD_USER'] = 'test'
os.environ['DASHBOARD_PASS'] = 'test'

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
import dashboard.app as app_mod

client = TestClient(app_mod.app)


def _basic_auth_header(username: str, password: str) -> dict:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_api_summary_unauthorized():
    r = client.get('/api/summary')
    assert r.status_code == 401


def test_api_summary_authorized():
    r = client.get('/api/summary', headers=_basic_auth_header('test', 'test'))
    assert r.status_code == 200
    data = r.json()
    assert 'severity_counts' in data


def test_index_and_websocket_token():
    r = client.get('/', headers=_basic_auth_header('test', 'test'))
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
