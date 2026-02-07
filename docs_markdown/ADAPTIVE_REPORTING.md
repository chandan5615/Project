# Sentinel Agent - Adaptive Reporting System

## Overview

The Adaptive Reporting System automatically adjusts the Sentinel Agent's behavior based on the deployment environment. This enables seamless operation across different scenarios:

- **GUI Environments** (Desktop/Workstation) → Web Dashboard with metrics
- **CLI Environments** (Terminal/SSH) → Rich terminal UI
- **Docker Containers** → Logging-only mode
- **Systemd Services** → Logging-only mode

All modes persist incident data to SQLite for comprehensive auditing and historical analysis.

## Architecture

### Components

#### 1. **Environment Detector** (`environment_detector.py`)
Detects the deployment environment and capabilities:
- Checks for display servers (X11, Wayland, Windows Terminal)
- Detects Docker containers
- Detects systemd services
- Returns configuration for appropriate UI mode

**Key Functions:**
- `EnvironmentDetector.has_display()` - Checks if graphical output is available
- `EnvironmentDetector.is_docker()` - Checks if running in Docker container
- `EnvironmentDetector.is_systemd()` - Checks if running as systemd service
- `EnvironmentDetector.get_mode()` - Returns mode: "gui", "cli", "docker", or "systemd"
- `EnvironmentDetector.get_config()` - Returns full configuration dictionary

#### 2. **Adaptive Logging** (`logging_adapter.py`)
Provides intelligent logging that respects environment:
- File logging (always on, rotating handler to prevent disk bloat)
- Console output (conditional based on mode)
- Heartbeat messages for GUI mode (minimal terminal output)
- Full detailed logging for CLI mode

**Key Classes:**
- `AdaptiveLogger` - Handles environment-aware logging
- `AdaptivePrinter` - Handles environment-aware printing
- Functions: `create_adaptive_logger()`, `create_adaptive_printer()`

#### 3. **Web Dashboard** (`dashboard/web_dashboard.py`)
Streamlit-based browser interface for GUI environments:
- Security Score (0-100%) with real-time status
- Wall of Shame (blocked IPs with timestamps)
- Incident Feed (recent threats with details)
- Network Health (requests/minute graph)
- Auto-refresh capability

**Features:**
- Binds to 127.0.0.1:8501 (zero-exposure)
- Dark theme with clean UI
- Real-time metrics from SQLite database
- Configurable refresh interval

#### 4. **CLI Dashboard** (`dashboard/cli_dashboard.py`)
Rich terminal UI for headless environments:
- Security Score with progress bar
- Wall of Shame table (recent blocks)
- Incident Alerts table
- Summary statistics
- Live or static update modes

**Features:**
- Colorized output (red, yellow, green status)
- Formatted tables with Rich library
- Heartbeat-based updates
- Works over SSH/remote terminals

#### 5. **Dashboard Controller** (`dashboard_controller.py`)
Manages dashboard lifecycle and configuration:
- Starts appropriate dashboard based on environment
- Manages dashboard processes and threads
- Provides configuration management
- Handles graceful shutdown

**Key Classes:**
- `DashboardController` - Manages dashboard lifecycle
- `DashboardConfig` - Provides default configurations
- Function: `create_dashboard_controller()`

## Usage Guide

### Quick Start

#### 1. Install Dependencies
```bash
# Install new dependencies
pip install -r requirements.txt

# Or install specific packages
pip install streamlit rich pandas
```

#### 2. GUI Mode (Desktop)
```python
from environment_detector import EnvironmentDetector
from dashboard_controller import create_dashboard_controller
from logging_adapter import create_adaptive_logger

# Detect environment
detector = EnvironmentDetector()
config = detector.get_environment_config()

# Setup logging and dashboard
logger = create_adaptive_logger(config)
controller = create_dashboard_controller(config)

# Start dashboard (automatically starts web UI)
controller.start_dashboard()

# Log events normally - output adapts to environment
logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
```

#### 2. CLI Mode (Terminal)
Same code as above - the system automatically detects CLI environment and uses Rich terminal UI instead.

#### 3. Docker/Systemd Mode
Logging-only - dashboards disabled, all output goes to logs/sentinel.log

### Configuration

#### Environment Detection
Modify detection logic in `environment_detector.py`:
```python
# Current detection order:
# 1. Check for display servers (GUI)
# 2. Check for Docker container
# 3. Check for systemd service
# 4. Default to CLI mode
```

#### Logging Configuration
Customize in `logging_adapter.py`:
```python
# File logging: Always enabled
# Console level: WARNING in GUI, DEBUG in CLI/Docker/systemd
# Log file: app/logs/sentinel.log (rotating, 10MB max, 5 backups)

logger = AdaptiveLogger(
    mode="cli",
    log_file="app/logs/sentinel.log",
    console_level=logging.WARNING,
    file_level=logging.DEBUG
)
```

#### Dashboard Configuration
Default settings in `dashboard_controller.py`:
```python
DEFAULTS = {
    "gui": {
        "type": "streamlit",
        "port": 8501,
        "address": "127.0.0.1",
        "refresh_interval": 30,
        "auto_start": True,
        "theme": "dark"
    },
    "cli": {
        "type": "rich",
        "live_mode": False,
        "refresh_interval": 30,
        "auto_start": False,
        "width": 120,
        "height": 40
    }
}
```

## Integration Examples

### Basic Integration into main.py
```python
from environment_detector import EnvironmentDetector
from logging_adapter import create_adaptive_logger, create_adaptive_printer
from dashboard_controller import create_dashboard_controller

class SentinelAgent:
    def __init__(self):
        # Detect environment
        detector = EnvironmentDetector()
        self.config = detector.get_environment_config()
        
        # Setup adaptive components
        self.logger = create_adaptive_logger(self.config)
        self.printer = create_adaptive_printer(self.config)
        self.dashboard = create_dashboard_controller(self.config)
        
        # Start dashboards
        self.dashboard.start_dashboard()
    
    def process_threat(self, threat_type, source_ip, action):
        # Log threat (adapts to environment)
        self.logger.log_threat_detected(threat_type, source_ip, action)
        
        # Print if terminal (suppressed in GUI)
        self.printer.print_threat_alert(threat_type, source_ip, action)
```

### Running in Different Environments

#### Development (GUI - Desktop)
```bash
# Automatically detects display and starts Streamlit dashboard
python main.py
# Output: Dashboard at http://127.0.0.1:8501
# Console: Minimal heartbeat messages only
```

#### Testing (CLI - Terminal/SSH)
```bash
# Automatically detects no display, starts Rich terminal UI
ssh user@remote-server
python main.py
# Output: Rich formatted tables in terminal
# Detailed logs to app/logs/sentinel.log
```

#### Production (Docker)
```bash
# Automatically detects Docker environment
docker run sentinel-agent:latest
# Output: Logs to stdout and file only
# No interactive dashboard
```

#### Deployment (Systemd)
```bash
# Automatically detects systemd service
systemctl start sentinel-agent
# Output: Journalctl entries and file logs
# No dashboard
```

## Database Schema

All modes use the same SQLite database (`sentinel_intel.db`):

### incidents table
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    source_ip TEXT,
    threat_type TEXT,
    details TEXT,
    action TEXT,
    FOREIGN KEY (action) REFERENCES actions(id)
);
```

### actions table
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    action_name TEXT,
    timestamp TEXT,
    details TEXT
);
```

### threat_intel table
```sql
CREATE TABLE threat_intel (
    id INTEGER PRIMARY KEY,
    threat_type TEXT,
    severity TEXT,
    description TEXT,
    mitigation TEXT
);
```

## Logging Output Examples

### GUI Mode Output
```
[16:45] Monitoring Active
[16:45] Monitoring Active - 2 Threats
[16:55] Monitoring Active - 5 Threats - 3 Blocked IPs
```
*File logs: `app/logs/sentinel.log` (detailed)*

### CLI Mode Output
```
============================================================
️  SENTINEL AGENT - CLI DASHBOARD
============================================================

️  SECURITY STATE
Security Score: 78%
████████████████████████░░░░░░░░
Status: CAUTION

 WALL OF SHAME                    INCIDENT FEED
IP: 192.168.1.100                  192.168.1.100 | Brute Force
Threat: Brute Force                Action: BLOCK | 16:45:32
Count: 3
Last: 16:45:32
```

### Docker/Systemd Mode Output
```
(console silent - all output to logs)
```
*File logs: `app/logs/sentinel.log` only*

## Performance Considerations

- **Web Dashboard**: ~50MB memory, 1% CPU (Streamlit overhead)
- **CLI Dashboard**: ~20MB memory, <1% CPU
- **Database**: SQLite rotating backups, max 50MB active + 5×10MB backups
- **Logging**: Rotating handler (10MB per file, 5 backups = 60MB max)

## Troubleshooting

### Dashboard not starting
```
# Check logs
tail -f app/logs/sentinel.log

# Verify environment detection
python -c "from environment_detector import EnvironmentDetector; print(EnvironmentDetector().get_mode())"
```

### Web dashboard not accessible
```
# Check if port 8501 is in use
lsof -i :8501

# Change port in configuration
config = environment_config.copy()
config['dashboard_url'] = 'http://127.0.0.1:8502'
```

### CLI dashboard not showing
```
# Requires no DISPLAY variable
unset DISPLAY
python main.py

# Or force CLI mode
export SENTINEL_MODE=cli
python main.py
```

## Security Notes

1. **Zero-Exposure**: All dashboards bind to 127.0.0.1 (localhost only)
2. **No Authentication Required**: CLI/Web dashboards don't require login (network-isolated)
3. **Log Permissions**: Ensure `app/logs/sentinel.log` has restricted permissions (600)
4. **Database Security**: SQLite file should not be world-readable

## Future Enhancements

- [ ] Remote dashboard access with authentication
- [ ] Grafana integration for advanced visualizations
- [ ] Real-time metrics export (Prometheus format)
- [ ] Mobile-friendly web dashboard
- [ ] TUI mode with Textual library
- [ ] WebSocket live updates for web dashboard

## Related Files

- `environment_detector.py` - Environment detection
- `logging_adapter.py` - Adaptive logging
- `dashboard/web_dashboard.py` - Streamlit web UI
- `dashboard/cli_dashboard.py` - Rich CLI UI
- `dashboard_controller.py` - Dashboard lifecycle management
- `adaptive_reporting_example.py` - Integration example
- `requirements.txt` - Dependencies (streamlit, rich, pandas)
