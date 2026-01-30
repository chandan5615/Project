# Sentinel Agent v2.1

An autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. Sentinel Agent uses CrewAI for orchestration and local Ollama (Llama 3) as the LLM engine to monitor, analyze, and respond to security threats in real-time with quiet logging and an internal admin dashboard.

## Features

- **Real-time Log Monitoring**: Watches `/var/log/auth.log` and `/var/log/apache2/access.log` for attacks
- **Multi-Agent AI Analysis**: Four specialized AI agents work together:
  - **Triage Analyst**: Analyzes logs and determines event severity
  - **Threat Intelligence Researcher**: Checks IP reputation and threat intelligence
  - **Incident Response Specialist**: Generates remediation plans and firewall rules
  - **Enforcer Agent**: Prepares and executes defensive measures
- **Quiet Logging**: Console shows only WARNING+ messages; full logs to `/app/logs/sentinel.log`
- **SQLite Data Persistence**: Tracks incidents, actions, and threat intelligence
- **Zero-Exposure Admin Dashboard**: Internal-only FastAPI UI with Basic Auth and WebSocket real-time updates
- **Human-in-the-Loop Security**: Requires explicit approval before executing any blocking actions
- **Professional Output**: Clean, formatted text-based reports (no emojis/icons)
- **Modular Architecture**: Clean separation of sensors, agents, tasks, and tools

## Architecture

```
Sentinel Agent
├── sensors/          # Input modules (log watchers, network sniffers)
│   └── auth_sensor.py
├── tools/            # Python functions for OSINT and firewall actions
│   └── tools.py
├── agents.py         # AI Crew definitions
├── tasks.py          # Security playbooks
└── main.py           # Entry point and event loop
```

## Prerequisites

- **Python**: 3.9 or higher (3.10+ recommended)
- **OS**: Linux system (tested on Ubuntu 20.04+, Debian 11+)
- **Ollama**: Local LLM engine (no cloud API keys required)
  - Install: [https://ollama.ai](https://ollama.ai)
  - Model: Llama 3 (8b recommended)
- **Privileges**: Root/sudo access (for reading logs and firewall operations)

### Quick Ollama Setup

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull Llama 3 model
ollama pull llama3:8b

# Verify it's running
curl http://localhost:11434/api/tags
```

### Environment Variables (Optional)

```bash
# Dashboard credentials (defaults: sentinel/sentinel)
export DASHBOARD_USER=yourusername
export DASHBOARD_PASS=yourpassword

# Logging location (default: /app/logs/sentinel.log)
export LOG_DIR=/var/log/sentinel

# Database location (default: /app/data/sentinel_intel.db)
export DATA_DIR=/var/lib/sentinel
```

## Installation

### Option 1: Docker Deployment (Recommended for Production)

```bash
# Clone and deploy
git clone https://github.com/yourorg/sentinel-agent.git
cd sentinel-agent

# Start all services (Sentinel Agent + optional dashboard)
docker compose up -d

# View logs
docker compose logs -f sentinel
```

### Option 2: Manual Installation (Development/Testing)

**Linux:**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Quick Start

**Ensure Ollama is running first:**
```bash
ollama pull llama3:8b
ollama serve  # In another terminal
```

**Then run Sentinel Agent:**
```bash
sudo python main.py
```

The system will start monitoring logs and output professional, easy-to-understand alerts to the console with full details logged to `/app/logs/sentinel.log`.

## Admin Dashboard (Optional)

Start the internal dashboard on `127.0.0.1:8080`:

```bash
uvicorn dashboard.app:app --host 127.0.0.1 --port 8080
```

Access via SSH tunnel (secure):
```bash
ssh -L 8080:127.0.0.1:8080 user@server
# Then visit http://localhost:8080 (default credentials: sentinel/sentinel)
```

For Docker: `docker compose up -d` includes the dashboard service (profile: dashboard).

## Architecture

```
Sentinel Agent v2.1
├── Quiet Logging Engine
│   ├── Console: WARNING+ only
│   ├── File: Full DEBUG logs
│   └── Rotating: 10MB files, 5 backup copies
│
├── Data Persistence (SQLite)
│   ├── incidents: Attack records
│   ├── actions: Response actions taken
│   └── threat_intel: IP reputation cache
│
├── Multi-Agent AI Crew (CrewAI + Ollama)
│   ├── Triage Analyst
│   ├── Threat Intelligence Researcher
│   ├── Incident Response Specialist
│   └── Enforcer Agent
│
├── Sensor Layer (Watchdog)
│   ├── Auth Sensor: /var/log/auth.log
│   └── Web Sensor: /var/log/apache2/access.log
│
└── Admin Dashboard (FastAPI)
    ├── HTTP Basic Auth
    ├── JSON REST API
    ├── WebSocket real-time updates
    └── Single-page Plotly UI
```

## Testing

Run the unit test suite to verify all components:

```bash
python -m pytest -q
# Expected: 5 passed, 1 skipped
```

**Tests include:**
- Data engine (SQLite) operations
- Remediation workflow (approval/execution)
- View attacks output formatting
- Dashboard (BasicAuth + WebSocket tokens)

---

## Documentation

See the following files for detailed information:

- **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** — Complete technical documentation, architecture, and v2.0/v2.1 improvements
- **[SETUP_GUIDE_WEB_APPLICATIONS.md](SETUP_GUIDE_WEB_APPLICATIONS.md)** — Web-based setup and deployment
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Quick commands and tips
- **[ENVIRONMENT.md](ENVIRONMENT.md)** — Environment variables and configuration
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** — Docker and compose deployment
- **[docs/DASHBOARD_SETUP.md](docs/DASHBOARD_SETUP.md)** — Admin dashboard setup and SSH tunneling

---

## Project Structure

```
sentinel-agent/
├── main.py                    # Entry point and event orchestrator
├── agents.py                  # CrewAI agent definitions
├── tasks.py                   # Security analysis tasks
├── data_engine.py             # SQLite data persistence
├── output_formatter.py        # Professional output formatting
├── view_attacks.py            # Attack records viewer
├── requirements.txt           # Python dependencies
│
├── sensors/                   # Log monitoring modules
│   ├── __init__.py
│   ├── auth_sensor.py         # SSH brute force detection
│   └── web_sensor.py          # Web attack detection
│
├── tools/                     # Security tools & utilities
│   ├── __init__.py
│   └── tools.py              # IP reputation, firewall, system tools
│
├── defense/                   # Attack detection & logging
│   ├── __init__.py
│   ├── attack_detector.py     # Threat pattern matching
│   └── attack_logger.py       # SQLite logging
│
├── dashboard/                 # Admin UI (optional)
│   ├── app.py               # FastAPI + WebSocket server
│   └── ...
│
├── tests/                     # Unit tests
│   ├── test_data_engine.py
│   ├── test_remediation.py
│   ├── test_view_attacks.py
│   └── test_dashboard.py
│
├── docs/                      # Documentation
│   └── DASHBOARD_SETUP.md
│
├── scripts/                   # Helper scripts
│   ├── tunnel_admin.sh
│   └── tunnel_admin.ps1
│
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Container image
└── README.md                 # This file
```

---

## Key Features in Detail

### 1. Quiet Logging (v2.1)
- **Console output**: WARNING and above only (production-friendly)
- **File logs**: Full DEBUG level to `/app/logs/sentinel.log`
- **Rotation**: Automatic 10MB rolling logs with 5 backups
- **No emojis/icons**: Clean, professional text output

### 2. Data Persistence (v2.1)
- **SQLite database**: `/app/data/sentinel_intel.db`
- **Three tables**:
  - `incidents`: Attack records with timestamps, severity, source IP
  - `actions`: Response actions taken (approvals, blocks, etc.)
  - `threat_intel`: IP reputation cache for fast lookups
- **Context manager support**: Automatic DB connection cleanup

### 3. Multi-Agent AI Analysis
- **Triage Analyst**: Scores severity (low/medium/high/critical)
- **Threat Intel Researcher**: Queries IP reputation database
- **Incident Response Specialist**: Generates firewall rules and remediation
- **Enforcer Agent**: Validates and prepares defensive actions

### 4. Admin Dashboard (v2.1)
- **Access**: HTTP Basic Auth (default: sentinel/sentinel)
- **Real-time**: WebSocket streaming of incident summary updates
- **Endpoints**:
  - `/api/summary` — Statistics (severity, attack type distribution)
  - `/api/records` — Incident records paginated
  - `/api/network` — Network graph (IP ↔ attack type relationships)
  - `/ws/summary` — WebSocket for live updates
- **UI**: Single-page app with Plotly charts (client-side CDN)
- **Network**: Internal only (`127.0.0.1:8080`); SSH tunnel for remote access

### 5. Security Hardening
- **Human-in-the-loop**: Approval required before firewall rule execution
- **File rotation handling**: Automatic inode tracking and position reset
- **IP validation**: Bulletproof validation (rejects invalid octets)
- **JSON parsing**: Robust brace-counting algorithm for nested structures
- **Type hints**: 100% type coverage for Python 3.9+ compatibility

---

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for your changes
4. Run `python -m pytest -q` to verify
5. Commit and push: `git push origin feature/your-feature`
6. Open a pull request with a clear description

---

## Support & Issues

- **Bug reports**: Open an issue with reproduction steps and logs
- **Feature requests**: Describe the use case and expected behavior
- **Security issues**: Email to [security contact] (do not open public issue)

---

## License

This project is provided as-is for educational and security research purposes.

## Disclaimer

This tool is designed for authorized security monitoring only. Ensure you have proper authorization before monitoring systems or blocking IP addresses. The authors are not responsible for misuse of this software.

---

**Version**: 2.1 (Quiet Logging + Dashboard + Professional Output)  
**Last Updated**: January 30, 2026  
**Status**: ✅ Production Ready
