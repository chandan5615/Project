# 🛡️ Sentinel Agent v2.2

**AI-Powered Security Monitoring System for Linux**

Real-time threat detection and automated response using AI crew analysis. Deploy on any Ubuntu server with **ONE command** in 15 minutes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![GitHub](https://img.shields.io/badge/GitHub-chandan5615%2FProject-blue?logo=github)](https://github.com/chandan5615/Project)

> **📚 DOCUMENTATION:** Every single feature is documented! See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete index of all documentation files.

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

---

## 📑 Complete Table of Contents

### **Quick Start & Installation**
- [Quick Start (One Command Installation)](#-quick-start-one-command-installation)
- [What Does It Do?](#-what-does-it-do)
- [System Requirements](#-system-requirements)
- [Manual Installation Options](#-manual-installation-options)
- [Post-Installation Steps](#-post-installation-steps)

### **Features & Capabilities**
- [Core Features](#-core-features)
- [AI-Powered Analysis](#-ai-powered-analysis)
- [Dashboard Features (9 Tabs)](#-dashboard-features-v20---9-comprehensive-tabs)
- [Features by Category](#-features-by-category)
- [Complete Feature Reference](#-complete-feature-reference)

### **File Structure & Components**
- [Project Structure & Files](#-project-structure--files)
  - Core Application Modules
  - Dashboard Applications
  - Utility Scripts
  - Testing & Attack Simulation
  - Installation & Setup Scripts
  - Troubleshooting & Fix Scripts
  - Docker Configuration
  - Documentation Files

### **Configuration & Environment**
- [Complete Environment Variables Reference](#-complete-environment-variables-reference)
  - Ollama LLM Configuration
  - Log File Paths
  - Database Configuration
  - Web Dashboard Settings
  - API Server Configuration
  - Authentication & Security
  - AI Analysis Configuration
  - Threat Response
  - Logging Configuration
  - Email Notifications (Future)
  - Third-Party Integrations (Future)

### **Command-Line Interface**
- [Complete Command-Line Reference](#-complete-command-line-reference)
  - Main Application
  - Web Dashboard
  - CLI Dashboard
  - Database Cleanup
  - View Attacks
  - Test Web Attacks
  - Continuous Attacks
  - System Validation
  - Docker Commands
  - Ollama Commands

### **API Documentation**
- [API Endpoints Complete List](#-api-endpoints-complete-list)
  - Health & Status Endpoints
  - Incident Endpoints
  - IP Management Endpoints
  - Action Endpoints
  - Statistics Endpoints
  - Export Endpoints
  - Threat Intelligence Endpoints
  - Log Endpoints

### **Database & Data Management**
- [Database Tables](#-database-tables)
- [Schema Details](#schema-details)
- [Data Export & Import](#data-export--import)

### **Attack Detection**
- [Attack Detection Patterns](#-attack-detection-patterns)
  - SQL Injection
  - Cross-Site Scripting (XSS)
  - Path Traversal
  - Command Injection
  - Brute Force
  - Directory Scanning
  - Attack Tool Signatures

### **Usage & Examples**
- [Use Cases](#-use-cases)
- [Testing the System](#-testing-the-system)
- [Attack Testing Guide](#attack-testing-guide)
- [Real-World Deployment](#real-world-deployment)

### **Troubleshooting & Support**
- [Support & Troubleshooting](#-support--troubleshooting)
- [Critical Issue: Ollama Connection](#-critical-issue-ollama-connection-refused)
- [Common Problems](#common-problems)
- [Get Help](#-get-help)

### **Advanced Topics**
- [Architecture Deep Dive](#-architecture-deep-dive)
- [Performance Stats](#-performance-stats)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---
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

**📖 COMPLETE FEATURE DOCUMENTATION:**
- 🔍 **[COMPLETE_FEATURE_REFERENCE.md](COMPLETE_FEATURE_REFERENCE.md)** - **COMPREHENSIVE!** Every single feature, module, script, API, configuration option, environment variable, database table, and capability documented in exhaustive detail

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
- ✨ **[DASHBOARD_FEATURES.md](DASHBOARD_FEATURES.md)** - NEW: Enhanced features guide (v2.0)
- 🛡️ **[IP_MANAGER_CLI_GUIDE.md](IP_MANAGER_CLI_GUIDE.md)** - **NEW!** IP blocking CLI tool guide
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

#### **🎯 Core Features:**
- 🛡️ **Wall of Shame** - Real-time blocked IPs monitoring
- 📋 **Incident Feed** - Live security incident tracking
- 📈 **Network Health** - Traffic metrics and trends
- 📊 **Security Score** - Real-time security posture

#### **✨ Enhanced Features (NEW):**
- 📄 **Log File Viewer** - Tail and search auth logs and Apache logs
  - Real-time log tailing with configurable line count
  - Search and filter capabilities
  - Download log content
  - Support for custom log paths

- 🌐 **Apache Traffic Analysis** - Comprehensive web server monitoring
  - Total requests and unique IPs
  - HTTP status code distribution
  - Top client IPs and requested URLs
  - Error rate tracking (4xx/5xx)
  - User agent analysis
  - Detailed error request breakdown

- 🚫 **IP Blocking/Unblocking** - Manual firewall control
  - Block/unblock IPs via UFW or iptables
  - View currently blocked IPs
  - IP address validation
  - Real-time firewall rule updates

- 🎯 **Attack Patterns** - Visual attack trend analysis
  - Attack type distribution (7-day view)
  - Hourly attack patterns (24-hour view)
  - Interactive charts and graphs

- 📊 **Export Reports** - Data export and archival
  - Export incidents to CSV (flexible time ranges)
  - Export threat intelligence to JSON
  - Database statistics dashboard
  - Timestamped export files

- 💻 **System Information** - Server health monitoring
  - System uptime tracking
  - Load average (1m, 5m)
  - Disk usage with visual progress
  - Resource monitoring

#### **Access & Configuration:**
- 🌐 Auto-detected LAN IP display
- ⚙️ Configurable refresh intervals (5-60 seconds)
- 🎨 Dark theme with professional styling
- 📱 Responsive design for all devices

**📚 For detailed feature documentation, see [DASHBOARD_FEATURES.md](DASHBOARD_FEATURES.md)**

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
DASHBOARD_BIND_IP=0.0.0.0  # set to your LAN IP to restrict access

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

**LAN-only access (recommended):**
1) Set the host bind IP to your LAN IP in `.env` (or export it before `docker compose up -d`).
2) Restart Docker.

```bash
# .env
DASHBOARD_BIND_IP=YOUR_LAN_IP

# Apply
docker compose down
docker compose up -d
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

## 📂 Project Structure & Files

### **Core Application Modules**

| File | Purpose | Key Features |
|------|---------|--------------|
| **main.py** | Main application entry point | Log monitoring, attack detection, AI orchestration, incident handling |
| **agents.py** | AI agent definitions | 4 specialized agents: Triage, Intel, Responder, Enforcer |
| **tasks.py** | AI task workflows | Log analysis, threat research, response planning, enforcement |
| **data_engine.py** | Database operations | SQLite management, incident logging, queries, exports |
| **sentinel_api.py** | REST API server | FastAPI endpoints, authentication, JSON responses |
| **auth.py** | Authentication system | HTTP Basic Auth, credential verification, session management |
| **security_manager.py** | Security & encryption | Password hashing (PBKDF2), encryption, secret management |
| **threat_intelligence.py** | Threat intel management | IP reputation, geolocation, blacklist checking |
| **anomaly_scorer.py** | Anomaly detection | Statistical analysis, baseline modeling, deviation alerts |
| **metrics.py** | Performance metrics | Prometheus metrics, response times, throughput tracking |

### **Dashboard Applications**

| File | Purpose | Features |
|------|---------|----------|
| **dashboard/web_dashboard.py** | Streamlit web UI | 9 tabs: Incidents, logs, Apache traffic, IP blocking, exports, system info |
| **dashboard/cli_dashboard.py** | Terminal UI | Rich TUI, real-time updates, color-coded severity, minimal bandwidth |
| **dashboard_controller.py** | Dashboard management | Start/stop dashboards, service monitoring, configuration |

### **Utility Scripts**

| File | Purpose | Usage |
|------|---------|-------|
| **ip_manager_cli.py** | **⭐ IP blocking CLI** | `python3 ip_manager_cli.py block\|unblock\|list\|check IP` |
| **clear_database.py** | Database cleanup | `python3 clear_database.py --all\|--incidents\|--ip IP` |
| **view_attacks.py** | Attack viewer | `python3 view_attacks.py --limit 50 --severity HIGH` |
| **validate_system.py** | System validation | `python3 validate_system.py --check-all` |
| **verify_sentinel_setup.py** | Setup verification | `python3 verify_sentinel_setup.py` |
| **init_database.py** | Database initialization | `python3 init_database.py --fresh` |
| **environment_detector.py** | Environment detection | Detects Docker, cloud providers, resources |
| **password_manager.py** | Password utilities | Secure generation, strength validation |
| **list_manager.py** | Blacklist/whitelist | Manage IP lists, import/export |
| **logging_adapter.py** | Structured logging | JSON logs, context injection, rotation |
| **output_formatter.py** | Output formatting | JSON, tables, colors, Rich text |

### **Testing & Attack Simulation**

| File | Purpose | Attack Types |
|------|---------|--------------|
| **test_web_attacks.py** | Web attack simulator | SQL injection, XSS, path traversal, command injection, directory scanning |
| **test_client_attacks.py** | Client-side attacks | Stored XSS, reflected XSS, DOM XSS, CSRF, session hijacking, cookie tampering |
| **test_auth.py** | Authentication tests | Brute force, credential stuffing, session fixation, password reset abuse |
| **test_security.py** | Security feature tests | Firewall, rate limiting, input validation, CSRF protection |
| **test_attacks.py** | Comprehensive suite | All attack types, scenarios, reporting |
| **continuous_attacks.py** | Sustained attacks | Configurable rate, mixed types, long-duration testing |

### **Installation & Setup Scripts**

| File | Platform | Purpose |
|------|----------|---------|
| **AUTO_INSTALL.sh** | Linux (Ubuntu/Debian) | Fully automated one-command installation |
| **AUTO_INSTALL_WINDOWS.bat** | Windows + WSL2 | Windows installer using WSL |
| **install.sh** | Linux | Manual step-by-step installation |
| **install.bat** | Windows | Windows manual installer |
| **install.ps1** | Windows (PowerShell) | PowerShell installation script |
| **install.py** | Cross-platform | Python-based installer |
| **setup.sh** | Linux | Interactive setup wizard |
| **setup.bat** | Windows | Windows setup wizard |
| **setup.ps1** | Windows (PowerShell) | PowerShell setup script |
| **sentinel_setup.sh** | Linux | Production setup with hardening |
| **verify_setup.sh** | Linux | Verify installation completeness |

### **Troubleshooting & Fix Scripts**

| File | Purpose |
|------|---------|
| **configure_ollama_network.sh** | Fix Ollama connection issues (most common problem) |
| **fix_ollama_connection.sh** | Alternative Ollama fix script |
| **fix_ollama_connection.bat** | Windows Ollama fix |
| **quick_fix_ollama.sh** | Fast Ollama fix |
| **quick_fix_ollama.bat** | Windows quick Ollama fix |
| **fix_logs.sh** | Fix log file permissions |
| **deploy_fixes.ps1** | PowerShell deployment fixes |
| **rebuild_no_cache.bat** | Docker rebuild without cache |

### **Activation Scripts**

| File | Purpose |
|------|---------|
| **activate_env.sh** | Activate Python virtual environment (Linux) |
| **activate_env.bat** | Activate Python virtual environment (Windows) |
| **start.sh** | Start all services (Linux) |
| **LAUNCH_ATTACKS.bat** | Launch attack tests (Windows) |

### **Docker Configuration**

| File | Purpose |
|------|---------|
| **docker-compose.yml** | Main Docker Compose configuration |
| **docker-compose.prod.yml** | Production Docker configuration |
| **Dockerfile** | Container image build instructions |
| **docker-entrypoint.sh** | Container startup script |
| **docker-startup.sh** | Service startup orchestration |
| **.dockerignore** | Files to exclude from Docker build |

### **Configuration Files**

| File | Purpose |
|------|---------|
| **requirements.txt** | Python package dependencies |
| **nginx.conf** | Nginx reverse proxy configuration (optional) |
| **.env** | Environment variables (create from examples) |
| **.gitignore** | Files to exclude from Git |

### **Documentation Files**

| File | Description |
|------|-------------|
| **README.md** | Main project documentation (this file) |
| **START_HERE.md** | Quick start guide for new users |
| **COMPLETE_FEATURE_REFERENCE.md** | **COMPREHENSIVE feature documentation** |
| **DASHBOARD_FEATURES.md** | Enhanced dashboard features (v2.0) |
| **DASHBOARD_GUIDE.md** | Complete dashboard tutorial |
| **DASHBOARD_UPDATE_SUMMARY.md** | Dashboard features overview |
| **AUTOMATION_SUMMARY.md** | What's automated in installation |
| **TROUBLESHOOTING_COMPLETE.md** | Complete troubleshooting guide |
| **QUICK_TROUBLESHOOTING.md** | Quick reference troubleshooting card |
| **ATTACK_TESTING_GUIDE.txt** | How to test the system |
| **DEPLOYMENT_FIXES.md** | Deployment issue fixes |
| **DOCUMENTATION_SUMMARY.txt** | Documentation summary |
| **CHANGES_2026-02-23.md** | Changelog |

### **Verification Scripts**

| File | Purpose |
|------|---------|
| **check_crewai_api.py** | Test CrewAI functionality |
| **check_crew_instance.py** | Validate crew configuration |
| **sentinel_auto.py** | Automated deployment tool |

---

## 🔧 Complete Environment Variables Reference

### **Ollama LLM Configuration**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Ollama server URL
OLLAMA_MODEL=llama3:8b                             # LLM model to use
OLLAMA_TIMEOUT=30000                               # Request timeout (ms)
OLLAMA_NUM_CTX=4096                                # Context window size
OLLAMA_TEMPERATURE=0.7                             # Response creativity (0.0-1.0)
```

### **Log File Paths**
```bash
AUTH_LOG_PATH=/var/log/auth.log                    # Authentication log
WEB_LOG_PATH=/var/log/apache2/access.log           # Web server access log
CUSTOM_LOG_PATH=/path/to/custom.log                # Additional custom logs
```

### **Database Configuration**
```bash
SENTINEL_DB_PATH=/app/data/sentinel_intel.db       # SQLite database path
SENTINEL_DATA_DIR=/app/data                        # Data directory
DB_BACKUP_ENABLED=true                             # Enable automatic backups
DB_BACKUP_DIR=/app/data/backups                    # Backup location
DB_RETENTION_DAYS=90                               # Data retention period
```

### **Web Dashboard Settings**
```bash
DASHBOARD_PORT=8501                                # Dashboard port
DASHBOARD_BIND_IP=0.0.0.0                          # Bind to all interfaces (or specific IP)
DASHBOARD_USER=sentinel                            # Dashboard username
DASHBOARD_PASS=sentinel                            # Dashboard password (CHANGE THIS!)
DASHBOARD_THEME=dark                               # Theme: dark or light
DASHBOARD_REFRESH=30                               # Auto-refresh interval (seconds)
```

### **CLI Dashboard Settings**
```bash
CLI_REFRESH_INTERVAL=5                             # Refresh rate (seconds)
CLI_MAX_INCIDENTS=20                               # Rows to display
CLI_SHOW_STATS=true                                # Show summary statistics
```

### **API Server Configuration**
```bash
API_PORT=8000                                      # API server port
API_HOST=0.0.0.0                                   # API bind address
API_WORKERS=4                                      # Uvicorn workers
API_TIMEOUT=60                                     # Request timeout (seconds)
API_MAX_REQUESTS=1000                              # Max requests before restart
```

### **Authentication & Security**
```bash
SENTINEL_ADMIN_USER=sentinel                       # Admin username
SENTINEL_ADMIN_PASS=sentinel                       # Admin password (CHANGE THIS!)
SECRET_KEY=your-secret-key-here                    # Encryption secret key
HASH_ITERATIONS=100000                             # Password hash iterations
ENABLE_HTTPS=false                                 # Enable HTTPS (requires certificates)
```

### **AI Analysis Configuration**
```bash
ENABLE_AI_ANALYSIS=true                            # Enable AI crew analysis
AI_THRESHOLD=HIGH                                  # Minimum severity for AI (HIGH, MEDIUM, LOW)
AI_MAX_ITER=25                                     # Max AI agent iterations
AI_VERBOSE=false                                   # Verbose AI output
AI_TIMEOUT=60                                      # AI analysis timeout (seconds)
```

### **Threat Response**
```bash
BLOCK_AUTO=true                                    # Automatically block detected threats
BLOCK_DURATION=3600                                # Block duration (seconds, 0=permanent)
BLACKLIST_ENABLED=true                             # Enable IP blacklist
WHITELIST_ENABLED=true                             # Enable IP whitelist
```

### **Logging Configuration**
```bash
LOG_LEVEL=INFO                                     # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                                    # json or text
LOG_FILE=/app/logs/sentinel.log                   # Log file path
LOG_MAX_SIZE=104857600                             # Max log size (100MB)
LOG_BACKUP_COUNT=10                                # Number of backup log files
METRICS_ENABLED=true                               # Enable Prometheus metrics
METRICS_PORT=9090                                  # Metrics endpoint port
```

### **Email Notifications (Future Feature)**
```bash
SMTP_HOST=smtp.gmail.com                           # SMTP server
SMTP_PORT=587                                      # SMTP port
SMTP_USER=your-email@example.com                   # SMTP username
SMTP_PASS=your-password                            # SMTP password
EMAIL_FROM=sentinel@example.com                    # From address
EMAIL_TO=admin@example.com                         # To address
ENABLE_EMAIL_ALERTS=false                          # Enable email alerts
```

### **Third-Party Integrations (Future)**
```bash
ENABLE_SIEM=false                                  # Enable SIEM integration
SIEM_ENDPOINT=http://siem-server:514               # SIEM server endpoint
SYSLOG_ENABLED=false                               # Enable syslog forwarding
WEBHOOK_URL=http://slack-webhook-url               # Webhook for notifications
```

---

## 🎯 Complete Command-Line Reference

### **Main Application**
```bash
python3 main.py [OPTIONS]

Options:
  --auth-log PATH        Authentication log path (default: /var/log/auth.log)
  --web-log PATH         Web log path (default: /var/log/apache2/access.log)
  --db-path PATH         Database path (default: ./data/sentinel_intel.db)
  --ollama-url URL       Ollama server URL (default: http://127.0.0.1:11434)
  --model NAME           LLM model name (default: llama3:8b)
  --no-ai                Disable AI analysis completely
  --verbose              Enable debug logging
  --daemon               Run as background daemon

Examples:
  # Standard run
  python3 main.py
  
  # Custom log paths
  python3 main.py --auth-log /custom/auth.log --web-log /custom/web.log
  
  # Disable AI (fast logging only)
  python3 main.py --no-ai
  
  # Debug mode
  python3 main.py --verbose
```

### **Web Dashboard**
```bash
streamlit run dashboard/web_dashboard.py [OPTIONS]

Streamlit Options:
  --server.port PORT             Port to run on (default: 8501)
  --server.address ADDRESS       Address to bind (default: localhost)
  --server.headless true         Run in headless mode
  --server.enableCORS false      Disable CORS
  --server.enableXsrfProtection  Enable XSRF protection

Environment Variables:
  SENTINEL_DB_PATH=/path/to/db.sqlite
  DASHBOARD_PORT=8501
  DASHBOARD_USER=username
  DASHBOARD_PASS=password

Examples:
  # Run locally
  streamlit run dashboard/web_dashboard.py
  
  # Run accessible from network
  streamlit run dashboard/web_dashboard.py --server.address 0.0.0.0 --server.port 8501
  
  # Custom database
  SENTINEL_DB_PATH=./custom.db streamlit run dashboard/web_dashboard.py
  
  # Inside Docker container
  docker exec -it sentinel-agent streamlit run dashboard/web_dashboard.py --server.address 0.0.0.0 --server.port 8501
```

### **CLI Dashboard**
```bash
python3 dashboard/cli_dashboard.py [OPTIONS]

Options:
  --refresh SECONDS      Auto-refresh interval (default: 5)
  --max-rows INT         Maximum rows to display (default: 20)
  --db-path PATH         Database path

Examples:
  # Standard run
  python3 dashboard/cli_dashboard.py
  
  # Faster refresh
  python3 dashboard/cli_dashboard.py --refresh 2
  
  # Show more rows
  python3 dashboard/cli_dashboard.py --max-rows 50
```

### **Database Cleanup**
```bash
python3 clear_database.py [OPTIONS]

Options:
  --all                  Clear all data (incidents, actions, threat intel)
  --incidents            Clear incidents table only
  --threat-intel         Clear threat intelligence only
  --ip IP_ADDRESS        Clear all records for specific IP
  --older-than DAYS      Clear data older than N days
  --list                 List top attacking IPs
  --dry-run              Show what would be deleted without deleting

Examples:
  # List top attackers
  python3 clear_database.py --list
  
  # Clear specific IP
  python3 clear_database.py --ip 1.2.3.4
  
  # Clear old data (dry run)
  python3 clear_database.py --older-than 90 --dry-run
  
  # Clear old data (execute)
  python3 clear_database.py --older-than 90
  
  # Clear all data
  python3 clear_database.py --all
```

### **⭐ IP Manager CLI (NEW!)**
```bash
python3 ip_manager_cli.py [COMMAND] [OPTIONS]

Commands:
  block IP [IP2...]      Block one or more IP addresses
  unblock IP [IP2...]    Unblock one or more IP addresses
  list                   List all currently blocked IPs
  check IP               Check if an IP is blocked
  flush                  Remove ALL blocks (dangerous!)
  (no command)           Interactive mode

Options:
  --reason TEXT, -r      Reason/comment for blocking
  --details, -d          Show detailed information

Features:
  ✓ Works with both UFW and iptables
  ✓ Validates IP addresses before blocking
  ✓ Batch operations (block/unblock multiple IPs)
  ✓ Interactive mode available
  ✓ Color-coded output
  ✓ Fast and lightweight

Examples:
  # Interactive mode (recommended)
  python3 ip_manager_cli.py
  
  # Block a single IP
  sudo python3 ip_manager_cli.py block 1.2.3.4
  
  # Block with reason
  sudo python3 ip_manager_cli.py block 1.2.3.4 --reason "SQL injection attack"
  
  # Block multiple IPs at once
  sudo python3 ip_manager_cli.py block 1.2.3.4 5.6.7.8 9.10.11.12
  
  # Unblock an IP
  sudo python3 ip_manager_cli.py unblock 1.2.3.4
  
  # List all blocked IPs
  sudo python3 ip_manager_cli.py list
  
  # Check if IP is blocked
  sudo python3 ip_manager_cli.py check 1.2.3.4
  
  # Interactive session
  sudo python3 ip_manager_cli.py
  > block 1.2.3.4
  > list
  > check 1.2.3.4
  > unblock 1.2.3.4
  > exit

See IP_MANAGER_CLI_GUIDE.md for complete documentation.
```

### **View Attacks**
```bash
python3 view_attacks.py [OPTIONS]

Options:
  --limit INT            Number of attacks to show (default: 50)
  --severity LEVEL       Filter by severity (HIGH, MEDIUM, LOW)
  --ip IP_ADDRESS        Filter by IP address
  --since DATETIME       Filter by date (YYYY-MM-DD or ISO-8601)
  --attack-type TYPE     Filter by attack type
  --export FILE.csv      Export to CSV file
  --stats                Show statistics summary

Examples:
  # View latest 50 attacks
  python3 view_attacks.py
  
  # View HIGH severity only
  python3 view_attacks.py --severity HIGH --limit 100
  
  # View attacks from specific IP
  python3 view_attacks.py --ip 1.2.3.4
  
  # Export to CSV
  python3 view_attacks.py --export attacks.csv --since 2024-01-01
  
  # Show statistics
  python3 view_attacks.py --stats
```

### **Test Web Attacks**
```bash
python3 test_web_attacks.py [OPTIONS]

Options:
  --target URL           Target URL (default: http://10.76.250.89:8000)
  --intensity LEVEL      Attack intensity: low, medium, high, extreme
  --attack-type TYPE     Specific attack: sql, xss, path, cmd, all
  --delay SECONDS        Delay between requests (default: 1.0)
  --count INT            Number of attacks to generate (default: 50)
  --verbose              Detailed output

Examples:
  # Basic test
  python3 test_web_attacks.py
  
  # High intensity attack
  python3 test_web_attacks.py --intensity high --count 100
  
  # SQL injection only
  python3 test_web_attacks.py --attack-type sql --delay 0.5
  
  # Custom target
  python3 test_web_attacks.py --target http://myserver.com:8000
```

### **Continuous Attacks**
```bash
python3 continuous_attacks.py [OPTIONS]

Options:
  --interval SECONDS     Attack every N seconds (default: 5)
  --duration MINUTES     Run for N minutes (default: 60)
  --burst INT            Attacks per burst (default: 3)
  --randomize            Randomize attack types
  --target URL           Target URL

Examples:
  # Light continuous attacks (1 hour)
  python3 continuous_attacks.py --interval 10 --duration 60
  
  # Heavy attacks (5 minutes)
  python3 continuous_attacks.py --interval 1 --burst 10 --duration 5
  
  # Randomized attacks
  python3 continuous_attacks.py --randomize --duration 120
```

### **System Validation**
```bash
python3 validate_system.py [OPTIONS]

Options:
  --check-all            Run all checks
  --check-deps           Check dependencies only
  --check-config         Check configuration only
  --check-perms          Check permissions only
  --fix                  Attempt to fix issues automatically

Examples:
  # Full validation
  python3 validate_system.py --check-all
  
  # Check and fix
  python3 validate_system.py --check-all --fix
  
  # Check dependencies
  python3 validate_system.py --check-deps
```

### **Docker Commands**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f sentinel-agent

# Restart specific service
docker-compose restart sentinel-agent

# Rebuild containers
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Execute command inside container
docker exec -it sentinel-agent <command>

# Access container shell
docker exec -it sentinel-agent bash

# View container status
docker-compose ps

# Check resource usage
docker stats sentinel-agent
```

### **Ollama Commands**
```bash
# Check Ollama status
systemctl status ollama

# Start/Stop Ollama
sudo systemctl start ollama
sudo systemctl stop ollama
sudo systemctl restart ollama

# Pull model
ollama pull llama3:8b

# List models
ollama list

# Test model
ollama run llama3:8b "Hello"

# Check Ollama network binding
ss -tlnp | grep 11434

# Configure Ollama network (fix connection issues)
sudo ./configure_ollama_network.sh
```

---

## 📊 API Endpoints Complete List

### **Health & Status Endpoints**
- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/version` - Version information

### **Incident Endpoints**
- `GET /api/incidents` - List incidents (with filters)
- `GET /api/incidents/{id}` - Get specific incident
- `POST /api/incidents` - Create incident
- `DELETE /api/incidents/{id}` - Delete incident

### **IP Management Endpoints**
- `GET /api/ips/blocked` - List blocked IPs
- `POST /api/ips/block` - Block IP address
- `DELETE /api/ips/block/{ip}` - Unblock IP address
- `GET /api/ips/reputation/{ip}` - Get IP reputation
- `PUT /api/ips/reputation/{ip}` - Update IP reputation

### **Action Endpoints**
- `GET /api/actions` - List actions
- `GET /api/actions/{id}` - Get specific action

### **Statistics Endpoints**
- `GET /api/stats/summary` - Overall statistics
- `GET /api/stats/timeline` - Time-series data
- `GET /api/stats/attackers` - Top attackers
- `GET /api/stats/attack-types` - Attack type distribution

### **Export Endpoints**
- `GET /api/export/incidents` - Export incidents (CSV/JSON)
- `GET /api/export/threat-intel` - Export threat intel (JSON)
- `GET /api/export/database` - Backup database (Admin only)

### **Threat Intelligence Endpoints**
- `GET /api/threat-intel` - List threat intelligence
- `POST /api/threat-intel` - Add threat intel
- `DELETE /api/threat-intel/{ip}` - Remove threat intel

### **Log Endpoints**
- `GET /api/logs` - Get logs
- `GET /api/logs/search` - Search logs

**📘 For detailed API documentation with request/response examples, see [COMPLETE_FEATURE_REFERENCE.md](COMPLETE_FEATURE_REFERENCE.md#api-endpoints-reference)**

---

## 🗄️ Database Tables

### **Main Tables**
1. **incidents** - Security incident records
2. **actions** - Automated response actions
3. **threat_intel** - IP reputation and intelligence
4. **blacklist** - Blocked IP addresses
5. **whitelist** - Trusted IP addresses

### **Schema Details**
See [COMPLETE_FEATURE_REFERENCE.md](COMPLETE_FEATURE_REFERENCE.md#database-schema) for complete table structures, indexes, and example data.

---

## 🔍 Attack Detection Patterns

### **Detected Attack Types**

1. **SQL Injection**
   - Union-based SQLi
   - Boolean-based blind SQLi
   - Error-based SQLi
   - Time-based blind SQLi
   - Stacked queries

2. **Cross-Site Scripting (XSS)**
   - Stored XSS
   - Reflected XSS  
   - DOM-based XSS
   - JavaScript injection
   - Event handler injection

3. **Path Traversal**
   - Directory traversal (../)
   - URL encoding variants
   - Double encoding
   - Null byte injection

4. **Command Injection**
   - Shell command injection
   - Code injection
   - LDAP injection
   - XPath injection

5. **Brute Force**
   - SSH brute force
   - Login brute force
   - Password spraying
   - Credential stuffing

6. **Directory Scanning**
   - Common file/directory enumeration
   - Admin panel discovery
   - Configuration file access
   - Backup file detection

7. **Attack Tool Signatures**
   - SQLmap
   - Nikto
   - Nmap
   - Burp Suite
   - Metasploit
   - DirBuster

**📘 For complete pattern regex and examples, see [COMPLETE_FEATURE_REFERENCE.md](COMPLETE_FEATURE_REFERENCE.md#detection-patterns)**

---

## 🎯 Features by Category

### **🔍 Detection Features**
- ✅ Real-time log monitoring (auth.log, apache access.log)
- ✅ Pattern-based attack detection (regex)
- ✅ Anomaly detection (statistical)
- ✅ Threat intelligence correlation
- ✅ IP reputation scoring
- ✅ Attack signature matching
- ✅ Behavioral analysis

### **🤖 AI Features**
- ✅ Multi-agent AI crew (CrewAI)
- ✅ Local LLM (Ollama + Llama 3)
- ✅ Conditional AI analysis (HIGH severity only)
- ✅ Log analysis automation
- ✅ Threat intelligence automation
- ✅ Response planning automation
- ✅ Natural language incident reports

### **🛡️ Response Features**
- ✅ Automatic IP blocking (iptables/UFW)
- ✅ Manual IP blocking via dashboard
- ✅ Temporary/permanent blocks
- ✅ IP whitelisting
- ✅ Configurable block duration
- ✅ Dry-run mode for testing

### **📊 Dashboard Features**
- ✅ **Web Dashboard** (Streamlit)
  - 9 comprehensive tabs
  - Real-time metrics
  - Log viewer
  - Apache traffic analysis
  - IP blocking controls
  - Attack pattern visualization
  - Data export (CSV/JSON)
  - System information

- ✅ **CLI Dashboard** (Rich TUI)
  - Terminal-based UI
  - Auto-refresh every 5 seconds
  - Color-coded severity
  - Top attackers table
  - Attack type statistics
  - Low bandwidth usage

### **🔌 API Features**
- ✅ RESTful API (FastAPI)
- ✅ 25+ endpoints
- ✅ JSON responses
- ✅ HTTP Basic Auth
- ✅ Rate limiting
- ✅ CORS support
- ✅ Swagger/OpenAPI docs

### **💾 Data Management**
- ✅ SQLite database
- ✅ Incident logging
- ✅ Action tracking
- ✅ Threat intelligence storage
- ✅ Data export (CSV/JSON/SQLite)
- ✅ Automatic backups (configurable)
- ✅ Data retention policies

### **🔐 Security Features**
- ✅ Password hashing (PBKDF2)
- ✅ Secret encryption
- ✅ HTTP Basic Auth
- ✅ Audit logging
- ✅ Secure credential storage
- ✅ Input validation
- ✅ Output sanitization

### **🧪 Testing Features**
- ✅ Web attack simulator
- ✅ Client-side attack tests
- ✅ Authentication attack tests
- ✅ Continuous attack generator
- ✅ Security feature validation
- ✅ 100+ attack patterns

### **🛠️ Utility Features**
- ✅ Database cleanup tools
- ✅ Attack viewer/analyzer
- ✅ System validation
- ✅ Configuration verification
- ✅ Log file management
- ✅ Blacklist/whitelist management

### **🐳 Deployment Features**
- ✅ One-command installation
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Automated setup scripts
- ✅ Cross-platform support
- ✅ Production configuration

### **📈 Monitoring Features**
- ✅ Prometheus metrics
- ✅ Performance tracking
- ✅ Resource monitoring
- ✅ System health checks
- ✅ Uptime tracking
- ✅ Load average monitoring

---

## 🎓 Use Cases

### **1. Web Server Protection**
Monitor Apache/Nginx logs for attacks, automatically block malicious IPs, get AI analysis of serious threats.

### **2. SSH Brute Force Prevention**
Detect and block SSH brute force attempts in real-time, track repeat offenders.

### **3. Security Research**
Generate controlled attacks for testing, analyze attack patterns, export data for research.

### **4. Compliance & Reporting**
Log all security incidents, generate compliance reports, export audit trails.

### **5. Training & Education**
Learn about attacks, understand AI-powered security, study threat patterns.

### **6. SOC Automation**
Automate initial threat triage, reduce false positives, focus on real threats.

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

MIT License - See LICENSE file for details

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

