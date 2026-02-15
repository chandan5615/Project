# Sentinel Agent - Zero Interaction Automation

**Complete automation - no passwords to remember, no manual configuration!**

---

## 🚀 Quick Start (3 Minutes)

```bash
# 1. Start Ollama
ollama serve  # Terminal 1

# 2. Deploy (Terminal 2)
docker-compose up -d --build && sleep 30

# 3. Auto-setup and demo (ZERO interaction!)
python3 sentinel_auto.py setup   # Extracts password, gets token
python3 sentinel_auto.py demo    # Runs all security tests
python3 sentinel_auto.py status  # View results
```

**Done! Zero manual steps.** ✅

---

## 🎯 What Gets Automated

| Task | Manual Method | Automated | Time Saved |
|------|---------------|-----------|-----------|
| Extract password | Search logs manually | ✅ Auto-extract | 5 min |
| Authenticate & get token | curl commands | ✅ Automatic | 3 min |
| Save token | Copy/paste | ✅ Auto-save to file | 2 min |
| Run SSH tests | 15 manual commands | ✅ One command | 10 min |
| Run SQL tests | 4-10 manual requests | ✅ One command | 5 min |
| Run DDoS tests | Manual scripting | ✅ One command | 5 min |
| **TOTAL** | **30+ Minutes** | **~3 Minutes** | **90% Saved!** |

---

## 📂 sentinel_auto.py - Main Tool

**The only automation tool you need!** ✅ All features verified.

### All Commands

```bash
# Setup & Testing
python3 sentinel_auto.py setup    # Auto-authenticate (zero interaction)
python3 sentinel_auto.py demo     # Run all security tests  
python3 sentinel_auto.py status   # Live dashboard

# Individual Tests
python3 sentinel_auto.py test-ssh    # SSH brute force (15 attempts)
python3 sentinel_auto.py test-sql    # SQL injection (4 payloads)
python3 sentinel_auto.py test-ddos   # DDoS simulation (50 requests)

# Utilities
python3 sentinel_auto.py check       # Check detected incidents
python3 sentinel_auto.py help        # Show help
```

### Web Dashboard Access

```bash
# Access interactive web dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

**Open:** http://localhost:8501

**See [WEB_DASHBOARD_SETUP.md](WEB_DASHBOARD_SETUP.md) for complete guide**

---

## 🔧 Command Details

### `setup` - Zero Interaction Authentication

**Automatically:**
1. ✅ Waits for container health (auto-retry)
2. ✅ Tests API connectivity
3. ✅ Extracts admin password from logs
4. ✅ Authenticates with API
5. ✅ Gets Bearer token (24hr validity)
6. ✅ Saves to `.sentinel_token` file
7. ✅ Validates token works

**Output:**
```
✓ Container is healthy
✓ API is healthy (v2.2)
✓ Password extracted: s3cur3***...***xyz
✓ API token obtained: eyJ***...***abc
✓ Token saved to .sentinel_token
✅ Setup complete!
```

**Files created:** `.sentinel_token` (your API token)

---

### `demo` - Full Security Test

**Runs:**
1. Baseline metrics capture
2. SSH brute force (15 attempts)
3. SQL injection (4 payloads)
4. DDoS simulation (50 requests)
5. AI analysis (30s wait)
6. Show detected incidents

**Output:**
```
✓ Baseline captured (0 events, 0 threats)
✓ SSH brute force test completed (15 attempts)
✓ SQL injection test completed
✓ DDoS test completed (50 requests)
⏳ Waiting 30 seconds for analysis...
⚠ No incidents detected yet

View dashboard: python3 sentinel_auto.py status
```

---

### `status` - Live Dashboard

```
============================================================
              Sentinel Agent Status Dashboard
============================================================

System Health:
  Status: healthy
  Version: 2.2
  Uptime: 3600s

Detection Metrics:
  Total Events: 1542
  Threats Detected: 142
  Detection Rate: 9.2%

Recent Incidents:
  • SSH Brute Force (HIGH) from 192.168.1.100
  • SQL Injection (CRITICAL) from 203.0.113.45

IP Lists:
  Whitelisted: 5
  Blacklisted: 23
```

---

## 🔑 Token Management

### Auto-Saved Token: `.sentinel_token`

After `setup`, your token is auto-saved.

**Usage:**
```bash
# Bash
TOKEN=$(cat .sentinel_token)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/incidents/recent

# Python
with open('.sentinel_token') as f:
    token = f.read().strip()
headers = {'Authorization': f'Bearer {token}'}
```

### Token Expiration

Tokens last **24 hours**. If expired:
```bash
python3 sentinel_auto.py setup  # Takes 10 seconds
```

---

## 🌐 Remote Deployment (Windows → Linux)

```powershell
# From Windows PowerShell
ssh ubuntu@IP_ADDRESS "cd ~/sentinel-agent && docker-compose up -d --build && sleep 30 && python3 sentinel_auto.py setup && python3 sentinel_auto.py demo"
```

**Or step by step:**
```powershell
ssh ubuntu@IP_ADDRESS
cd sentinel-agent
docker-compose up -d --build && sleep 30
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

---

## 🔄 Typical Workflows

### First Time Setup
```bash
docker-compose up -d --build && sleep 30
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

### Daily Usage
```bash
python3 sentinel_auto.py status  # View dashboard
python3 sentinel_auto.py check   # Check incidents
```

### After Container Restart
```bash
# Container generates new password
python3 sentinel_auto.py setup  # Re-authenticate (10 seconds)
```

---

## 🛠️ API Integration

### Using Auto-Saved Token

```bash
TOKEN=$(cat .sentinel_token)

# Get incidents
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/incidents/recent | jq

# Get metrics
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/metrics/detection | jq

# Blacklist IP
curl -s -X POST http://localhost:8000/api/lists/blacklist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.168.1.100","reason":"Brute force"}' | jq
```

### Python Integration

```python
import requests

with open('.sentinel_token') as f:
    token = f.read().strip()

headers = {'Authorization': f'Bearer {token}'}
r = requests.get('http://localhost:8000/api/incidents/recent', headers=headers)
print(r.json())
```

---

## 📝 Troubleshooting

### Container not healthy
```bash
docker-compose logs sentinel-agent
docker-compose down -v
docker-compose up -d --build && sleep 30
python3 sentinel_auto.py setup
```

### Invalid credentials / Invalid API key
Token expired. Re-run:
```bash
python3 sentinel_auto.py setup
```

### Connection refused
Start Ollama:
```bash
ollama serve
```

### Demo shows no incidents
Normal - simulated attacks don't generate real logs. For real detection:
```bash
# From another machine
ssh user@sentinel-host  # Try wrong passwords
curl "http://sentinel-host/api?id=1' OR '1'='1"
```

---

## ✅ Summary

**sentinel_auto.py features:**
- ✅ Zero human interaction
- ✅ Automatic password extraction
- ✅ Auto-authentication
- ✅ Token persistence
- ✅ Full test suite
- ✅ Live dashboard
- ✅ Cross-platform (Windows, Linux, macOS)

**One command to deploy:**
```bash
docker-compose up -d --build && sleep 30 && python3 sentinel_auto.py setup && python3 sentinel_auto.py demo
```

For more details:
- [README.md](README.md) - Main documentation
- [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) - Quick start
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
