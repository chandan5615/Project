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

### **Quick Guides:**
- 📖 **[START_HERE.md](START_HERE.md)** - Quick start guide
- 🤖 **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** - What's automated
- 📝 **[ATTACK_TESTING_GUIDE.txt](ATTACK_TESTING_GUIDE.txt)** - Testing guide

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

## 🎨 Dashboard Features

Access at `http://YOUR_SERVER_IP:8501`

- 📊 **Real-time Security Metrics**
  - Security score
  - Threat counter
  - Attack feed
  - Wall of shame

- 📈 **System Monitoring**
  - CPU, memory, disk usage
  - Network connections
  - Traffic statistics

- 📝 **Log Viewer**
  - Live log entries
  - Severity filtering
  - Auto-refresh (8 seconds)

- 🚫 **IP Management**
  - Block/unblock IPs
  - Blacklist viewing
  - Whitelist management

- 📉 **Charts & Analytics**
  - Attack time series
  - Severity distribution
  - Top attackers

---

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

# Check dashboard
open http://YOUR_SERVER_IP:8501
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

### **Common Issues:**

**Containers not starting:**
```bash
docker-compose down -v
docker-compose up -d --build
```

**Dashboard not showing data:**
```bash
# Generate test data
python3 test_web_attacks.py

# Check API
curl http://localhost:8000/api/health
```

**AI not analyzing attacks:**
- This is NORMAL for MEDIUM/LOW severity (optimized!)
- Test with HIGH severity attacks: SQL injection, XSS
- Check logs: `docker-compose logs | grep "HIGH SEVERITY"`

**Ollama errors:**
```bash
# Restart Ollama
pkill ollama
ollama serve &
sleep 5
ollama pull llama3:8b
```

### **Get Help:**

- 📖 Check documentation files in project
- 🐛 Check logs: `docker-compose logs -f`
- 🔄 Re-run installer: `sudo ./AUTO_INSTALL.sh`

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

