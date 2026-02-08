# Sentinel Agent v2.2 - User Guide

Complete guide for end-users to access features, manage accounts, and use the system effectively.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Authentication & Account Management](#authentication--account-management)
3. [Dashboard Access](#dashboard-access)
4. [Key Features & How to Use](#key-features--how-to-use)
5. [API Access](#api-access)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is Sentinel Agent?

Sentinel Agent is an **AI-powered security monitoring system** that:
- ✅ Monitors system logs in real-time
- ✅ Detects suspicious login attempts and web attacks
- ✅ Analyzes threats using local AI (Ollama)
- ✅ Manages IP whitelists/blacklists
- ✅ Provides metrics and analytics
- ✅ Offers REST API for integration

### Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| **REST API** | http://localhost:8000 | Programmatic access |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Health Check** | http://localhost:8000/api/health | System status |
| **Dashboard** | http://localhost:8501 | (Optional) Web UI |

---

## Authentication & Account Management

### Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | Auto-generated (see below) |

### Finding Your Password

**First Time Setup:**
```bash
# In Docker
docker-compose logs sentinel-agent | grep "DEFAULT ADMIN"

# Traditional Installation
cat data/INITIAL_CREDENTIALS.txt
```

**Example Output:**
```
DEFAULT ADMIN CREDENTIALS
========================
Username: admin
Password: s3cur3Rand0mP@ssw0rd123
```

### Change Your Password

**Method 1: Using Password Manager Script**
```bash
python password_manager.py

# Menu appears:
# 1. Change Password
# 2. Reset to Default
# 3. Export Credentials
# Select: 1
# Enter new password: [your_new_password]
# Confirm password: [your_new_password]
```

**Method 2: Using API**
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "X-API-Key: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "old_password": "old_pass",
    "new_password": "new_pass"
  }'
```

### Get API Token

Once logged in, obtain a token for API access:

```bash
# Method 1: Get session token (expires in 24 hours)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_PASSWORD_HERE"

# Response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIs...",
#   "expires_in": 86400,
#   "token_type": "Bearer"
# }
```

Store the token in an environment variable:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

---

## Dashboard Access

### Web Dashboard (Optional)

If enabled, access at: **http://localhost:8501**

**Features:**
- Real-time incident monitoring
- Metrics and analytics charts
- IP list management (visual)
- System health status
- Log viewer

**Login:**
1. Open browser → http://localhost:8501
2. Username: `admin`
3. Password: (same as API password)
4. Click "Login"

### REST API (Always Available)

Primary access method - works on any system:

```bash
# Root endpoint
curl http://localhost:8000/

# Health status
curl http://localhost:8000/api/health

# View system info
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/info
```

---

## Key Features & How to Use

### 1. System Health & Monitoring

**Check System Status:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.2",
  "ollama": "connected",
  "uptime_seconds": 3600,
  "memory_mb": 245
}
```

**Get Detailed Metrics:**
```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/dashboard
```

---

### 2. Threat Intelligence

#### Check an IP Reputation

**Scenario:** You detected traffic from an unknown IP and want to check if it's malicious.

```bash
# Check single IP
curl -X POST http://localhost:8000/api/threats/check-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.0.2.1"}'

# Response:
# {
#   "ip": "192.0.2.1",
#   "is_malicious": true,
#   "threat_score": 8.5,
#   "categories": ["botnet", "malware"],
#   "last_seen": "2024-02-07T14:32:00Z"
# }
```

#### Add Malicious IP to Database

**Scenario:** You've confirmed an IP is attacking your system and want to block it.

```bash
curl -X POST http://localhost:8000/api/threats/add-malicious \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.45",
    "reason": "Brute force SSH attacks detected",
    "threat_level": "critical",
    "added_by": "admin"
  }'

# Response:
# {
#   "success": true,
#   "message": "IP added to threat database"
# }
```

#### View All Threat Patterns

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/threats/patterns
```

---

### 3. IP Management (Whitelist/Blacklist)

#### Whitelist Safe IPs

**Scenario:** Your office IP should never be blocked, even if suspicious activity is detected.

```bash
curl -X POST http://localhost:8000/api/lists/whitelist-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.100",
    "reason": "Office network - trusted",
    "added_by": "admin"
  }'

# Response:
# {
#   "success": true,
#   "message": "IP whitelisted",
#   "total_whitelisted": 5
# }
```

#### Blacklist Malicious IPs

**Scenario:** You want to block a specific IP address from all access.

```bash
curl -X POST http://localhost:8000/api/lists/blacklist-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "198.51.100.50",
    "reason": "Known botnet - prevent all access",
    "added_by": "admin"
  }'
```

#### View Your Lists

```bash
# View summary
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/summary

# Response:
# {
#   "whitelisted_count": 5,
#   "blacklisted_count": 12,
#   "last_updated": "2024-02-07T15:00:00Z"
# }

# View all whitelisted IPs
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/whitelisted-ips

# View all blacklisted IPs
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/blacklisted-ips
```

#### Remove IP from List

```bash
curl -X DELETE http://localhost:8000/api/lists/remove-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.100"
  }'
```

---

### 4. Anomaly Detection & Scoring

#### Check Anomaly Score for an IP

**Scenario:** Determine if an IP's behavior is suspicious based on multiple factors.

```bash
curl -X POST http://localhost:8000/api/anomaly/score \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "attack_type": "ssh_brute_force",
    "severity": "high",
    "fail_count": 25
  }'

# Response:
# {
#   "ip": "192.0.2.1",
#   "anomaly_score": 0.87,
#   "risk_level": "CRITICAL",
#   "reasoning": [
#     "SSH brute force attempts (25 failures)",
#     "Attack type severity is HIGH",
#     "Score exceeds critical threshold"
#   ]
# }

# Risk Levels:
# 0.0-0.3: GREEN (Normal)
# 0.3-0.6: YELLOW (Suspicious)
# 0.6-0.85: ORANGE (High Risk)
# 0.85+: RED (Critical)
```

#### View IP Behavior Profile

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/anomaly/ip-profile/192.0.2.1

# Response shows:
# {
#   "ip": "192.0.2.1",
#   "first_seen": "2024-02-05T10:00:00Z",
#   "last_seen": "2024-02-07T15:30:00Z",
#   "incident_count": 42,
#   "typical_time": "02:00 UTC",
#   "typical_port": 22
# }
```

---

### 5. Incident Management

#### View Recent Incidents

**Scenario:** Check what security events occurred recently.

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent

# Response:
# [
#   {
#     "id": "INC-2024-00142",
#     "timestamp": "2024-02-07T14:32:00Z",
#     "type": "SSH Brute Force",
#     "source_ip": "192.0.2.1",
#     "severity": "HIGH",
#     "status": "Flagged",
#     "details": "25 failed login attempts"
#   },
#   {
#     "id": "INC-2024-00141",
#     "timestamp": "2024-02-07T13:15:00Z",
#     "type": "SQL Injection Attempt",
#     "source_ip": "198.51.100.55",
#     "severity": "CRITICAL",
#     "status": "Analyzed"
#   }
# ]
```

#### View Specific Incident

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/INC-2024-00142
```

#### View Incidents from Specific IP

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/by-ip/192.0.2.1
```

---

### 6. Metrics & Analytics

#### Detection Metrics

**Scenario:** Track system performance and detection effectiveness.

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/detection

# Response:
# {
#   "total_events_analyzed": 15420,
#   "threats_detected": 127,
#   "detection_rate": 0.82,
#   "most_common_threat": "SSH Brute Force",
#   "avg_analysis_time_ms": 45
# }
```

#### Response Metrics

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/response

# Response:
# {
#   "incidents_recorded": 127,
#   "avg_response_time_sec": 2.3,
#   "ips_blacklisted": 12,
#   "ips_whitelisted": 5,
#   "accuracy": 0.94
# }
```

#### System Health Metrics

```bash
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/health

# Response:
# {
#   "cpu_usage_percent": 12.5,
#   "memory_usage_mb": 245,
#   "disk_usage_percent": 34,
#   "ollama_latency_ms": 350,
#   "api_uptime_percent": 99.8
# }
```

---

## API Access

### Authentication Header

All API calls (except `/health`) require authentication:

```bash
# Using token
curl -H "X-API-Key: YOUR_TOKEN" \
  http://localhost:8000/api/endpoint

# Or using Bearer token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/endpoint
```

### API Documentation

**Interactive Documentation:**
- Open: http://localhost:8000/docs
- Shows all available endpoints
- Try endpoints directly in browser
- See request/response examples

**Alternative Documentation:**
- OpenAPI JSON: http://localhost:8000/openapi.json
- Use with Postman, Insomnia, or other API tools

### Common HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| **GET** | Retrieve data | `curl http://localhost:8000/api/metrics/detection` |
| **POST** | Create/submit data | Check IP, add to list |
| **PUT** | Update data | Edit existing entry |
| **DELETE** | Remove data | Remove IP from list |

---

## Common Tasks

### Task 1: Set Up Your First Day

```bash
# Step 1: Change default password
python password_manager.py
# Select: 1. Change Password
# Enter new strong password

# Step 2: Get API token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=YOUR_NEW_PASSWORD" \
  | jq -r '.token')

export TOKEN  # Save for later use

# Step 3: Verify system is healthy
curl http://localhost:8000/api/health

# Step 4: Check current metrics
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/dashboard
```

### Task 2: Whitelist Your Office IPs

```bash
# Get your IP
curl ifconfig.me

# Whitelist it
curl -X POST http://localhost:8000/api/lists/whitelist-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.100",
    "reason": "Office network",
    "added_by": "admin"
  }'

# Verify
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/whitelisted-ips
```

### Task 3: Respond to an Attack

**Scenario:** You see suspicious login attempts from IP `192.0.2.1`

```bash
# Step 1: Get details
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/by-ip/192.0.2.1

# Step 2: Check threat intelligence
curl -X POST http://localhost:8000/api/threats/check-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.0.2.1"}'

# Step 3: Calculate threat score
curl -X POST http://localhost:8000/api/anomaly/score \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "attack_type": "ssh_brute_force",
    "severity": "high",
    "fail_count": 50
  }'

# Step 4: If confirmed malicious, blacklist it
curl -X POST http://localhost:8000/api/lists/blacklist-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "reason": "SSH brute force attack - 50+ failed attempts",
    "added_by": "admin"
  }'

# Step 5: Verify blacklisting
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/blacklisted-ips
```

### Task 4: Generate Security Report

```bash
# Collect all metrics
METRICS=$(curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/dashboard | jq .)

INCIDENTS=$(curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | jq .)

THREATS=$(curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/threats/patterns | jq .)

# Save to file
echo "=== Sentinel Security Report ===" > report.txt
echo "$METRICS" >> report.txt
echo "$INCIDENTS" >> report.txt
echo "$THREATS" >> report.txt

# View
cat report.txt
```

### Task 5: Check System Status (Dashboard)

If dashboard is enabled:

1. **Open Browser:** http://localhost:8501
2. **Login:** Username: `admin`, Password: (your password)
3. **View:**
   - Real-time incident chart
   - Top attacking IPs
   - Detection statistics
   - System health indicators

---

## Troubleshooting

### Q: I forgot my password
**A:** Use password manager to reset:
```bash
python password_manager.py
# Select: 2. Reset to Default
# Check data/INITIAL_CREDENTIALS.txt for new password
```

### Q: API returns "Unauthorized" (401)
**A:** Token expired or invalid:
```bash
# Get new token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=YOUR_PASSWORD" | jq '.token'

# Use new token
export TOKEN="new_token_here"
```

### Q: Getting "404 Not Found"
**A:** Check endpoint spelling and use correct base URL:
```bash
# Correct format
curl http://localhost:8000/api/health

# NOT
curl localhost:8000/health     # Missing http://
curl http://localhost:8000api/health  # Missing /
```

### Q: Dashboard not accessible (http://localhost:8501)
**A:** Dashboard is optional and may not be running:
```bash
# Check if it's enabled in docker-compose.yml
# If enabled but not working:
docker-compose logs dashboard  # View logs
docker-compose restart dashboard  # Restart it
```

### Q: How do I export my data?
**A:** Export credentials and settings:
```bash
# Export credentials
python password_manager.py
# Select: 3. Export Credentials

# Export incident data (via API)
curl -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent > incidents.json
```

### Q: Can I automate API calls?
**A:** Yes, use scripts or cron jobs:

```bash
#!/bin/bash
# check_threats.sh - Run hourly to check for new threats

TOKEN="your_token"
INCIDENTS=$(curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent)

CRITICAL=$(echo "$INCIDENTS" | jq '[.[] | select(.severity=="CRITICAL")] | length')

if [ "$CRITICAL" -gt 0 ]; then
  echo "ALERT: $CRITICAL critical incidents detected!"
  # Send email, webhook, etc.
fi
```

Add to crontab:
```bash
0 * * * * /path/to/check_threats.sh  # Run hourly
```

---

## Additional Resources

- **Full Feature List:** [README_FEATURES.md](README_FEATURES.md)
- **API Documentation:** http://localhost:8000/docs
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Docker Setup:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Security Tips:** [SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md)

---

## Getting Help

**Check System Health:**
```bash
curl http://localhost:8000/api/health
```

**View Recent Logs:**
```bash
# Docker
docker-compose logs sentinel-agent --tail 50

# Traditional
tail -50 logs/sentinel.log
```

**Report Issues:**
- Check [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Check API endpoint: http://localhost:8000/docs

---

**Last Updated:** February 2024 | **Version:** 2.2
