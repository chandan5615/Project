#!/usr/bin/env python3
"""
Update README.md with current project state (v2.3)
"""

README_CONTENT = """# 🛡️ Sentinel Agent v2.3

**AI-Powered Security Monitoring & Automated Response System**

Real-time threat detection with intelligent auto-blocking, whitelist protection, and progressive punishment. Deploy on any Ubuntu server with **ONE command** in 15 minutes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/version-2.3-green.svg)](https://github.com/chandan5615/Project)

---

## 🚀 Quick Start (One Command)

```bash
# Download and run automated installer
wget -O- https://raw.githubusercontent.com/chandan5615/Project/main/AUTO_INSTALL.sh | sudo bash

# OR if you have the files:
chmod +x AUTO_INSTALL.sh
sudo ./AUTO_INSTALL.sh
```

**That's it!** The installer automatically:
- ✅ Installs Docker & Docker Compose
- ✅ Sets up Ollama LLM with llama3:8b
- ✅ Configures system dependencies
- ✅ **Auto-detects your server IP** (no hardcoded addresses!)
- ✅ Creates secure `.env` configuration
- ✅ Builds and starts containers
- ✅ Initializes database with security features
- ✅ Configures firewall and monitoring

**Time:** 10-15 minutes (fully automated)

**Access After Installation:**
```
📊 Dashboard: http://YOUR_SERVER_IP:8501 (local network only, requires login)
🔌 API:       http://YOUR_SERVER_IP:8000
💚 Health:    http://YOUR_SERVER_IP:8000/api/health
```

**Default Credentials:**
```
Username: admin
Password: (auto-generated - check: docker logs sentinel-agent | grep "DEFAULT ADMIN")
```

> ⚠️ **SECURITY:** Dashboard is automatically restricted to local network only. Change admin password after first login!

---

## ⚡ What's New in v2.3

### **🆕 Major Features**

#### **1. Auto-Unblocking (Temporary Bans)**
- 🕐 IPs are blocked temporarily, not permanently
- ⏰ Automatic expiry based on offense severity
- 🧹 Background cleanup thread checks every 60 seconds
- 📊 Track ban duration and expiry in database

#### **2. Whitelist Protection (Admin God-Mode)**
- 🛡️ Auto-detects and protects admin IPs (localhost, server IP, local network)
- 🚫 Whitelisted IPs can NEVER be blocked
- 📝 Manual whitelist management via CLI
- ✅ Prevents accidental self-lockout

#### **3. Progressive Punishment**
- 1️⃣ **1st offense:** 15-minute ban
- 2️⃣ **2nd offense:** 2-hour ban
- 3️⃣ **3rd+ offense:** 24-hour ban
- 🚨 **CRITICAL severity:** Always 24-hour ban (overrides count)

#### **4. Dashboard Authentication**
- 🔐 Secure login with bcrypt-hashed passwords
- 🎫 Session-based authentication (24-hour expiry)
- 📝 Failed login attempts logged
- 👥 Multi-user support (admin, analyst, viewer roles)

#### **5. Auto IP Detection**
- 🔍 Automatically detects server's primary IP on installation
- 💾 Creates `.env` file with correct configuration
- 🔄 No hardcoded IPs - works even if IP changes!
- 🔒 Binds dashboard to local network automatically

---

## 🎯 What Does It Do?

Sentinel Agent is a comprehensive security monitoring system that:

### **Detects Attacks**
- 🔓 SSH brute force attacks
- 💉 SQL injection attempts
- 📂 Path traversal / directory scanning
- ⚡ Cross-site scripting (XSS)
- 🤖 Automated attack tool signatures (sqlmap, nikto, etc.)
- 🌐 Suspicious web requests and patterns

### **Responds Intelligently**
- 🚫 **Automatic blocking** with iptables firewall rules
- ⏰ **Temporary bans** with auto-expiry
- 📈 **Progressive punishment** for repeat offenders
- 🛡️ **Whitelist protection** to prevent admin lockout
- 🤖 **AI crew analysis** for critical threats (4 specialized agents)
- 📊 **Real-time logging** and dashboard visualization

### **Monitors Continuously**
- 📁 `/var/log/auth.log` (SSH attacks)
- 📁 `/var/log/apache2/access.log` (web attacks)
- ⚡ Real-time file watching with instant response
- 🔄 Background cleanup of expired bans
- 📈 Statistics tracking and trending

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[START_HERE.md](START_HERE.md)** | Quick start guide and first steps |
| **[FEATURES_AUTO_UNBLOCK_WHITELIST.md](FEATURES_AUTO_UNBLOCK_WHITELIST.md)** | Complete feature documentation (auto-unblock, whitelist, progressive punishment) |
| **[DASHBOARD_SECURITY_GUIDE.md](DASHBOARD_SECURITY_GUIDE.md)** | Dashboard authentication, password management, security best practices |
| **[TESTING_GUIDE_V2.3.md](TESTING_GUIDE_V2.3.md)** | Testing procedures, attack simulation, verification steps |
| **[TROUBLESHOOTING_COMPLETE.md](TROUBLESHOOTING_COMPLETE.md)** | Common issues and solutions |
| **[ANSWERS_TO_YOUR_QUESTIONS.md](ANSWERS_TO_YOUR_QUESTIONS.md)** | FAQ and detailed Q&A |
| **[IP_MANAGER_CLI_GUIDE.md](IP_MANAGER_CLI_GUIDE.md)** | Command-line IP management |
| **[SECURE_DASHBOARD_PORT_8501.md](SECURE_DASHBOARD_PORT_8501.md)** | Port security configuration |

---

## �� System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          SENTINEL AGENT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 Log Monitoring          →  🤖 AI Analysis                   │
│  ├─ auth.log (SSH)             └─ 4 AI Agents                   │
│  └─ access.log (Web)              ├─ Security Analyst           │
│                                   ├─ Network Specialist         │
│  🔍 Pattern Detection             ├─ Threat Intelligence        │
│  ├─ SQL Injection                 └─ Incident Coordinator       │
│  ├─ XSS                                                         │
│  ├─ Path Traversal         →  🛡️ Auto Response                 │
│  ├─ Brute Force                └─ Whitelist Check ✅             │
│  └─ Command Injection          └─ Calculate Ban Duration        │
│                                └─ Execute iptables Block        │
│  💾 Database                   └─ Schedule Auto-Unblock         │
│  ├─ incidents                                                   │
│  ├─ blocked_ips (with expiry)  →  📊 Dashboard                  │
│  ├─ safe_ips (whitelist)          ├─ Real-time Monitoring       │
│  ├─ threat_intel                  ├─ Attack Visualization       │
│  └─ actions                       ├─ IP Management              │
│                                   └─ Statistics & Reports       │
│  🧹 Background Cleanup                                          │
│  └─ Expired Ban Removal (60s)  →  🔔 Notifications (Future)     │
│                                   └─ Email/Slack/Webhook        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 System Requirements

### **Minimum:**
- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** 4 GB (8 GB recommended for AI analysis)
- **CPU:** 2 cores (4 cores recommended)
- **Disk:** 20 GB free space
- **Network:** Static or DHCP IP (auto-detected)

### **Software (auto-installed):**
- Docker 20.10+
- Docker Compose 2.0+
- Ollama (for AI LLM)
- Python 3.10+
- iptables (firewall)

---

## 🛠️ Manual Installation

If you prefer manual setup or need customization:

### **1. Clone Repository**
```bash
git clone https://github.com/chandan5615/Project.git
cd Project
```

### **2. Install Dependencies**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Install Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama3:8b
```

### **3. Configure Environment**
```bash
# Option A: Use AUTO_INSTALL.sh (recommended - auto-detects IP)
sudo ./AUTO_INSTALL.sh

# Option B: Manually create .env:
cat > .env << EOF
DASHBOARD_BIND_IP=10.87.146.89  # Your server IP
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3:8b
LOG_LEVEL=INFO
EOF
```

### **4. Build and Start**
```bash
docker-compose build --no-cache
docker-compose up -d
```

### **5. Verify Installation**
```bash
docker-compose ps
docker logs sentinel-agent
curl http://localhost:8000/api/health
```

---

## 🎮 Usage Examples

### **Dashboard Access**
```bash
# Open in browser:
http://YOUR_SERVER_IP:8501

# Login with credentials from:
docker logs sentinel-agent | grep "DEFAULT ADMIN"
```

### **View Real-Time Logs**
```bash
docker-compose logs -f sentinel-agent
```

### **Check Blocked IPs**
```bash
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT ip, banned_until, offense_count, status FROM blocked_ips;"
```

### **Check Whitelist**
```bash
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT ip, reason, auto_detected FROM safe_ips;"
```

### **Manually Block IP**
```bash
docker exec sentinel-agent python3 -c "
from data_engine import get_data_engine
db = get_data_engine()
db.block_ip('192.168.1.100', 60, 'Manual block')
print('IP blocked for 60 minutes')
"
```

### **Manually Whitelist IP**
```bash
docker exec sentinel-agent python3 -c "
from data_engine import get_data_engine
db = get_data_engine()
db.add_safe_ip('192.168.1.200', 'Trusted admin workstation', auto_detected=False)
print('IP whitelisted')
"
```

---

## 🧪 Testing the System

### **Simulate SSH Brute Force**
```bash
# Generate fake auth.log entries
docker exec sentinel-agent python3 test_direct_logs.py --auth-count 10

# Check dashboard for detections
```

### **Simulate Web Attack**
```bash
# SQL injection test
python3 test_web_attacks.py

# Or use GoldenEye DDoS tool (real attack):
python3 goldeneye.py http://YOUR_SERVER_IP:8000 -w 10 -s 100
```

### **Verify Blocking**
```bash
# Check if IP was blocked
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT * FROM blocked_ips WHERE ip='ATTACKING_IP';"

# Check iptables
docker exec sentinel-agent iptables -L INPUT -n | grep ATTACKING_IP
```

### **Test Auto-Unblock**
```bash
# Block an IP with 1-minute ban
docker exec sentinel-agent python3 -c "
from data_engine import get_data_engine
db = get_data_engine()
db.block_ip('192.168.1.99', 1, 'Test ban')
"

# Wait 2 minutes and check if auto-unblocked
sleep 120
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT ip, status FROM blocked_ips WHERE ip='192.168.1.99';"
# Should show: status='expired'
```

---

## 🗂️ Project Structure

```
Project/
├── main.py                          # Main orchestrator with AI crew
├── data_engine.py                   # Database with auto-unblock, whitelist, progressive punishment
├── agents.py                        # 4 AI agents (Analyst, Network, ThreatIntel, Coordinator)
├── tasks.py                         # AI crew task definitions
├── anomaly_scorer.py                # Anomaly detection scoring
├── threat_intelligence.py           # Threat intel database
├── auth.py                          # Dashboard authentication
├── security_manager.py              # Password encryption, token management
│
├── dashboard/
│   └── web_dashboard.py             # Streamlit dashboard with login
│
├── sensors/
│   ├── log_monitor.py               # File watching (auth.log, access.log)
│   └── attack_patterns.py           # Pattern matching for attacks
│
├── defense/
│   └── firewall_manager.py          # iptables integration
│
├── tools/
│   └── tools.py                     # IP detection, network utilities
│
├── tests/
│   ├── test_attacks.py              # Attack simulation
│   ├── test_web_attacks.py          # HTTP-based attacks
│   └── test_direct_logs.py          # Direct log writing
│
├── scripts/
│   ├── AUTO_INSTALL.sh              # One-click installer with auto IP detection
│   ├── verify_port_security.sh      # Port security checker
│   └── run_tests_in_docker.sh       # Docker test runner
│
├── docker-compose.yml               # Container orchestration
├── Dockerfile                       # Container build
├── requirements.txt                 # Python dependencies
├── .env                             # Environment config (auto-generated)
│
└── Documentation/
    ├── README.md                    # This file
    ├── START_HERE.md                # Quick start
    ├── FEATURES_AUTO_UNBLOCK_WHITELIST.md
    ├── DASHBOARD_SECURITY_GUIDE.md
    ├── TESTING_GUIDE_V2.3.md
    └── TROUBLESHOOTING_COMPLETE.md
```

---

## 🔧 Configuration

### **Environment Variables** (`.env` file - auto-generated by AUTO_INSTALL.sh)

```bash
# Dashboard Binding (AUTO-DETECTED)
DASHBOARD_BIND_IP=10.87.146.89      # Auto-detected on install

# Ollama LLM
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT=60

# Database
SENTINEL_DB_PATH=/app/data/sentinel_intel.db

# Logging
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
LITELLM_LOG=ERROR                     # Reduce LLM noise

# Performance
CREW_TIMEOUT=60
CREW_VERBOSE=0                        # 0=quiet, 1=verbose
```

### **docker-compose.yml Ports**

```yaml
ports:
  - "8000:8000"                       # API (can be public)
  - "${DASHBOARD_BIND_IP:-127.0.0.1}:8501:8501"  # Dashboard (local only, auto-detected)
```

---

## 🚨 Troubleshooting

### **Dashboard Not Accessible**

**Problem:** Can't access http://YOUR_IP:8501

**Solution:**
```bash
# Check if container is running
docker-compose ps

# Check what IP dashboard is bound to
docker port sentinel-agent 8501

# If IP changed, re-run installer to detect new IP
sudo ./AUTO_INSTALL.sh

# Or manually update .env:
nano .env
# Change DASHBOARD_BIND_IP=<new_ip>
docker-compose down && docker-compose up -d
```

### **No Attacks Detected**

**Problem:** Dashboard shows no incidents

**Solution:**
```bash
# Check if log files exist and are readable
docker exec sentinel-agent ls -la /var/log/auth.log /var/log/apache2/access.log

# Generate test attacks
docker exec sentinel-agent python3 test_direct_logs.py --auth-count 5 --web-count 5

# Check database
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT COUNT(*) FROM incidents;"
```

### **Auto-Unblock Not Working**

**Problem:** Banned IPs not getting auto-unblocked

**Solution:**
```bash
# Check cleanup thread status
docker logs sentinel-agent | grep "Auto-unblock cleanup"

# Check for expired IPs
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT ip, banned_until, status FROM blocked_ips WHERE banned_until < datetime('now');"

# Restart container to reinitialize cleanup thread
docker-compose restart
```

**More troubleshooting:** See [TROUBLESHOOTING_COMPLETE.md](TROUBLESHOOTING_COMPLETE.md)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Email/Slack notifications
- [ ] GeoIP location tracking
- [ ] More AI models (qwen, mistral)
- [ ] Web UI for IP management
- [ ] Integration with fail2ban
- [ ] Webhook support

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 📞 Support

- **Documentation:** See markdown files in project root
- **Issues:** [GitHub Issues](https://github.com/chandan5615/Project/issues)

---

## 📈 Project Stats

- **Version:** 2.3
- **Last Updated:** February 25, 2026
- **Lines of Code:** ~15,000+
- **AI Agents:** 4 specialized agents
- **Attack Patterns:** 50+ signatures
- **Auto Features:** Auto-unblock, Whitelist, Progressive Punishment, Auto IP Detection

---

**🛡️ Protect Your Server. Monitor Threats. Respond Intelligently.**

**Star ⭐ this repo if you find it useful!**
"""

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    print("✅ README.md updated successfully!")
    print("📄 Version: 2.3")
    print("📝 Documentation cleaned and updated")
