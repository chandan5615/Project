# Sentinel Defense Module

The Sentinel Defense Module extends the base Sentinel Agent with advanced multi-vector security capabilities.

## Features

### 1. Multi-Vector Ingestion

The system simultaneously monitors multiple log sources:

- **Auth Log Sensor** (`/var/log/auth.log`): Monitors SSH login attempts and authentication failures
- **Web Log Sensor** (`/var/log/apache2/access.log` or Nginx): Monitors web server access logs for suspicious patterns

Both sensors run concurrently and feed events to the AI crew for analysis.

### 2. Autonomous Tool-Use (Enforcer Agent)

The **Enforcer Agent** has a comprehensive tool-belt for autonomous security actions:

- **`execute_iptables_rule()`**: Execute firewall rules with automatic retry logic
- **`verify_firewall_rule()`**: Verify that firewall rules were successfully added
- **`kill_process()`**: Terminate processes using systemctl or kill commands
- **`change_permissions()`**: Modify file/directory permissions using chmod

### 3. Cross-Correlation Logic

The **Researcher Agent** performs intelligent cross-correlation:

- When an IP is detected brute-forcing SSH, it **automatically checks** if that same IP appears in web access logs
- This identifies multi-vector attacks (same attacker hitting multiple services)
- Escalates threat level when cross-correlation is detected
- Provides comprehensive threat intelligence combining multiple data sources

### 4. Resilience Loop

The Enforcer Agent implements a robust resilience mechanism:

1. **Execute** firewall rule using `execute_iptables_rule()`
2. **Verify** rule was added using `verify_firewall_rule()`
3. **Retry** with alternative commands if verification fails (up to 3 attempts):
   - Different iptables command syntax
   - Alternative insertion methods
   - Fallback to ufw if iptables fails
4. **Report** final status with verification details

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Sentinel Defense Module                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ Auth Sensor  │         │ Web Sensor   │            │
│  │ (SSH logs)   │         │ (HTTP logs)  │            │
│  └──────┬───────┘         └──────┬───────┘            │
│         │                         │                     │
│         └──────────┬──────────────┘                     │
│                    │                                     │
│         ┌──────────▼──────────┐                         │
│         │  Event Handler     │                         │
│         │  (Multi-Vector)     │                         │
│         └──────────┬──────────┘                         │
│                    │                                     │
│         ┌──────────▼──────────────────────────┐         │
│         │         AI Crew                     │         │
│         ├──────────────────────────────────────┤         │
│         │ 1. Triage Analyst                   │         │
│         │ 2. Researcher (Cross-Correlation)   │         │
│         │ 3. Incident Responder               │         │
│         │ 4. Enforcer (Resilience Loop)      │         │
│         └──────────────────────────────────────┘         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run with default log paths
sudo python main.py
```

### Custom Log Paths

```bash
# Specify custom log paths
sudo python main.py --auth-log /var/log/secure --web-log /var/log/nginx/access.log
```

## Agent Workflow

1. **Triage Analyst**: Analyzes the initial security event
2. **Researcher Agent**: 
   - Checks threat intelligence
   - **Performs cross-correlation** (checks web logs for same IP)
   - Escalates if multi-vector attack detected
3. **Incident Responder**: Creates remediation plan
4. **Enforcer Agent**: 
   - Executes firewall rules
   - **Verifies rule was added** (resilience loop)
   - Retries with alternatives if verification fails

## Example Scenario

1. **Auth Sensor** detects: `Failed password for user from 192.168.1.100`
2. **Researcher Agent** cross-correlates:
   - Checks threat intelligence for `192.168.1.100`
   - **Automatically checks web logs** for same IP
   - Finds: `192.168.1.100 - - [timestamp] "GET /admin.php?cmd=..." 403`
3. **Result**: Multi-vector attack detected - IP is attacking both SSH and web services
4. **Enforcer Agent**:
   - Executes: `iptables -A INPUT -s 192.168.1.100 -j DROP`
   - Verifies rule exists in firewall table
   - If verification fails, retries with alternative command
   - Reports success/failure with verification details

## Configuration

### Web Log Paths

The system supports multiple web server log formats:

- **Apache**: `/var/log/apache2/access.log` (default)
- **Nginx**: `/var/log/nginx/access.log`
- **Custom**: Specify with `--web-log` parameter

### Suspicious Patterns Detected

The web sensor automatically detects:
- HTTP error codes (4xx, 5xx)
- Path traversal attempts (`../`)
- XSS attempts (`<script>`, `javascript:`, `onerror=`)
- SQL injection (`union select`, `drop table`)
- Command injection (`cmd=`, `exec=`, `system(`)

## Security Considerations

- **Human-in-the-Loop**: Firewall rules still require approval before execution
- **Verification**: All firewall rules are verified after execution
- **Resilience**: Automatic retry with alternative methods if initial attempt fails
- **Logging**: All actions are logged for audit purposes

## Troubleshooting

### Web log not found
- Check if web server is installed and running
- Verify log path with: `ls -la /var/log/apache2/access.log`
- Use `--web-log` to specify custom path

### Cross-correlation not working
- Ensure both sensors are running (check startup logs)
- Verify IP addresses are being extracted correctly
- Check web log format matches expected patterns

### Resilience loop failing
- Verify iptables is installed: `which iptables`
- Check permissions: Run with `sudo`
- Review error messages in enforcement task output
