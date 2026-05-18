"""
Enhanced Sentinel Admin Dashboard (FastAPI)
- Advanced security operations center dashboard
- Features: Log details, IP management, traffic monitoring, real-time analytics
- Internal-only: bind to 127.0.0.1 (local only)

USAGE:
------
# Automatic (via Docker)
docker-compose up -d

# Manual standalone
python3 dashboard/app.py

# With custom port
PORT=8000 python3 dashboard/app.py

# With custom host binding
DASHBOARD_HOST=0.0.0.0 PORT=8000 python3 dashboard/app.py

ACCESS:
-------
http://localhost:8000         (local only)
http://192.168.31.91:8000     (local network, if running standalone)

AUTHENTICATION:
---------------
Default credentials are generated on first run and saved to:
  /app/data/INITIAL_CREDENTIALS.txt (Docker)
  ./data/INITIAL_CREDENTIALS.txt (local)

Configurable via environment variables:
  DASHBOARD_USER: Username (default: generated)
  DASHBOARD_PASS: Password (default: generated, never 'admin')

ENDPOINTS:
----------
GET  /               - HTML dashboard
GET  /api/summary    - Security summary
GET  /api/incidents  - Incident list
GET  /api/ips        - IP information
POST /api/block-ip   - Block an IP
POST /api/whitelist  - Add IP to whitelist
WS   /ws             - WebSocket for real-time updates
"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request, Depends, status, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from data_engine import get_engine
from list_manager import get_list_manager
from metrics import get_metrics
from collections import Counter, defaultdict
import json
from datetime import datetime, timedelta
import os
import secrets
import uuid
import asyncio
import psutil
import requests

app = FastAPI(title="Sentinel Enhanced Admin Dashboard")

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
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

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
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    records = data_engine.query_incidents(limit=limit, offset=offset)
    if ip:
        records = [r for r in records if r.get('source_ip') == ip]
    return JSONResponse(records)


@app.get("/api/network")
def api_network(credentials: HTTPBasicCredentials = Depends(security), limit: int = 200):
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

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


@app.get("/api/traffic")
def api_traffic(credentials: HTTPBasicCredentials = Depends(security)):
    """Get current server traffic and resource usage"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        # Get active connections
        connections = psutil.net_connections(kind='inet')
        active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        return JSONResponse({
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "network_bytes_sent": net_io.bytes_sent,
            "network_bytes_recv": net_io.bytes_recv,
            "active_connections": active_connections,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/logs")
def api_logs(credentials: HTTPBasicCredentials = Depends(security), limit: int = 100, severity: str = None):
    """Get recent log entries with filtering"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    incidents = data_engine.query_incidents(limit=limit)
    if severity:
        incidents = [i for i in incidents if i.get('severity', '').lower() == severity.lower()]
    
    # Enhance with additional details
    for incident in incidents:
        incident['details_parsed'] = {
            'ip': incident.get('source_ip'),
            'attack_type': incident.get('attack_type'),
            'severity': incident.get('severity'),
            'timestamp': incident.get('timestamp'),
            'raw_log': incident.get('raw_log', '')[:200] + '...' if len(incident.get('raw_log', '')) > 200 else incident.get('raw_log', '')
        }
    
    return JSONResponse(incidents)


@app.post("/api/ip/block")
async def api_block_ip(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Block an IP address"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    data = await request.json()
    ip = data.get('ip')
    reason = data.get('reason', 'Manual block from dashboard')
    
    if not ip:
        return JSONResponse({"error": "IP address required"}, status_code=400)
    
    try:
        # Use the list manager to blacklist the IP
        list_mgr = get_list_manager()
        list_mgr.add_ip_to_blacklist(ip, reason=reason)
        return JSONResponse({"success": True, "message": f"IP {ip} blocked successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/ip/unblock")
async def api_unblock_ip(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Unblock an IP address"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    data = await request.json()
    ip = data.get('ip')
    
    if not ip:
        return JSONResponse({"error": "IP address required"}, status_code=400)
    
    try:
        # Remove from blacklist
        list_mgr = get_list_manager()
        list_mgr.remove_ip_from_blacklist(ip)
        return JSONResponse({"success": True, "message": f"IP {ip} unblocked successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/ip/status")
def api_ip_status(credentials: HTTPBasicCredentials = Depends(security)):
    """Get list of blocked and whitelisted IPs"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    try:
        list_mgr = get_list_manager()
        blacklist_data = list_mgr.get_blacklisted_ips()
        whitelist_data = list_mgr.get_whitelisted_ips()
        
        # Extract just the IP addresses for display
        blacklist = [item['ip'] for item in blacklist_data]
        whitelist = [item['ip'] for item in whitelist_data]
        
        return JSONResponse({
            "blacklist": blacklist,
            "whitelist": whitelist,
            "blacklist_count": len(blacklist),
            "whitelist_count": len(whitelist)
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/metrics/dashboard")
def api_metrics_dashboard(credentials: HTTPBasicCredentials = Depends(security)):
    """Get comprehensive dashboard metrics"""
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    try:
        metrics_mgr = get_metrics()
        incidents = data_engine.query_incidents(limit=1000)
        
        # Calculate metrics
        total_incidents = len(incidents)
        high_severity = len([i for i in incidents if i.get('severity', '').lower() == 'high'])
        blocked_ips_data = get_list_manager().get_blacklisted_ips()
        blocked_ips = len(blocked_ips_data)
        
        # Recent activity (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_incidents = [i for i in incidents if datetime.fromisoformat(i['timestamp']) > one_hour_ago] if incidents else []
        
        return JSONResponse({
            "total_incidents": total_incidents,
            "high_severity_count": high_severity,
            "blocked_ips_count": blocked_ips,
            "recent_incidents_1h": len(recent_incidents),
            "attack_types": dict(Counter([i.get('attack_type') for i in incidents])),
            "top_attackers": dict(Counter([i.get('source_ip') for i in incidents]).most_common(10))
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.websocket("/ws/summary")
async def websocket_summary(websocket: WebSocket):
    # Validate token passed as query param: wss://host/ws/summary?token=...
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
    correct_user = secrets.compare_digest(credentials.username.encode('utf-8'), DASHBOARD_USER.encode('utf-8'))
    correct_pass = secrets.compare_digest(credentials.password.encode('utf-8'), DASHBOARD_PASS.encode('utf-8'))
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

    # Generate short-lived websocket token
    token = str(uuid.uuid4())
    _active_tokens[token] = datetime.utcnow() + timedelta(seconds=TOKEN_TTL)

    # Enhanced SPA with modern UI
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sentinel SOC Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.24.2.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .dashboard-container {
      max-width: 1400px;
      margin: 0 auto;
    }
    .header {
      background: rgba(255,255,255,0.95);
      padding: 20px 30px;
      border-radius: 15px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .header h1 {
      color: #667eea;
      font-size: 28px;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .header-stats {
      display: flex;
      gap: 30px;
    }
    .stat-item {
      text-align: center;
    }
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #667eea;
    }
    .stat-label {
      font-size: 12px;
      color: #666;
      text-transform: uppercase;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }
    .card {
      background: rgba(255,255,255,0.95);
      border-radius: 15px;
      padding: 20px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #f0f0f0;
    }
    .card-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .card-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }
    .icon-purple { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .icon-green { background: linear-gradient(135deg, #56ab2f, #a8e063); color: white; }
    .icon-orange { background: linear-gradient(135deg, #f46b45, #eea849); color: white; }
    .icon-red { background: linear-gradient(135deg, #eb3349, #f45c43); color: white; }
    .icon-blue { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
    .chart { width: 100%; height: 300px; }
    .table-container {
      max-height: 400px;
      overflow-y: auto;
      margin-top: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th {
      background: #667eea;
      color: white;
      padding: 12px 8px;
      text-align: left;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    td {
      padding: 10px 8px;
      border-bottom: 1px solid #f0f0f0;
    }
    tr:hover {
      background: #f8f9fa;
    }
    .severity-high { color: white; background: #dc3545; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .severity-medium { color: white; background: #ffc107; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .severity-low { color: white; background: #28a745; padding: 4px 8px; border-radius: 4px; font-size:11px; font-weight: bold; }
    .btn {
      padding: 8px 16px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.3s;
      font-weight: 600;
    }
    .btn-danger {
      background: linear-gradient(135deg, #eb3349, #f45c43);
      color: white;
    }
    .btn-success {
      background: linear-gradient(135deg, #56ab2f, #a8e063);
      color: white;
    }
    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .traffic-gauge {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 10px;
      background: #f8f9fa;
      border-radius: 8px;
      margin: 5px 0;
    }
    .gauge-label {
      flex: 0 0 120px;
      font-weight: 600;
      color: #555;
    }
    .gauge-bar-container {
      flex: 1;
      height: 20px;
      background: #e9ecef;
      border-radius: 10px;
      overflow: hidden;
      position: relative;
    }
    .gauge-bar {
      height: 100%;
      border-radius: 10px;
      transition: width 0.5s ease;
    }
    .gauge-value {
      flex: 0 0 60px;
      text-align: right;
      font-weight: bold;
      color: #333;
    }
    .log-entry {
      background: #f8f9fa;
      border-left: 4px solid #667eea;
      padding: 12px;
      margin: 8px 0;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
    }
    .log-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-weight: bold;
    }
    .log-body {
      color: #555;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .ip-manager {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
    }
    .ip-input {
      flex: 1;
      padding: 10px;
      border: 2px solid #e9ecef;
      border-radius: 6px;
      font-size: 14px;
    }
    .ip-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    .ip-badge {
      background: #667eea;
      color: white;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .ip-badge-blocked {
      background: #dc3545;
    }
    .ip-badge button {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 14px;
    }
    .status-indicator {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
      animation: pulse 2s infinite;
    }
    .status-online { background: #28a745; }
    .status-warning { background: #ffc107; }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .metric-card {
      text-align: center;
      padding: 20px;
    }
    .metric-value {
      font-size: 36px;
      font-weight: bold;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .metric-label {
      font-size: 14px;
      color: #666;
      text-transform: uppercase;
      margin-top: 5px;
    }
    .refresh-btn {
      background: none;
      border: 2px solid #667eea;
      color: #667eea;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      transition: all 0.3s;
    }
    .refresh-btn:hover {
      background: #667eea;
      color: white;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .spinning {
      animation: spin 1s linear infinite;
    }
  </style>
</head>
<body>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      <h1>
        <span class="status-indicator status-online"></span>
        <i class="fas fa-shield-alt"></i>
        Sentinel SOC Dashboard
      </h1>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value" id="total-incidents">0</div>
          <div class="stat-label">Total Incidents</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="blocked-ips">0</div>
          <div class="stat-label">Blocked IPs</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="high-severity">0</div>
          <div class="stat-label">High Severity</div>
        </div>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="grid">
      <div class="card metric-card">
        <div class="card-icon icon-purple"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="metric-value" id="recent-1h">0</div>
        <div class="metric-label">Incidents (Last Hour)</div>
      </div>
      <div class="card metric-card">
        <div class="card-icon icon-blue"><i class="fas fa-network-wired"></i></div>
        <div class="metric-value" id="active-connections">0</div>
        <div class="metric-label">Active Connections</div>
      </div>
      <div class="card metric-card">
        <div class="card-icon icon-green"><i class="fas fa-microchip"></i></div>
        <div class="metric-value" id="cpu-usage">0%</div>
        <div class="metric-label">CPU Usage</div>
      </div>
      <div class="card metric-card">
        <div class="card-icon icon-orange"><i class="fas fa-memory"></i></div>
        <div class="metric-value" id="memory-usage">0%</div>
        <div class="metric-label">Memory Usage</div>
      </div>
    </div>

    <!-- Traffic Monitoring -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <div class="card-icon icon-blue"><i class="fas fa-tachometer-alt"></i></div>
          Server Traffic & Resources
        </div>
        <button class="refresh-btn" onclick="refreshTraffic()">
          <i class="fas fa-sync-alt" id="traffic-refresh-icon"></i> Refresh
        </button>
      </div>
      <div id="traffic-gauges">
        <div class="traffic-gauge">
          <div class="gauge-label">CPU</div>
          <div class="gauge-bar-container">
            <div class="gauge-bar" id="cpu-bar" style="background: linear-gradient(90deg, #56ab2f, #a8e063); width: 0%"></div>
          </div>
          <div class="gauge-value" id="cpu-text">0%</div>
        </div>
        <div class="traffic-gauge">
          <div class="gauge-label">Memory</div>
          <div class="gauge-bar-container">
            <div class="gauge-bar" id="memory-bar" style="background: linear-gradient(90deg, #4facfe, #00f2fe); width: 0%"></div>
          </div>
          <div class="gauge-value" id="memory-text">0%</div>
        </div>
        <div class="traffic-gauge">
          <div class="gauge-label">Disk</div>
          <div class="gauge-bar-container">
            <div class="gauge-bar" id="disk-bar" style="background: linear-gradient(90deg, #f46b45, #eea849); width: 0%"></div>
          </div>
          <div class="gauge-value" id="disk-text">0%</div>
        </div>
        <div class="traffic-gauge">
          <div class="gauge-label">Network Sent</div>
          <div class="gauge-bar-container">
            <div class="gauge-bar" id="net-sent-bar" style="background: linear-gradient(90deg, #667eea, #764ba2); width: 50%"></div>
          </div>
          <div class="gauge-value" id="net-sent-text">0 MB</div>
        </div>
        <div class="traffic-gauge">
          <div class="gauge-label">Network Recv</div>
          <div class="gauge-bar-container">
            <div class="gauge-bar" id="net-recv-bar" style="background: linear-gradient(90deg, #764ba2, #667eea); width: 50%"></div>
          </div>
          <div class="gauge-value" id="net-recv-text">0 MB</div>
        </div>
      </div>
    </div>

    <!-- IP Management -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <div class="card-icon icon-red"><i class="fas fa-ban"></i></div>
          IP Address Management
        </div>
      </div>
      <div class="ip-manager">
        <input type="text" id="ip-input" class="ip-input" placeholder="Enter IP address (e.g., 192.168.1.1)">
        <button class="btn btn-danger" onclick="blockIP()"><i class="fas fa-ban"></i> Block IP</button>
      </div>
      <div>
        <strong>Blocked IPs:</strong>
        <div class="ip-list" id="blocked-ips-list"></div>
      </div>
      <div style="margin-top: 15px;">
        <strong>Whitelisted IPs:</strong>
        <div class="ip-list" id="whitelisted-ips-list"></div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <div class="card-icon icon-purple"><i class="fas fa-chart-line"></i></div>
            Incidents Timeline
          </div>
        </div>
        <div id="time_series" class="chart"></div>
      </div>
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <div class="card-icon icon-orange"><i class="fas fa-chart-pie"></i></div>
            Severity Distribution
          </div>
        </div>
        <div id="severity_donut" class="chart"></div>
      </div>
    </div>

    <!-- Attack Types -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <div class="card-icon icon-red"><i class="fas fa-bug"></i></div>
          Top Attack Types
        </div>
      </div>
      <div id="type_bar" class="chart"></div>
    </div>

    <!-- Log Details -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <div class="card-icon icon-blue"><i class="fas fa-file-medical-alt"></i></div>
          Recent Log Details
        </div>
        <select id="severity-filter" onchange="filterLogs()" style="padding: 6px 12px; border-radius: 6px; border: 2px solid #e9ecef;">
          <option value="">All Severities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>
      <div class="table-container" id="logs-container"></div>
    </div>

    <!-- Recent Incidents Table -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <div class="card-icon icon-purple"><i class="fas fa-list"></i></div>
          Recent Incidents
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp</th>
              <th>Source IP</th>
              <th>Attack Type</th>
              <th>Severity</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="records-table"></tbody>
        </table>
      </div>
    </div>
  </div>

<script>
const WS_TOKEN = '%%WS_TOKEN%%';

// Format bytes to readable format
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Update traffic gauges
async function refreshTraffic() {
  const icon = document.getElementById('traffic-refresh-icon');
  icon.classList.add('spinning');
  
  try {
    const data = await fetch('/api/traffic', {credentials: 'include'}).then(r => r.json());
   
    document.getElementById('cpu-bar').style.width = data.cpu_percent + '%';
    document.getElementById('cpu-text').textContent = data.cpu_percent.toFixed(1) + '%';
    document.getElementById('cpu-usage').textContent = data.cpu_percent.toFixed(0) + '%';
    
    document.getElementById('memory-bar').style.width = data.memory_percent + '%';
    document.getElementById('memory-text').textContent = data.memory_percent.toFixed(1) + '%';
    document.getElementById('memory-usage').textContent = data.memory_percent.toFixed(0) + '%';
    
    document.getElementById('disk-bar').style.width = data.disk_percent + '%';
    document.getElementById('disk-text').textContent = data.disk_percent.toFixed(1) + '%';
    
    document.getElementById('net-sent-text').textContent = formatBytes(data.network_bytes_sent);
    document.getElementById('net-recv-text').textContent = formatBytes(data.network_bytes_recv);
    
    document.getElementById('active-connections').textContent = data.active_connections;
  } catch (error) {
    console.error('Error fetching traffic data:', error);
  } finally {
    icon.classList.remove('spinning');
  }
}

// Block IP
async function blockIP() {
  const ip = document.getElementById('ip-input').value.trim();
  if (!ip) {
    alert('Please enter an IP address');
    return;
  }
  
  try {
    const response = await fetch('/api/ip/block', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({ip: ip, reason: 'Blocked from dashboard'})
    });
    
    const data = await response.json();
    if (data.success) {
      document.getElementById('ip-input').value = '';
      await refreshIPStatus();
      alert(`IP ${ip} blocked successfully`);
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error blocking IP:', error);
    alert('Failed to block IP');
  }
}

// Unblock IP
async function unblockIP(ip) {
  if (!confirm(`Unblock IP ${ip}?`)) return;
  
  try {
    const response = await fetch('/api/ip/unblock', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({ip: ip})
    });
    
    const data = await response.json();
    if (data.success) {
      await refreshIPStatus();
      alert(`IP ${ip} unblocked successfully`);
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error unblocking IP:', error);
    alert('Failed to unblock IP');
  }
}

// Refresh IP status
async function refreshIPStatus() {
  try {
    const data = await fetch('/api/ip/status', {credentials: 'include'}).then(r => r.json());
    
    // Blocked IPs
    const blockedList = document.getElementById('blocked-ips-list');
    blockedList.innerHTML = '';
    data.blacklist.forEach(ip => {
      const badge = document.createElement('div');
      badge.className = 'ip-badge ip-badge-blocked';
      badge.innerHTML = `
        ${ip}
        <button onclick="unblockIP('${ip}')"><i class="fas fa-times"></i></button>
      `;
      blockedList.appendChild(badge);
    });
    
    // Whitelisted IPs
    const whitelistedList = document.getElementById('whitelisted-ips-list');
    whitelistedList.innerHTML = '';
    data.whitelist.forEach(ip => {
      const badge = document.createElement('div');
      badge.className = 'ip-badge';
      badge.innerHTML = `${ip}`;
      whitelistedList.appendChild(badge);
    });
    
    document.getElementById('blocked-ips').textContent = data.blacklist_count;
  } catch (error) {
    console.error('Error fetching IP status:', error);
  }
}

// Filter logs
async function filterLogs() {
  const severity = document.getElementById('severity-filter').value;
  const url = severity ? `/api/logs?severity=${severity}&limit=50` : '/api/logs?limit=50';
  
  try {
    const logs = await fetch(url, {credentials: 'include'}).then(r => r.json());
    const container = document.getElementById('logs-container');
    container.innerHTML = '';
    
    logs.forEach(log => {
      const entry = document.createElement('div');
      entry.className = 'log-entry';
      const severityClass = `severity-${log.severity || 'unknown'}`.toLowerCase();
      entry.innerHTML = `
        <div class="log-header">
          <span><strong>IP:</strong> ${log.source_ip} | <strong>Type:</strong> ${log.attack_type}</span>
          <span class="${severityClass}">${log.severity || 'UNKNOWN'}</span>
        </div>
        <div class="log-body">
          <strong>Time:</strong> ${new Date(log.timestamp).toLocaleString()}<br>
          <strong>Raw Log:</strong> ${log.raw_log || 'N/A'}
        </div>
      `;
      container.appendChild(entry);
    });
  } catch (error) {
    console.error('Error fetching logs:', error);
  }
}

// Update charts
function updateCharts(s) {
  const days = s.time_series.map(x => x[0]);
  const counts = s.time_series.map(x => x[1]);
  Plotly.react('time_series', [{
    x: days,
    y: counts,
    type: 'scatter',
    mode: 'lines+markers',
    line: {color: '#667eea', width: 3},
    marker: {size: 8}
  }], {
    title: '',
    margin: {t: 20, b: 40, l: 40, r: 20},
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  });

  const sevKeys = Object.keys(s.severity_counts);
  const sevVals = Object.values(s.severity_counts);
  const colors = sevKeys.map(k => {
    if (k === 'high') return '#dc3545';
    if (k === 'medium') return '#ffc107';
    return '#28a745';
  });
  Plotly.react('severity_donut', [{
    labels: sevKeys,
    values: sevVals,
    type: 'pie',
    hole: 0.6,
    marker: {colors: colors}
  }], {
    title: '',
    margin: {t: 20, b: 20, l: 20, r: 20},
    paper_bgcolor: 'rgba(0,0,0,0)',
    showlegend: true
  });

  const tKeys = Object.keys(s.type_counts);
  const tVals = Object.values(s.type_counts);
  Plotly.react('type_bar', [{
    x: tKeys,
    y: tVals,
    type: 'bar',
    marker: {
      color: tVals,
      colorscale: 'Viridis'
    }
  }], {
    title: '',
    margin: {t: 20, b: 80, l: 40, r: 20},
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  });

  const rec = s.records || [];
  const tbody = document.getElementById('records-table');
  tbody.innerHTML = '';
  rec.forEach(r => {
    const row = tbody.insertRow();
    const severityClass = `severity-${r.severity || 'unknown'}`.toLowerCase();
    row.innerHTML = `
      <td>${r.id}</td>
      <td>${new Date(r.timestamp).toLocaleString()}</td>
      <td>${r.source_ip}</td>
      <td>${r.attack_type}</td>
      <td><span class="${severityClass}">${r.severity || 'UNKNOWN'}</span></td>
      <td>
        <button class="btn btn-danger" onclick="blockIP(); document.getElementById('ip-input').value='${r.source_ip}'">
          <i class="fas fa-ban"></i> Block
        </button>
      </td>
    `;
  });
}

// Fetch and render
async function fetchAndRender() {
  const s = await fetch('/api/summary', {credentials: 'include'}).then(r => r.json());
  const rec = await fetch('/api/records?limit=50', {credentials: 'include'}).then(r => r.json());
  const metrics = await fetch('/api/metrics/dashboard', {credentials: 'include'}).then(r => r.json());
  
  s.records = rec;
  updateCharts(s);
  
  // Update header stats
  document.getElementById('total-incidents').textContent = metrics.total_incidents;
  document.getElementById('high-severity').textContent = metrics.high_severity_count;
  document.getElementById('recent-1h').textContent = metrics.recent_incidents_1h;
}

// Initialize
fetchAndRender();
refreshTraffic();
refreshIPStatus();
filterLogs();

// Auto-refresh
setInterval(fetchAndRender, 10000);   // Every 10 seconds
setInterval(refreshTraffic, 5000);     // Every 5 seconds
setInterval(refreshIPStatus, 15000);   // Every 15 seconds
setInterval(filterLogs, 8000);         // Every 8 seconds - refresh logs
</script>
</body>
</html>
"""
