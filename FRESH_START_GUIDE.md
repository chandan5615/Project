# Fresh Start Guide - Complete Setup

**Goal:** Set up Sentinel Agent from scratch with full understanding.

**Time Required:** 20-30 minutes for full setup and understanding

---

## 📋 Prerequisites

### Required Software
- ✅ **Ubuntu 20.04+** or similar Linux distribution
- ✅ **Docker & Docker Compose** installed
- ✅ **Ollama** installed with llama3:8b model
- ✅ **Python 3.8+** for automation scripts

### Install Prerequisites

**1. Install Docker**
```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group (no sudo needed)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker-compose --version
```

**2. Install Ollama**
```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3:8b

# Verify
ollama list
# Should show: llama3:8b
```

**3. Clone Repository**
```bash
cd ~
git clone <your-repo-url> Project
cd Project
```

---

## 🚀 Installation (Automated)

### The Recommended Way - Zero Human Interaction

```bash
# 1. Start Ollama (Terminal 1)
ollama serve
# Keep this running in background

# 2. Deploy and setup (Terminal 2)
cd ~/Project
docker-compose up -d --build
sleep 30  # Wait for initialization

# 3. Auto-setup (one command, zero interaction)
python3 sentinel_auto.py setup
```

**What `setup` does automatically:**
1. ✅ Waits for container to be healthy
2. ✅ Tests API connectivity
3. ✅ Extracts admin password from logs
4. ✅ Authenticates with API
5. ✅ Gets Bearer token (24hr validity)
6. ✅ Saves token to `.sentinel_token` file
7. ✅ Validates authentication works

**Output:**
```
✓ Container is healthy
✓ API is healthy (v2.2)
✓ Password extracted: s3cur3***...***xyz
✓ API token obtained: eyJ***...***abc
✓ Token saved to .sentinel_token
✅ Setup complete!
```

**Time:** ~3 minutes
**Manual steps:** 0 ✅

---
6. Waits for healthy status
7. Shows you the password

**Expected output:**
```
============================================================
  Quick Rebuild - Adding Missing Dependency
============================================================

[1/4] Stopping container...
[2/4] Cleaning old data (requires sudo)...
[3/4] Rebuilding container with python-multipart...
[4/4] Starting container...

============================================================
  ADMIN CREDENTIALS
============================================================
  Username: admin
  Password: 8YSUsLUToBj7G8yugQcSuA
============================================================

Next: Test authentication
  python3 sentinel_auto.py setup
```

**Time:** ~5 minutes

---

### Method 2: Manual Setup

**For those who prefer step-by-step control:**

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Setup Sentinel Agent

# Step 1: Stop old containers
docker-compose down -v

# Step 2: Clean old data (requires sudo - Docker creates files as root)
sudo rm -rf data/ logs/
rm -f .api_token

# Step 3: Rebuild container (no cache for fresh build)
docker-compose build --no-cache
# Takes ~5 minutes

# Step 4: Start container
docker-compose up -d

# Step 5: Wait for startup (60 seconds for initialization)
sleep 60

# Step 6: Check status
docker-compose ps
# Should show: sentinel-agent   Up   healthy

# Step 7: View logs
docker-compose logs sentinel-agent

# Step 8: Extract admin password
docker-compose logs sentinel-agent | grep "Password:"
# Copy the password shown
```

**Time:** ~10 minutes

---

## ✅ Verification

### 1. Check Container Status

```bash
docker-compose ps
```

**Expected output:**
```
     Name                   Command               State             Ports
-----------------------------------------------------------------------------------
sentinel-agent   /usr/local/bin/docker-entr...   Up (healthy)   0.0.0.0:8000->8000/tcp
```

**Key:** Status should show "**Up (healthy)**"

### 2. Check API Health

```bash
curl http://localhost:8000/api/health
```

**Expected output:**
```json
{"status":"healthy","version":"2.2"}
```

### 3. View Logs

```bash
docker-compose logs --tail=50 sentinel-agent
```

**Look for:**
```
✓ ALL DATABASES INITIALIZED SUCCESSFULLY
✓ Monitor started (PID: 20)
✓ Monitor is running
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🔐 Authentication Setup

### Automated (Recommended)

```bash
python3 sentinel_auto.py setup
```

**What it does:**
1. Waits for container to be healthy
2. Extracts password from Docker logs
3. Tests API connection
4. Authenticates with admin credentials
5. Saves JWT token to `.api_token` file

**Expected output:**
```
============================================================
              Sentinel Agent - Complete Setup
============================================================

⏳ Waiting for Sentinel Agent to be healthy...
✓ Container is healthy!

Extracting admin credentials...
✓ Password found: 8YSUsLUToBj7G8yugQcSuA

Testing authentication...
✓ Successfully authenticated
✓ Token saved to .api_token

Setup complete! Ready to use.
```

### Manual Authentication

```bash
# Get the password
PASSWORD=$(docker-compose logs sentinel-agent | grep "Password:" | tail -1 | awk '{print $NF}')

echo "Username: admin"
echo "Password: $PASSWORD"

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=$PASSWORD"

# Should return JSON with token
```

---

## 🎯 Run Security Demo

### Automated Demo

```bash
python3 sentinel_auto.py demo
```

**What it does:**
1. Generates 20 SSH brute force attacks
2. Generates 20 web application attacks (SQL injection, XSS, etc.)
3. Waits for AI agents to analyze
4. Displays detection results
5. Shows AI recommendations
6. Provides performance metrics

**Expected output:**
```
============================================================
          Sentinel Agent - Attack Demonstration
============================================================

Generating simulated attacks...
✓ Generated 20 SSH brute force attempts
✓ Generated 20 web attacks

Waiting for AI analysis (this takes ~2 minutes)...

===================  DETECTED INCIDENTS ==================

1. SSH Brute Force Attack
   Attacker: 192.168.1.100
   Severity: HIGH
   AI Analysis: "Detected 15 failed login attempts in 30 seconds.
                 IP matches known botnet behavior. 
                 RECOMMEND: Immediate block."

2. SQL Injection Attempt
   Target: /api/users
   Severity: CRITICAL
   AI Analysis: "Classic SQL injection pattern detected.
                 Attempted to bypass authentication.
                 RECOMMEND: Block IP and patch vulnerable endpoint."

[... more incidents ...]

Performance Metrics:
- Detection Time: 1.2s average
- AI Analysis Time: 8.5s average
- Total Incidents: 40
- Blocked: 38
- Allowed (whitelisted): 2
```

### Manual Testing

```bash
# Generate attacks manually
python3 test_attacks.py --auth-count 50 --web-count 50

# View results
python3 view_attacks.py
```

---

## 📊 Access Dashboard

### CLI Dashboard (Rich Terminal UI)

```bash
python3 run_dashboard.py
```

**Features:**
- Real-time incident list
- Threat intelligence lookups
- Performance metrics
- System health status
- Color-coded severity levels
- Keyboard navigation

### Web Dashboard (Streamlit)

```bash
# In separate terminal
streamlit run dashboard/web_dashboard.py
```

Then open: http://localhost:8501

**Features:**
- Interactive charts and graphs
- Incident timeline
- Attack heatmap
- IP geolocation (if enabled)
- Export to CSV

---

## 🔍 Usage Examples

### REST API

```bash
# Get auth token (saved during setup)
TOKEN=$(cat .api_token)

# List all incidents
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/incidents

# Get specific incident
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/incidents/1

# Lookup IP in threat intelligence
curl http://localhost:8000/api/threat-intel/1.2.3.4

# Add IP to blocklist
curl -X POST http://localhost:8000/api/lists/blocklist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "1.2.3.4",
    "reason": "Brute force attack",
    "duration": 86400
  }'

# Remove IP from blocklist
curl -X DELETE http://localhost:8000/api/lists/blocklist/1.2.3.4 \
  -H "Authorization: Bearer $TOKEN"

# Get performance metrics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/metrics/detection

# Get system health
curl http://localhost:8000/api/health
```

**API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## 🛠️ Troubleshooting

### Container Won't Start / Keeps Restarting

```bash
# Check logs for errors
docker-compose logs --tail=100 sentinel-agent

# Run crash diagnostic
chmod +x diagnose_crash.sh
./diagnose_crash.sh
```

**Common issues:**
1. **Port 8000 already in use**
   ```bash
   sudo lsof -i :8000
   # Kill the process using the port
   ```

2. **Ollama not running**
   ```bash
   # Check if Ollama is accessible
   curl http://localhost:11434/api/tags
   
   # If not, start it
   ollama serve
   ```

3. **Permission errors**
   ```bash
   # Docker creates files as root
   sudo rm -rf data/ logs/
   ./quick-rebuild.sh
   ```

### Authentication Fails

```bash
# Run auth diagnostic
chmod +x diagnose_auth.sh
./diagnose_auth.sh

# Or test manually
python3 test_auth.py
```

### API Not Responding

```bash
# Check if API is running inside container
docker exec -it sentinel-agent curl http://localhost:8000/api/health

# Check processes
docker exec -it sentinel-agent ps aux | grep python

# Restart container
docker-compose restart sentinel-agent
```

### No Incidents Detected

```bash
# Generate test attacks
python3 test_attacks.py --auth-count 20 --web-count 20

# Check if monitoring is active
docker-compose logs sentinel-agent | grep "monitoring: ACTIVE"

# View database directly
docker exec -it sentinel-agent python3 view_attacks.py
```

**Full Troubleshooting Guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📁 Understanding The System

### What's Monitoring?

```
/var/log/auth.log         → SSH attempts, sudo commands, authentication
/var/log/apache2/access.log → Web requests, SQL injection, XSS, etc.
```

### Attack Detection Flow

```
Log Entry → Sensor → Pattern Matcher → Whitelist Check → Threat Intel →
ML Scoring → AI Agents → Response → Database → API/Dashboard
```

### AI Agents (4 Specialists)

1. **Triage Analyst**
   - Classifies attack type
   - Assigns severity level
   - Prioritizes for investigation

2. **Threat Intel Researcher**
   - Looks up IP in threat database
   - Checks attack history
   - Identifies patterns

3. **Incident Responder**
   - Analyzes impact
   - Recommends actions
   - Creates response plan

4. **Enforcer**
   - Executes iptables blocks
   - Updates blocklists
   - Monitors effectiveness

### Databases (6 SQLite DBs)

```
data/
├── sentinel_intel.db    # Incidents, actions, detections
├── auth.db              # Users, sessions, API keys
├── threat_intel.db      # Known malicious IPs/domains
├── lists.db             # Allow/block lists
├── metrics.db           # Performance tracking
└── anomalies.db         # ML anomaly scores
```

---

## 🎓 Next Steps

### 1. Explore API Documentation
```bash
# Open in browser
http://localhost:8000/docs
```

### 2. Monitor Real-Time Logs
```bash
docker-compose logs -f sentinel-agent
```

### 3. Generate Custom Attacks
```bash
python3 test_attacks.py \
  --auth-count 100 \
  --web-count 100 \
  --pattern brute-force
```

### 4. Create Custom Rules
Edit `defense/attack_detector.py` to add new patterns.

### 5. Integrate with SIEM
Use REST API to send incidents to your SIEM system.

### 6. Performance Tuning
Adjust Ollama model size, agent prompts, detection thresholds.

---

## 📚 Additional Resources

- **README.md** - Project overview and quick start
- **COMPLETE_FIX_SUMMARY.md** - All fixes and improvements
- **TROUBLESHOOTING.md** - Solutions to common problems
- **AUTOMATION_GUIDE.md** - Automation scripts reference
- **DOCUMENTATION_MAP.md** - All available documentation

---

## ✅ Success Checklist

- [ ] Ollama installed and running
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] Container built and started
- [ ] Container status shows "healthy"
- [ ] API responds to health check
- [ ] Admin password extracted
- [ ] Authentication successful
- [ ] Demo attacks generated
- [ ] Incidents detected and displayed
- [ ] Dashboard accessible

---

**Ready to start?** Run `chmod +x quick-rebuild.sh && ./quick-rebuild.sh` 🚀

For questions or issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or run the diagnostic scripts.