# Sentinel Agent v2.2 - Production Ready

An autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. Sentinel Agent uses CrewAI for orchestration and local Ollama (Llama 3) as the LLM engine to monitor, analyze, and respond to security threats in real-time.

---

## Installation (Choose One - All Are Clean & No-Mess!)

### Docker (Recommended - Fastest!) ⭐

**Using Host Ollama (Production - v2.2 Optimized)**

**Step 1: Ensure Ollama is Running**
```bash
# Terminal 1: Start host Ollama (if not already running)
ollama serve

# Verify Ollama is working
curl http://localhost:11434/api/tags
```

**Step 2: Deploy Sentinel Agent**
```bash
# Terminal 2: Clone and navigate to project
git clone <repo> sentinel-agent
cd sentinel-agent

# Build the Docker image
docker-compose build

# Start the services
docker-compose up -d

# Wait a few seconds for services to start
sleep 5
```

**Step 3: Verify Deployment**
```bash
# Check container status
docker-compose ps
# Should show: sentinel-agent   Up (healthy)

# Test API health endpoint
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"2.2"}

# View logs (optional)
docker-compose logs -f sentinel-agent
```

**That's it!** Your system is ready. Access:
- **API**: http://localhost:8000 (REST API for all operations)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/api/health
- **Ollama**: http://localhost:11434 (local AI engine)

**Why Host Ollama?**
✅ Better performance (no container overhead)
✅ Direct GPU access
✅ Simpler setup
✅ Native system integration

**Troubleshooting:**
```bash
# If container is unhealthy or API not responding:
docker-compose logs sentinel-agent  # View logs
docker-compose restart              # Restart services
docker-compose down && docker-compose up -d  # Full restart
```

**Using Docker Ollama (Alternative):**
```bash
# Edit docker-compose.yml and uncomment ollama services
# Then run:
docker-compose --profile with-ollama up -d
```

 **Docker Guide**: [DOCKER_QUICKSTART.md](docs_markdown/DOCKER_QUICKSTART.md) | [Full Guide](docs_markdown/DOCKER_DEPLOYMENT.md) | [Troubleshooting](docs_markdown/DOCKER_TROUBLESHOOTING.md)

---

## 🚀 Running Sentinel Agent (Docker)

### Complete Startup Sequence

**Terminal 1: Start Ollama (if not already running)**
```bash
ollama serve
# Output: Listening on 127.0.0.1:11434
```

**Terminal 2: Build and Start Sentinel Agent**
```bash
cd ~/Project  # or wherever you cloned it
docker-compose build --no-cache
docker-compose up -d
```

### ⚡ Automated Setup (Recommended!)

**Instead of manual commands, use automation tools:**

```bash
# Python (easiest - Windows, Mac, Linux)
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
python3 sentinel_auto.py status

# OR Bash (Linux/macOS)
chmod +x sentinel_setup.sh
./sentinel_setup.sh setup
./sentinel_setup.sh demo
./sentinel_setup.sh status
```

**What gets automated:**
- ✅ Password extraction from logs
- ✅ API token generation  
- ✅ Container health verification
- ✅ All attack simulations
- ✅ Incident detection verification
- ✅ Test result reports

**Time saved: 48 minutes → 2 minutes!**

👉 **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Complete automation guide

---

### Manual Setup (If Preferred)

**After `docker-compose up -d`:**
```
Creating volume "project_ollama_data" with default driver
Creating sentinel-agent ... done
```

**Check real-time logs:**
```bash
docker-compose logs sentinel-agent
```

**Expected log output (successful startup):**
```
=========================================
Sentinel Agent - Container Starting
=========================================

Detecting Ollama server...
[SUCCESS] Found Ollama on host at http://127.0.0.1:11434
Checking for model: llama3:8b...
[SUCCESS] Model llama3:8b is available

[SUCCESS] Auth log found: /var/log/auth.log
[SUCCESS] Web log found: /var/log/apache2/access.log

=========================================
Configuration:
  Ollama URL: http://127.0.0.1:11434
  Ollama Model: llama3:8b
  Auth Log: /var/log/auth.log
  Web Log: /var/log/apache2/access.log
  Data Directory: /app/data
=========================================

Starting Sentinel Agent services...

[1/2] Starting Sentinel Agent monitor (main.py)...
      Monitor started (PID: 15)

[2/2] Starting REST API server (sentinel_api.py on port 8000)...
      Uvicorn running on http://0.0.0.0:8000
```

### Verify Everything is Running

```bash
# Check container status
docker-compose ps
# Should show: sentinel-agent   Up (healthy)

# Test the API
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"2.2"}

# View ongoing logs (streaming)
docker-compose logs -f sentinel-agent
```

### Access Sentinel Agent

- **REST API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:8000/api/health
- **Metrics**: http://localhost:8000/api/metrics/detection
- **Dashboard**: http://localhost:8501 (if enabled)

### Stop the Agent

```bash
# Graceful stop (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v

# View logs after stopping
docker-compose logs sentinel-agent
```

---

### Traditional Installation (Non-Docker)

**Windows Users**

**PowerShell (Recommended) ⭐**
```powershell
# Step 1: Ensure Ollama is running
ollama serve  # In separate terminal

# Step 2: Install Sentinel Agent (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1

# Step 3: Activate environment
.\venv\Scripts\Activate.ps1

# Step 4: Run in two terminals
# Terminal 1: Start monitoring (runs indefinitely)
python main.py

# Terminal 2: Start REST API (in another PowerShell)
.\venv\Scripts\Activate.ps1
python sentinel_api.py
# Should see: Uvicorn running on http://0.0.0.0:8000
```

**Command Prompt (Alternative)**
```cmd
install.bat
venv\Scripts\activate.bat
python main.py
```

**Linux/macOS Users**

**Step 1: Install (one-time)**
```bash
chmod +x install.sh
./install.sh
# This creates venv, installs dependencies, and creates databases
```

**Step 2: Ensure Ollama is running**
```bash
ollama serve  # Terminal 1
```

**Step 3: Activate and Run**
```bash
# Terminal 2: Start monitoring
source venv/bin/activate
python main.py
# Expected output:
# [INFO:__main__:] SENTINEL AGENT v2.0 INITIALIZATION
# [INFO:__main__:]   Auth log monitoring: ACTIVE
# [INFO:__main__:]   Web log monitoring: ACTIVE

# Terminal 3: Start REST API (open new terminal)
source venv/bin/activate
python sentinel_api.py
# Expected output:
# INFO:     Started server process [PID]
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Any Platform (Python)**
```bash
# Install dependencies and set up
python install.py

# Then run as shown above for your OS
```

### Traditional: Verify It's Working

```bash
# Test the API (Terminal 3 or new terminal)
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"2.2"}

# View API documentation
# Open browser: http://localhost:8000/docs
```

### Traditional: Stop the Agent

```bash
# In Terminal 1 and 2, press:
Ctrl+C

# Logs will show shutdown message:
# INFO:__main__:Shutting down monitors...
# INFO:__main__:Sentinel Agent stopped
```

**⏱️ Installation Time:** 3-6 minutes | **Includes:** venv + all dependencies + databases



---

## What's New in v2.2

**6 Enterprise Features Added:**
- [YES] **Offline Threat Intelligence** - Local IP reputation database
- [YES] **Dashboard Authentication** - Secure token-based access
- [YES] **Whitelist/Blacklist Management** - Flexible IP filtering
- [YES] **Performance Metrics** - Detection & response time tracking
- [YES] **REST API** - 20+ endpoints for external integration
- [YES] **ML Anomaly Scoring** - Multi-factor threat detection

[ Full Documentation](docs_markdown/README_FEATURES.md)

---

##  Core Features

### Security Detection & Response
- **Real-time Log Monitoring**: Watches auth.log and web logs
- **Multi-Agent AI Analysis**: 4 specialized security agents
- **Intelligent Detection**: Pattern-based + ML-based anomaly scoring
- **Human-in-the-Loop**: Approval required before blocking actions
- **Professional Logging**: SQLite persistence + rotating logs

### Advanced Capabilities
- **Offline Threat Intelligence**: Local IP reputation database
- **IP Management**: Whitelist safe IPs, blacklist malicious ones
- **Performance Metrics**: Track detection time & response accuracy
- **REST API**: 20+ endpoints for system integration
- **Adaptive Dashboard**: Auto-selects GUI/CLI/logging based on environment

---

##  Quick Start (5 Minutes)

### Prerequisites
```bash
python --version          # Should be 3.10+
ollama --version          # Should be installed
ollama pull llama3:8b     # Pull LLM model
```

### Installation & Start
```bash
# 1. Activate environment
source activate_env.sh    # Linux/Mac
activate_env.bat          # Windows

# 2. Start main system (Terminal 1)
python main.py
# Output: "Log monitoring started..."

# 3. Start REST API (Terminal 2)
python sentinel_api.py
# Output: "Uvicorn running on http://0.0.0.0:8000"

# 4. Verify (Terminal 3)
curl http://localhost:8000/api/health
# Response: {"status":"healthy","version":"2.2"}
```

---

##  Authentication & Security

### ⚡ NEW: Enterprise-Grade Encryption

**v2.2 now includes bcrypt password hashing and Fernet encryption!**

**First-time users:** System generates a **secure random password** on startup.

```bash
# Find your password in logs:
docker-compose logs sentinel-agent | grep "DEFAULT ADMIN"

# Or check the credentials file:
cat data/INITIAL_CREDENTIALS.txt
```

 **Change password immediately:**
```bash
python password_manager.py
# Select: 1. Change Password
```

 **Full Security Guide:** [SECURITY_UPGRADE.md](SECURITY_UPGRADE.md)

---

### Get API Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=YOUR_PASSWORD_HERE"
# Returns: {"token":"eyJhbGc...","expires_in":86400}
```

### Use in API Calls
```bash
TOKEN="your_token_here"
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/metrics/dashboard
```

---

##  API Endpoints (20+)

### Core Endpoints
```bash
# Health & Info
GET  /api/health                          # System health check
GET  /api/info                            # System information

# Authentication
POST /api/auth/login                      # Get session token
POST /api/auth/api-key                    # Create API key

# Threat Intelligence
POST /api/threats/check-ip                # Check IP reputation
POST /api/threats/add-malicious           # Add malicious IP
GET  /api/threats/patterns                # Get threat patterns

# IP Management
POST /api/lists/whitelist-ip              # Whitelist IP
POST /api/lists/blacklist-ip              # Blacklist IP
GET  /api/lists/summary                   # View all lists
GET  /api/lists/whitelisted-ips           # Get whitelist
GET  /api/lists/blacklisted-ips           # Get blacklist
DELETE /api/lists/remove-ip               # Remove from list

# Metrics & Analytics
GET  /api/metrics/detection               # Detection statistics
GET  /api/metrics/response                # Response statistics
GET  /api/metrics/health                  # System health
GET  /api/metrics/dashboard               # All dashboard metrics

# Anomaly Detection
POST /api/anomaly/score                   # Calculate anomaly score
GET  /api/anomaly/ip-profile              # Get IP behavior profile

# Incident Management
GET  /api/incidents/recent                # Recent incidents
GET  /api/incidents/{id}                  # Get specific incident
GET  /api/incidents/by-ip/{ip}            # Incidents from IP
```

---

## ️ Project Structure

```
Sentinel/Project/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── main.py                        # Core system entry point
├── sentinel_api.py               # REST API server
│
├── Feature Modules (NEW - v2.2)
├── threat_intelligence.py        # Offline threat database
├── auth.py                       # Authentication & tokens
├── list_manager.py               # Whitelist/blacklist
├── metrics.py                    # Performance tracking
├── anomaly_scorer.py             # ML anomaly detection
│
├── Core Modules
├── agents.py                     # AI crew definition
├── tasks.py                      # Security playbooks
├── data_engine.py                # SQLite persistence
├── output_formatter.py           # Formatted output
│
├── Sensors
├── sensors/
│   ├── auth_sensor.py           # Auth log monitoring
│   └── web_sensor.py            # Web log monitoring
│
├── Security & Defense
├── defense/
│   ├── attack_detector.py       # Attack pattern detection
│   ├── attack_logger.py         # Incident logging
│   └── __init__.py
│
├── Tools & Utilities
├── tools/
│   └── tools.py                 # OSINT & firewall tools
│
├── Dashboards
├── dashboard/
│   ├── web_dashboard.py         # Streamlit web UI
│   ├── cli_dashboard.py         # Rich terminal UI
│   └── app.py                   # Dashboard controller
│
├── Documentation (in docs_markdown/)
├── docs_markdown/
│   ├── FEATURE_INTEGRATION.md          # Feature integration guide
│   ├── DEPLOYMENT_GUIDE.md             # Practical usage guide
│   ├── README_FEATURES.md              # Feature quick reference
│   ├── DOCKER_DEPLOYMENT.md            # Docker setup guide
│   ├── SECURITY_IMPLEMENTATION.md      # Security documentation
│   ├── CHANGELOG.md                    # Version history
│   └── QUICK_REFERENCE.md              # Command reference
│
└── Configuration & Scripts
    ├── activate_env.sh / .bat
    ├── setup.sh / .bat / .ps1
    ├── docker-compose.yml
    └── Dockerfile
```

---

##  Documentation

All essential documentation is in [`docs_markdown/`](docs_markdown/) folder:

### ⚡ Automation (Recommended - Save 90% of setup time!)
- [**AUTOMATION_GUIDE.md**](AUTOMATION_GUIDE.md) - ⭐ **Automated setup & testing (Python or Bash)**

### For End Users
- [**USER_GUIDE.md**](docs_markdown/USER_GUIDE.md) - Features, access, and tasks
- [**README_FEATURES.md**](docs_markdown/README_FEATURES.md) - Feature overview
- [**QUICK_REFERENCE.md**](docs_markdown/QUICK_REFERENCE.md) - Command reference

### For Testing & Validation
- [**ATTACK_TESTING_GUIDE.md**](docs_markdown/ATTACK_TESTING_GUIDE.md) - Test attacks (DDoS, SQL injection, brute force, etc.)
- [**DEPLOYMENT_GUIDE.md**](docs_markdown/DEPLOYMENT_GUIDE.md) - Usage and deployment guide

### For System Setup
- [**DOCKER_DEPLOYMENT.md**](docs_markdown/DOCKER_DEPLOYMENT.md) - Docker setup guide
- [**DOCKER_QUICKSTART.md**](docs_markdown/DOCKER_QUICKSTART.md) - Docker quick start
- [**DOCKER_TROUBLESHOOTING.md**](docs_markdown/DOCKER_TROUBLESHOOTING.md) - Docker troubleshooting

### For Technical Reference
- [**FEATURE_INTEGRATION.md**](docs_markdown/FEATURE_INTEGRATION.md) - Feature integration guide
- [**ENVIRONMENT.md**](docs_markdown/ENVIRONMENT.md) - Environment variables
- [**SECURITY_IMPLEMENTATION.md**](docs_markdown/SECURITY_IMPLEMENTATION.md) - Security setup

### Additional Resources
- [**CHANGELOG.md**](docs_markdown/CHANGELOG.md) - Version history
- [**CONTRIBUTING.md**](docs_markdown/CONTRIBUTING.md) - Contribution guidelines
- [**ADAPTIVE_REPORTING.md**](docs_markdown/ADAPTIVE_REPORTING.md) - Reporting features

---

## ⚙️ Configuration

### Environment Variables
```bash
# Logging
export SENTINEL_LOG_DIR=/app/logs
export LOG_LEVEL=INFO

# Database
export DATA_DIR=/app/data

# API
export API_PORT=8000
export API_HOST=0.0.0.0

# Authentication
export DASHBOARD_USER=admin
export DASHBOARD_PASS=sentinel123
```

### Key Settings
- **Session Duration**: 24 hours (configurable in auth.py)
- **Anomaly Threshold**: 0.6 (normal) → 0.85 (critical)
- **Log Rotation**: 10MB per file, 5 backup files
- **API Rate Limit**: No limit (add reverse proxy for production)

---

##  Testing

### Quick Verification
```bash
# 1. Check system health
curl http://localhost:8000/api/health

# 2. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=sentinel123" | jq -r '.token')

# 3. Query metrics
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/metrics/dashboard

# 4. Check threat intelligence
curl -X POST http://localhost:8000/api/threats/check-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.0.2.1"}'
```

### Python Testing
```python
# Test threat intelligence
from threat_intelligence import get_threat_intelligence
ti = get_threat_intelligence()
result = ti.check_ip_reputation("192.0.2.1")

# Test whitelist
from list_manager import get_list_manager
mgr = get_list_manager()
mgr.whitelist_ip("192.168.1.100", "Internal server", "admin")

# Test anomaly scoring
from anomaly_scorer import get_anomaly_scorer
scorer = get_anomaly_scorer()
result = scorer.calculate_anomaly_score({
    "ip": "192.0.2.1",
    "attack_type": "ssh_brute_force",
    "severity": "high"
})
```

---

##  Docker Deployment

### Quick Start (Recommended)
```bash
# 1. Ensure Ollama is running on host
ollama serve  # Terminal 1

# 2. Build and deploy (Terminal 2)
docker-compose build --no-cache
docker-compose up -d

# 3. Verify deployment
docker-compose ps  # Should show: Up (healthy)
curl http://localhost:8000/api/health

# 4. View logs
docker-compose logs -f sentinel-agent

# 5. Stop services
docker-compose down
```

### Advanced Docker Operations
```bash
# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d --force-recreate

# View real-time logs
docker-compose logs -f sentinel-agent

# Execute commands inside container
docker-compose exec sentinel-agent bash

# Check container health
docker-compose ps
docker inspect sentinel-agent | grep -i health

# Full cleanup (WARNING: Deletes data!)
docker-compose down -v  # -v removes volumes
```

### Docker Services Architecture (v2.2.1)
- **Network Mode**: host (direct access to localhost:11434 for Ollama)
- **Services**: main.py (monitoring) + sentinel_api.py (REST API)
- **Startup**: Both services launch via docker-startup.sh
- **Ports**: 8000 (API), 8501 (optional dashboard), 11434 (Ollama)
- **Volumes**: ollama_data (persistent model storage)

### Production Deployment
See [DOCKER_DEPLOYMENT.md](docs_markdown/DOCKER_DEPLOYMENT.md) for:
- SSL/TLS configuration
- Health checks and monitoring
- Resource limits and scaling
- Persistent storage and backups
- Docker Compose profiles (with-ollama)

---

##  Security Considerations

### Initial Setup
- [ ] Change default admin password
- [ ] Set up HTTPS/TLS certificate
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable audit logging

### Best Practices
- Use strong passwords (20+ characters)
- Rotate API keys monthly
- Monitor access logs for suspicious patterns
- Keep threat database updated
- Review whitelist/blacklist rules regularly

### Production Hardening
- Run behind reverse proxy (nginx/Apache)
- Implement rate limiting
- Set up WAF rules
- Enable CORS restriction
- Use environment variables for secrets

---

##  Performance

### Benchmarks
- **Detection Overhead**: ~10-15ms per event (<2% of analysis time)
- **API Throughput**: 100+ requests/second
- **Storage**: <10 MB initially, scales to <100 MB at 10K+ incidents
- **Memory**: ~200-300 MB steady state

### Optimization Tips
1. Enable threat intelligence caching
2. Use whitelist to reduce false positives
3. Archive old metrics regularly
4. Configure log rotation
5. Use separate database server for scale

---

##  Troubleshooting

### Docker Issues (v2.2.1 Fixes Applied)

**1. Docker Compose Validation Errors** ✅ FIXED

**Error:** `'network_mode' and 'networks' cannot be combined`
```bash
# Fixed in v2.2.1: Removed 'networks' section (incompatible with network_mode:host)
# Verify fix:
docker-compose config --quiet  # Should have no errors
```

**Error:** `"host" network_mode is incompatible with port_bindings`
```bash
# Fixed in v2.2.1: Removed 'ports' section (not needed with host mode)
# Ports are directly accessible: http://localhost:8000
```

**Error:** `Unsupported config option for services.sentinel-agent: 'driver'`
```bash
# Fixed in v2.2.1: Restored proper YAML volumes section structure
# volumes: should be at root level, not under services
```

**2. Container Unhealthy / API Not Responding** ✅ FIXED

**Symptoms:** Container shows "Up (unhealthy)", `curl http://localhost:8000/api/health` fails

```bash
# Fixed in v2.2.1: Created docker-startup.sh to run both services
# - main.py (monitoring) runs in background
# - sentinel_api.py (API) runs in foreground

# Verify both services are running:
docker-compose logs sentinel-agent | grep "Starting"
# Should show:
# [1/2] Starting Sentinel Agent monitor (main.py)...
# [2/2] Starting REST API server (sentinel_api.py on port 8000)...

# If still unhealthy, rebuild:
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**3. Ollama Connection Issues**

```bash
# Check if host Ollama is running:
curl http://localhost:11434/api/tags

# If not running, start Ollama:
ollama serve  # In separate terminal

# Verify container can reach it:
docker-compose logs sentinel-agent | grep -i ollama
# Should show: "Ollama connectivity check passed"
```

**4. General Docker Troubleshooting**

```bash
# View detailed logs
docker-compose logs sentinel-agent

# Check port conflicts
docker-compose ps
netstat -an | grep 8000

# Full reset (WARNING: Deletes data!)
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check container health status
docker inspect sentinel-agent | grep -i health
```

 **Comprehensive Guide:** [DOCKER_TROUBLESHOOTING.md](docs_markdown/DOCKER_TROUBLESHOOTING.md)

---

### Traditional Installation Issues

**API won't start**
```bash
# Check if port is in use
netstat -an | grep 8000

# Kill existing process
pkill -f "python sentinel_api.py"

# Try different port
python sentinel_api.py --port 8001
```

**"Module not found" error**
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt

# Check working directory
pwd  # Should be project root
```

### Database locked
```bash
# Check who's accessing
lsof *.db

# Restart system
pkill -f "python main.py"
pkill -f "python sentinel_api.py"
```

### Whitelist not working
```bash
# Verify IP format (X.X.X.X)
sqlite3 lists.db "SELECT * FROM ip_whitelist;"

# Check for spaces/duplicates
sqlite3 lists.db ".mode column" "SELECT ip, reason FROM ip_whitelist;"
```

See [DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md#troubleshooting) for more help.

---

##  Monitoring & Maintenance

### Check System Status
```bash
# View recent incidents
sqlite3 sentinel_intel.db "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 10;"

# Check metrics
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/metrics/health

# Monitor logs
tail -f logs/sentinel.log
```

### Regular Maintenance
- **Daily**: Review recent incidents
- **Weekly**: Check whitelist/blacklist
- **Monthly**: Rotate API keys, update threat database
- **Quarterly**: Performance review, security audit

---

##  Contributing

We welcome contributions! See [CONTRIBUTING.md](docs_markdown/CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Feature request procedure

---

##  Support

### Documentation
- Full API docs in [FEATURE_INTEGRATION.md](docs_markdown/FEATURE_INTEGRATION.md)
- Deployment guide in [DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md)
- Code examples in source docstrings

### Quick Links
- [Features Overview](docs_markdown/README_FEATURES.md)
- [API Reference](docs_markdown/FEATURE_INTEGRATION.md#rest-api-endpoints)
- [Troubleshooting](docs_markdown/DEPLOYMENT_GUIDE.md#troubleshooting)
- [FAQ](docs_markdown/QUICK_REFERENCE.md)

---

##  License

[Add your license information here]

---

##  Acknowledgments

- CrewAI for multi-agent orchestration
- Ollama for local LLM inference
- FastAPI for REST API framework
- Streamlit for dashboard UI

---

##  Version History

**v2.2** (Current)
- ✅ Added offline threat intelligence
- ✅ Added dashboard authentication
- ✅ Added whitelist/blacklist management
- ✅ Added performance metrics
- ✅ Added REST API
- ✅ Added ML anomaly scoring
- ✅ Reorganized documentation

**v2.1**
- Added adaptive reporting system
- Added multiple dashboard modes

**v2.0**
- Complete rewrite with CrewAI
- Multi-agent architecture

**v1.0**
- Initial release

---

##  Next Steps

1. **Review** the documentation in [docs_markdown/](docs_markdown/)
2. **Configure** your environment (see Configuration section)
3. **Deploy** using Docker or manual setup
4. **Test** with the quick start examples
5. **Monitor** using the REST API or dashboards
6. **Customize** threat database and whitelist rules

---

**Ready to deploy? Start with:**
```bash
python main.py                    # Terminal 1
python sentinel_api.py            # Terminal 2
curl http://localhost:8000/api/health  # Terminal 3
```

For detailed instructions, see [DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md).

---

**Questions?** Check [docs_markdown/](docs_markdown/) folder for comprehensive documentation.

**Found an issue?** Please report it with steps to reproduce.

**Have a suggestion?** We'd love to hear about it!

---

Sentinel Agent v2.2 - **Production Ready** ✨
