# Sentinel Agent v2.2 - Troubleshooting Guide

Fix common issues - most have a one-command solution!

---

## 🔧 Quick Fixes

### Container Unhealthy or Not Responding

**Symptoms:**
```bash
docker-compose ps
# Shows: sentinel-agent   Up (unhealthy)
# OR curl http://localhost:8000/api/health → Connection refused
```

**Fix:**
```bash
# Full rebuild
docker-compose down -v
docker-compose up -d --build
sleep 30

# Verify
docker-compose ps
curl http://localhost:8000/api/health

# Re-authenticate
python3 sentinel_auto.py setup
```

---

### Authentication Failed / Invalid API Key

**Symptoms:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/incidents
# 401 Unauthorized
```

**Cause:** Token expired (24hr limit) or container restarted

**Fix:**
```bash
# Just re-run setup (takes 10 seconds)
python3 sentinel_auto.py setup
```

---

### Connection Refused (port 8000)

**Symptoms:**
```bash
curl http://localhost:8000/api/health
# curl: (7) Failed to connect
```

**Root Cause:** API hasn't started yet, or Docker container isn't healthy

**Solution:**
```bash
# Check container status
docker-compose ps

# If unhealthy, check logs
docker-compose logs sentinel-agent | tail -50

# Wait longer for startup (can take 15-30 seconds)
sleep 30

# Try again
curl http://localhost:8000/api/health

# If still failing, restart
docker-compose restart sentinel-agent
sleep 10
curl http://localhost:8000/api/health
```

---

### 4. API Error: 401 Unauthorized

**Symptom:**
```bash
curl -X GET http://localhost:8000/api/incidents/recent
# {"detail":"Missing API key"}
```

**Root Cause:** You need to get a valid API token first

**Solution (Option A - Use Automation):**
```bash
python3 sentinel_auto.py setup
# This extracts password and gets a token
```

**Solution (Option B - Manual):**
```bash
# 1. Get password from logs
PASS=$(docker-compose logs sentinel-agent | grep "Password:" | awk '{print $NF}')
echo "Password: $PASS"

# 2. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" \
  -w "\n" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"

# 3. Save for later use
echo "$TOKEN" > .sentinel_token

# 4. Use in API calls
curl -X GET http://localhost:8000/api/incidents/recent \
  -H "X-API-Key: $TOKEN"
```

---

### 5. "Ollama connection failed"

**Symptom:**
```bash
docker-compose logs sentinel-agent
# ERROR: http://127.0.0.1:11434 - Connection refused
# [errno 111] Connection refused
```

**Root Cause:** Ollama not running on host machine

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If connection refused, start Ollama (in a new terminal):
ollama serve

# Wait 3 seconds for Ollama to start
sleep 3

# Verify it's working
curl http://localhost:11434/api/tags
# Should return: {"models":[...]}

# Back in project folder, restart container
docker-compose restart sentinel-agent
sleep 10
docker-compose ps  # Should show healthy
```

---

### 6. "Token file not found" after setup

**Symptom:**
```bash
python3 sentinel_auto.py status
# ✗ Token file not found. Run: python3 sentinel_auto.py setup
```

**Root Cause:** `sentinel_auto.py setup` didn't complete successfully

**Solution:**
```bash
# Run setup with verbose output
python3 sentinel_auto.py setup

# Check what went wrong - look for error messages
# Common issues:
#  - Password extraction failed (use docker-compose logs)
#  - API login failed (check credentials file)
#  - File write permission issue

# Manual recovery:
PASS=$(cat data/INITIAL_CREDENTIALS.txt | grep Password | awk '{print $NF}')
echo "Password is: $PASS"

# Get token manually
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}"

# Copy the token from response and save
echo "PASTE_TOKEN_HERE" > .sentinel_token
ls -la .sentinel_token  # Verify it exists
```

---

### 7. "Port 8000 already in use"

**Symptom:**
```bash
docker-compose up -d
# Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Root Cause:** Another service is using port 8000

**Solution (Option A - Free the port):**
```bash
# Find what's using port 8000
netstat -tuln | grep 8000

# Get the PID and kill it
lsof -i :8000
kill -9 <PID>

# Then try docker-compose up again
docker-compose up -d
```

**Solution (Option B - Use different port):**
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Find: ports:
#       - "8000:8000"
# Change to: - "8001:8000"

# Then start
docker-compose up -d

# Access API on port 8001 now
curl http://localhost:8001/api/health
```

---

### 8. Permission Denied on data files

**Symptom:**
```bash
rm -f data/auth.db
# rm: cannot remove 'data/auth.db': Permission denied
```

**Root Cause:** Docker ran with different user, files owned by root

**Solution:**
```bash
# Use sudo to remove files
sudo rm -rf data/auth.db data/INITIAL_CREDENTIALS.txt

# Or change ownership back to your user
sudo chown -R $USER:$USER data/
sudo chown -R $USER:$USER logs/

# Then try removing files
rm -f data/auth.db
```

---

### 9. Test Fails: "No Incidents Detected"

**Symptom:**
```bash
python3 sentinel_auto.py demo
# ✗ No incidents found after DDoS test
```

**Root Cause:** Tests might be running too fast, or rate limiting disabled

**Solution:**
```bash
# Give container more time to process logs
python3 sentinel_auto.py demo
# Wait 60+ seconds instead of 30

# Or check manually:
PASS=$(cat data/INITIAL_CREDENTIALS.txt | grep Password | awk '{print $NF}')
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Check incidents
curl -X GET http://localhost:8000/api/incidents/recent?limit=20 \
  -H "X-API-Key: $TOKEN" | python3 -m json.tool

# Check metrics
curl -X GET http://localhost:8000/api/metrics/detection \
  -H "X-API-Key: $TOKEN" | python3 -m json.tool

# View container logs
docker-compose logs sentinel-agent | grep -i "detection\|incident\|alert"
```

---

### 10. "requests library not found"

**Symptom:**
```bash
python3 sentinel_auto.py setup
# ModuleNotFoundError: No module named 'requests'
```

**Root Cause:** requests library not installed

**Solution:**
```bash
# Install requests
pip3 install requests

# Verify it's installed
python3 -c "import requests; print(requests.__version__)"

# Try sentinel_auto.py again
python3 sentinel_auto.py setup
```

---

## 🔍 Debug & Verification Commands

### Check Everything

```bash
#!/bin/bash
echo "=== System ==="
docker --version
docker-compose --version
python3 --version

echo "=== Project ==="
ls -la docker-compose.yml Dockerfile

echo "=== Docker ==="
docker-compose ps
docker-compose logs sentinel-agent 2>&1 | tail -30

echo "=== Ollama ==="
curl -s http://localhost:11434/api/tags | head -20

echo "=== API ==="
curl -s http://localhost:8000/api/health | python3 -m json.tool

echo "=== Data ==="
ls -la data/

echo "=== Credentials ==="
cat data/INITIAL_CREDENTIALS.txt 2>/dev/null || echo "File not found"
```

### Run Verification Script

```bash
# Use the provided script
bash verify_setup.sh

# It checks all prerequisites and requirements
```

---

## 🆘 Still Stuck?

Collect this information:

```bash
# Create debug report
mkdir -p debug_report

echo "=== Docker Status ===" > debug_report/status.txt
docker-compose ps >> debug_report/status.txt 2>&1

echo "=== Container Logs ===" > debug_report/logs.txt
docker-compose logs sentinel-agent >> debug_report/logs.txt 2>&1

echo "=== Ollama Status ===" > debug_report/ollama.txt
curl -s http://localhost:11434/api/tags >> debug_report/ollama.txt 2>&1

echo "=== API Health ===" > debug_report/api.txt
curl -s http://localhost:8000/api/health >> debug_report/api.txt 2>&1

echo "=== File Structure ===" > debug_report/files.txt
ls -la data/ >> debug_report/files.txt 2>&1
ls -la *.py | head -10 >> debug_report/files.txt 2>&1

# View collected info
cat debug_report/*.txt
```

Then share these files when asking for help!

---

## 📚 Related Documentation

- [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) - Complete step-by-step setup
- [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) - 2-minute quick start
- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Full automation tools guide
- [USER_GUIDE.md](docs_markdown/USER_GUIDE.md) - Feature and API documentation
- [DOCKER_TROUBLESHOOTING.md](docs_markdown/DOCKER_TROUBLESHOOTING.md) - Docker-specific issues
