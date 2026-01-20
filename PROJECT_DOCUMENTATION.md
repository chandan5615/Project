# Sentinel Agent - Comprehensive Project Documentation

## Executive Summary

Sentinel Agent is an autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. It uses CrewAI for orchestration and Google Gemini API as the LLM engine to monitor, analyze, and respond to security threats in real-time. The system implements a sophisticated "Sensor-Brain-Action" pipeline that detects attacks, analyzes threats, and executes defensive measures with human oversight.

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
- Continuous log file monitoring using watchdog
- Instant attack detection
- Low latency response

### 2. AI-Powered Analysis
- Multi-agent AI crew for comprehensive analysis
- Context-aware threat assessment
- Intelligent decision making

### 3. Autonomous Defense
- Automatic IP blocking
- Process termination
- Permission management
- Resilience verification

### 4. Human-in-the-Loop
- Approval required for critical actions
- Double confirmation for firewall rules
- Audit trail for all actions

### 5. Comprehensive Logging
- Complete attack history
- Action tracking
- Report generation
- Query interface

### 6. Multi-Vector Protection
- Simultaneous monitoring of multiple log sources
- Cross-correlation analysis
- Multi-vector attack detection

## Technical Stack

- **Language**: Python 3.10+
- **Orchestration**: CrewAI (Multi-agent framework)
- **LLM**: Google Gemini API (gemini-1.5-flash)
- **Log Monitoring**: Watchdog library
- **Firewall**: iptables/ufw
- **Process Management**: systemctl, kill
- **File Permissions**: chmod

## Project Structure

```
Sentinel Agent/
├── main.py                  # Entry point and event loop
├── agents.py                # AI crew definitions
├── tasks.py                 # Security playbooks
├── view_attacks.py          # Attack records viewer
├── sensors/
│   ├── auth_sensor.py       # SSH log monitoring
│   └── web_sensor.py        # Web log monitoring
├── tools/
│   └── tools.py             # Security tools (IP check, firewall, etc.)
├── defense/
│   ├── attack_detector.py   # Attack pattern detection
│   └── attack_logger.py     # Attack logging system
└── attack_records.json      # Attack history database
```

## Usage Examples

### Starting the System
```bash
# Activate virtual environment
source venv/bin/activate

# Set API key
export GOOGLE_API_KEY="your-key"

# Run Sentinel Agent
sudo python main.py
```

### Viewing Attack Records
```bash
python view_attacks.py
```

### Custom Log Paths
```bash
sudo python main.py --auth-log /var/log/secure --web-log /var/log/nginx/access.log
```

## Security Considerations

1. **Permissions**: Requires sudo for log access and firewall management
2. **API Key Security**: Store API keys securely (environment variables or .env)
3. **Attack Records**: Contains sensitive information - keep secure
4. **Human Oversight**: Critical actions require approval
5. **Audit Trail**: All actions are logged for compliance

## Limitations & Future Enhancements

### Current Limitations
- Linux-only (requires iptables and Linux log structure)
- Requires manual API key setup
- Limited to log-based detection

### Potential Enhancements
- Network packet analysis
- Real-time process monitoring
- Integration with SIEM systems
- Machine learning-based anomaly detection
- Cloud platform support
- Docker container monitoring

## Conclusion

Sentinel Agent provides comprehensive, autonomous security monitoring and response capabilities for Linux systems. It detects 14 different attack types, implements multi-vector correlation, and maintains complete audit trails. The system combines AI-powered analysis with automated defense mechanisms while maintaining human oversight for critical actions.
