# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1] - 2026-01-30

### Added
- **Quiet Logging Engine**: Console shows WARNING+ only; full DEBUG logs to rotating file (`/app/logs/sentinel.log`)
- **SQLite Data Persistence**: Incidents, actions, and threat intelligence stored in relational database
- **Admin Dashboard (FastAPI)**:
  - HTTP Basic Auth with customizable credentials
  - JSON REST API endpoints (`/api/summary`, `/api/records`, `/api/network`)
  - WebSocket `/ws/summary` for real-time incident updates (5-second polling)
  - Single-page app with Plotly charts (client-side CDN, no server-side rendering)
  - Zero-exposure design (127.0.0.1-only, no public port binding)
  - SSH tunnel scripts for secure remote access (`scripts/tunnel_admin.sh`, `.ps1`)
- **Unit Test Suite**: 5 passing tests covering data engine, remediation workflow, dashboard auth/WebSocket, and view_attacks
- **Docker Support**: Added dashboard service profile to `docker-compose.yml` with network isolation
- **Documentation**: Complete setup guide for dashboard, tunnel scripts, and environment variables

### Changed
- **Output Formatting**: Professional text-based alerts and reports (no emojis/icons)
- **Logging Configuration**: Switched from simple console logging to rotating file handler + WARNING-level console
- **Data Persistence**: Main event loop now inserts incidents and actions into SQLite on alert detection
- **Dashboard Credentials**: Environment-based configuration (defaults: sentinel/sentinel)
- **Requirements**: Added `uvicorn[standard]>=0.20.0` and `pytest>=7.0.0`

### Fixed
- **F-string Syntax Error**: Removed f-string prefix from embedded HTML template to avoid JavaScript brace conflicts
- **WebSocket Token Injection**: Use safe `.replace()` instead of f-string to inject tokens without escaping issues
- **Dashboard Test Compatibility**: Added `pytest.importorskip("fastapi")` to skip dashboard tests gracefully if FastAPI missing

### Documentation
- Updated `README.md` with v2.1 features, Ollama setup, and dashboard instructions
- Updated `PROJECT_DOCUMENTATION.md` with latest improvements and production readiness status
- Added `docs/DASHBOARD_SETUP.md` with deployment, access, and SSH tunnel guidance
- Updated `SETUP_GUIDE_WEB_APPLICATIONS.md` with v2.1 configuration
- Archived legacy documentation to `archive/docs-legacy/` (v2.0 summaries, output examples, etc.)

---

## [2.0] - 2026-01-26

### Added
- **Type Hint Completeness**: 100% type coverage; Python 3.9+ compatibility (changed `list[Task]` → `List[Task]`)
- **Bulletproof IP Validation**: Enhanced sensor validation to reject invalid IPs like `192.168.abc.1`
- **Robust JSON Parsing**: Brace-counting algorithm handles nested JSON structures in agent responses
- **File Rotation Detection**: Inode tracking prevents log loss during logrotate operations
- **Comprehensive Error Handling**: Better exception handling and recovery across all modules
- **Return Type Hints**: Added missing type annotations (e.g., `get_ollama_url() -> str`)

### Changed
- **IP Validation Logic**: All octets now validated as digits before range check (0-255)
- **JSON Extraction**: Replaced simple regex with robust brace-counting parser
- **File Reading**: Added inode tracking and position reset on log rotation

### Fixed
- **tasks.py**: Type hint compatibility (Python 3.9+)
- **sensors/auth_sensor.py**: IP validation bug and log rotation handling
- **sensors/web_sensor.py**: IP validation bug and log rotation handling
- **main.py**: Nested JSON parsing robustness
- **agents.py**: Missing return type hint

### Testing
- Verified syntax with Pylance for all modules
- Type checked for Python 3.9+ compatibility
- Logic verified for all fixes
- Backward compatibility confirmed

---

## [1.0] - 2026-01-15

### Initial Release
- Multi-agent AI SOC analyst using CrewAI
- Real-time authentication log monitoring with Watchdog
- Four specialized AI agents (Triage, Threat Intel, Incident Response, Enforcer)
- Human-in-the-loop approval workflow
- iptables firewall rule execution
- Professional structured JSON communication
- Modular sensor/agent/tool architecture
