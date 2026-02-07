# Sentinel Agent v2.2 - Production Ready

An autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. Sentinel Agent uses CrewAI for orchestration and local Ollama (Llama 3) as the LLM engine to monitor, analyze, and respond to security threats in real-time.

---

## ⚡ Installation (Choose One - All Are Clean & No-Mess!)

### 🐳 Docker (Recommended - Fastest!) ⭐

**No Python environment setup needed. Everything is containerized.**

```bash
# Clone and deploy in 30 seconds
git clone <repo> sentinel-agent
cd sentinel-agent
docker-compose --profile with-ollama up -d

# Verify it's running
curl http://localhost:8000/api/health
```

**That's it!** Your system is ready. Access:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501 (optional)

**For Docker Host Ollama (Production):**
```bash
ollama pull llama3:8b && ollama serve
# In another terminal:
docker-compose up -d
```

📚 **Docker Guide**: [DOCKER_QUICKSTART.md](docs_markdown/DOCKER_QUICKSTART.md) | [Full Guide](docs_markdown/DOCKER_DEPLOYMENT.md)

---

### 🪟 Windows Users (Traditional Setup)

**PowerShell (Recommended) ⭐**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1
```

**Command Prompt (Alternative)**
```cmd
install.bat
```

### 🐧 Linux/macOS Users (Traditional Setup)

```bash
chmod +x install.sh
./install.sh
```

### 🐍 Any Platform (Python)

```bash
python install.py
```

**⏱️ Installation Time:** 3-6 minutes | **Includes:** venv + all dependencies + databases

📚 **Need More Info?** See [QUICK_INSTALL.md](QUICK_INSTALL.md) or [INSTALLATION.md](INSTALLATION.md)

---

## ✨ What's New in v2.2

**6 Enterprise Features Added:**
- ✅ **Offline Threat Intelligence** - Local IP reputation database
- ✅ **Dashboard Authentication** - Secure token-based access
- ✅ **Whitelist/Blacklist Management** - Flexible IP filtering
- ✅ **Performance Metrics** - Detection & response time tracking
- ✅ **REST API** - 20+ endpoints for external integration
- ✅ **ML Anomaly Scoring** - Multi-factor threat detection

[📚 Full Documentation](docs_markdown/README_FEATURES.md)

---

## 🎯 Core Features

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

## 🚀 Quick Start (5 Minutes)

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

## 🔐 Authentication

### Default Credentials
```
Username: admin
Password: sentinel123
⚠️ CHANGE IMMEDIATELY IN PRODUCTION
```

### Get API Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=sentinel123"
# Returns: {"token":"eyJhbGc...","expires_in":86400}
```

### Use in API Calls
```bash
TOKEN="your_token_here"
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/metrics/dashboard
```

---

## 📊 API Endpoints (20+)

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

## 🗂️ Project Structure

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
│   ├── FEATURE_INTEGRATION.md          # Integration guide
│   ├── DEPLOYMENT_GUIDE.md             # Usage guide
│   ├── COMPLETE_FEATURES_SUMMARY.md    # Feature overview
│   ├── README_FEATURES.md              # Quick reference
│   ├── CODE_REVIEW_REPORT.md           # Code quality
│   └── ... (23 more documentation files)
│
└── Configuration & Scripts
    ├── activate_env.sh / .bat
    ├── setup.sh / .bat / .ps1
    ├── docker-compose.yml
    └── Dockerfile
```

---

## 📚 Documentation

Full documentation is available in [`docs_markdown/`](docs_markdown/) folder:

### Getting Started
- [**FEATURE_INTEGRATION.md**](docs_markdown/FEATURE_INTEGRATION.md) - Feature-by-feature integration guide
- [**DEPLOYMENT_GUIDE.md**](docs_markdown/DEPLOYMENT_GUIDE.md) - Practical usage and deployment
- [**README_FEATURES.md**](docs_markdown/README_FEATURES.md) - Quick feature reference

### Technical Details
- [**CODE_REVIEW_REPORT.md**](docs_markdown/CODE_REVIEW_REPORT.md) - Code quality assessment
- [**IMPLEMENTATION_COMPLETE.md**](docs_markdown/IMPLEMENTATION_COMPLETE.md) - Implementation status
- [**PROJECT_DOCUMENTATION.md**](docs_markdown/PROJECT_DOCUMENTATION.md) - System architecture

### Deployment & Operations
- [**DOCKER_DEPLOYMENT.md**](docs_markdown/DOCKER_DEPLOYMENT.md) - Docker setup
- [**GITHUB_DEPLOYMENT.md**](docs_markdown/GITHUB_DEPLOYMENT.md) - GitHub deployment
- [**ENVIRONMENT.md**](docs_markdown/ENVIRONMENT.md) - Environment variables

### Additional Resources
- [**QUICK_REFERENCE.md**](docs_markdown/QUICK_REFERENCE.md) - Command reference
- [**CHANGELOG.md**](docs_markdown/CHANGELOG.md) - Version history
- [**CONTRIBUTING.md**](docs_markdown/CONTRIBUTING.md) - Contribution guidelines

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

## 🧪 Testing

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

## 🐳 Docker Deployment

### Quick Start
```bash
docker-compose up -d

# Check logs
docker-compose logs -f sentinel

# Stop
docker-compose down
```

### Production Deployment
See [DOCKER_DEPLOYMENT.md](docs_markdown/DOCKER_DEPLOYMENT.md) for:
- SSL/TLS configuration
- Health checks
- Resource limits
- Persistent storage

---

## 🔒 Security Considerations

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

## 📊 Performance

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

## 🐛 Troubleshooting

### API won't start
```bash
# Check if port is in use
netstat -an | grep 8000

# Kill existing process
pkill -f "python sentinel_api.py"

# Try different port
python sentinel_api.py --port 8001
```

### "Module not found" error
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

## 📈 Monitoring & Maintenance

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

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs_markdown/CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Feature request procedure

---

## 📞 Support

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

## 📜 License

[Add your license information here]

---

## 🙏 Acknowledgments

- CrewAI for multi-agent orchestration
- Ollama for local LLM inference
- FastAPI for REST API framework
- Streamlit for dashboard UI

---

## 📋 Version History

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

## 🚀 Next Steps

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
