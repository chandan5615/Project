# Sentinel Agent - Adaptive Reporting Quick Reference

**Last Updated**: January 30, 2026  
**Version**: 2.1  

## 🚀 Quick Start (60 seconds)

### Installation
```bash
# Install dependencies (one-time)
pip install -r requirements.txt

# That's it! Environment detection is automatic.
```

### Running

```bash
# Desktop (automatically uses GUI/Web dashboard)
python main.py

# SSH Terminal (automatically uses CLI/Rich dashboard)
ssh user@server
python main.py

# Docker (automatically logs-only mode)
docker run sentinel-agent:latest

# Systemd (automatically logs-only mode)
systemctl start sentinel-agent
```

---

## 🎨 Environment Modes

| Mode | Triggered When | Interface | Console |
|------|---|---|---|
| **GUI** | X11/Wayland/WT_SESSION detected | Streamlit @ `127.0.0.1:8501` | Heartbeat only |
| **CLI** | Terminal + no display | Rich formatted tables | Live updates |
| **Docker** | Running in container | None | Logs only |
| **Systemd** | Running as service | None | Logs only |

---

## 💻 Dashboard Features

### 🛡️ Web Dashboard (GUI Mode)
- **URL**: `http://127.0.0.1:8501` (automatically starts)
- **Components**:
  - Security Score card (0-100%)
  - Wall of Shame (blocked IPs table)
  - Incident Feed (recent threats)
  - Network Health (incidents/minute graph)
- **Refresh**: 5-60 seconds (configurable via sidebar)

### 🖥️ CLI Dashboard (Terminal Mode)
- **Display**: Rich formatted tables in terminal
- **Updates**: Every 5-30 seconds
- **Components**:
  - Security state with progress bar
  - Recent blocks table (colorized)
  - Incident alerts table
  - Summary stats
- **SSH Compatible**: ✅ Works over remote terminals

### 📦 Docker/Systemd Mode
- **Display**: None (logging-only)
- **Output**: Via `docker logs` or `journalctl`
- **Logging**: Full logs to `/app/logs/sentinel.log`

---

## 🔧 Core Components

### 1. Environment Detector
```python
from environment_detector import EnvironmentDetector

detector = EnvironmentDetector()
mode = detector.get_mode()  # Returns: "gui", "cli", "docker", "systemd"
config = detector.get_environment_config()
```

### 2. Adaptive Logger
```python
from logging_adapter import create_adaptive_logger

config = {...}  # From environment_detector
logger = create_adaptive_logger(config)

logger.heartbeat(threat_count=5, blocked_ips=3)
logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
logger.log_system_status("Monitoring", "All sensors active")
logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
logger.log_system_status("Monitoring", "Active")
logger.log_error("Test error", exception)
```

### Dashboard Controller
```python
from dashboard_controller import create_dashboard_controller

config = {...}  # From environment_detector
controller = create_dashboard_controller(config)

# Start appropriate dashboard automatically
controller.start_dashboard()

# Stop when done
controller.stop_dashboard()

# Check status
status = controller.get_dashboard_status()
```

### Adaptive Printer
```python
from logging_adapter import create_adaptive_printer

config = {...}
printer = create_adaptive_printer(config)

printer.print_dashboard_header()
printer.print_threat_alert("Brute Force", "192.168.1.100", "BLOCK")
printer.print_status_message("System ready")
printer.print_network_summary(threats=10, blocked=5, score=85)
```

---

## 🎯 Integration into main.py

```python
from environment_detector import EnvironmentDetector
from logging_adapter import create_adaptive_logger, create_adaptive_printer
from dashboard_controller import create_dashboard_controller

class SentinelAgent:
    def __init__(self):
        # 1. Detect environment
        detector = EnvironmentDetector()
        self.config = detector.get_environment_config()
        
        # 2. Setup logging
        self.logger = create_adaptive_logger(self.config)
        self.printer = create_adaptive_printer(self.config)
        
        # 3. Setup dashboards
        self.dashboard = create_dashboard_controller(self.config)
    
    def start(self):
        # Start dashboards
        self.dashboard.start_dashboard()
        
        # Log startup
        self.logger.log_system_status("Starting", f"Mode: {self.config['mode']}")
    
    def process_threat(self, threat_type, source_ip, action):
        # Log threat
        self.logger.log_threat_detected(threat_type, source_ip, action)
        
        # Print alert (if CLI)
        self.printer.print_threat_alert(threat_type, source_ip, action)
    
    def heartbeat(self):
        # Send heartbeat with metrics
        threat_count = 5  # From your sensors
        blocked_ips = 3   # From your database
        self.logger.heartbeat(threat_count, blocked_ips)
    
    def shutdown(self):
        self.logger.log_system_status("Shutting down")
        self.dashboard.stop_dashboard()
```

---

## 🖥️ Dashboard Features by Mode

### GUI Mode (Streamlit)
**When**: Display server detected (X11, Wayland, or Windows Terminal)  
**URL**: `http://127.0.0.1:8501`  
**Features**:
- 🛡️ Security Score (0-100%) with status indicator
- 🚫 Wall of Shame (blocked IPs table)
- 📋 Incident Feed (recent threats)
- 📊 Network Health (incidents/minute graph)
- ⚙️ Configuration panel

**Console Output**:
```
[16:45] Monitoring Active
[16:50] Monitoring Active - 5 Threats
[16:55] Monitoring Active - 3 Threats - 2 Blocked IPs
```

### CLI Mode (Rich)
**When**: No display server (SSH, terminal, or headless)  
**Features**:
- 🛡️ Security Score with progress bar
- 🚫 Wall of Shame (last 5 blocks)
- 📋 Incident Feed (last 5 incidents)
- 📊 Summary statistics
- Live or static updates

**Console Output**:
```
============================================================
🛡️  SENTINEL AGENT - CLI DASHBOARD
============================================================

🛡️  SECURITY STATE
Security Score: 78%
████████████████████████░░░░░░░░
Status: CAUTION

🚫 WALL OF SHAME
IP: 192.168.1.100
Threat: Brute Force
Count: 3
Last: 16:45:32
```

### Docker Mode
**When**: Running in Docker container  
**Features**: Logging only, no dashboard  
**Output**: Stdout + `/app/logs/sentinel.log`

### Systemd Mode
**When**: Running as systemd service  
**Features**: Logging only, no dashboard  
**Output**: Journal + `/app/logs/sentinel.log`

---

## 📊 Database Access

All dashboards read from `sentinel_intel.db`:

```python
import sqlite3

conn = sqlite3.connect("sentinel_intel.db")
cursor = conn.cursor()

# Get recent incidents
cursor.execute("""
    SELECT timestamp, source_ip, threat_type, action 
    FROM incidents 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

incidents = cursor.fetchall()
conn.close()
```

**Schema**:
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    source_ip TEXT,
    threat_type TEXT,
    details TEXT,
    action TEXT
);

CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    action_name TEXT,
    timestamp TEXT,
    details TEXT
);

CREATE TABLE threat_intel (
    id INTEGER PRIMARY KEY,
    threat_type TEXT,
    severity TEXT,
    description TEXT,
    mitigation TEXT
);
```

---

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/test_adaptive_reporting.py -v
```

### Run Specific Test
```bash
python -m pytest tests/test_adaptive_reporting.py::TestEnvironmentDetector -v
```

### Test Individual Component
```bash
# Test environment detection
python -c "from environment_detector import EnvironmentDetector; print(EnvironmentDetector().get_config())"

# Test CLI dashboard
python -c "from dashboard.cli_dashboard import start_cli_dashboard; start_cli_dashboard(live_mode=False, refresh_interval=5)"

# Test web dashboard
streamlit run dashboard/web_dashboard.py
```

---

## 🔍 Troubleshooting

### Dashboard not starting
```bash
# Check logs
tail -f app/logs/sentinel.log

# Verify environment
python -c "from environment_detector import EnvironmentDetector; print(EnvironmentDetector().get_environment_config())"
```

### Port already in use
```bash
# Check what's using port 8501
lsof -i :8501

# Kill process (if safe)
kill -9 <PID>

# Or change port in configuration
```

### Logging not working
```bash
# Create logs directory
mkdir -p app/logs

# Check permissions
ls -la app/logs/

# Fix if needed
chmod 755 app/logs
chmod 644 app/logs/sentinel.log
```

### Streamlit crashes
```bash
# Install missing dependencies
pip install streamlit>=1.35.0

# Try running directly
streamlit run dashboard/web_dashboard.py --logger.level=error
```

---

## 📚 Documentation

- **ADAPTIVE_REPORTING.md** - Comprehensive guide (300+ lines)
- **README.md** - Project overview with adaptive reporting section
- **PROJECT_DOCUMENTATION.md** - Full project documentation
- **IMPLEMENTATION_SUMMARY.md** - Detailed implementation notes
- **This file** - Quick reference

---

## 🔐 Security Notes

1. **Always bind to 127.0.0.1** - Never expose dashboards to internet
2. **Use SSH tunneling** for remote access:
   ```bash
   ssh -L 8501:127.0.0.1:8501 user@server
   # Then visit http://localhost:8501
   ```
3. **Restrict log file permissions**:
   ```bash
   chmod 600 app/logs/sentinel.log
   ```
4. **Backup database regularly**:
   ```bash
   cp sentinel_intel.db sentinel_intel.db.backup
   ```

---

## 📝 Common Tasks

### Add New Threat Detection
```python
# In your threat detection code
source_ip = "192.168.1.100"
threat_type = "Brute Force"
action = "BLOCK"

# 1. Store in database
# (Your code)

# 2. Log the threat
logger.log_threat_detected(threat_type, source_ip, action)

# 3. Print alert (if terminal)
printer.print_threat_alert(threat_type, source_ip, action)
```

### Update Dashboard Metrics
```python
# Dashboards automatically read from database
# Just ensure incidents are stored in sentinel_intel.db

# CLI and Web dashboards both run these queries:
# - SELECT COUNT(*) FROM incidents WHERE timestamp > datetime('now', '-1 hour')
# - SELECT DISTINCT source_ip FROM incidents WHERE timestamp > datetime('now', '-1 hour')
# - SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 20
```

### Send Heartbeat
```python
# Every 30 seconds (or your interval)
threat_count = db.get_incident_count_1h()
blocked_ips = db.get_unique_blocked_ips_1h()

logger.heartbeat(threat_count=threat_count, blocked_ips=blocked_ips)

# Output (GUI mode): [16:45] Monitoring Active - 5 Threats - 3 Blocked IPs
# Output (CLI mode): Checkpoint 10: Threats=5, Blocked_IPs=3
```

---

## Version Info

- **Version**: v2.1.0
- **Status**: Production Ready ✅
- **Python**: 3.9, 3.10, 3.11, 3.12+
- **Last Updated**: January 30, 2026

---

For detailed documentation, see **[ADAPTIVE_REPORTING.md](ADAPTIVE_REPORTING.md)**
