# Attack Defense System

The Sentinel Agent now includes comprehensive defense mechanisms for multiple attack types with automatic logging and recording.

## Supported Attack Types

### 1. Injection Attacks
- **SQL Injection (SQLi)**: Detects union select, drop table, exec(), and other SQL manipulation patterns
- **Command Injection**: Detects shell command execution attempts (ls, cat, bash, etc.)
- **Cross-Site Scripting (XSS)**:
  - Stored XSS: Scripts permanently stored on server
  - Reflected XSS: Scripts reflected in error messages

### 2. Authentication & Session Attacks
- **Brute Force**: Multiple failed password attempts
- **Credential Stuffing**: Using compromised credentials
- **Session Hijacking**: Cookie manipulation and session theft

### 3. Access Control Attacks
- **IDOR (Insecure Direct Object References)**: Unauthorized access to user/admin resources
- **Directory Traversal**: Accessing files outside web root (../, /etc/passwd, etc.)

### 4. Client-Side Attacks
- **CSRF (Cross-Site Request Forgery)**: Forced actions on authenticated sessions
- **Clickjacking**: UI overlay attacks

### 5. Infrastructure Attacks
- **DoS/DDoS**: Denial of service attacks
- **Man-in-the-Middle (MitM)**: SSL/TLS certificate errors
- **SSRF (Server-Side Request Forgery)**: Forcing server to access internal resources

## Attack Logging System

Every detected attack is automatically recorded with:

- **Date & Time**: Precise timestamp of detection
- **Attack Type**: Specific attack category detected
- **IP Address**: Source of the attack
- **Severity**: Critical, High, Medium, or Low
- **Description**: Human-readable attack description
- **Source**: Auth log or Web log
- **Log Line**: Original log entry that triggered detection
- **Actions Taken**: List of defensive actions executed

### Attack Record Format

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

## Viewing Attack Records

### Command Line Viewer

```bash
python view_attacks.py
```

This displays:
- Summary statistics (total attacks, by severity, by type, top IPs)
- Recent attacks (last 10)
- Actions taken for each attack

### Programmatic Access

```python
from defense.attack_logger import AttackLogger

logger = AttackLogger()

# Get all attacks from an IP
attacks = logger.get_attacks_by_ip("192.168.1.100")

# Get all SQL injection attacks
sql_attacks = logger.get_attacks_by_type("sql_injection")

# Get recent attacks
recent = logger.get_recent_attacks(limit=20)

# Generate report
report = logger.generate_report()
print(report)
```

## Defense Strategies

Each attack type has specific defense strategies:

### SQL Injection
- Immediate: Block IP, sanitize queries, enable parameterized queries
- Long-term: Input validation, prepared statements, least privilege access

### Command Injection
- Immediate: Block IP, kill suspicious processes, review logs
- Long-term: Input sanitization, command whitelisting, execution restrictions

### XSS
- Immediate: Block IP, sanitize stored content, remove malicious scripts
- Long-term: Content Security Policy (CSP), output encoding, input validation

### Brute Force
- Immediate: Block IP, enable account lockout, rate limiting
- Long-term: CAPTCHA, two-factor authentication, password policy

### SSRF
- Immediate: Block IP, review request handlers, check internal access
- Long-term: URL validation, domain allowlisting, network segmentation

## Integration

The attack detection and logging is automatically integrated into the main Sentinel Agent workflow:

1. **Detection**: Sensors detect attacks using pattern matching
2. **Logging**: Attack is immediately logged with all details
3. **Analysis**: AI crew analyzes the attack
4. **Response**: Enforcer Agent takes defensive actions
5. **Recording**: Actions taken are recorded in the attack log

## Attack Record File

Attack records are stored in `attack_records.json` in the project root. This file:
- Is automatically created on first attack
- Persists across restarts
- Can be backed up for analysis
- Contains complete attack history

## Example Attack Flow

1. **Detection**: Web sensor detects SQL injection in log line
2. **Logging**: Attack logged with ID #1, severity "high"
3. **Analysis**: AI crew determines threat level and recommends blocking
4. **Action**: Enforcer Agent blocks IP with firewall rule
5. **Verification**: Firewall rule verified successfully
6. **Recording**: Action added to attack record #1 with success=true
7. **Status**: Attack record status updated to "mitigated"

## Security Considerations

- Attack records contain sensitive information (IPs, attack patterns)
- Keep `attack_records.json` secure and backed up
- Regularly review attack records for patterns
- Use attack data to improve detection rules
- Consider exporting to SIEM systems for long-term analysis
