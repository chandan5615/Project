# 🛡️ Sentinel Agent v2.2

**AI-Powered Security Monitoring System for Linux**

Real-time threat detection and automated response using AI crew analysis. Deploy on any Ubuntu server with **ONE command** in 15 minutes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![GitHub](https://img.shields.io/badge/GitHub-chandan5615%2FProject-blue?logo=github)](https://github.com/chandan5615/Project)

---

## ⚡ Quick Start (One Command Installation)

### Fresh Ubuntu Server

```bash
# Download and run automated installer
wget -O- https://raw.githubusercontent.com/chandan5615/Project/main/AUTO_INSTALL.sh | sudo bash

# OR if you have the files:
chmod +x AUTO_INSTALL.sh
sudo ./AUTO_INSTALL.sh
```

**That's it!** Installer automatically handles:
- ✅ Docker & Docker Compose installation
- ✅ Ollama LLM setup with llama3:8b model  
- ✅ System dependencies
- ✅ Container build and deployment
- ✅ Database initialization
- ✅ Firewall configuration

**Time:** 10-15 minutes (hands-off)

**Access:**
- 📊 Dashboard: `http://YOUR_SERVER_IP:8501`
- 🔌 API: `http://YOUR_SERVER_IP:8000`
- 👤 Login: `sentinel` / `sentinel`

---

## � What Does It Do?

Sentinel Agent monitors your Linux server for security threats in real-time:

### **Detects:**
- 🔓 SSH brute force attacks
- 💉 SQL injection attempts
- 📂 Path traversal attacks
- ⚡ Cross-site scripting (XSS)
- 🚫 Directory scanning
- 🌐 Suspicious web requests
- 🤖 Attack tool signatures (sqlmap, nikto, etc.)

### **Analyzes:**
- 🤖 **AI Crew Analysis** for HIGH severity threats
- 📊 **Automated Logging** for MEDIUM/LOW threats
- 🧠 Multi-agent investigation (4 specialized AI agents)
- 🔍 Threat intelligence correlation
- 📈 Behavioral anomaly detection

### **Responds:**
- 🛡️ Automatic IP blocking (iptables)
- 📝 Detailed incident reporting
- 💾 Forensic data collection
- 🔔 Real-time alerts
- 📊 Security dashboard with metrics

---

## 🚀 Features

### **✨ NEW: Optimized Performance**
- **Smart AI Usage:** AI analysis only for HIGH severity attacks
- **90% Resource Savings:** MEDIUM/LOW attacks logged without AI overhead
- **Fast Response:** Sub-second detection and logging
- **Scalable:** Handles 1000+ attacks/hour efficiently

### **Core Capabilities:**
- **Real-time Monitoring:** Auth logs, web logs, file system changes
- **AI-Powered Analysis:** 4-agent CrewAI crew with local Ollama LLM
- **Automated Response:** Configurable blocking and remediation
- **Interactive Dashboard:** Real-time metrics, logs, and IP management
- **REST API:** Full programmatic access to all features
- **Zero External Dependencies:** Runs completely offline with local LLM

### **Security:**
- HTTP Basic Authentication
- Encrypted secret storage
- Role-based access control
- Audit logging for all actions
- Secure password management

---

## 📋 System Requirements

### **Minimum:**
- Ubuntu 20.04+ (or Debian-based Linux)
- 4 CPU cores
- 8GB RAM
- 20GB disk space
- Docker 20.10+
- Internet (for initial setup only)

### **Recommended:**
- Ubuntu 22.04 LTS
- 8 CPU cores
- 16GB RAM
- 50GB SSD
- Docker 24.0+

### **Software Dependencies:**
Auto-installed by `AUTO_INSTALL.sh`:
- Docker & Docker Compose
- Ollama (local LLM server)
- Python 3.10+
- Apache2 (monitoring target)
- System utilities (iptables, curl, etc.)

---

## 📚 Documentation

### **🚀 Getting Started:**
- 📖 **[README.md](README.md)** - Main documentation (you are here)
- 🎯 **[START_HERE.md](START_HERE.md)** - Quick start guide
- 🤖 **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** - What's automated

### **🔧 Troubleshooting (NEW!):**
- 🆘 **[QUICK_TROUBLESHOOTING.md](QUICK_TROUBLESHOOTING.md)** - **Print this!** Quick reference card for common issues
- 📋 **[TROUBLESHOOTING_COMPLETE.md](TROUBLESHOOTING_COMPLETE.md)** - Complete troubleshooting guide (all known issues)
- 🔴 **[configure_ollama_network.sh](configure_ollama_network.sh)** - Fix Ollama connection errors (most common issue)

### **📊 Dashboard & Features:**
- 🎨 **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete dashboard tutorial
- 📝 **[DASHBOARD_UPDATE_SUMMARY.md](DASHBOARD_UPDATE_SUMMARY.md)** - Dashboard features overview
- ⚙️ **[FEATURE_INTEGRATION.md](docs_markdown/FEATURE_INTEGRATION.md)** - Feature details

### **🧪 Testing & Deployment:**
- 📝 **[ATTACK_TESTING_GUIDE.txt](ATTACK_TESTING_GUIDE.txt)** - How to test the system
- 🐳 **[DOCKER_DEPLOYMENT.md](docs_markdown/DOCKER_DEPLOYMENT.md)** - Docker deployment details
- 🚀 **[DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md)** - Production deployment

### **📖 Additional Resources:**
- 💡 **[QUICK_REFERENCE.md](docs_markdown/QUICK_REFERENCE.md)** - Command cheat sheet
- 🔐 **[SECURITY_IMPLEMENTATION.md](docs_markdown/SECURITY_IMPLEMENTATION.md)** - Security details
- 👥 **[USER_GUIDE.md](docs_markdown/USER_GUIDE.md)** - User manual

### **Key Commands:**

```bash
# View logs
docker-compose logs -f sentinel-agent

# Check status
docker-compose ps

# Restart system
docker-compose restart

# Stop system
docker-compose down

# Rebuild after updates
docker-compose down && docker-compose up -d --build

# Generate test attacks
python3 test_web_attacks.py
python3 continuous_attacks.py --interval 10 --duration 5
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Sentinel Agent v2.2                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  Auth Sensor │      │  Web Sensor  │                   │
│  │ /var/log/    │      │ /var/log/    │                   │
│  │  auth.log    │      │ apache2/...  │                   │
│  └──────┬───────┘      └──────┬───────┘                   │
│         │                     │                            │
│         └──────────┬──────────┘                            │
│                    ▼                                        │
│           ┌─────────────────┐                              │
│           │ Attack Detector │                              │
│           │  & Classifier   │                              │
│           └────────┬────────┘                              │
│                    │                                        │
│         ┌──────────┴──────────┐                           │
│         ▼                     ▼                            │
│  ┌─────────────┐      ┌──────────────┐                   │
│  │   MEDIUM/   │      │ HIGH SEVERITY│                   │
│  │ LOW Attacks │      │   Attacks    │                   │
│  │             │      │              │                   │
│  │ Auto-log &  │      │   AI Crew    │                   │
│  │   Block     │      │   Analysis   │                   │
│  └─────────────┘      └──────┬───────┘                   │
│                              │                            │
│                    ┌─────────┴─────────┐                 │
│                    ▼                   ▼                  │
│         ┌──────────────────┐  ┌──────────────┐          │
│         │ Threat Intel DB  │  │ Remediation  │          │
│         │ & Correlation    │  │   Actions    │          │
│         └──────────────────┘  └──────────────┘          │
│                                                           │
│  ┌───────────────────────────────────────────────┐      │
│  │          Dashboard & API (Port 8501/8000)     │      │
│  └───────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘

        Powered by: CrewAI + Ollama (llama3:8b)
```

### **AI Crew Agents:**
1. **Triage Analyst** - Log analysis and severity assessment
2. **Threat Intel Researcher** - IP reputation and correlation
3. **Incident Responder** - Action planning and remediation
4. **Enforcer Agent** - Automated response execution

---

### ⚙️ Technical Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **AI Framework** | CrewAI | 0.100.1 | Multi-agent orchestration |
| **LLM** | Ollama + Llama 3 | 8b | Local language model (offline) |
| **API Server** | FastAPI | 0.115.8 | REST endpoints |
| **Database** | SQLite | 3.x | Persistent data storage |
| **File Monitoring** | Watchdog | 4.0+ | Log file detection |
| **Dashboard** | Streamlit | 1.28+ | Web UI |
| **Container** | Docker | 20.10+ | Deployment and isolation |
| **Python** | Python | 3.10 | Runtime environment |

---

## 🎨 Dashboard Guide

### **Two Dashboard Options Available:**

Sentinel Agent provides both a web-based dashboard and a powerful CLI dashboard for different use cases.

---

## 🌐 **WEB DASHBOARD** (Streamlit UI)

**Best for:** Visual monitoring, executives, non-technical users, GUI preference

### **Quick Start:**

#### **Option 1: Via Docker (Recommended)**
```bash
# Already running in container with main system
# Access at: http://YOUR_SERVER_IP:8501
# Login: sentinel / sentinel

# If you need to start the web dashboard manually inside the container
docker exec -it sentinel-agent streamlit run dashboard/web_dashboard.py \
  --server.address 0.0.0.0 --server.port 8501

# View logs (if needed)
docker-compose logs -f sentinel-agent | head -50
```

#### **Option 2: Standalone on Your PC/Laptop**
```bash
# Clone/download the project
git clone https://github.com/chandan5615/Project.git
cd Project

# Install dependencies
pip install streamlit pandas plotly rich requests

# Copy database from server (or use local)
# scp ubuntu@YOUR_SERVER_IP:~/Project/data/sentinel_intel.db ./data/

# Run dashboard locally
SENTINEL_DB_PATH=./data/sentinel_intel.db streamlit run dashboard/web_dashboard.py

# Opens automatically at: http://localhost:8501
```

### **Web Dashboard Features:**

- 📊 **Real-time Security Metrics** - Score, threat count, attack feed
- 📈 **System Monitoring** - CPU, memory, disk usage, network stats
- 📝 **Live Log Viewer** - Searchable, filterable incident logs
- 🚫 **IP Management** - Block/unblock IPs, manage blacklists/whitelists
- 📉 **Analytics Charts** - Attack timeline, severity distribution, top attackers
- 🔐 **Authentication** - Basic auth login screen
- 🎨 **Dark Theme** - Easy on the eyes with professional look

### **Web Dashboard Keyboard Shortcuts:**
- `R` - Refresh data
- `I` - IP management panel
- `L` - Log viewer
- `M` - Metrics view

---

## 💻 **CLI DASHBOARD** (Rich Terminal UI)

**Best for:** Headless servers, SSH sessions, terminal lovers, minimal bandwidth

### **Quick Start:**

#### **Option 1: From Server**
```bash
# SSH into your server
ssh ubuntu@YOUR_SERVER_IP

# Navigate to project
cd ~/Project

# Run CLI dashboard  
python3 dashboard/cli_dashboard.py

# Auto-refreshes every 5 seconds with:
# ✓ Real-time incident table
# ✓ Top attackers with counts
# ✓ Attack types breakdown
# ✓ System resource usage
# ✓ Security state indicator
# ✓ Color-coded indicators (Red/Yellow/Green)
```

#### **Option 2: Inside Container**
```bash
# Docker exec into container
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Same features, runs inside container context
```

#### **Option 3: From Your PC (Remote)**
```bash
# SSH tunnel to server
ssh -L 9000:localhost:9000 ubuntu@YOUR_SERVER_IP

# Then run (in another terminal)
ssh ubuntu@YOUR_SERVER_IP "cd ~/Project && python3 dashboard/cli_dashboard.py"

# Output streams to your terminal in real-time
```

### **CLI Dashboard Features:**

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    SENTINEL AGENT - CLI DASHBOARD                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  🔴 SECURITY STATE: CRITICAL (3 incidents in last hour)                  ║
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐ ║
║  │ RECENT INCIDENTS (Last 24 Hours)                                    │ ║
║  ├──────┬────────────────┬───────┬────────┬─────────────────────────┤ ║
║  │ Time │ IP Address     │ Type  │ Status │ Details                 │ ║
║  ├──────┼────────────────┼───────┼────────┼─────────────────────────┤ ║
║  │ 14:23│ 192.168.1.100  │ SSH   │ Blocked│ Brute force - 5 attempts│ ║
║  │ 14:15│ 10.0.0.50      │ SQL   │ Blocked│ SQL injection detected   │ ║
║  │ 14:02│ 203.0.113.45   │ XSS   │ Blocked│ Possible XSS payload     │ ║
║  └──────┴────────────────┴───────┴────────┴─────────────────────────┘ ║
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐ ║
║  │ TOP ATTACKERS                                                       │ ║
║  ├──────────────────┬───────┬──────────────────────────────────────┤ ║
║  │ IP Address       │ Count │ Latest Attack                        │ ║
║  ├──────────────────┼───────┼──────────────────────────────────────┤ ║
║  │ 192.168.1.100    │  12   │ SSH brute force (14:23)             │ ║
║  │ 203.0.113.45     │   8   │ XSS attempt (14:02)                │ ║
║  │ 10.0.0.50        │   5   │ SQL injection (14:15)               │ ║
║  └──────────────────┴───────┴──────────────────────────────────────┘ ║
║                                                                           ║
║  ATTACK TYPES:  SSH: 12  │  SQL: 5  │  XSS: 8  │  PATH: 3  │  API: 2   ║
║  STATUS:        📊 Auto-refresh every 5 seconds                         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

**CLI Dashboard Updates Automatically:**
- ✅ Real-time incident feed
- ✅ Top attackers ranking
- ✅ Attack type statistics
- ✅ Security state (🟢 Green / 🟡 Yellow / 🔴 Red)
- ✅ System resource usage (CPU, Memory, Disk)
- ✅ Color-coded severity levels
- ✅ Refreshes every 5 seconds

---

## 🚀 **Running Both Dashboards Simultaneously**

```bash
# Terminal 1: Web Dashboard (for visual monitoring)
ssh ubuntu@YOUR_SERVER_IP "cd ~/Project && \
  docker exec -d sentinel-agent streamlit run dashboard/web_dashboard.py \
  --server.address 0.0.0.0 --server.port 8501"

# Terminal 2: CLI Dashboard (for live terminal updates)
ssh ubuntu@YOUR_SERVER_IP "cd ~/Project && \
  docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py"

# Terminal 3: Monitor Raw Logs
docker-compose logs -f sentinel-agent | grep -E "(HIGH|ALERT|Incident)"

# Now you can:
# - Watch web dashboard at http://YOUR_SERVER_IP:8501
# - Monitor CLI dashboard in Terminal 2 (live updates every 5s)
# - Track raw logs in Terminal 3
```

---

## 🔧 **Dashboard Configuration**

### **Environment Variables for Dashboards:**

```bash
# Create .env file or add to docker-compose.yml
# Web Dashboard Settings
DASHBOARD_PORT=8501
DASHBOARD_USER=sentinel
DASHBOARD_PASS=sentinel
DASHBOARD_THEME=dark  # or 'light'
DASHBOARD_PUBLIC_HOST=YOUR_SERVER_IP  # optional, shows public URL in dashboard

# CLI Dashboard Settings
CLI_REFRESH_INTERVAL=5  # seconds
CLI_MAX_INCIDENTS=20    # rows to display
CLI_SHOW_STATS=true     # show summary stats

# Database
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data
```

### **Accessing External Network Dashboards:**

```bash
# From another PC on local network
# Web Dashboard:
http://YOUR_SERVER_IP:8501

# API Health Check:
http://YOUR_SERVER_IP:8000/api/health

# Via SSH Tunnel (from anywhere):
ssh -L 8501:localhost:8501 ubuntu@YOUR_SERVER_IP
# Then: http://localhost:8501
```

---

## 📊 Dashboard Comparison

| Feature | Web Dashboard | CLI Dashboard |
|---------|:----------:|:----------:|
| **GUI Interface** | ✅ Yes (Streamlit) | ✅ Yes (Rich TUI) |
| **Real-time Updates** | ✅ 8s refresh | ✅ 5s refresh |
| **IP Management** | ✅ Block/Unblock | ❌ View only |
| **Charts & Graphs** | ✅ Interactive | ❌ Table-based |
| **Mobile Friendly** | ✅ Yes | ❌ No |
| **SSH Terminal** | ❌ Requires browser | ✅ Full support |
| **Bandwidth** | 📊 Moderate | 📉 Minimal |
| **Login Required** | ✅ Yes (auth) | ❌ Direct access |
| **Dark Theme** | ✅ Available | ✅ Default |
| **Export Logs** | ✅ CSV/JSON | ✅ Copy/Export |
| **Performance** | 🟡 Medium | 🟢 Light |
| **Customizable** | ✅ Yes | ✅ Yes |

---

## 🎨 Dashboard Features

## 🧪 Testing

### **Generate Test Attacks:**

```bash
# Quick burst (50+ attacks in 1 minute)
python3 test_web_attacks.py

# Continuous stream
python3 continuous_attacks.py --interval 5 --duration 2 --burst 3
```

### **Monitor Results:**

```bash
# Watch AI analysis (only HIGH severity)
docker-compose logs -f | grep -E "(HIGH|AI|crew)"

# View all detections
docker-compose logs -f | grep -E "(SQL|XSS|attack)"

# Check dashboards
# Web: http://YOUR_SERVER_IP:8501
# CLI: docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py
```

---

## ⚡ Quick Reference Commands

### **Dashboard Access:**

```bash
# Web Dashboard
http://YOUR_SERVER_IP:8501                    # Browser access
docker-compose logs -f                       # View logs

# CLI Dashboard  
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Both Dashboards (3 terminals)
# Terminal 1: Web dashboard (automatic, already running)
# Terminal 2: CLI - docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py
# Terminal 3: Logs - docker-compose logs -f | grep ALERT
```

### **System Control:**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart sentinel-agent

# Status
docker-compose ps

# Rebuild
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### **Testing & Monitoring:**

```bash
# Generate attacks
python3 test_web_attacks.py

# Monitor detections
docker-compose logs -f | grep -i incident

# Check API
curl http://192.168.31.91:8000/api/health

# Query incidents
sqlite3 data/sentinel_intel.db "SELECT COUNT(*) FROM incidents;"
```

### **Troubleshooting:**

```bash
# CRITICAL: Fix Ollama connection refused error
# (Most common issue - see TROUBLESHOOTING_COMPLETE.md)
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama

# Verify Ollama is accessible
ss -tlnp | grep 11434  # Should show *:11434 not 127.0.0.1:11434

# Check Docker container status
docker-compose ps
docker-compose logs --tail=50 sentinel-agent

# Test Ollama connection from container
docker exec sentinel-agent curl http://host.docker.internal:11434/api/tags

# Full health check
curl http://localhost:8000/api/health
curl http://localhost:11434/api/tags

# View errors only
docker-compose logs sentinel-agent | grep -E "(ERROR|CRITICAL|WARNING)"

# Fix line endings (Windows development)
find ~/Project -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Clean rebuild (if all else fails)
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d

# See TROUBLESHOOTING_COMPLETE.md for detailed guide
```

---

## 🔧 Configuration

### **Environment Variables:**

Create `.env` file or set in `docker-compose.yml`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3:8b

# Log Paths
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# Security
SENTINEL_ADMIN_USER=sentinel
SENTINEL_ADMIN_PASS=sentinel  # CHANGE THIS!

# Data Directories
DATA_DIR=/app/data
LOG_DIR=/app/logs
```

### **Customize AI Behavior:**

Edit [main.py](main.py):
```python
# Line ~230: Change AI trigger threshold
use_ai_analysis = (severity == "HIGH")  # or "MEDIUM", "CRITICAL", etc.
```

---

## 📊 API Reference

### **Health Check:**
```bash
curl http://localhost:8000/api/health
```

### **Get Attacks:**
```bash
curl http://localhost:8000/api/attacks
```

### **Get Logs:**
```bash
curl http://localhost:8000/api/logs?limit=50&severity=high
```

### **Block IP:**
```bash
curl -X POST http://localhost:8000/api/ip/block \
  -u sentinel:sentinel \
  -H "Content-Type: application/json" \
  -d '{"ip": "1.2.3.4"}'
```

### **Traffic Stats:**
```bash
curl http://localhost:8000/api/traffic
```

See full API documentation in dashboard.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional attack patterns
- [ ] More AI agents (forensics, compliance)
- [ ] Better anomaly detection models
- [ ] Integration with SIEM systems
- [ ] Performance optimizations
- [ ] Additional dashboards

---

## 📝 License

License - See LICENSE file for details

---

## 🆘 Support & Troubleshooting

### **🔴 CRITICAL ISSUE: Ollama Connection Refused**

**Symptoms:**
```
[WARNING] Could not connect to Ollama server
   Tried: http://127.0.0.1:11434 and http://ollama:11434
WARNING:agents:⚠️  Warning: Cannot reach Ollama server at http://127.0.0.1:11434
   Error: [Errno 111] Connection refused
```

**Root Cause:**  
Ollama is listening only on `127.0.0.1:11434` (localhost), which Docker containers cannot access. Containers need Ollama to listen on all interfaces (`0.0.0.0`).

**Solution:**

**Step 1: Check Ollama binding**
```bash
ss -tlnp | grep 11434
```

If you see `127.0.0.1:11434`, Ollama is only on localhost (PROBLEM).  
If you see `*:11434` or `0.0.0.0:11434`, it's accessible (GOOD).

**Step 2: Fix Ollama network binding**
```bash
# Create systemd override
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Verify (should show *:11434)
ss -tlnp | grep 11434
```

**Step 3: Restart Sentinel container**
```bash
cd ~/Project
docker-compose restart sentinel-agent
docker-compose logs -f sentinel-agent
```

**Expected output:**
```
[SUCCESS] Found Ollama via host.docker.internal at http://host.docker.internal:11434
✅ Ollama server is reachable at http://host.docker.internal:11434
```

**Alternative (Docker Ollama):**  
If you prefer Ollama in Docker instead of on the host:
```bash
# Use Docker Ollama (uncomment in docker-compose.yml)
docker-compose --profile with-ollama up -d
```

---

### **🐧 Line Endings Issue (Windows Development)**

**Symptoms:**
```
exec /usr/local/bin/docker-entrypoint.sh: no such file or directory
```

**Root Cause:**  
Shell scripts from Windows have CRLF line endings (`\r\n`) instead of Unix LF (`\n`). Linux interprets shebang as `#!/bin/bash\r` which doesn't exist.

**Solution:**  
The Dockerfile automatically fixes this with `sed -i 's/\r$//'`. If you still encounter this:

```bash
# Manually fix on server
cd ~/Project
sed -i 's/\r$//' docker-entrypoint.sh
sed -i 's/\r$//' docker-startup.sh

# Rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Prevention:**  
Configure Git to handle line endings:
```bash
# On Windows development machine
git config --global core.autocrlf input
```

---

### **🌐 Network/Port Issues**

#### **Issue 1: Can't access dashboard from other devices**

**Symptoms:**  
- Dashboard works on server (`localhost:8501`) but not from other devices
- Browser shows "Connection refused" on `http://SERVER_IP:8501`

**Diagnosis:**
```bash
# Check port bindings
docker-compose ps
```

**Solution:**  
Verify `docker-compose.yml` has correct port bindings:
```yaml
ports:
  - "192.168.31.91:8000:8000"  # Replace with YOUR server IP
  - "192.168.31.91:8501:8501"
```

Change to your actual server IP:
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Update IP addresses, then restart
docker-compose down
docker-compose up -d
```

#### **Issue 2: Port already in use**

**Symptoms:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find what's using port 8000 or 8501
sudo lsof -i :8000
sudo lsof -i :8501

# Kill the process or change port in docker-compose.yml
ports:
  - "YOUR_IP:9000:8000"  # Use different external port
  - "YOUR_IP:9501:8501"
```

---

### **🐳 Docker Issues**

#### **Container constantly restarting**

**Diagnosis:**
```bash
# Check container status
docker-compose ps

# View last 100 lines of logs
docker-compose logs --tail=100 sentinel-agent

# Check for errors
docker-compose logs sentinel-agent | grep -E "(ERROR|CRITICAL|Failed)"
```

**Common fixes:**
```bash
# Clean restart
docker-compose down -v  # WARNING: Deletes data!
docker-compose up -d --build

# Preserve data but rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### **Out of disk space**

**Symptoms:**
```
no space left on device
```

**Solution:**
```bash
# Check disk space
df -h

# Clean Docker cache
docker system prune -a --volumes  # WARNING: Deletes unused data!

# Remove old images
docker images | grep sentinel-agent
docker rmi <old-image-ids>
```

---

### **📊 Dashboard Issues**

#### **Dashboard not showing data**

**Solution:**
```bash
# 1. Generate test attacks
python3 test_web_attacks.py

# 2. Check if database has data
sqlite3 data/sentinel_intel.db "SELECT COUNT(*) FROM incidents;"

# 3. Check API health
curl http://localhost:8000/api/health
curl http://localhost:8000/api/summary

# 4. Check dashboard logs
docker-compose logs web-dashboard  # If separate container
# OR for integrated dashboard
docker-compose logs sentinel-agent | grep streamlit
```

#### **Authentication fails (sentinel/sentinel)**

**Solution:**
```bash
# Reset credentials (edit docker-compose.yml)
environment:
  DASHBOARD_USER: newuser
  DASHBOARD_PASS: newpassword

# Restart to apply
docker-compose restart sentinel-agent
```

---

### **⚠️ AI Analysis Issues**

#### **AI not analyzing attacks (EXPECTED for MEDIUM/LOW)**

**This is NORMAL behavior!**  
The system is optimized to only use AI for HIGH severity threats:

- ✅ HIGH severity → AI crew analysis (SQL injection, XSS, etc.)
- 📝 MEDIUM/LOW → Fast logging without AI (90% of attacks)

**Verify it's working:**
```bash
# Test HIGH severity attack (will trigger AI)
python3 test_web_attacks.py --severity high

# Search logs for AI analysis
docker-compose logs | grep "HIGH SEVERITY"
docker-compose logs | grep "crew.kickoff"

# Should see analysis within 30 seconds
```

#### **Ollama model not found**

**Symptoms:**
```
[WARNING] Model llama3:8b not found
```

**Solution:**
```bash
# Pull the model
ollama pull llama3:8b

# Verify it's available
ollama list

# Restart container
docker-compose restart sentinel-agent
```

---

### **🔒 Permission Issues**

#### **Can't write to logs or data directories**

**Symptoms:**
```
Permission denied: /app/data
Permission denied: /var/log/auth.log
```

**Solution:**
```bash
# Fix permissions on host
sudo chmod -R 755 ~/Project/data
sudo chmod -R 755 ~/Project/logs

# If using mounted system logs
sudo chmod 644 /var/log/auth.log
sudo chmod 644 /var/log/apache2/access.log

# Restart container
docker-compose restart sentinel-agent
```

---

### **🔥 Firewall Blocking Issues**

#### **Container can't reach internet**

**Solution:**
```bash
# Check firewall status
sudo ufw status

# Allow Docker subnet
sudo ufw allow from 172.0.0.0/8

# Or disable temporarily for testing
sudo ufw disable
```

#### **Dashboard accessible from public internet (SECURITY RISK)**

**Solution:**  
The default configuration binds to specific IP for local network only:
```yaml
ports:
  - "192.168.31.91:8501:8501"  # Local network only
  # NOT "0.0.0.0:8501:8501" - This would expose publicly!
```

To restrict further:
```bash
# Use firewall rules
sudo ufw allow from 192.168.31.0/24 to any port 8501
sudo ufw enable
```

---

### **📦 Installation Issues**

#### **AUTO_INSTALL.sh fails**

**Solution:**
```bash
# Run with verbose logging
sudo bash -x AUTO_INSTALL.sh 2>&1 | tee install.log

# Check the log for errors
cat install.log | grep -i error

# Manual installation (see INSTALLATION.md)
```

#### **Docker not installed correctly**

**Verify Docker:**
```bash
docker --version
docker-compose --version
docker ps

# Reinstall if needed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

---

### **🔍 Diagnostic Commands**

**Quick health check:**
```bash
# Container status
docker-compose ps

# View logs
docker-compose logs -f sentinel-agent

# Check Ollama connection
curl http://localhost:11434/api/tags

# Check API
curl http://localhost:8000/api/health

# Check disk space
df -h

# Check memory
free -h
```

**Full diagnostic:**
```bash
# Save diagnostic info to file
{
  echo "=== Container Status ==="
  docker-compose ps
  
  echo -e "\n=== Ollama Status ==="
  systemctl status ollama
  ss -tlnp | grep 11434
  
  echo -e "\n=== Port Usage ==="
  sudo lsof -i :8000 -i :8501 -i :11434
  
  echo -e "\n=== Disk Space ==="
  df -h
  
  echo -e "\n=== Recent Logs ==="
  docker-compose logs --tail=50 sentinel-agent
  
  echo -e "\n=== Database Stats ==="
  sqlite3 data/sentinel_intel.db "SELECT 
    (SELECT COUNT(*) FROM incidents) as incidents,
    (SELECT COUNT(*) FROM actions) as actions;"
    
} > diagnostic_report.txt

cat diagnostic_report.txt
```

---

### **📞 Get Help:**

1. **Check Logs:**
   ```bash
   docker-compose logs -f sentinel-agent
   ```

2. **Check Documentation:**
   - See `TROUBLESHOOTING.md` for detailed guides
   - See `DASHBOARD_GUIDE.md` for dashboard issues
   - See `DOCKER_TROUBLESHOOTING.md` for container issues

3. **Re-run Installer:**
   ```bash
   sudo ./AUTO_INSTALL.sh
   ```

4. **Clean Installation:**
   ```bash
   docker-compose down -v  # WARNING: Deletes data!
   rm -rf data/ logs/
   sudo ./AUTO_INSTALL.sh
   ```

5. **Report Issues:**
   - GitHub Issues: https://github.com/chandan5615/Project/issues
   - Include: OS version, Docker version, logs, error messages

---

## 🙏 Acknowledgments

Built with:
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [Ollama](https://ollama.ai/) - Local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Docker](https://www.docker.com/) - Containerization
- [Plotly](https://plotly.com/) - Interactive charts

---

## 📈 Performance Stats

- **Detection Speed:** < 1 second for log parsing
- **AI Analysis:** 10-30 seconds for HIGH severity threats
- **Resource Usage:** ~2GB RAM, 10-20% CPU (idle)
- **Throughput:** 1000+ attacks/hour sustained
- **AI Optimization:** 90% reduction in LLM calls vs naive implementation

---

## 🗺️ Roadmap

- [ ] Machine learning-based attack prediction
- [ ] Email/Slack/Discord notifications
- [ ] Multi-server monitoring (agent deployment)
- [ ] Custom attack signature creation
- [ ] Integration with SIEM systems
- [ ] Kubernetes deployment support

---

**Made with ❤️ for the security community**

**Deploy anywhere, anytime, with ONE command!** 🚀

---

## ⭐ Star this repo if it helps you!

