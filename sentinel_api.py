"""
Sentinel Agent - REST API Module
FastAPI endpoints for external system integration.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel

from auth import get_authenticator, DashboardAuthenticator
from metrics import get_metrics, PerformanceMetrics
from list_manager import get_list_manager, ListManager
from threat_intelligence import get_threat_intelligence, OfflineThreatIntelligence
from anomaly_scorer import get_anomaly_scorer, AnomalyScorer
from data_engine import get_engine

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel Agent API",
    description="REST API for Sentinel Security Agent",
    version="2.2"
)

# Dependency injection
def get_auth() -> DashboardAuthenticator:
    return get_authenticator()

def get_list_mgr() -> ListManager:
    return get_list_manager()

def get_threat_intel() -> OfflineThreatIntelligence:
    return get_threat_intelligence()

def get_scorer() -> AnomalyScorer:
    return get_anomaly_scorer()

def get_perf_metrics() -> PerformanceMetrics:
    return get_metrics()

def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    auth: DashboardAuthenticator = Depends(get_auth)
) -> str:
    """Verify API key from headers."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    valid, username = auth.verify_api_key(x_api_key)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return username


# ============ HEALTH & INFO ENDPOINTS ============

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.2",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info")
def system_info(username: str = Depends(verify_api_key)):
    """Get system information."""
    engine = get_engine()
    
    return {
        "system": "Sentinel Agent v2.2",
        "authenticated_user": username,
        "features": [
            "Multi-agent AI",
            "Real-time log monitoring",
            "Attack detection",
            "Firewall integration",
            "Performance metrics",
            "Anomaly detection",
            "IP management"
        ]
    }


# ============ THREAT INTELLIGENCE ENDPOINTS ============

@app.post("/api/threats/check-ip")
def check_ip_threat(
    ip: str,
    threat_intel: OfflineThreatIntelligence = Depends(get_threat_intel),
    username: str = Depends(verify_api_key)
):
    """Check reputation of an IP address."""
    result = threat_intel.check_ip_reputation(ip)
    return result

@app.post("/api/threats/add-malicious")
def add_malicious_ip(
    ip: str,
    reason: str,
    severity: str = "high",
    threat_intel: OfflineThreatIntelligence = Depends(get_threat_intel),
    username: str = Depends(verify_api_key)
):
    """Add IP to malicious list."""
    threat_intel.add_malicious_ip(ip, severity, reason)
    return {"status": "added", "ip": ip}

@app.get("/api/threats/patterns")
def get_threat_patterns(
    threat_intel: OfflineThreatIntelligence = Depends(get_threat_intel),
    username: str = Depends(verify_api_key)
):
    """Get all known malicious patterns."""
    patterns = threat_intel.get_malicious_patterns()
    return {
        "count": len(patterns),
        "patterns": patterns
    }


# ============ IP WHITELIST/BLACKLIST ENDPOINTS ============

@app.post("/api/lists/whitelist-ip")
def whitelist_ip(
    ip: str,
    reason: str = "",
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Add IP to whitelist."""
    success = list_mgr.whitelist_ip(ip, reason, username)
    return {
        "status": "success" if success else "failed",
        "ip": ip,
        "action": "whitelist"
    }

@app.post("/api/lists/blacklist-ip")
def blacklist_ip(
    ip: str,
    reason: str = "",
    severity: str = "high",
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Add IP to blacklist."""
    success = list_mgr.blacklist_ip(ip, reason, severity, username)
    return {
        "status": "success" if success else "failed",
        "ip": ip,
        "action": "blacklist"
    }

@app.get("/api/lists/whitelisted-ips")
def get_whitelisted_ips(
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Get all whitelisted IPs."""
    ips = list_mgr.get_whitelisted_ips()
    return {
        "count": len(ips),
        "ips": ips
    }

@app.get("/api/lists/blacklisted-ips")
def get_blacklisted_ips(
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Get all blacklisted IPs."""
    ips = list_mgr.get_blacklisted_ips()
    return {
        "count": len(ips),
        "ips": ips
    }

@app.get("/api/lists/summary")
def get_lists_summary(
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Get summary of all lists."""
    return list_mgr.get_summary()

@app.delete("/api/lists/remove-ip")
def remove_ip(
    ip: str,
    list_type: str = "whitelist",
    list_mgr: ListManager = Depends(get_list_mgr),
    username: str = Depends(verify_api_key)
):
    """Remove IP from whitelist or blacklist."""
    if list_type == "whitelist":
        success = list_mgr.remove_whitelist_ip(ip)
    else:
        success = list_mgr.remove_blacklist_ip(ip)
    
    return {
        "status": "success" if success else "failed",
        "ip": ip,
        "list": list_type
    }


# ============ PERFORMANCE METRICS ENDPOINTS ============

@app.get("/api/metrics/detection")
def get_detection_metrics(
    hours: int = 24,
    perf_metrics: PerformanceMetrics = Depends(get_perf_metrics),
    username: str = Depends(verify_api_key)
):
    """Get detection statistics."""
    return perf_metrics.get_detection_stats(hours)

@app.get("/api/metrics/response")
def get_response_metrics(
    hours: int = 24,
    perf_metrics: PerformanceMetrics = Depends(get_perf_metrics),
    username: str = Depends(verify_api_key)
):
    """Get response action statistics."""
    return perf_metrics.get_response_stats(hours)

@app.get("/api/metrics/health")
def get_health_metrics(
    perf_metrics: PerformanceMetrics = Depends(get_perf_metrics),
    username: str = Depends(verify_api_key)
):
    """Get system health status."""
    return perf_metrics.get_health_status()

@app.get("/api/metrics/dashboard")
def get_dashboard_metrics(
    perf_metrics: PerformanceMetrics = Depends(get_perf_metrics),
    username: str = Depends(verify_api_key)
):
    """Get all metrics for dashboard."""
    return perf_metrics.get_dashboard_metrics()


# ============ ANOMALY DETECTION ENDPOINTS ============

@app.post("/api/anomaly/score")
def score_anomaly(
    incident: dict,
    scorer: AnomalyScorer = Depends(get_scorer),
    username: str = Depends(verify_api_key)
):
    """Calculate anomaly score for incident."""
    result = scorer.calculate_anomaly_score(incident)
    return result

@app.get("/api/anomaly/ip-profile")
def get_ip_profile(
    ip: str,
    scorer: AnomalyScorer = Depends(get_scorer),
    username: str = Depends(verify_api_key)
):
    """Get behavior profile for IP."""
    conn = __import__('sqlite3').connect(scorer.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT total_incidents, avg_severity, attack_types, behavior_pattern
        FROM ip_profiles WHERE ip = ?
    """, (ip,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        import json
        return {
            "ip": ip,
            "total_incidents": row[0],
            "avg_severity": row[1],
            "attack_types": json.loads(row[2]),
            "behavior_pattern": row[3]
        }
    else:
        return {"ip": ip, "status": "no_profile"}


# ============ INCIDENTS ENDPOINTS ============

@app.get("/api/incidents/recent")
def get_recent_incidents(
    limit: int = 20,
    username: str = Depends(verify_api_key)
):
    """Get recent incidents."""
    engine = get_engine()
    incidents = engine.query_incidents(limit)
    
    return {
        "count": len(incidents),
        "incidents": incidents
    }

@app.get("/api/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    username: str = Depends(verify_api_key)
):
    """Get specific incident details."""
    engine = get_engine()
    incidents = engine.query_incidents()
    
    for incident in incidents:
        if incident.get('id') == incident_id:
            return incident
    
    raise HTTPException(status_code=404, detail="Incident not found")

@app.get("/api/incidents/by-ip/{ip}")
def get_incidents_by_ip(
    ip: str,
    username: str = Depends(verify_api_key)
):
    """Get all incidents from specific IP."""
    engine = get_engine()
    incidents = engine.query_incidents()
    
    matching = [i for i in incidents if i.get('source_ip') == ip]
    
    return {
        "ip": ip,
        "count": len(matching),
        "incidents": matching
    }


# ============ AUTHENTICATION ENDPOINTS ============

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    auth: DashboardAuthenticator = Depends(get_auth)
):
    """Login and get session token (accepts form data or query params)."""
    success, token = auth.authenticate(username, password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return {
        "token": token,
        "type": "bearer",
        "expires_in": 86400  # 24 hours
    }

@app.post("/api/auth/login-json")
def login_json(
    request: LoginRequest,
    auth: DashboardAuthenticator = Depends(get_auth)
):
    """Login and get session token (JSON format)."""
    success, token = auth.authenticate(request.username, request.password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return {
        "token": token,
        "type": "bearer",
        "expires_in": 86400  # 24 hours
    }

@app.post("/api/auth/api-key")
def create_api_key(
    key_name: str,
    username: str = Depends(verify_api_key),
    auth: DashboardAuthenticator = Depends(get_auth)
):
    """Create API key for user."""
    api_key = auth.create_api_key(username, key_name)
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Failed to create API key")
    
    return {
        "key": api_key,
        "name": key_name,
        "created_at": datetime.now().isoformat(),
        "warning": "Store this key safely - you won't see it again"
    }


# ============ ERROR HANDLERS ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
