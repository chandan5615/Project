# Sentinel Agent - Comprehensive Project Documentation

**Last Updated:** January 30, 2026  
**Version:** 2.1 (Quiet Logging + Admin Dashboard + Professional Output)  
**Status:** ✅ Production Ready for GitHub  
**Python Compatibility:** 3.9, 3.10, 3.11, 3.12+

## Executive Summary

Sentinel Agent is an autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. It uses CrewAI for orchestration and local Ollama LLM inference to monitor, analyze, and respond to security threats in real-time. The system implements a sophisticated "Sensor-Brain-Action" pipeline that detects attacks, analyzes threats, and executes defensive measures with human oversight.

### Recent Improvements (v2.1)
- ✅ **Quiet Logging**: Console WARNING+, full DEBUG to `/app/logs/sentinel.log` with rotation
- ✅ **SQLite Persistence**: Track incidents, actions, and threat intelligence
- ✅ **Admin Dashboard**: Internal-only FastAPI UI with Basic Auth, WebSocket real-time updates, Plotly charts
- ✅ **Adaptive Reporting System**: Environment-aware UI (GUI/CLI/Docker/systemd modes)
- ✅ **Professional Output**: Clean text-based formatting (no icons/emojis) for enterprise-grade appearance
- ✅ **Test Suite**: Unit tests for data engine, remediation, dashboard, adaptive system (5 passed, 1 skipped)
- ✅ **All v2.0 Fixes**: Type hints, IP validation, JSON parsing, file rotation, comprehensive error handling

## Version 2.0 Improvements & Bug Fixes

### Critical Fixes Implemented

#### 1. Type Hint Compatibility (tasks.py)
**Issue**: Used Python 3.10+ `list[Task]` syntax  
**Fix**: Changed to `List[Task]` from typing module  
**Impact**: Now compatible with Python 3.9+  
**Benefit**: Broader system compatibility

```python
# Before
def create_security_incident_tasks(...) -> list[Task]:

# After
from typing import List
def create_security_incident_tasks(...) -> List[Task]:
```

#### 2. Enhanced IP Validation (sensors/)
**Issue**: Accepted invalid IPs like `192.168.abc.1`  
**Files**: auth_sensor.py, web_sensor.py  
**Fix**: Ensured ALL octets are digits before range check

```python
# Before - BUGGY (filters out non-digits)
all(0 <= int(p) <= 255 for p in parts if p.isdigit())

# After - FIXED (validates all parts)
all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
```

**Impact**: Bulletproof IP validation, prevents bypass attempts

#### 3. Nested JSON Parsing (main.py)
**Issue**: Regex failed on nested JSON objects  
**Original Pattern**: `\{[^{}]*"action_required"[^{}]*\}`  
**Fix**: Implemented brace-counting algorithm

```python
# Before - FRAGILE
json_match = re.search(r'\{[^{}]*"action_required"[^{}]*\}', result_str)

# After - ROBUST
brace_count = 0
json_end = json_start
for i in range(json_start, len(result_str)):
    if result_str[i] == '{':
        brace_count += 1
    elif result_str[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            json_end = i + 1
            break
```

**Impact**: Correctly parses complex agent responses with nested structures

#### 4. File Rotation Detection (sensors/)
**Issue**: Lost logs when logrotate ran  
**Files**: auth_sensor.py, web_sensor.py  
**Fix**: Added inode tracking for file rotation detection

```python
# Added to __init__
self._last_inode = None

# Added to _process_new_lines
current_stat = self.log_path.stat()
current_inode = current_stat.st_ino

if self._last_inode is not None and current_inode != self._last_inode:
    logger.info("Log file rotated. Starting from beginning.")
    self.last_position = 0

self._last_inode = current_inode
```

**Impact**: Seamless handling of log rotation, no logs lost

#### 5. Type Hints Completeness (agents.py)
**Issue**: Missing return type hint on `get_ollama_url()`  
**Fix**: Added `-> str` return type annotation

```python
# Before
def get_ollama_url():

# After
def get_ollama_url() -> str:
```

**Impact**: Better code quality, proper type checking

### Performance & Stability Improvements

- **Error Handling**: More robust exception handling in all critical paths
- **Logging**: Enhanced logging messages for better debugging
- **Validation**: Stricter input validation across all sensors
- **Memory**: More efficient JSON parsing with brace counting
- **Resilience**: Better handling of edge cases (file rotation, invalid input)

### Testing & Quality Assurance

All changes have been:
- ✅ Syntax validated with Pylance
- ✅ Type checked for Python 3.9+ compatibility
- ✅ Logic verified for correctness
- ✅ Integration tested with existing modules
- ✅ Backward compatible with existing code

---

## Project Architecture

### Core Design Pattern: Sensor-Brain-Action Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENSOR LAYER                                 │
│  ┌──────────────┐              ┌──────────────┐               │
│  │ Auth Sensor  │              │ Web Sensor   │               │
│  │ (SSH logs)   │              │ (HTTP logs)  │               │
│  └──────┬───────┘              └──────┬───────┘               │
│         │                              │                        │
│         └──────────┬────────────────────┘                        │
│                    │                                             │
│         ┌──────────▼──────────┐                                  │
│         │  Attack Detector    │                                  │
│         │  (Pattern Matching) │                                  │
│         └──────────┬──────────┘                                  │
└────────────────────┼─────────────────────────────────────────────┘
                     │
┌────────────────────┼─────────────────────────────────────────────┐
│                    │          BRAIN LAYER                        │
│         ┌──────────▼──────────────────────────┐                 │
│         │      AI Crew (CrewAI)                │                 │
│         ├──────────────────────────────────────┤                 │
│         │ 1. Triage Analyst                    │                 │
│         │    - Analyzes log patterns           │                 │
│         │    - Determines severity             │                 │
│         │    - Assesses legitimacy             │                 │
│         ├──────────────────────────────────────┤                 │
│         │ 2. Threat Intelligence Researcher    │                 │
│         │    - Checks IP reputation            │                 │
│         │    - Cross-correlates web logs       │                 │
│         │    - Identifies multi-vector attacks │                 │
│         ├──────────────────────────────────────┤                 │
│         │ 3. Incident Responder                │                 │
│         │    - Creates remediation plans        │                 │
│         │    - Generates firewall rules        │                 │
│         │    - Assesses risk                   │                 │
│         ├──────────────────────────────────────┤                 │
│         │ 4. Enforcer Agent                    │                 │
│         │    - Executes firewall rules         │                 │
│         │    - Verifies actions (resilience)    │                 │
│         │    - Manages processes               │                 │
│         └──────────┬───────────────────────────┘                 │
└────────────────────┼─────────────────────────────────────────────┘
                     │
┌────────────────────┼─────────────────────────────────────────────┐
│                    │          ACTION LAYER                       │
│         ┌──────────▼──────────────────────────┐                 │
│         │    Defense Execution                │                 │
│         │  - Firewall blocking (iptables)     │                 │
│         │  - Process termination              │                 │
│         │  - Permission changes                │                 │
│         │  - Attack logging                   │                 │
│         └────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Attack Types Handled

Sentinel Agent can detect and defend against **14 distinct attack types** across 5 major categories:

### 1. Injection Attacks

#### SQL Injection (SQLi)
**Detection Patterns:**
- `UNION SELECT` statements
- `DROP TABLE` commands
- `INSERT INTO`, `DELETE FROM`, `UPDATE` statements
- SQL comment injection (`--`, `#`, `/*`)
- Boolean-based SQLi (`OR 1=1`, `AND 1=1`)
- Parameter manipulation (`'`, `"`)

**How It Works:**
- Web sensor monitors HTTP requests for SQL patterns
- Detects attempts to manipulate database queries
- Severity: **HIGH**

**Defense Strategy:**
- Immediate: Block IP address, sanitize queries, enable parameterized queries
- Long-term: Input validation, prepared statements, least privilege database access

**Example Detection:**
```
Log: GET /login.php?id=1' OR 1=1--
Attack Type: sql_injection
Severity: high
Action: IP blocked, firewall rule applied
```

#### Command Injection
**Detection Patterns:**
- Shell command execution (`ls`, `cat`, `pwd`, `whoami`)
- Pipe operators (`|`, `||`)
- Backtick execution (`` `command` ``)
- Command substitution (`$(command)`)
- PHP/system functions (`exec()`, `system()`, `passthru()`)
- URL parameters (`cmd=`, `command=`)

**How It Works:**
- Detects attempts to execute OS commands through web applications
- Monitors for command execution patterns in URLs and parameters
- Severity: **CRITICAL**

**Defense Strategy:**
- Immediate: Block IP immediately, kill suspicious processes, review logs
- Long-term: Input sanitization, command whitelisting, execution restrictions

**Example Detection:**
```
Log: GET /api.php?cmd=ls -la /etc
Attack Type: command_injection
Severity: critical
Action: IP blocked, process killed if detected
```

#### Cross-Site Scripting (XSS)

**Stored XSS:**
- `<script>` tags in content
- JavaScript event handlers (`onerror=`, `onload=`, `onclick=`)
- `<iframe>` tags
- `alert()` function calls
- `document.cookie` access

**Reflected XSS:**
- Script injection in URLs
- JavaScript protocol (`javascript:`)
- Reflected in error messages or search results

**How It Works:**
- Detects malicious scripts injected into web pages
- Distinguishes between stored (persistent) and reflected (temporary) XSS
- Severity: **HIGH** (stored), **MEDIUM** (reflected)

**Defense Strategy:**
- Immediate: Block IP, sanitize stored content, remove malicious scripts
- Long-term: Content Security Policy (CSP), output encoding, input validation

**Example Detection:**
```
Log: POST /comment.php body: <script>alert(document.cookie)</script>
Attack Type: xss_stored
Severity: high
Action: IP blocked, content sanitized
```

### 2. Authentication & Session Management Attacks

#### Brute Force Attacks
**Detection Patterns:**
- Multiple "Failed password" entries
- Rapid authentication failures
- Sequential login attempts
- Multiple username attempts

**How It Works:**
- Auth sensor monitors `/var/log/auth.log` for failed login attempts
- Tracks IP addresses with multiple failures
- Severity: **MEDIUM**

**Defense Strategy:**
- Immediate: Block IP, enable account lockout, implement rate limiting
- Long-term: CAPTCHA, two-factor authentication, password policy enforcement

**Example Detection:**
```
Log: Failed password for user admin from 192.168.1.100 port 22
Attack Type: brute_force
Severity: medium
Action: IP blocked after threshold, account lockout enabled
```

#### Credential Stuffing
**Detection Patterns:**
- Multiple failed login attempts with different credentials
- Invalid user/credential combinations
- Patterns matching known credential dumps

**How It Works:**
- Detects systematic attempts using compromised credentials
- Cross-references with threat intelligence
- Severity: **MEDIUM**

**Defense Strategy:**
- Immediate: Block IP, monitor for successful logins
- Long-term: Password breach monitoring, account security alerts

#### Session Hijacking
**Detection Patterns:**
- Session cookie manipulation
- Invalid session tokens
- Session expiration anomalies
- Cookie theft indicators

**How It Works:**
- Monitors for session-related anomalies
- Detects cookie manipulation attempts
- Severity: **HIGH**

**Defense Strategy:**
- Immediate: Invalidate sessions, force re-authentication
- Long-term: Secure session management, HTTP-only cookies, CSRF tokens

### 3. Broken Access Control Attacks

#### IDOR (Insecure Direct Object References)
**Detection Patterns:**
- URL parameter manipulation (`/user/123` → `/user/124`)
- Direct object ID access (`/admin/456`, `/api/789`)
- Unauthorized resource access attempts

**How It Works:**
- Detects attempts to access resources by manipulating IDs
- Monitors for unauthorized object access patterns
- Severity: **MEDIUM**

**Defense Strategy:**
- Immediate: Block IP, review access controls
- Long-term: Implement proper authorization checks, use indirect references

**Example Detection:**
```
Log: GET /api/user/12345 (user only authorized for /api/user/12344)
Attack Type: idor
Severity: medium
Action: Access denied, IP logged
```

#### Directory Traversal
**Detection Patterns:**
- Path traversal sequences (`../`, `..\\`)
- Encoded traversal (`%2e%2e%2f`, `%2e%2e%5c`)
- System file access (`/etc/passwd`, `/etc/shadow`)
- Windows system access (`windows/system32`)

**How It Works:**
- Detects attempts to access files outside web root
- Monitors for directory traversal patterns
- Severity: **HIGH**

**Defense Strategy:**
- Immediate: Block IP, review file access controls, restrict permissions
- Long-term: Proper path validation, chroot/containerization, permission restrictions

**Example Detection:**
```
Log: GET /files/../../../etc/passwd
Attack Type: directory_traversal
Severity: high
Action: IP blocked, file access restricted
```

### 4. Client-Side Attacks

#### CSRF (Cross-Site Request Forgery)
**Detection Patterns:**
- Missing or null referer headers
- Missing origin headers
- Cross-site request patterns

**How It Works:**
- Detects requests that may be forged from external sites
- Monitors for missing CSRF protection headers
- Severity: **MEDIUM**

**Defense Strategy:**
- Immediate: Validate requests, check referer/origin
- Long-term: CSRF tokens, SameSite cookies, origin validation

#### Clickjacking
**Detection Patterns:**
- Missing `X-Frame-Options` headers
- Missing `Content-Security-Policy: frame-ancestors`
- Frame embedding vulnerabilities

**How It Works:**
- Detects missing frame protection headers
- Identifies clickjacking vulnerabilities
- Severity: **LOW**

**Defense Strategy:**
- Immediate: Add frame protection headers
- Long-term: Implement CSP frame-ancestors, X-Frame-Options

### 5. Infrastructure & Availability Attacks

#### DoS/DDoS (Denial of Service)
**Detection Patterns:**
- Connection resets
- Timeout patterns
- Excessive request rates
- Resource exhaustion indicators

**How It Works:**
- Monitors for patterns indicating service disruption attempts
- Tracks connection patterns and resource usage
- Severity: **HIGH**

**Defense Strategy:**
- Immediate: Block attacking IPs, enable rate limiting, scale resources
- Long-term: DDoS protection services, CDN distribution, auto-scaling

**Example Detection:**
```
Log: Multiple connection resets from 192.168.1.100
Attack Type: dos
Severity: high
Action: IP blocked, rate limiting enabled
```

#### Man-in-the-Middle (MitM)
**Detection Patterns:**
- SSL/TLS certificate errors
- Invalid certificate warnings
- Certificate validation failures

**How It Works:**
- Detects potential MitM attack indicators
- Monitors for certificate anomalies
- Severity: **HIGH**

**Defense Strategy:**
- Immediate: Investigate certificate issues, verify connections
- Long-term: Certificate pinning, HSTS, secure communication protocols

#### SSRF (Server-Side Request Forgery)
**Detection Patterns:**
- Localhost access attempts (`localhost`, `127.0.0.1`)
- Internal IP access (`0.0.0.0`)
- Dangerous protocols (`file://`, `gopher://`, `dict://`)
- Internal resource access

**How It Works:**
- Detects attempts to force server to access internal resources
- Monitors for SSRF attack patterns
- Severity: **CRITICAL**

**Defense Strategy:**
- Immediate: Block IP immediately, review request handlers, check internal access
- Long-term: URL validation, domain allowlisting, network segmentation

**Example Detection:**
```
Log: GET /api/fetch?url=http://localhost/admin
Attack Type: ssrf
Severity: critical
Action: IP blocked immediately, internal access reviewed
```

## Multi-Vector Detection & Cross-Correlation

### How Cross-Correlation Works

When an IP address is detected attacking SSH (brute force), the Researcher Agent **automatically**:

1. Checks if the same IP appears in web access logs
2. Identifies multi-vector attack patterns
3. Escalates threat level if both vectors are detected
4. Provides comprehensive threat intelligence

**Example Scenario:**
```
1. Auth Sensor detects: Failed password from 192.168.1.100
2. Researcher Agent checks web logs for same IP
3. Finds: SQL injection attempt from 192.168.1.100
4. Result: Multi-vector attack detected - threat escalated to CRITICAL
5. Response: Aggressive blocking and enhanced monitoring
```

## Resilience Loop Mechanism

### How It Works

1. **Execute**: Enforcer Agent executes firewall rule
2. **Verify**: Checks firewall table to confirm rule exists
3. **Retry**: If verification fails, tries alternative commands (up to 3 attempts):
   - Different iptables syntax
   - Alternative insertion methods
   - Fallback to ufw
4. **Report**: Provides final status with verification details

**Example Flow:**
```
Attempt 1: iptables -A INPUT -s 192.168.1.100 -j DROP
Verification: FAILED (rule not found)
Attempt 2: iptables -I INPUT 1 -s 192.168.1.100 -j DROP
Verification: SUCCESS (rule confirmed)
Status: Mitigated
```

## Attack Logging & Recording System

### What Gets Recorded

Every attack is automatically logged with:

- **Timestamp**: Date and time of detection
- **Attack Type**: Specific attack category
- **IP Address**: Source of the attack
- **Severity**: Critical, High, Medium, or Low
- **Description**: Human-readable attack description
- **Source**: Auth log or Web log
- **Log Line**: Original log entry
- **Actions Taken**: All defensive actions with success/failure status

### Attack Record Structure

```json
{
  "id": 1,
  "date": "2024-01-15",
  "time": "14:30:25",
  "timestamp": "2024-01-15T14:30:25.123456",
  "ip_address": "192.168.1.100",
  "attack_type": "sql_injection",
  "severity": "high",
  "description": "SQL Injection attempt detected",
  "source": "web",
  "log_line": "192.168.1.100 - - [15/Jan/2024:14:30:25] \"GET /login.php?id=1' OR 1=1--\" 200",
  "actions_taken": [
    {
      "timestamp": "2024-01-15T14:30:26.123456",
      "action_type": "firewall_block",
      "details": "Firewall rule: iptables -A INPUT -s 192.168.1.100 -j DROP",
      "success": true
    }
  ],
  "status": "mitigated"
}
```

## Key Features

### 1. Real-Time Monitoring
- Continuous log file monitoring using watchdog library
- Instant attack detection (< 1 second response time)
- Low latency analysis and response
- **v2.0**: Automatic log rotation detection with inode tracking

### 2. AI-Powered Analysis
- Multi-agent AI crew for comprehensive analysis (4 specialized agents)
- Context-aware threat assessment from multiple data sources
- Intelligent decision making with explanations
- Local LLM inference with Ollama (no cloud dependencies)
- Supports custom models via Ollama

### 3. Autonomous Defense
- Automatic IP blocking via iptables/ufw
- Process termination for suspicious activity
- Permission modification for containment
- **v2.0**: Resilience loops with verification (retry up to 3 times)
- **v2.0**: Enhanced error handling and recovery

### 4. Human-in-the-Loop
- Approval required for critical firewall actions
- Double confirmation before IP blocking
- Audit trail for all actions
- Customizable approval workflows

### 5. Comprehensive Logging
- Complete attack history in JSON format
- Action tracking with timestamps
- Report generation and querying
- Command-line interface for records access
- Sortable by IP, attack type, timestamp, severity

### 6. Multi-Vector Protection
- Simultaneous monitoring of multiple log sources (auth + web)
- Cross-correlation analysis across attack vectors
- Multi-vector attack detection and response
- **v2.0**: Bulletproof IP validation for all sources

### 7. Code Quality Improvements (v2.0)
- **Type Safety**: Full type hints compatible with Python 3.9+
- **IP Validation**: Bulletproof validation ensures octets are digits AND 0-255
- **JSON Parsing**: Robust brace-counting algorithm handles nested structures
- **Log Rotation**: Seamless handling with inode tracking
- **Error Handling**: Comprehensive error checking and recovery

## Technical Stack

### Core Components
- **Language**: Python 3.9+ (Type hints fully compatible)
- **Orchestration**: CrewAI v0.100.1 (Multi-agent framework)
- **LLM**: Ollama (Local inference - llama3:8b default on port 11434)
- **Log Monitoring**: Watchdog library with enhanced inode tracking
- **Firewall**: iptables/ufw with command verification
- **Process Management**: systemctl, pkill, kill commands
- **File Permissions**: chmod with recursive support
- **Data Format**: JSON for persistence and interchange

### Key Libraries
```
crewai==0.100.1                 # Multi-agent orchestration
langchain>=0.1.0                # LLM framework
langchain-community>=0.0.20     # Community integrations
watchdog>=3.0.0                 # File system monitoring (with inode tracking)
requests>=2.31.0                # HTTP requests
python-dotenv>=0.19.0           # Environment variable management
```

### System Requirements
- **OS**: Linux (tested on Ubuntu 20.04+, RHEL/CentOS compatible)
- **Python**: 3.9 or higher (v2.0 verified on 3.9+)
- **Ollama**: Running locally on port 11434 with llama3:8b model
- **Privileges**: Root/sudo for firewall rules and process management
- **Disk Space**: ~100MB for base installation, variable for attack records
- **Memory**: 2GB minimum (for Ollama LLM inference)
- **Network**: Local access to Ollama API

## Project Structure

```
Sentinel Agent/
├── main.py                      # Entry point and event loop
├── agents.py                    # AI crew definitions
├── tasks.py                     # Security playbooks
├── view_attacks.py              # Attack records viewer
├── requirements.txt             # Python dependencies
│
├── sensors/
│   ├── __init__.py
│   ├── auth_sensor.py           # SSH log monitoring (with inode tracking)
│   └── web_sensor.py            # Web log monitoring (with inode tracking)
│
├── tools/
│   ├── __init__.py
│   └── tools.py                 # Security tools (IP check, firewall, etc.)
│
├── defense/
│   ├── __init__.py
│   ├── attack_detector.py       # Attack pattern detection (14 types)
│   └── attack_logger.py         # Attack logging system
│
├── Documentation/
│   ├── PROJECT_DOCUMENTATION.md # This file (updated v2.0)
│   ├── CODE_ANALYSIS_REPORT.md  # Code quality analysis
│   ├── FIXES_IMPLEMENTED.md     # Detailed fix documentation
│   ├── VERIFICATION_REPORT.md   # QA verification results
│   ├── ERROR_LOCATIONS.md       # Original error locations
│   ├── DETAILED_ERROR_FIXES.md  # Detailed fix instructions
│   ├── QUICK_FIX_CHECKLIST.md   # Progress tracking
│   ├── README_ANALYSIS.md       # Documentation index
│   └── ANALYSIS_SUMMARY.md      # Visual analysis summary
│
└── attack_records.json          # Attack history database
```

### File Descriptions

| File | Purpose | Last Updated |
|------|---------|--------------|
| main.py | Main orchestrator with event loop | v2.0 ✅ |
| agents.py | CrewAI agent definitions | v2.0 ✅ |
| tasks.py | Task definitions for crew workflow | v2.0 ✅ |
| view_attacks.py | CLI viewer for attack records | v1.0 |
| auth_sensor.py | Auth log sensor with rotation detection | v2.0 ✅ |
| web_sensor.py | Web log sensor with rotation detection | v2.0 ✅ |
| tools.py | Security tool implementations | v1.0 |
| attack_detector.py | Pattern-based attack detection | v1.0 |
| attack_logger.py | JSON-based attack logging | v1.0 |

## Usage Examples

### 1. Basic Setup & Execution

```bash
# Activate virtual environment
source activate_env.sh          # Unix/Linux/macOS
# or
activate_env.bat                # Windows

# Install dependencies
pip install -r requirements.txt

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Start the Sentinel Agent (requires sudo for firewall access)
sudo python main.py
```

### 2. Ollama Configuration (v2.0)

The system now uses **Ollama for local inference** instead of cloud APIs. This provides:
- **Privacy**: No API keys needed, all processing local
- **Cost**: Free operation after Ollama installation
- **Speed**: Fast response times with llama3:8b model
- **Reliability**: No external service dependencies

**Setup Ollama:**
```bash
# macOS / Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download

# Pull the default model
ollama pull llama3:8b

# Verify it's running
ollama serve  # Should start on port 11434
```

**Environment Variables (.env file):**
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT=60
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
ENABLE_FIREWALL=true
DRY_RUN=false
DEBUG=true
```

### 3. Real-Time Monitoring Example

Once started, the system automatically monitors and responds:

```
[2026-01-26 14:32:15] AUTH_SENSOR: Monitoring /var/log/auth.log
[2026-01-26 14:32:15] WEB_SENSOR: Monitoring /var/log/apache2/access.log
[2026-01-26 14:32:20] ⚠️  ATTACK DETECTED: Failed password (192.168.1.100)
[2026-01-26 14:32:21] 🔄 Triage Agent: Analyzing attack pattern...
[2026-01-26 14:32:23] 🔄 Intelligence Agent: Checking IP reputation...
[2026-01-26 14:32:25] 🔄 Response Agent: Generating firewall rule...
[2026-01-26 14:32:27] 🔄 Enforcer Agent: Executing firewall rule...
[2026-01-26 14:32:29] ✅ Remediation: IP blocked in iptables
[2026-01-26 14:32:30] 📊 Attack recorded in attack_records.json
```

### 4. Viewing Attack Records

```bash
# View all attacks
python view_attacks.py

# View attacks by IP
python view_attacks.py --ip 192.168.1.100

# View attacks by type
python view_attacks.py --type "Brute Force"

# Export to CSV
python view_attacks.py --export attacks.csv
```

### 5. Docker Deployment (Production)

```bash
# Build container
docker-compose -f docker-compose.prod.yml build

# Run with Ollama backend
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f sentinel
```

### 6. Testing IP Validation (v2.0)

The improved IP validation now properly validates all octets:

```python
# Examples:
valid_ip("192.168.1.1")           # ✅ True - valid IP
valid_ip("192.168.1.256")         # ❌ False - octet out of range
valid_ip("192.168.abc.1")         # ❌ False - non-numeric octet
valid_ip("192.168.1")             # ❌ False - incomplete IP

# The fix ensures ALL parts are digits AND within 0-255 range
# Before: all(0 <= int(p) <= 255 for p in parts if p.isdigit())  # ❌ Buggy
# After:  all(p.isdigit() and 0 <= int(p) <= 255 for p in parts) # ✅ Fixed
```

### 7. Log Rotation Handling (v2.0)

The sensors now seamlessly handle log rotation via inode tracking:

```bash
# Force log rotation
sudo logrotate -f /etc/logrotate.d/rsyslog

# Console output shows:
# [AUTH_SENSOR] Log rotation detected, resetting position
# [WEB_SENSOR] Log rotation detected, resetting position

# The system automatically:
# 1. Detects inode change (file replacement)
# 2. Resets file position to beginning
# 3. Continues processing without missing logs
```

### 8. Custom Log Paths

```bash
# Edit .env or set environment variables
export AUTH_LOG_PATH=/var/log/secure          # RHEL/CentOS
export WEB_LOG_PATH=/var/log/nginx/access.log # Nginx

# Run with custom paths
sudo python main.py
```

### 9. Production Checklist

- [x] Python 3.9+ environment configured
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] Ollama running with llama3:8b model on port 11434
- [x] Read permissions for log files (auth.log, web logs)
- [x] Sudo/firewall write permissions for iptables/ufw
- [x] Create attack records file: `echo '[]' > attack_records.json`
- [x] Verify Ollama connectivity: `curl http://localhost:11434/api/tags`
- [x] Environment variables configured (.env file)

## Security Considerations

1. **Permissions**: Requires sudo for log access and firewall management
2. **Log Access**: Ensure read permissions on /var/log/auth.log and web server logs
3. **Attack Records**: Contains sensitive information - keep `attack_records.json` secure
4. **Human Oversight**: Critical actions require approval before execution
5. **Audit Trail**: All actions logged for compliance and forensics
6. **Local Inference**: Ollama provides privacy - no external API calls
7. **Firewall Rules**: Validated before execution with dry-run capability

## Limitations & Future Enhancements (v2.0)

### Previous Limitations (Now Fixed)
- ❌ Type hints incompatible with Python 3.9 → **✅ Fixed in v2.0**
- ❌ IP validation bypasses → **✅ Fixed in v2.0**
- ❌ JSON parsing fails on nested structures → **✅ Fixed in v2.0**
- ❌ Lost logs during log rotation → **✅ Fixed in v2.0**
- ❌ Missing type hints in agents → **✅ Fixed in v2.0**

### Current Limitations
- Linux-only (requires iptables and Linux log structure)
- Requires local Ollama installation (not cloud-dependent, but local setup required)
- Limited to SSH and HTTP log-based detection

### Planned Enhancements
- Network packet analysis for non-log-based detection
- Real-time process monitoring and behavioral analysis
- SIEM system integration (Splunk, ELK, etc.)
- Machine learning-based anomaly detection algorithms
- Multi-platform support (Windows with Event Logs)
- Container orchestration monitoring (Kubernetes security events)

## Conclusion

Sentinel Agent provides comprehensive, autonomous security monitoring and response capabilities for Linux systems. It detects 14 different attack types, implements multi-vector correlation, and maintains complete audit trails. The system combines AI-powered analysis with automated defense mechanisms while maintaining human oversight for critical actions.
