"""
Sentinel Agent - Brute Force Detection Configuration
Tune sensitivity of brute-force detection to reduce false positives
"""

# BRUTE FORCE DETECTION SETTINGS

# Time window for counting attempts (in seconds)
BRUTE_FORCE_TIME_WINDOW = 300  # 5 minutes (was likely too small before)

# Minimum number of failed attempts to trigger a block
# INCREASED from 3 to 15 to reduce false positives
BRUTE_FORCE_THRESHOLD = 15

# IPs to exclude from brute-force detection (development/admin IPs)
BRUTE_FORCE_WHITELIST = [
    "127.0.0.1",           # localhost
    "::1",                 # localhost IPv6
    "192.168.31.186",      # Your development machine
    "192.168.31.91",       # The server itself
    "localhost",
]

# Patterns that should NOT trigger brute-force detection
# These are normal admin/application activities
EXCLUDE_PATTERNS = [
    "sudo",                # sudo attempts are normal admin activity
    "cron",                # cron jobs are normal
    "systemd",             # system service attempts are normal
    "docker",              # docker/container processes
    "streamlit",           # streamlit dashboard access
    "python",              # python scripts
]

# Logging configuration
LOG_BRUTE_FORCE_EVENTS = True
LOG_EXCLUDED_EVENTS = False  # Set to True to debug

# Blocking behavior
AUTO_BLOCK_ON_THRESHOLD = False  # Requires manual approval (safer)
ALLOW_AUTOMATIC_BLOCKING = False  # Set to True for high-security environments

# Block duration (in seconds)
BLOCK_DURATION = 3600  # 1 hour, then auto-unblock

# Monitoring and reporting
ENABLE_BRUTE_FORCE_MONITORING = True
REPORT_INTERVAL = 300  # Report every 5 minutes
