# Sentinel Agent v2.2 - Fresh Start Complete Guide

## Overview
This guide walks you through setting up Sentinel Agent from a fresh clone, including handling the cloned database that may contain stale credentials.

---

## ⚡ Quick Start (5 Minutes)

### For Ubuntu/Linux:

```bash
# 1. Clone the repository
git clone https://github.com/chandan5615/Project.git
cd Project

# 2. Reset the database to generate fresh credentials
docker-compose down
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt
rm -rf data/attack_records.json data/sentinel_intel.db data/metrics.db

# 3. Start Ollama on host machine (in another terminal)
ollama serve

# 4. Build and start the container
docker-compose build --no-cache
docker-compose up -d

# 5. Wait for startup and get the password
sleep 5
docker-compose logs sentinel-agent | grep -A 2 "DEFAULT ADMIN"

# 6. Run automated setup
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo

# Done! Check results
python3 sentinel_auto.py status
```

---

## 📋 Prerequisites

### System Requirements
- **Docker & Docker Compose** installed
- **Python 3.7+** (for host machine automation)
- **Ollama** running on host machine (port 11434)
- **Ubuntu/Linux** recommended (Windows WSL2 also works)
- **Ports available**: 8000 (API), 8501 (Dashboard), 11434 (Ollama)

### Installation Check

```bash
# Verify Docker
docker --version
docker-compose --version

# Verify Python
python3 --version

# Verify Ollama (should be running)
curl http://localhost:11434/api/tags
```

---

## 🔧 Fresh Setup (Step-by-Step)

### Step 1: Clone the Repository

```bash
cd ~
git clone https://github.com/chandan5615/Project.git
cd Project
```

**Expected output:**
```
Cloning into 'Project'...
Receiving objects: 100% (480/480), 21.98 MiB | 1.54 MiB/s, done.
```

### Step 2: Clean Database (CRITICAL!)

The cloned repo includes existing database files. Reset them:

```bash
# Stop any running container
docker-compose down

# Remove old database files
rm -f data/auth.db
rm -f data/INITIAL_CREDENTIALS.txt
rm -f data/attack_records.json
rm -f data/sentinel_intel.db
rm -f data/metrics.db

# Optional: Remove old logs
rm -rf logs/*
```

**Why?** The old `auth.db` contains stored credentials. Removing it forces the container to create a NEW admin user with a NEW password that gets logged.

### Step 3: Start Ollama on Host (CRITICAL!)

Open a **separate terminal**:

```bash
# Start Ollama (keep running in background)
ollama serve

# Expected output:
# 2026/02/08 17:00:00 Listening on 127.0.0.1:11434 (http)
```

Pull the model if needed:
```bash
ollama pull llama3:8b
```

**Leave this terminal open!** Docker needs to reach Ollama at `http://127.0.0.1:11434`

### Step 4: Build Docker Image

```bash
cd Project
docker-compose build --no-cache
```

**Expected output:**
```
Building sentinel-agent
[+] Building 3.7s (19/19) FINISHED

=> [stage-1 10/10] RUN mkdir -p /app/logs /app/data...
=> naming to docker.io/library/sentinel-agent:2.2
```

### Step 5: Start the Container

```bash
docker-compose up -d
```

**Verify startup:**
```bash
# Should show: Up (healthy)
docker-compose ps

# Check full logs
docker-compose logs sentinel-agent
```

**Expected in logs** (look for this):
```
Detecting Ollama server...
[SUCCESS] Found Ollama on host at http://127.0.0.1:11434
[SUCCESS] Model llama3:8b is available

[1/2] Starting Sentinel Agent monitor (main.py)...
[2/2] Starting REST API server (sentinel_api.py on port 8000)...
```

### Step 6: Extract Credentials

```bash
# Get the password from logs
docker-compose logs sentinel-agent | grep -A 2 "DEFAULT ADMIN CREDENTIALS"
```

**Expected output:**
```
DEFAULT ADMIN CREDENTIALS (SAVE THESE NOW!):
  Username: admin
  Password: <RANDOM_32_CHAR_PASSWORD>
CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!
```

Or check the credentials file:
```bash
cat data/INITIAL_CREDENTIALS.txt
```

### Step 7: Test API Connectivity

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected output:
# {"status":"healthy","version":"2.2","timestamp":"2026-02-08T17:57:49.752296"}
```

### Step 8: Verify Authentication

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PASSWORD_HERE"}'

# Expected output:
# {"token":"<your_api_token>","expires_in":86400}
```

---

## 🚀 Run Automated Testing

### Option A: Python Automation (Recommended for Cross-Platform)

```bash
# Install requests if needed
pip3 install requests

# Setup: Extracts password and token
python3 sentinel_auto.py setup

# Run full demo: SSH + SQL + DDoS tests
python3 sentinel_auto.py demo

# Check results
python3 sentinel_auto.py status

# View test results
cat test_results/incidents.json
```

### Option B: Bash Automation (Native for Linux/macOS)

```bash
# Make script executable
chmod +x sentinel_setup.sh

# Setup
./sentinel_setup.sh setup

# Run demo
./sentinel_setup.sh demo

# Check status
./sentinel_setup.sh status
```

### Option C: Manual Testing (Step-by-Step)

```bash
# 1. Get password
PASS=$(docker-compose logs sentinel-agent | grep "Password:" | awk '{print $NF}')
echo "Password: $PASS"

# 2. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 3. Test SSH attack detection
curl -s http://localhost:22 &        # Dummy SSH connection
curl -s http://localhost:22 &
# ... repeat several times ...

# 4. Check incidents
curl -X GET "http://localhost:8000/api/incidents/recent?limit=10" \
  -H "X-API-Key: $TOKEN"

# 5. View metrics
curl -X GET "http://localhost:8000/api/metrics/detection" \
  -H "X-API-Key: $TOKEN"
```

---

## ✅ Verification Checklist

After setup, verify each item:

- [ ] Ollama is running (`curl http://localhost:11434/api/tags` returns model list)
- [ ] Docker container is healthy (`docker-compose ps` shows "Up (healthy)")
- [ ] API is responding (`curl http://localhost:8000/api/health` returns JSON)
- [ ] Password is visible in logs (`docker-compose logs | grep "DEFAULT ADMIN"`)
- [ ] Login works (`curl /api/auth/login` returns token)
- [ ] Automation script found password (`sentinel_auto.py setup` succeeds)
- [ ] Tests ran successfully (`sentiment_auto.py demo` shows attack detection)
- [ ] Results saved (`ls test_results/` shows JSON files)

---

## 🐛 Troubleshooting

### Issue 1: "Container is not healthy"

**Symptoms:**
```
docker-compose ps
# Shows: sentinel-agent    Up (unhealthy)
```

**Solutions:**
```bash
# Check what's wrong
docker-compose logs sentinel-agent

# Common fixes:
# 1. Ollama not running on host
ollama serve

# 2. Ollama port blocked
netstat -tuln | grep 11434

# 3. Model not pulled
ollama pull llama3:8b

# 4. Restart container
docker-compose restart sentinel-agent
```

---

### Issue 2: "Could not find password in logs"

**Symptoms:**
```
python3 sentinel_auto.py setup
# ✗ Could not find password in logs
```

**Solutions:**
```bash
# Check if auth.db still exists from old clone
ls -la data/auth.db

# If it exists, the default user was never created
# Solution: Reset database
docker-compose down
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt
docker-compose up -d
sleep 5
docker-compose logs sentinel-agent | grep "DEFAULT ADMIN"
```

---

### Issue 3: "Connection refused on port 8000"

**Symptoms:**
```
curl http://localhost:8000/api/health
# Connection refused
```

**Solutions:**
```bash
# Check if API is actually running
docker-compose logs sentinel-agent | grep "Uvicorn running"

# Wait longer for startup
sleep 10
curl http://localhost:8000/api/health

# Check port availability
netstat -tuln | grep 8000

# Restart API service
docker-compose restart sentinel-agent
```

---

### Issue 4: "Token file not found" after setup

**Symptoms:**
```
python3 sentinel_auto.py status
# ✗ Token file not found. Run: python3 sentinel_auto.py setup
```

**Solutions:**
```bash
# The setup didn't complete successfully
# Check what went wrong:
python3 sentinel_auto.py setup

# Get token manually
PASS=$(cat data/INITIAL_CREDENTIALS.txt | grep Password | awk '{print $NF}')
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$PASS\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
  
echo "$TOKEN" > .sentinel_token
echo "$PASS" > .sentinel_password
```

---

### Issue 5: "Ollama connection failed"

**Symptoms:**
```
docker-compose logs sentinel-agent
# ERROR: Could not reach Ollama server
# http://127.0.0.1:11434
```

**Solutions:**
```bash
# 1. Make sure Ollama is running
ollama serve

# 2. In a new terminal, verify connectivity
curl http://localhost:11434/api/tags

# 3. Check if model is available
ollama list

# 4. If not, pull it
ollama pull llama3:8b

# 5. Restart container
docker-compose restart sentinel-agent
```

---

### Issue 6: Permission denied on data files

**Symptoms:**
```
rm: cannot remove 'Project/data/auth.db': Permission denied
```

**Solutions:**
```bash
# Use sudo to remove files
sudo rm -rf Project/data/*
sudo rm -rf Project/logs/*

# Or change ownership
sudo chown -R $USER:$USER Project/data
sudo chown -R $USER:$USER Project/logs
```

---

## 📊 Dashboard Access

After successful setup:

```bash
# View detected incidents
curl -X GET "http://localhost:8000/api/incidents/recent?limit=10" \
  -H "X-API-Key: $(cat .sentinel_token)"

# View detection metrics
curl -X GET "http://localhost:8000/api/metrics/detection" \
  -H "X-API-Key: $(cat .sentinel_token)"

# View system health
curl -X GET "http://localhost:8000/api/system/health" \
  -H "X-API-Key: $(cat .sentinel_token)"
```

---

## 📚 Next Steps

1. **Read USER_GUIDE.md** - Learn all features and how to use them
2. **Read ATTACK_TESTING_GUIDE.md** - Understand how to test attack detection
3. **Read AUTOMATION_GUIDE.md** - Detailed automation tool documentation
4. **Check QUICK_REFERENCE.md** - API endpoint reference

---

## 🆘 Still Having Issues?

```bash
# Collect debug information
echo "=== Docker Status ==="
docker-compose ps

echo "=== Container Logs ==="
docker-compose logs sentinel-agent 2>&1 | tail -50

echo "=== API Health ==="
curl -s http://localhost:8000/api/health

echo "=== Ollama Status ==="
curl -s http://localhost:11434/api/tags

echo "=== Files ==="
ls -la data/
ls -la test_results/

# Share this output when asking for help
```

---

## 📞 Support

- **Documentation**: See `docs_markdown/` folder
- **Quick Reference**: `QUICK_REFERENCE.md`
- **API Documentation**: `USER_GUIDE.md`
- **Testing Guide**: `ATTACK_TESTING_GUIDE.md`
