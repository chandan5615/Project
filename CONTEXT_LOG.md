# Context Log

This file tracks project changes, what was done, and what remains.

## 2026-02-22
- Fixed critical, medium, and low issues across core services, dashboard, and tooling.
- Cleaned up obsolete files and restored install/setup scripts.
- Made AUTO_INSTALL.sh non-interactive by default and added optional --interactive flag.
- Updated docker-compose host bindings to be configurable and use host-gateway.
- Added streamlit-autorefresh to requirements.
- Updated README documentation links and quick-start instructions.
- **Fixed all .sh files to use Unix LF line endings (was causing "not found" errors on Linux).**
- **Removed UTF-8 BOM from all .sh files (was causing shebang parsing errors).**
- **CRITICAL: Fixed missing `#` character in all shebang lines (!/bin/bash → #!/bin/bash) - was causing wrong interpreter and garbled color output.**
- **✅ SUCCESSFUL DEPLOYMENT: Sentinel Agent v2.2 fully operational on Ubuntu 192.168.31.91**
  - All databases initialized
  - Auth and web sensors active
  - Ollama llama3:8b connected
  - API responding on port 8000
  - Dashboard ready on port 8501
  - Default admin credentials: admin / BqdlN7lwEfbHaP_Zf6-mXg
- **🎯 AI OPTIMIZATION: Changed LLM trigger from HIGH to CRITICAL severity**
  - SQL injection (high) now logs without AI analysis
  - Only command_injection and ssrf (critical) trigger AI Crew
  - Significantly reduces resource usage and LLM API calls
- **🔇 LOGGING OPTIMIZATION: Disabled verbose/debug output**
  - Changed root logger from DEBUG to INFO level
  - Disabled verbose mode in CrewAI Crew and all 4 agents
  - Suppressed LiteLLM debug output with environment variable and suppress_debug_info
  - Cleaner, production-ready log output

## Pending
- User should change default admin password after first login
- Optional: Enable firewall with `sudo ufw enable`