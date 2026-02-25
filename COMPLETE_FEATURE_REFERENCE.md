# 🔍 Complete Feature Reference - Sentinel Agent v2.2

**Every Single Feature Documented**

This document provides exhaustive documentation for every feature, module, script, configuration option, and capability in the Sentinel Agent project.

---

## 📑 Table of Contents

1. [Core Python Modules](#core-python-modules)
2. [Installation & Setup Scripts](#installation--setup-scripts)
3. [Testing & Attack Simulation](#testing--attack-simulation)
4. [Dashboard Applications](#dashboard-applications)
5. [Utility Scripts](#utility-scripts)
6. [Configuration Files](#configuration-files)
7. [Environment Variables](#environment-variables)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Database Schema](#database-schema)
10. [Docker Components](#docker-components)
11. [Command-Line Interfaces](#command-line-interfaces)
12. [AI Agents & Tasks](#ai-agents--tasks)
13. [Detection Patterns](#detection-patterns)
14. [Response Actions](#response-actions)
15. [Log File Handling](#log-file-handling)
16. [Security Features](#security-features)
17. [Monitoring & Metrics](#monitoring--metrics)
18. [Data Export & Reports](#data-export--reports)
19. [Firewall Integration](#firewall-integration)
20. [Troubleshooting Tools](#troubleshooting-tools)

---

## 🐍 Core Python Modules

### 1. **main.py** - Primary Application Entry Point

**Purpose:** Main event loop for security monitoring and threat response

**Features:**
- Real-time log file monitoring (auth.log, apache2/access.log)
- Multi-threaded log processing
- Attack pattern detection and classification
- Severity assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Conditional AI analysis (HIGH severity only)
- Automatic incident logging
- Database persistence
- Threat intelligence integration

**Key Classes:**
- `SentinelAgent` - Main orchestrator class

**Key Methods:**
- `__init__(auth_log_path, web_log_path)` - Initialize agent
- `start_monitoring()` - Begin log monitoring
- `process_log_entry(line, source)` - Parse and analyze log lines
- `handle_threat(incident)` - Process detected threats
- `execute_ai_analysis(incident)` - Trigger AI crew
- `log_to_database(incident)` - Persist incident data

**Command-Line Arguments:**
```bash
python3 main.py
  --auth-log PATH        # Auth log path (default: /var/log/auth.log)
  --web-log PATH         # Web log path (default: /var/log/apache2/access.log)
  --db-path PATH         # Database path (default: ./data/sentinel_intel.db)
  --ollama-url URL       # Ollama server URL (default: http://127.0.0.1:11434)
  --model NAME           # LLM model (default: llama3:8b)
  --no-ai                # Disable AI analysis completely
  --verbose              # Enable debug logging
  --daemon               # Run as background daemon
```

**Environment Variables:**
- `AUTH_LOG_PATH` - Override auth log location
- `WEB_LOG_PATH` - Override web log location
- `SENTINEL_DB_PATH` - Override database location
- `OLLAMA_BASE_URL` - Ollama server address
- `OLLAMA_MODEL` - LLM model name

**Exit Codes:**
- `0` - Normal shutdown
- `1` - Configuration error
- `2` - Ollama connection error
- `3` - Database error
- `4` - Permission error

---

### 2. **agents.py** - AI Crew Agent Definitions

**Purpose:** Define specialized AI agents for threat analysis

**Agents:**

#### **Triage Analyst**
- **Role:** Log Analysis Specialist
- **Goal:** Analyze security logs and assess threat severity
- **Backstory:** Expert in parsing logs and identifying attack patterns
- **Tools:**
  - `extract_ip_from_log()` - IP extraction
  - `parse_log_timestamp()` - Timestamp parsing
  - `identify_attack_type()` - Attack classification

#### **Threat Intelligence Researcher**
- **Role:** Cybersecurity Intelligence Analyst
- **Goal:** Research IP reputation and correlate with known threats
- **Backstory:** Maintains threat intelligence database
- **Tools:**
  - `query_threat_database()` - Look up IP reputation
  - `get_geolocation()` - IP geolocation
  - `check_blacklist()` - Cross-reference blocklists

#### **Incident Responder**
- **Role:** Security Operations Center (SOC) Analyst
- **Goal:** Plan and coordinate incident response
- **Backstory:** Experienced in incident handling
- **Tools:**
  - `generate_firewall_rule()` - Create iptables rules
  - `assess_impact()` - Determine attack impact
  - `recommend_action()` - Suggest remediation

#### **Enforcer Agent**
- **Role:** Automated Response System
- **Goal:** Execute firewall rules and blocking actions
- **Backstory:** Automated enforcement system
- **Tools:**
  - `verify_firewall_rule()` - Validate iptables syntax
  - `check_rule_exists()` - Prevent duplicate rules
  - `execute_block()` - Apply firewall rules (dry-run mode)

**Configuration:**
```python
# In agents.py, customize agent behavior
AGENT_VERBOSE = True/False  # Agent output verbosity
AGENT_MEMORY = True/False   # Enable agent memory
AGENT_MAX_ITER = 25         # Maximum iterations per agent
```

---

### 3. **tasks.py** - AI Crew Task Definitions

**Purpose:** Define workflow tasks for AI agents

**Tasks:**

#### **Task 1: Log Analysis**
- **Agent:** Triage Analyst
- **Description:** Parse and analyze security log entry
- **Output:** Severity assessment, attack type, affected resources
- **Expected Output Format:**
  ```json
  {
    "severity": "HIGH|MEDIUM|LOW",
    "attack_type": "SQL_INJECTION|XSS|BRUTE_FORCE|...",
    "source_ip": "x.x.x.x",
    "timestamp": "ISO-8601",
    "raw_log": "original log line"
  }
  ```

#### **Task 2: Threat Intelligence**
- **Agent:** Threat Intel Researcher
- **Description:** Research IP reputation and threat context
- **Output:** IP reputation score, geolocation, known associations
- **Expected Output Format:**
  ```json
  {
    "ip": "x.x.x.x",
    "reputation_score": 0-100,
    "country": "US",
    "city": "San Francisco",
    "known_threats": ["botnet", "scanner"],
    "first_seen": "ISO-8601"
  }
  ```

#### **Task 3: Response Planning**
- **Agent:** Incident Responder
- **Description:** Plan appropriate response actions
- **Output:** Recommended actions, firewall rules, priority
- **Expected Output Format:**
  ```json
  {
    "recommended_action": "BLOCK|MONITOR|ALERT",
    "firewall_rule": "iptables -A INPUT -s x.x.x.x -j DROP",
    "priority": "CRITICAL|HIGH|MEDIUM|LOW",
    "rationale": "Explanation of decision"
  }
  ```

#### **Task 4: Response Execution**
- **Agent:** Enforcer
- **Description:** Validate and prepare firewall commands
- **Output:** Validated command, execution status
- **Expected Output Format:**
  ```json
  {
    "command": "iptables -A INPUT -s x.x.x.x -j DROP",
    "validated": true,
    "dry_run": true,
    "execution_status": "PREPARED|EXECUTED|FAILED"
  }
  ```

**Task Execution Flow:**
```
Log Entry → Task 1 (Triage) → Task 2 (Intel) → Task 3 (Planning) → Task 4 (Enforcement)
          ↓                    ↓                ↓                   ↓
     Severity Assessment   IP Reputation    Action Plan       Firewall Rule
```

---

### 4. **data_engine.py** - Database Management

**Purpose:** SQLite database operations and persistence

**Features:**
- Database initialization
- Incident logging
- Action tracking
- Threat intelligence storage
- Query interface
- Data export

**Key Classes:**
- `DataEngine` - Main database interface

**Methods:**
```python
DataEngine(db_path="/app/data/sentinel_intel.db")
  .init_database()                     # Create tables
  .log_incident(incident_dict)         # Save incident
  .log_action(action_dict)             # Save action
  .update_threat_intel(ip, score)      # Update IP reputation
  .get_incidents(limit, severity)      # Query incidents
  .get_top_attackers(limit)            # Get top offending IPs
  .get_recent_actions(limit)           # Get recent responses
  .export_to_csv(filename)             # Export incidents
  .cleanup_old_data(days)              # Purge old records
```

**Database Tables:**

#### **incidents**
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,            -- ISO-8601 datetime
    source_ip TEXT NOT NULL,            -- Attacker IP
    attack_type TEXT NOT NULL,          -- SQL_INJECTION, XSS, etc.
    severity TEXT NOT NULL,             -- LOW, MEDIUM, HIGH, CRITICAL
    raw_log TEXT,                       -- Original log line
    threat_type TEXT,                   -- Classification
    action TEXT,                        -- Response taken
    details TEXT                        -- JSON details
);
CREATE INDEX idx_timestamp ON incidents(timestamp);
CREATE INDEX idx_source_ip ON incidents(source_ip);
CREATE INDEX idx_severity ON incidents(severity);
```

#### **actions**
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER,                -- Foreign key to incidents
    action_type TEXT NOT NULL,          -- firewall_block, alert, etc.
    details TEXT,                       -- Action details
    success INTEGER,                    -- 1=success, 0=fail
    timestamp TEXT NOT NULL,            -- Execution time
    FOREIGN KEY (incident_id) REFERENCES incidents(id)
);
CREATE INDEX idx_incident_id ON actions(incident_id);
CREATE INDEX idx_action_timestamp ON actions(timestamp);
```

#### **threat_intel**
```sql
CREATE TABLE threat_intel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,            -- IP address
    reputation_score INTEGER DEFAULT 0, -- 0-100 (lower=worse)
    details TEXT,                       -- JSON metadata
    last_checked TEXT                   -- Last lookup time
);
CREATE INDEX idx_ip ON threat_intel(ip);
CREATE INDEX idx_reputation ON threat_intel(reputation_score);
```

**Configuration:**
```bash
# Environment Variables
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data
DB_BACKUP_ENABLED=true
DB_BACKUP_INTERVAL=86400  # seconds (daily)
DB_RETENTION_DAYS=90      # Keep 90 days of data
```

---

### 5. **security_manager.py** - Encryption & Authentication

**Purpose:** Password hashing, encryption, and secret management

**Features:**
- Password hashing (PBKDF2-HMAC-SHA256)
- Secret key management
- Environment variable encryption
- Credential storage

**Key Classes:**
- `SecurityManager` - Main security interface

**Methods:**
```python
SecurityManager(secrets_dir="/app/data/secrets")
  .hash_password(password)             # Hash password securely
  .verify_password(password, hash)     # Verify password
  .encrypt_data(plaintext)             # Encrypt data
  .decrypt_data(ciphertext)            # Decrypt data
  .generate_secret_key()               # Generate encryption key
  .store_credential(key, value)        # Store encrypted credential
  .retrieve_credential(key)            # Retrieve credential
```

**Security Settings:**
```python
# In security_manager.py
HASH_ITERATIONS = 100000       # PBKDF2 iterations
KEY_SIZE = 32                  # Encryption key bytes
SALT_SIZE = 16                 # Password salt bytes
```

**Stored Secrets:**
- `Master encryption key`: `.master.key` (600 permissions)
- `API credentials`: Encrypted in database
- `Dashboard password`: Hashed with salt

**Usage Example:**
```python
from security_manager import SecurityManager

sm = SecurityManager()

# Hash password
hashed = sm.hash_password("sentinel")

# Verify password
if sm.verify_password("sentinel", hashed):
    print("✅ Password correct")

# Encrypt sensitive data
encrypted = sm.encrypt_data("api_key_12345")
decrypted = sm.decrypt_data(encrypted)
```

---

### 6. **auth.py** - HTTP Authentication

**Purpose:** Basic authentication for API and dashboard

**Features:**
- HTTP Basic Auth
- Credential verification
- Session management
- Role-based access (future)

**Key Functions:**
```python
authenticate_user(username, password)  # Verify credentials
get_current_user(credentials)          # Extract user from header
create_access_token(data)              # Generate token (future)
verify_token(token)                    # Validate token (future)
```

**Default Credentials:**
```bash
Username: sentinel
Password: sentinel
```

**Change Credentials:**
```bash
# In docker-compose.yml or .env
SENTINEL_ADMIN_USER=newuser
SENTINEL_ADMIN_PASS=newpassword
```

---

### 7. **threat_intelligence.py** - IP Reputation & Intel

**Purpose:** Threat intelligence lookup and correlation

**Features:**
- IP reputation scoring
- Geolocation lookup
- Blacklist checking
- Historical tracking

**Key Classes:**
- `ThreatIntelligence` - Main intel interface

**Methods:**
```python
ThreatIntelligence(db_engine)
  .lookup_ip(ip)                       # Get IP reputation
  .update_reputation(ip, score)        # Update score
  .get_geolocation(ip)                 # Get location
  .check_blacklist(ip)                 # Check if blacklisted
  .add_to_blacklist(ip, reason)        # Blacklist IP
  .remove_from_blacklist(ip)           # Whitelist IP
  .get_historical_data(ip)             # Get IP history
```

**Reputation Scoring:**
```
Score Range:
  0-20:   CRITICAL (known attacker, botnet)
  21-40:  HIGH (suspicious, many attacks)
  41-60:  MEDIUM (some attacks)
  61-80:  LOW (rare attacks)
  81-100: CLEAN (no attacks)
```

**Data Sources:**
- Internal incident database
- User submissions
- (Future: External threat feeds)

---

### 8. **anomaly_scorer.py** - Anomaly Detection

**Purpose:** Statistical anomaly detection in traffic patterns

**Features:**
- Baseline traffic modeling
- Deviation detection
- Time-series analysis
- Threshold alerting

**Key Classes:**
- `AnomalyScorer` - Main anomaly detector

**Methods:**
```python
AnomalyScorer()
  .update_baseline(metric, value)      # Update normal baseline
  .calculate_score(metric, value)      # Get anomaly score
  .is_anomalous(metric, value)         # Boolean check
  .get_threshold(metric)               # Get alert threshold
  .set_threshold(metric, threshold)    # Set custom threshold
```

**Detected Anomalies:**
- Sudden traffic spikes
- Unusual request rates
- Geographic anomalies
- Time-of-day deviations
- User-agent changes

**Configuration:**
```python
# In anomaly_scorer.py
BASELINE_WINDOW = 3600        # 1 hour baseline
ANOMALY_THRESHOLD = 3.0       # 3 standard deviations
MIN_SAMPLES = 100             # Minimum data points
```

---

### 9. **sentinel_api.py** - REST API Server

**Purpose:** FastAPI REST API for programmatic access

**Features:**
- RESTful endpoints
- JSON responses
- Authentication
- CORS support
- Rate limiting

**API Endpoints:**

#### **Health & Status**
```http
GET /api/health
Response: {"status": "healthy", "uptime": 12345, "version": "2.2"}

GET /api/status
Response: {"agents_active": 4, "incidents_today": 42, "blocked_ips": 15}
```

#### **Incidents**
```http
GET /api/incidents?limit=50&severity=HIGH&since=2024-01-01T00:00:00Z
Response: [{"id": 1, "timestamp": "2024-01-01T12:00:00Z", ...}, ...]

GET /api/incidents/{incident_id}
Response: {"id": 1, "source_ip": "1.2.3.4", ...}

POST /api/incidents
Body: {"source_ip": "1.2.3.4", "attack_type": "SQL_INJECTION", ...}
Response: {"id": 42, "created": true}
```

#### **IP Management**
```http
GET /api/ips/blocked
Response: [{"ip": "1.2.3.4", "blocked_at": "2024-01-01T12:00:00Z", ...}, ...]

POST /api/ips/block
Body: {"ip": "1.2.3.4", "reason": "Brute force attack"}
Response: {"success": true, "rule_id": 123}

DELETE /api/ips/block/{ip}
Response: {"success": true, "unblocked": "1.2.3.4"}

GET /api/ips/reputation/{ip}
Response: {"ip": "1.2.3.4", "score": 25, "details": {...}}
```

#### **Actions**
```http
GET /api/actions?limit=20
Response: [{"id": 1, "action_type": "firewall_block", ...}, ...]

GET /api/actions/{action_id}
Response: {"id": 1, "incident_id": 42, "success": true, ...}
```

#### **Statistics**
```http
GET /api/stats/summary
Response: {
  "total_incidents": 1234,
  "incidents_today": 42,
  "blocked_ips": 15,
  "top_attack_types": [...]
}

GET /api/stats/timeline?interval=hour&duration=24
Response: {"data": [[timestamp, count], ...]}

GET /api/stats/attackers?limit=10
Response: [{"ip": "1.2.3.4", "attack_count": 25, ...}, ...]
```

#### **Export**
```http
GET /api/export/incidents?format=csv&since=2024-01-01
Response: CSV file download

GET /api/export/threat-intel?format=json
Response: JSON file download
```

**Authentication:**
```bash
# All endpoints require HTTP Basic Auth
curl -u sentinel:sentinel http://localhost:8000/api/health
```

**Rate Limiting:**
```
Default: 100 requests/minute per IP
Authenticated: 1000 requests/minute
```

---

### 10. **sentinel_auto.py** - Automated Deployment

**Purpose:** Automated installation and configuration

**Features:**
- Dependency installation
- Docker setup
- Database initialization
- Service configuration
- Health checks

**Usage:**
```bash
python3 sentinel_auto.py
  --install              # Full installation
  --configure            # Configure only
  --verify               # Verify installation
  --uninstall            # Remove system
```

---

### 11. **dashboard_controller.py** - Dashboard Management

**Purpose:** Control panel for dashboard services

**Features:**
- Start/stop dashboards
- Service monitoring
- Configuration management
- Log aggregation

**Methods:**
```python
DashboardController()
  .start_web_dashboard()
  .start_cli_dashboard()
  .stop_all()
  .get_status()
  .configure(settings)
```

---

### 12. **metrics.py** - Performance Metrics

**Purpose:** Collect and expose performance metrics

**Features:**
- Response time tracking
- Throughput measurement
- Resource usage monitoring
- Prometheus-compatible metrics

**Metrics Collected:**
```
sentinel_incidents_total{severity="HIGH"}
sentinel_incidents_total{severity="MEDIUM"}
sentinel_incidents_total{severity="LOW"}
sentinel_response_time_seconds{action="block"}
sentinel_ai_analysis_duration_seconds
sentinel_database_operations_total{operation="insert"}
sentinel_blocked_ips_total
sentinel_false_positives_total
```

**Endpoints:**
```http
GET /metrics
Response: Prometheus-format metrics
```

---

### 13. **output_formatter.py** - Output Formatting

**Purpose:** Format output for various display formats

**Features:**
- JSON formatting
- Table formatting
- Color-coded output
- Rich text support

**Functions:**
```python
format_json(data, indent=2)
format_table(data, headers)
format_colored(text, color)
format_severity(severity)
format_timestamp(timestamp)
```

---

### 14. **logging_adapter.py** - Logging Framework

**Purpose:** Structured logging with context

**Features:**
- Structured JSON logs
- Context injection
- Log level management
- File rotation

**Configuration:**
```python
LOG_LEVEL = "INFO"       # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "json"      # json, text
LOG_FILE = "/app/logs/sentinel.log"
LOG_MAX_SIZE = 100MB     # Rotate at 100MB
LOG_BACKUP_COUNT = 10    # Keep 10 old files
```

---

### 15. **list_manager.py** - Blacklist/Whitelist Management

**Purpose:** Manage IP blacklists and whitelists

**Features:**
- Blacklist management
- Whitelist management
- Import/export lists
- Rule verification

**Methods:**
```python
ListManager()
  .add_whitelist(ip)
  .remove_whitelist(ip)
  .is_whitelisted(ip)
  .add_blacklist(ip, reason)
  .remove_blacklist(ip)
  .is_blacklisted(ip)
  .export_list(filename, list_type)
  .import_list(filename, list_type)
```

---

### 16. **environment_detector.py** - Environment Detection

**Purpose:** Detect runtime environment (Docker, host, cloud)

**Features:**
- Docker detection
- Cloud provider detection
- Resource availability check
- Configuration adaptation

**Functions:**
```python
is_docker()                    # Returns True if in Docker
get_cloud_provider()           # Returns 'aws', 'gcp', 'azure', None
get_available_memory()         # Returns available RAM
should_use_ai()                # Returns True if resources sufficient
```

---

### 17. **password_manager.py** - Password Utilities

**Purpose:** Password generation and management

**Features:**
- Secure password generation
- Password strength validation
- Password history
- Expiration tracking

**Functions:**
```python
generate_password(length=16)         # Generate secure password
validate_strength(password)          # Check password strength
hash_password(password)              # Hash with salt
verify_password(password, hash)      # Verify password
```

---

### 18. **validate_system.py** - System Validation

**Purpose:** Validate system configuration and dependencies

**Features:**
- Dependency checking
- Configuration validation
- Permission verification
- Connectivity testing

**Usage:**
```bash
python3 validate_system.py
  --check-all            # Run all checks
  --check-deps           # Check dependencies only
  --check-config         # Check configuration only
  --check-perms          # Check permissions only
  --fix                  # Attempt to fix issues
```

---

### 19. **verify_sentinel_setup.py** - Setup Verification

**Purpose:** Verify Sentinel installation

**Features:**
- Component verification
- Service health checks
- Database connectivity
- API testing

**Checks:**
- ✓ Docker running
- ✓ Containers healthyOllama accessible
- ✓ Database initialized
- ✓ API responding
- ✓ Dashboard accessible
- ✓ Log files readable

---

### 20. **init_database.py** - Database Initialization

**Purpose:** Initialize database schema

**Features:**
- Create tables
- Create indexes
- Seed initial data
- Migration support

**Usage:**
```bash
python3 init_database.py
  --fresh                # Drop and recreate
  --migrate              # Run migrations
  --seed                 # Seed with test data
```

---

### 21. **clear_database.py** - Database Cleanup Utility

**Purpose:** Clean and maintain database

**Features:**
- Clear all data
- Clear old incidents
- Clear specific IPs
- Vacuum database

**Usage:**
```bash
python3 clear_database.py
  --all                  # Clear all data
  --incidents            # Clear incidents only
  --threat-intel         # Clear threat intel only
  --ip IP_ADDRESS        # Clear specific IP
  --older-than DAYS      # Clear data older than N days
  --list                 # List top IPs
  --dry-run              # Show what would be deleted
```

---

### 22. **view_attacks.py** - Attack Viewer

**Purpose:** View and analyze stored attacks

**Features:**
- List recent attacks
- Filter by IP/type/severity
- Export to CSV
- Statistics summary

**Usage:**
```bash
python3 view_attacks.py
  --limit 50             # Show last 50 attacks
  --severity HIGH        # Filter by severity
  --ip 1.2.3.4           # Filter by IP
  --since "2024-01-01"   # Filter by date
  --export attacks.csv   # Export to CSV
  --stats                # Show statistics
```

---

## 🔧 Installation & Setup Scripts

### 1. **AUTO_INSTALL.sh** - One-Command Installer (Linux)

**Purpose:** Fully automated installation for Ubuntu/Debian

**What it does:**
1. Detect OS and architecture
2. Install Docker & Docker Compose
3. Install Ollama
4. Pull llama3:8b model
5. Create project directories
6. Initialize database
7. Start containers
8. Configure firewall
9. Run health checks

**Usage:**
```bash
# Download and run
wget -O- https://raw.githubusercontent.com/chandan5615/Project/main/AUTO_INSTALL.sh | sudo bash

# Or local
chmod +x AUTO_INSTALL.sh
sudo ./AUTO_INSTALL.sh
```

**Options:**
```bash
AUTO_INSTALL.sh
  --skip-docker          # Skip Docker installation
  --skip-ollama          # Skip Ollama installation
  --no-firewall          # Don't configure firewall
  --dev-mode             # Developer mode (less strict)
```

**Logs:**
```
/var/log/sentinel_install.log
```

---

### 2. **AUTO_INSTALL_WINDOWS.bat** - Windows Installer

**Purpose:** Automated installation for Windows + WSL2

**Requirements:**
- Windows 10/11 with WSL2
- Ubuntu in WSL

**Usage:**
```batch
auto_install_windows.bat
```

**What it does:**
1. Check WSL2 installation
2. Install Ubuntu if needed
3. Run Linux installer in WSL
4. Configure Windows firewall
5. Create desktop shortcuts

---

### 3. **install.sh** - Manual Installation Script

**Purpose:** Step-by-step manual installation

**Usage:**
```bash
chmod +x install.sh
./install.sh
```

**Prompts:**
- Server IP address
- Dashboard password
- Data directory
- Log file paths

---

### 4. **setup.sh** - Initial Setup Wizard

**Purpose:** Interactive configuration wizard

**Features:**
- Database setup
- User creation
- Service configuration
- Integration testing

**Usage:**
```bash
./setup.sh
```

---

### 5. **configure_ollama_network.sh** - Ollama Network Fix

**Purpose:** Fix Ollama connection issues

**What it does:**
1. Stop Ollama service
2. Configure systemd override
3. Set OLLAMA_HOST=0.0.0.0:11434
4. Restart Ollama
5. Verify connectivity

**Usage:**
```bash
chmod +x configure_ollama_network.sh
sudo ./configure_ollama_network.sh
```

---

### 6. **sentinel_setup.sh** - Production Setup

**Purpose:** Production-grade setup with hardening

**Features:**
- Security hardening
- SSL certificate generation
- Backup configuration
- Monitoring setup

---

### 7. **verify_setup.sh** - Setup Verification

**Purpose:** Verify complete installation

**Checks:**
- Docker daemon
- Containers running
- Database accessible
- API responding
- Dashboard reachable
- Ollama functional

**Usage:**
```bash
./verify_setup.sh
```

---

## 🧪 Testing & Attack Simulation

### 1. **test_web_attacks.py** - Web Attack Simulator

**Purpose:** Generate realistic web attacks for testing

**Attack Types:**
- SQL Injection (12 patterns)
- XSS (8 patterns)
- Path Traversal (6 patterns)
- Command Injection (5 patterns)
- Directory Scanning (4 patterns)

**Usage:**
```bash
python3 test_web_attacks.py
  --target http://10.76.250.89:8000     # Target URL
  --intensity low|medium|high|extreme   # Attack intensity
  --attack-type sql|xss|path|all       # Specific attack type
  --delay 1.0                          # Delay between requests (seconds)
  --count 50                           # Number of attacks
  --verbose                            # Detailed output
```

**Attack Patterns:**

SQL Injection:
```
' OR '1'='1
admin' --
1'; DROP TABLE users--
' UNION SELECT NULL--
```

XSS:
```
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
```

Path Traversal:
```
../../etc/passwd
....//....//etc/passwd
%2e%2e%2f%2e%2e%2fetc%2fpasswd
```

---

### 2. **test_client_attacks.py** - Client-Side Attack Tests

**Purpose:** Test client-side attacks (XSS, CSRF, etc.)

**Attack Types:**
- Stored XSS (6 payloads)
- Reflected XSS (4 payloads)
- DOM-based XSS (3 payloads)
- CSRF (4 tests)
- Session Hijacking (2 tests)
- Cookie Tampering (2 tests)
- JavaScript Execution (3 tests)

**Usage:**
```bash
python3 test_client_attacks.py
  --target http://10.76.250.89:8000
  --test-type stored-xss|reflected-xss|csrf|all
  --browser chrome|firefox            # Browser automation
```

---

### 3. **test_auth.py** - Authentication Attack Tests

**Purpose:** Test authentication and authorization

**Tests:**
- Brute force login
- Credential stuffing
- Session fixation
- Password reset abuse
- Weak password detection

**Usage:**
```bash
python3 test_auth.py
  --target http://10.76.250.89:8000
  --wordlist passwords.txt
  --username admin
  --threads 10
```

---

### 4. **test_security.py** - Security Feature Tests

**Purpose:** Test all security features

**Tests:**
- Firewall blocking
- Rate limiting
- Input validation
- Output encoding
- CSRF protection
- Session management

---

### 5. **test_attacks.py** - Comprehensive Attack Suite

**Purpose:** Master test suite for all attack types

**Features:**
- Sequential attack execution
- Parallel attack generation
- Result aggregation
- Detailed reporting

**Usage:**
```bash
python3 test_attacks.py
  --scenario basic|medium|advanced|extreme
  --duration 300                      # Test duration (seconds)
  --report attacks_report.html        # Generate HTML report
```

---

### 6. **continuous_attacks.py** - Continuous Attack Generator

**Purpose:** Generate sustained attack traffic

**Features:**
- Configurable attack rate
- Mixed attack types
- Randomized patterns
- Long-duration support

**Usage:**
```bash
python3 continuous_attacks.py
  --interval 5                        # Attack every 5 seconds
  --duration 60                       # Run for 60 minutes
  --burst 3                           # 3 attacks per burst
  --randomize                         # Randomize attack types
  --target http://10.76.250.89:8000
```

**Attack Scenarios:**
- `light`: 5-10 attacks/minute
- `medium`: 20-50 attacks/minute
- `heavy`: 100-500 attacks/minute
- `extreme`: 1000+ attacks/minute

---

### 7. **LAUNCH_ATTACKS.bat** - Windows Attack Launcher

**Purpose:** Launch attacks from Windows

**Usage:**
```batch
LAUNCH_ATTACKS.bat
```

---

## 📊 Dashboard Applications

### 1. **web_dashboard.py** - Streamlit Web Dashboard

**Purpose:** Full-featured web-based security dashboard

**Features:**

#### **Tab 1: Wall of Shame**
- Blocked IPs table
- Block count per IP
- Last seen timestamps
- Threat types

#### **Tab 2: Incident Feed**
- Real-time incident stream
- Severity indicators
- Source IP details
- Attack types
- Actions taken

#### **Tab 3: Network Health**
- Last hour activity graph
- Incidents per minute
- Total incidents
- Average rate

#### **Tab 4: Log Viewer** (NEW)
- Log file selector
  - Auth log
  - Apache access log
  - Custom path
- Line count selector (10-500)
- Search/filter
- Download logs
- Syntax highlighting

#### **Tab 5: Apache Traffic** (NEW)
- Total requests
- Unique IPs
- Error count & rate
- HTTP status codes
- HTTP method distribution
- Top IPs
- Top URLs
- User agent stats
- Error request details

#### **Tab 6: IP Blocking** (NEW)
- Firewall type selector (UFW/iptables)
- Block IP interface
- Unblock IP interface
- Currently blocked IPs list
- IP validation

#### **Tab 7: Attack Patterns** (NEW)
- Attack type distribution (7 days)
- Hourly attack timeline (24h)
- Bar charts
- Line graphs

#### **Tab 8: Export Reports** (NEW)
- Export incidents to CSV
- Export threat intel to JSON
- Time range selection
- Database statistics

#### **Tab 9: System Info** (NEW)
- System uptime
- Load average
- Disk usage
- Resource monitoring

**Configuration:**
```bash
# Environment Variables
DASHBOARD_PORT=8501
DASHBOARD_BIND_IP=0.0.0.0
DASHBOARD_USER=sentinel
DASHBOARD_PASS=sentinel
DASHBOARD_THEME=dark
DASHBOARD_REFRESH=30         # Auto-refresh interval (seconds)
```

**Auto-Refresh:**
- Configurable in sidebar (5-60 seconds)
- Manual refresh button
- Real-time updates

**Keyboard Shortcuts:**
```
R - Refresh
L - Log viewer
M - Metrics
I - IP management
S - Settings
```

---

### 2. **cli_dashboard.py** - Terminal Dashboard

**Purpose:** Rich terminal-based dashboard

**Features:**
- Auto-refresh (5 seconds)
- Color-coded severity
- Real-time updates
- Keyboard controls
- Low bandwidth

**Controls:**
```
q - Quit
r - Refresh
f - Filter
s - Sort
c - Clear screen
```

---

## 🛠️ Utility Scripts

### 1. **check_crewai_api.py** - CrewAI API Tester

**Purpose:** Test CrewAI functionality

**Usage:**
```bash
python3 check_crewai_api.py
```

**Tests:**
- Agent creation
- Task execution
- Crew kickoff
- Output parsing

---

### 2. **check_crew_instance.py** - Crew Instance Validator

**Purpose:** Validate crew configuration

---

### 3. **fix_ollama_connection.sh** - Ollama Fix Script

**Purpose:** Fix Ollama connection issues

**Usage:**
```bash
./fix_ollama_connection.sh
```

---

### 4. **quick_fix_ollama.sh** - Quick Ollama Fix

**Purpose:** Fast fix for common Ollama issues

---

### 5. **fix_logs.sh** - Log File Permissions Fix

**Purpose:** Fix log file access issues

```bash
sudo ./fix_logs.sh
```

---

### 6. **rebuild_no_cache.bat** - Docker Rebuild

**Purpose:** Rebuild Docker images without cache

---

### 7. **deploy_fixes.ps1** - Deployment Fixes

**Purpose:** Fix deployment issues

---

## ⚙️ Configuration Files

### 1. **docker-compose.yml** - Docker Services

**Services:**

#### **sentinel-agent**
```yaml
services:
  sentinel-agent:
    build: .
    container_name: sentinel-agent
    restart: unless-stopped
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - OLLAMA_MODEL=llama3:8b
      - AUTH_LOG_PATH=/var/log/auth.log
      - WEB_LOG_PATH=/var/log/apache2/access.log
      - SENTINEL_DB_PATH=/app/data/sentinel_intel.db
      - DASHBOARD_PORT=8501
    ports:
      - "${DASHBOARD_BIND_IP:-0.0.0.0}:8501:8501"
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - /var/log:/var/log:ro
    networks:
      - sentinel-network
```

**Environment Variables:**
- `OLLAMA_BASE_URL` - Ollama server URL
- `OLLAMA_MODEL` - LLM model name
- `AUTH_LOG_PATH` - Auth log location
- `WEB_LOG_PATH` - Web log location
- `SENTINEL_DB_PATH` - Database path
- `DASHBOARD_BIND_IP` - Dashboard bind IP

**Volumes:**
- `./data` - Persistent database and intel
- `./logs` - Application logs
- `/var/log` - System logs (read-only)

**Networks:**
- `sentinel-network` - Internal bridge network

---

### 2. **Dockerfile** - Container Image

**Base Image:** `python:3.10-slim`

**Installed Packages:**
- Python 3.10+
- System utilities
- Security tools

**Exposed Ports:**
- 8000 - API
- 8501 - Dashboard

**Entry Point:** `docker-entrypoint.sh`

---

### 3. **.env** - Environment Configuration

**Template:**
```bash
# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3:8b

# Logs
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# Database
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data

# Dashboard
DASHBOARD_PORT=8501
DASHBOARD_BIND_IP=0.0.0.0
DASHBOARD_USER=sentinel
DASHBOARD_PASS=sentinel

# Security
ENABLE_AI_ANALYSIS=true
AI_THRESHOLD=HIGH
BLOCK_AUTO=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

### 4. **requirements.txt** - Python Dependencies

```
# AI & ML
crewai>=0.100.1
langchain>=0.1.0
ollama>=0.1.0

# Web Framework
fastapi>=0.115.8
uvicorn>=0.24.0
streamlit>=1.28.0

# Data & Database
pandas>=2.0.0
sqlite3
sqlalchemy>=2.0.0

# Monitoring
watchdog>=4.0.0
rich>=13.0.0
plotly>=5.17.0

# Utilities
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

### 5. **nginx.conf** - Nginx Configuration

**Purpose:** Reverse proxy configuration (optional)

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

### 6. **docker-compose.prod.yml** - Production Config

**Purpose:** Production-optimized configuration

**Differences:**
- Resource limits
- Health checks
- Restart policies
- Logging drivers
- SSL/TLS support

---

## 🔐 Environment Variables Complete Reference

### Core Application

```bash
# Ollama LLM
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT=30000
OLLAMA_NUM_CTX=4096
OLLAMA_TEMPERATURE=0.7

# Log Files
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
CUSTOM_LOG_PATH=/path/to/custom.log

# Database
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data
DB_BACKUP_ENABLED=true
DB_BACKUP_DIR=/app/data/backups
DB_RETENTION_DAYS=90

# Dashboard
DASHBOARD_PORT=8501
DASHBOARD_BIND_IP=0.0.0.0
DASHBOARD_USER=sentinel
DASHBOARD_PASS=sentinel
DASHBOARD_THEME=dark
DASHBOARD_REFRESH=30
CLI_REFRESH_INTERVAL=5

# API
API_PORT=8000
API_HOST=0.0.0.0
API_WORKERS=4
API_TIMEOUT=60
API_MAX_REQUESTS=1000

# Security
SENTINEL_ADMIN_USER=sentinel
SENTINEL_ADMIN_PASS=sentinel
SECRET_KEY=your-secret-key-here
HASH_ITERATIONS=100000
ENABLE_HTTPS=false

# AI Configuration
ENABLE_AI_ANALYSIS=true
AI_THRESHOLD=HIGH
AI_MAX_ITER=25
AI_VERBOSE=false
AI_TIMEOUT=60

# Threat Response
BLOCK_AUTO=true
BLOCK_DURATION=3600
BLACKLIST_ENABLED=true
WHITELIST_ENABLED=true

# Monitoring
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/app/logs/sentinel.log
LOG_MAX_SIZE=104857600
LOG_BACKUP_COUNT=10
METRICS_ENABLED=true
METRICS_PORT=9090

# Email Notifications (Future)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
EMAIL_FROM=sentinel@example.com
EMAIL_TO=admin@example.com
ENABLE_EMAIL_ALERTS=false

# Integrations
ENABLE_SIEM=false
SIEM_ENDPOINT=http://siem-server:514
SYSLOG_ENABLED=false
WEBHOOK_URL=http://slack-webhook-url
```

---

## 🌐 API Endpoints Complete Reference

### Authentication Required
All endpoints except `/api/health` require Basic Auth:
```
Authorization: Basic base64(username:password)
```

### Health & Status

```http
GET /api/health
Response: 200 OK
{
  "status": "healthy",
  "uptime": 12345,
  "version": "2.2",
  "ollama_connected": true,
  "database_connected": true
}

GET /api/status
Response: 200 OK
{
  "agents_active": 4,
  "incidents_today": 42,
  "blocked_ips": 15,
  "ai_analyses_today": 5,
  "total_incidents": 1234
}

GET /api/version
Response: 200 OK
{
  "version": "2.2",
  "build": "2024-02-25",
  "python_version": "3.10.12"
}
```

### Incidents

```http
GET /api/incidents
Query Parameters:
  - limit: int = 50
  - offset: int = 0
  - severity: str = None (HIGH, MEDIUM, LOW)
  - since: ISO-8601 datetime
  - until: ISO-8601 datetime
  - source_ip: str
  - attack_type: str

Response: 200 OK
{
  "total": 1234,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "timestamp": "2024-02-25T12:00:00Z",
      "source_ip": "1.2.3.4",
      "attack_type": "SQL_INJECTION",
      "severity": "HIGH",
      "action": "blocked",
      "details": {...}
    },
    ...
  ]
}

GET /api/incidents/{incident_id}
Response: 200 OK
{
  "id": 1,
  "timestamp": "2024-02-25T12:00:00Z",
  "source_ip": "1.2.3.4",
  "attack_type": "SQL_INJECTION",
  "severity": "HIGH",
  "raw_log": "...",
  "ai_analysis": {...},
  "actions": [...]
}

POST /api/incidents
Body:
{
  "source_ip": "1.2.3.4",
  "attack_type": "SQL_INJECTION",
  "severity": "HIGH",
  "raw_log": "...",
  "details": {...}
}
Response: 201 Created
{
  "id": 42,
  "created": true,
  "timestamp": "2024-02-25T12:00:00Z"
}

DELETE /api/incidents/{incident_id}
Response: 200 OK
{
  "deleted": true,
  "id": 42
}
```

### IP Management

```http
GET /api/ips/blocked
Response: 200 OK
{
  "total": 15,
  "ips": [
    {
      "ip": "1.2.3.4",
      "blocked_at": "2024-02-25T12:00:00Z",
      "reason": "Brute force attack",
      "incident_count": 25,
      "firewall_rule": "iptables -A INPUT -s 1.2.3.4 -j DROP"
    },
    ...
  ]
}

POST /api/ips/block
Body:
{
  "ip": "1.2.3.4",
  "reason": "Manual block",
  "duration": 3600,
  "firewall": "ufw"
}
Response: 200 OK
{
  "success": true,
  "ip": "1.2.3.4",
  "firewall_rule": "ufw deny from 1.2.3.4",
  "expires_at": "2024-02-25T13:00:00Z"
}

DELETE /api/ips/block/{ip}
Response: 200 OK
{
  "success": true,
  "ip": "1.2.3.4",
  "unblocked_at": "2024-02-25T12:00:00Z"
}

GET /api/ips/reputation/{ip}
Response: 200 OK
{
  "ip": "1.2.3.4",
  "reputation_score": 25,
  "category": "malicious",
  "total_attacks": 42,
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-02-25T12:00:00Z",
  "geolocation": {
    "country": "US",
    "city": "San Francisco",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "known_threats": ["botnet", "scanner"]
}

PUT /api/ips/reputation/{ip}
Body:
{
  "reputation_score": 50,
  "details": {...}
}
Response: 200 OK
{
  "updated": true,
  "ip": "1.2.3.4",
  "new_score": 50
}
```

### Actions

```http
GET /api/actions
Query Parameters:
  - limit: int = 50
  - offset: int = 0
  - action_type: str
  - success: bool
  - since: ISO-8601 datetime

Response: 200 OK
{
  "total": 100,
  "data": [
    {
      "id": 1,
      "incident_id": 42,
      "action_type": "firewall_block",
      "details": "Blocked 1.2.3.4",
      "success": true,
      "timestamp": "2024-02-25T12:00:00Z"
    },
    ...
  ]
}

GET /api/actions/{action_id}
Response: 200 OK
{
  "id": 1,
  "incident_id": 42,
  "action_type": "firewall_block",
  "details": {...},
  "success": true,
  "timestamp": "2024-02-25T12:00:00Z"
}
```

### Statistics

```http
GET /api/stats/summary
Response: 200 OK
{
  "total_incidents": 1234,
  "incidents_today": 42,
  "incidents_this_hour": 5,
  "blocked_ips": 15,
  "active_threats": 3,
  "ai_analyses": 124,
  "top_attack_types": [
    {"type": "SQL_INJECTION", "count": 523},
    {"type": "XSS", "count": 412},
    {"type": "BRUTE_FORCE", "count": 299}
  ],
  "severity_distribution": {
    "HIGH": 45,
    "MEDIUM": 523,
    "LOW": 666
  }
}

GET /api/stats/timeline
Query Parameters:
  - interval: str = "hour" (minute, hour, day, week)
  - duration: int = 24
  - metric: str = "incidents" (incidents, blocks, ai_analyses)

Response: 200 OK
{
  "interval": "hour",
  "duration": 24,
  "data": [
    ["2024-02-25T00:00:00Z", 12],
    ["2024-02-25T01:00:00Z", 8],
    ...
  ],
  "total": 187
}

GET /api/stats/attackers
Query Parameters:
  - limit: int = 10
  - since: ISO-8601 datetime

Response: 200 OK
{
  "data": [
    {
      "ip": "1.2.3.4",
      "attack_count": 42,
      "last_attack": "2024-02-25T12:00:00Z",
      "attack_types": ["SQL_INJECTION", "XSS"],
      "reputation_score": 10,
      "blocked": true
    },
    ...
  ]
}

GET /api/stats/attack-types
Response: 200 OK
{
  "data": [
    {
      "attack_type": "SQL_INJECTION",
      "count": 523,
      "percentage": 42.3,
      "severity_avg": 7.5
    },
    ...
  ]
}
```

### Export

```http
GET /api/export/incidents
Query Parameters:
  - format: str = "csv" (csv, json, xlsx)
  - since: ISO-8601 datetime
  - until: ISO-8601 datetime
  - severity: str

Response: 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="incidents_2024-02-25.csv"

id,timestamp,source_ip,attack_type,severity,...
1,2024-02-25T12:00:00Z,1.2.3.4,SQL_INJECTION,HIGH,...

GET /api/export/threat-intel
Query Parameters:
  - format: str = "json" (json, csv)

Response: 200 OK
Content-Type: application/json
Content-Disposition: attachment; filename="threat_intel_2024-02-25.json"

[
  {
    "ip": "1.2.3.4",
    "reputation_score": 25,
    "details": {...}
  },
  ...
]

GET /api/export/database
Requires: Admin authentication
Response: 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="sentinel_intel_backup.db"

[Binary SQLite database file]
```

### Threat Intelligence

```http
GET /api/threat-intel
Query Parameters:
  - limit: int = 50
  - min_score: int = 0
  - max_score: int = 100

Response: 200 OK
{
  "total": 156,
  "data": [
    {
      "id": 1,
      "ip": "1.2.3.4",
      "reputation_score": 25,
      "details": {...},
      "last_checked": "2024-02-25T12:00:00Z"
    },
    ...
  ]
}

POST /api/threat-intel
Body:
{
  "ip": "1.2.3.4",
  "reputation_score": 50,
  "details": {...}
}
Response: 201 Created

DELETE /api/threat-intel/{ip}
Response: 200 OK
```

### Logs

```http
GET /api/logs
Query Parameters:
  - source: str = "auth" (auth, web, system)
  - lines: int = 100
  - search: str

Response: 200 OK
{
  "source": "auth",
  "total_lines": 100,
  "data": [
    {
      "timestamp": "2024-02-25T12:00:00Z",
      "line": "Feb 25 12:00:00 server sshd[1234]: Failed password..."
    },
    ...
  ]
}

GET /api/logs/search
Query Parameters:
  - query: str (required)
  - source: str = "all"
  - limit: int = 100

Response: 200 OK
{
  "query": "failed password",
  "matches": 42,
  "data": [...]
}
```

---

## 🗄️ Database Schema

### Complete Table Structures

#### **incidents** Table

```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,              -- ISO-8601: 2024-02-25T12:00:00Z
    source_ip TEXT NOT NULL,              -- IPv4: 1.2.3.4
    attack_type TEXT NOT NULL,            -- SQL_INJECTION, XSS, BRUTE_FORCE, etc.
    severity TEXT NOT NULL,               -- LOW, MEDIUM, HIGH, CRITICAL
    raw_log TEXT,                         -- Original log line
    threat_type TEXT,                     -- web_attack, auth_attack, etc.
    action TEXT,                          -- blocked, monitored, alerted
    details TEXT,                         -- JSON: additional metadata
    ai_analyzed BOOLEAN DEFAULT 0,        -- 1 if AI analyzed
    false_positive BOOLEAN DEFAULT 0,     -- 1 if marked as FP
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX idx_incidents_source_ip ON incidents(source_ip);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_attack_type ON incidents(attack_type);
CREATE INDEX idx_incidents_ai_analyzed ON incidents(ai_analyzed);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);

-- Foreign key constraints
-- None (base table)
```

**Example Data:**
```json
{
  "id": 42,
  "timestamp": "2024-02-25T12:00:00Z",
  "source_ip": "1.2.3.4",
  "attack_type": "SQL_INJECTION",
  "severity": "HIGH",
  "raw_log": "192.168.1.100 - - [25/Feb/2024:12:00:00] \"GET /api/users?id=1' OR '1'='1\" 200 1234",
  "threat_type": "web_attack",
  "action": "blocked",
  "details": "{\"method\": \"GET\", \"url\": \"/api/users\", \"payload\": \"' OR '1'='1\"}",
  "ai_analyzed": 1,
  "false_positive": 0,
  "created_at": "2024-02-25T12:00:05Z",
  "updated_at": "2024-02-25T12:00:05Z"
}
```

---

#### **actions** Table

```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER,                  -- Foreign key to incidents
    action_type TEXT NOT NULL,            -- firewall_block, alert, log, etc.
    details TEXT,                         -- JSON: action details
    success BOOLEAN NOT NULL DEFAULT 1,   -- 1=success, 0=failure
    timestamp TEXT NOT NULL,              -- Execution time
    duration_ms INTEGER,                  -- Execution duration
    error_message TEXT,                   -- If failed
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_actions_incident_id ON actions(incident_id);
CREATE INDEX idx_actions_timestamp ON actions(timestamp);
CREATE INDEX idx_actions_action_type ON actions(action_type);
CREATE INDEX idx_actions_success ON actions(success);
```

**Example Data:**
```json
{
  "id": 123,
  "incident_id": 42,
  "action_type": "firewall_block",
  "details": "{\"firewall\": \"ufw\", \"command\": \"ufw deny from 1.2.3.4\", \"rule_id\": 45}",
  "success": 1,
  "timestamp": "2024-02-25T12:00:10Z",
  "duration_ms": 125,
  "error_message": null,
  "created_at": "2024-02-25T12:00:10Z"
}
```

---

#### **threat_intel** Table

```sql
CREATE TABLE threat_intel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,              -- IPv4 address
    reputation_score INTEGER DEFAULT 0,   -- 0-100 (lower=worse)
    category TEXT,                        -- malicious, suspicious, clean
    details TEXT,                         -- JSON: metadata
    first_seen TEXT,                      -- First occurrence
    last_checked TEXT,                    -- Last intel update
    total_attacks INTEGER DEFAULT 0,      -- Attack count
    geolocation TEXT,                     -- JSON: geo data
    autonomous_system TEXT,               -- ASN info
    blacklisted BOOLEAN DEFAULT 0,        -- 1 if blacklisted
    whitelisted BOOLEAN DEFAULT 0,        -- 1 if whitelisted
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_threat_intel_ip ON threat_intel(ip);
CREATE INDEX idx_threat_intel_reputation_score ON threat_intel(reputation_score);
CREATE INDEX idx_threat_intel_category ON threat_intel(category);
CREATE INDEX idx_threat_intel_blacklisted ON threat_intel(blacklisted);
CREATE INDEX idx_threat_intel_last_checked ON threat_intel(last_checked);
```

**Example Data:**
```json
{
  "id": 78,
  "ip": "1.2.3.4",
  "reputation_score": 25,
  "category": "malicious",
  "details": "{\"known_threats\": [\"botnet\", \"scanner\"], \"confidence\": 0.95}",
  "first_seen": "2024-01-15T08:30:00Z",
  "last_checked": "2024-02-25T12:00:00Z",
  "total_attacks": 42,
  "geolocation": "{\"country\": \"US\", \"city\": \"San Francisco\", \"lat\": 37.7749, \"lon\": -122.4194}",
  "autonomous_system": "AS15169 Google LLC",
  "blacklisted": 1,
  "whitelisted": 0,
  "created_at": "2024-01-15T08:30:00Z",
  "updated_at": "2024-02-25T12:00:00Z"
}
```

---

#### **blacklist** Table

```sql
CREATE TABLE blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,
    reason TEXT NOT NULL,
    added_by TEXT,                        -- User/system that added
    expires_at TEXT,                      -- NULL for permanent
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_blacklist_ip ON blacklist(ip);
CREATE INDEX idx_blacklist_expires_at ON blacklist(expires_at);
```

---

#### **whitelist** Table

```sql
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,
    reason TEXT NOT NULL,
    added_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_whitelist_ip ON whitelist(ip);
```

---

#### **users** Table (Future)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',             -- admin, user, viewer
    active BOOLEAN DEFAULT 1,
    last_login TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
```

---

#### **api_keys** Table (Future)

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    name TEXT,
    permissions TEXT,                      -- JSON: allowed endpoints
    expires_at TEXT,
    last_used TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### Database Queries

**Common Queries:**

```sql
-- Get all HIGH severity incidents from last 24 hours
SELECT * FROM incidents 
WHERE severity = 'HIGH' 
  AND timestamp > datetime('now', '-1 day')
ORDER BY timestamp DESC;

-- Get top 10 attackers
SELECT source_ip, COUNT(*) as attack_count, MAX(timestamp) as last_attack
FROM incidents
GROUP BY source_ip
ORDER BY attack_count DESC
LIMIT 10;

-- Get attack type distribution
SELECT attack_type, COUNT(*) as count, 
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM incidents), 2) as percentage
FROM incidents
GROUP BY attack_type
ORDER BY count DESC;

-- Get incidents with their actions
SELECT i.*, a.action_type, a.success
FROM incidents i
LEFT JOIN actions a ON i.id = a.incident_id
WHERE i.timestamp > datetime('now', '-1 day')
ORDER BY i.timestamp DESC;

-- Get IPs with low reputation
SELECT ip, reputation_score, total_attacks, last_checked
FROM threat_intel
WHERE reputation_score < 40
ORDER BY reputation_score ASC, total_attacks DESC;

-- Get today's statistics
SELECT 
    COUNT(*) as total_incidents,
    SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high_severity,
    SUM(CASE WHEN ai_analyzed = 1 THEN 1 ELSE 0 END) as ai_analyzed,
    COUNT(DISTINCT source_ip) as unique_ips
FROM incidents
WHERE date(timestamp) = date('now');

-- Clean old data (older than 90 days)
DELETE FROM incidents
WHERE timestamp < datetime('now', '-90 days');

DELETE FROM actions
WHERE incident_id NOT IN (SELECT id FROM incidents);
```

---

## 🐳 Docker Components

### Containers

**sentinel-agent:**
- Main application container
- Python 3.10
- All Python dependencies
- Monitoring agents
- API server
- Dashboard server

**ollama:** (Optional)
- LLM server
- Running llama3:8b model  
- Inference engine

### Volumes

```yaml
volumes:
  # Application data (persistent)
  - ./data:/app/data
    # Contains: sentinel_intel.db, secrets/
  
  # Application logs (persistent)
  - ./logs:/app/logs
    # Contains: sentinel.log, error.log, access.log
  
  # System logs (read-only)
  - /var/log:/var/log:ro
    # Access to: auth.log, apache2/access.log
  
  # Docker socket (optional, for monitoring)
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Networks

```yaml
networks:
  sentinel-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 📝 Detection Patterns

### SQL Injection Patterns

```python
SQL_INJECTION_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # SQL meta-characters
    r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",  # Typical SQL injection
    r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",  # 'or keyword
    r"((\%27)|(\'))union",  # UNION attack
    r"exec(\s|\+)+(s|x)p\w+",  # Stored procedure execution
    r"UNION.+SELECT",  # UNION SELECT
    r"SELECT.+FROM.+WHERE",  # Basic SELECT
    r"INSERT.+INTO.+VALUES",  # INSERT
    r"UPDATE.+SET.+WHERE",  # UPDATE
    r"DELETE.+FROM.+WHERE",  # DELETE
    r"DROP.+TABLE",  # DROP TABLE
    r"CREATE.+TABLE",  # CREATE TABLE
    r"ALTER.+TABLE",  # ALTER TABLE
]
```

### XSS Patterns

```python
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",  # Script tags
    r"javascript:",  # JavaScript protocol
    r"onerror\s*=",  # onerror event
    r"onload\s*=",  # onload event
    r"onclick\s*=",  # onclick event
    r"<iframe[^>]*>",  # iframe injection
    r"<img[^>]*>",  # img tag injection
    r"<svg[^>]*>",  # SVG injection
    r"<object[^>]*>",  # object tag
    r"<embed[^>]*>",  # embed tag
    r"document\.cookie",  # Cookie theft
    r"document\.write",  # DOM manipulation
    r"window\.location",  # Redirection
]
```

### Path Traversal Patterns

```python
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",  # ../
    r"\.\.\\/",  # ..\
    r"\.\.%2f",  # URL encoded ../
    r"\.\.%5c",  # URL encoded ..\
    r"%2e%2e/",  # Double encoded
    r"%252e%252e/",  # Triple encoded
    r"/etc/passwd",  # Common target
    r"/windows/win.ini",  # Windows target
    r"c:\\windows",  # Windows path
]
```

### Command Injection Patterns

```python
COMMAND_INJECTION_PATTERNS = [
    r"(;|\||`|&|\$\(|\$\{)",  # Command separators
    r"\b(cat|ls|pwd|wget|curl|nc|bash|sh)\b",  # Common commands
    r">/dev/null",  # Output redirection
    r"\|\s*bash",  # Pipe to bash
    r"&&",  # Command chaining
    r"\$\(.*\)",  # Command substitution
]
```

### Brute Force Detection

```python
BRUTE_FORCE_INDICATORS = {
    'failed_login_threshold': 5,  # Failed attempts
    'time_window': 300,  # 5 minutes
    'lockout_duration': 3600,  # 1 hour
}
```

---

## 🔒 Security Features

### Password Security
- PBKDF2-HMAC-SHA256 hashing
- 100,000 iterations
- Random salt per password
- Secure random generation

### Encryption
- AES-256 encryption (if available)
- Fernet symmetric encryption
- Secure key storage (600 permissions)
- Environment variable encryption

### Authentication
- HTTP Basic Auth
- Session management
- Token-based auth (future)
- API key support (future)

### Authorization
- Role-based access control (future)
- Permission management (future)
- Audit logging

### Network Security
- IP whitelisting
- IP blacklisting
- Rate limiting
- CORS configuration
- Firewall integration

### Data Protection
- Database encryption at rest (future)
- Secure credential storage
- Audit logging
- Data retention policies

---

**This completes the comprehensive feature reference. Every module, script, configuration option, API endpoint, and database table is documented in detail.**
