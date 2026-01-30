"""
Zero-Exposure Admin Dashboard (FastAPI)
- Internal-only: bind to 127.0.0.1
- Provides simple JSON endpoints that query the DataEngine and a single-page UI using Plotly via CDN
"""
from fastapi import FastAPI, Request, Depends, status, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from data_engine import get_engine
from collections import Counter, defaultdict
import json
from datetime import datetime, timedelta
import os
import secrets
import uuid
import asyncio

app = FastAPI(title="Sentinel Admin Dashboard")

# Basic auth setup
security = HTTPBasic()
DASHBOARD_USER = os.getenv('DASHBOARD_USER', 'sentinel')
DASHBOARD_PASS = os.getenv('DASHBOARD_PASS', 'sentinel')
# Token expiry seconds
TOKEN_TTL = int(os.getenv('DASHBOARD_WS_TOKEN_TTL', '300'))
# In-memory token store: token -> expiry
_active_tokens = {}


data_engine = get_engine()


@app.get("/api/summary")
def api_summary(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, DASHBOARD_USER)
    correct_pass = secrets.compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    incidents = data_engine.query_incidents(limit=1000)

    # By severity
    severity_counts = Counter([i.get('severity', 'unknown').lower() for i in incidents])
    # By attack_type
    type_counts = Counter([i.get('attack_type', 'unknown').lower() for i in incidents])

    # Time series (group by day over last 14 days)
    now = datetime.utcnow()
    timeseries = defaultdict(int)
    for inc in incidents:
        ts = inc.get('timestamp')
        if ts:
            try:
                d = datetime.fromisoformat(ts)
                # Day bucket
                day = d.date().isoformat()
                timeseries[day] += 1
            except Exception:
                continue

    # Sort timeseries by day
    series = sorted([(day, timeseries[day]) for day in timeseries])

    return JSONResponse({
        "severity_counts": dict(severity_counts),
        "type_counts": dict(type_counts),
        "time_series": series,
    })


@app.get("/api/records")
def api_records(credentials: HTTPBasicCredentials = Depends(security), ip: str = None, limit: int = 100, offset: int = 0):
    correct_user = secrets.compare_digest(credentials.username, DASHBOARD_USER)
    correct_pass = secrets.compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    records = data_engine.query_incidents(limit=limit, offset=offset)
    if ip:
        records = [r for r in records if r.get('source_ip') == ip]
    return JSONResponse(records)


@app.get("/api/network")
def api_network(credentials: HTTPBasicCredentials = Depends(security), limit: int = 200):
    correct_user = secrets.compare_digest(credentials.username, DASHBOARD_USER)
    correct_pass = secrets.compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Build a simple node-link between IPs and attack types
    incidents = data_engine.query_incidents(limit=limit)
    nodes = {}
    links = []
    node_id = 0

    def get_node_id(key):
        nonlocal node_id
        if key not in nodes:
            nodes[key] = node_id
            node_id += 1
        return nodes[key]

    for inc in incidents:
        ip = inc.get('source_ip') or 'unknown'
        atype = inc.get('attack_type') or 'unknown'
        src = get_node_id(ip)
        dst = get_node_id(atype)
        links.append({"source": src, "target": dst})

    # Invert nodes map
    inv_nodes = [{"id": nid, "label": key} for key, nid in nodes.items()]

    return JSONResponse({"nodes": inv_nodes, "links": links})


@app.websocket("/ws/summary")
async def websocket_summary(websocket: WebSocket):
    # Validate token passed as query param: ws://host/ws/summary?token=...
    token = websocket.query_params.get('token')
    if token is None or token not in _active_tokens:
        await websocket.close(code=1008)
        return

    # Check expiry
    expiry = _active_tokens.get(token)
    if expiry is None or expiry < datetime.utcnow():
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            # Send a lightweight summary ping
            incidents = data_engine.query_incidents(limit=1000)
            severity_counts = Counter([i.get('severity', 'unknown').lower() for i in incidents])
            type_counts = Counter([i.get('attack_type', 'unknown').lower() for i in incidents])
            await websocket.send_text(json.dumps({
                'severity_counts': dict(severity_counts),
                'type_counts': dict(type_counts),
                'time': datetime.utcnow().isoformat()
            }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/", response_class=HTMLResponse)
def index(credentials: HTTPBasicCredentials = Depends(security)):
    # Validate basic auth
    correct_user = secrets.compare_digest(credentials.username, DASHBOARD_USER)
    correct_pass = secrets.compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Generate short-lived websocket token
    token = str(uuid.uuid4())
    _active_tokens[token] = datetime.utcnow() + timedelta(seconds=TOKEN_TTL)

    # Simple SPA using Plotly CDN and fetch() to the API endpoints
    html = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Sentinel Admin Dashboard (Internal Only)</title>
  <script src="https://cdn.plot.ly/plotly-2.24.2.min.js"></script>
  <style>body{{font-family: Arial, sans-serif; margin: 16px;}} .chart{{width:100%;height:400px;margin-bottom:24px;}} .table{{font-family:monospace; white-space:pre; background:#f8f8f8; padding:12px; border-radius:6px;}}</style>
</head>
<body>
  <h1>Sentinel Admin Dashboard (127.0.0.1 only)</h1>
  <div id="time_series" class="chart"></div>
  <div id="severity_donut" class="chart"></div>
  <div id="type_bar" class="chart"></div>
  <h2>Recent Records</h2>
  <div id="records" class="table"></div>

<script>
const WS_TOKEN = '%%WS_TOKEN%%';
function wsUrl(){
  const proto = (location.protocol === 'https:') ? 'wss' : 'ws';
  return `${{proto}}://${{location.host}}/ws/summary?token=${{WS_TOKEN}}`;
}

function updateCharts(s){
  const days = s.time_series.map(x => x[0]);
  const counts = s.time_series.map(x => x[1]);
  Plotly.react('time_series', [{{x: days, y: counts, type: 'bar'}}], {{title:'Incidents over time'}});

  const sevKeys = Object.keys(s.severity_counts);
  const sevVals = Object.values(s.severity_counts);
  Plotly.react('severity_donut', [{{labels: sevKeys, values: sevVals, type:'pie', hole:0.5}}], {{title:'Severity Distribution'}});

  const tKeys = Object.keys(s.type_counts);
  const tVals = Object.values(s.type_counts);
  Plotly.react('type_bar', [{{x: tKeys, y: tVals, type: 'bar'}}], {{title:'Top Attack Types'}});

  const rec = s.records || [];
  const lines = rec.map(r => `${{r.id}}\t${{r.timestamp}}\t${{r.source_ip}}\t${{r.attack_type}}\t${{r.severity}}`);
  document.getElementById('records').innerText = ['ID\tTimestamp\tIP\tType\tSeverity', ...lines].join('\n');
}

async function fetchAndRender(){
  const s = await fetch('/api/summary', {credentials: 'include'}).then(r => r.json());
  const rec = await fetch('/api/records?limit=50', {credentials: 'include'}).then(r => r.json());
  s.records = rec;
  updateCharts(s);
}

// WebSocket real-time updates
let ws;
function connectWs(){
  ws = new WebSocket(wsUrl());
  ws.onmessage = (ev) => {
    const payload = JSON.parse(ev.data);
    fetchAndRender(); // for additional record data + charts
  };
  ws.onclose = () => setTimeout(connectWs, 5000);
}

fetchAndRender();
connectWs();
</script>
</body>
</html>
"""
    # Inject WS token placeholder safely (avoids needing to escape JS braces in the HTML)
    html = html.replace('%%WS_TOKEN%%', token)
    return HTMLResponse(content=html)
