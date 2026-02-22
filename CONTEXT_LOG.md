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

## Pending
- None noted.