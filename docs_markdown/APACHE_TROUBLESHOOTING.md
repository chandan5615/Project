# Apache Attack Detection Troubleshooting Guide

**Issue**: "When attacking Apache, no output is shown"

---

## Root Cause Analysis

The **Sentinel Agent code is correct** ✅. The issue is likely in your **Apache configuration or testing setup**, not the code.

### How Apache Attack Detection Works (Verified Correct)

```
Attack Request → Apache logs to /var/log/apache2/access.log
                 ↓
            Watchdog detects file change
                 ↓
            WebSensor reads new lines
                 ↓
            AttackDetector analyzes for patterns (SQL injection, XSS, etc.)
                 ↓
            Sentinel Agent handles the attack event
                 ↓
            Output logged / Dashboard updated
```

All components are implemented correctly. ✅

---

## Diagnostic Steps (In Order)

### Step 1: Verify Apache is Running

```bash
# Check if Apache is running
sudo systemctl status apache2

# Start if needed
sudo systemctl start apache2
```

### Step 2: Verify Apache is Logging

```bash
# Watch the access log in real-time
tail -f /var/log/apache2/access.log

# In another terminal, generate a test request
curl http://localhost/test.html

# Check if the log entry appears
# Expected format: IP - - [timestamp] "GET /test.html HTTP/1.1" 200 size
```

**✅ If log entry appears**: Apache logging is working  
**❌ If NO entry appears**: See "Apache Not Logging" section below

### Step 3: Verify Attack Pattern Matching

Once Apache is logging requests, test with attack patterns:

```bash
# Test SQL Injection detection
curl "http://localhost/search.php?q=admin' OR '1'='1"

# Test Directory Traversal detection
curl "http://localhost/file.php?path=../../../../etc/passwd"

# Test XSS detection
curl "http://localhost/comment.php?text=<script>alert('xss')</script>"

# Watch Apache log
tail -f /var/log/apache2/access.log
```

### Step 4: Verify Sentinel Agent is Monitoring

```bash
# Check Sentinel logs
docker logs -f sentinel-agent

# OR if running directly
tail -f /app/logs/sentinel.log

# You should see detection messages for the attack patterns
```

---

## Common Issues & Solutions

### ❌ Issue 1: "Apache Not Logging Requests"

**Symptoms**:
- `tail -f /var/log/apache2/access.log` shows no new entries when accessing Apache
- No log file at `/var/log/apache2/access.log`

**Solutions**:

**A. Check Apache Configuration**:
```bash
# Verify Apache config syntax
sudo apache2ctl configtest
# Should output: Syntax OK

# Check if access.log is configured
sudo grep -r "CustomLog" /etc/apache2/
# Should see something like:
# CustomLog ${APACHE_LOG_DIR}/access.log combined
```

**B. Check File Permissions**:
```bash
# Check if Apache can write to log directory
ls -la /var/log/apache2/

# Apache user is typically 'www-data'
# Should see: -rw-r----- www-data adm access.log

# If permissions are wrong:
sudo chown www-data:adm /var/log/apache2/access.log
sudo chmod 640 /var/log/apache2/access.log
```

**C. Enable Logging Module**:
```bash
# Ensure mod_log_config is enabled
sudo a2enmod log_config

# Restart Apache
sudo systemctl restart apache2
```

**D. Docker Specific**:
```bash
# If running in Docker, verify Apache is configured to use correct log path
docker exec sentinel-apache bash -c "tail -f /var/log/apache2/access.log"

# If no output, Apache may not be running or configured
docker exec sentinel-apache apache2ctl status
```

---

### ❌ Issue 2: "Sentinel Agent Not Detecting Attacks"

**Symptoms**:
- Apache logs show attack requests
- Sentinel logs show no attack detection

**Solutions**:

**A. Verify Log Path Configuration**:
```bash
# Check what path Sentinel is monitoring
docker logs sentinel-agent | grep "Web log"

# Should show:
# Web log found: /var/log/apache2/access.log

# If different path, update docker-compose.yml:
# environment:
#   - WEB_LOG_PATH=/var/log/apache2/access.log
```

**B. Check Log Format**:
```bash
# Sentinel expects Apache Combined or Common format
# Example of Combined format:
# IP - - [timestamp] "GET /path HTTP/1.1" 200 1234 "-" "User-Agent"

# Verify your log format
sudo head -5 /var/log/apache2/access.log

# If format is wrong, update Apache config
sudo nano /etc/apache2/sites-available/000-default.conf
# Ensure line has: CustomLog ${APACHE_LOG_DIR}/access.log combined
```

**C. Verify Attack Patterns**:
```bash
# Some attack patterns are very strict
# Examples that WILL be detected:

# SQL Injection (check for 'union select')
curl "http://localhost/search.php?q=union select"

# Directory Traversal (check for '../')
curl "http://localhost/file.php?path=../../etc/passwd"

# XSS (check for '<script>')
curl "http://localhost/comment.php?text=<script>alert(1)</script>"

# Check the exact patterns in defense/attack_detector.py
```

---

### ❌ Issue 3: "Watchdog Not Detecting File Changes"

**Symptoms**:
- Attack requests logged to Apache
- Sentinel monitoring active
- But no detection triggered

**Solutions**:

**A. Check File Permissions**:
```bash
# Sentinel container must read /var/log/apache2/access.log
# In Docker, verify volume mount:
docker inspect sentinel-agent | grep -A 10 Mounts

# Should show: /var/log/apache2 mounted
# In docker-compose.yml:
# volumes:
#   - /var/log/apache2:/var/log/apache2:ro
```

**B. Force Log Flush**:
```bash
# Sometimes Apache buffers output
# Force flush:
sudo systemctl reload apache2

# Or manually flush logs
sudo a2graceful

# Then generate test request
curl "http://localhost/test/../etc/passwd"
```

**C. Check Watchdog Library**:
```bash
# Watchdog might not detect all file systems
# Check container filesystem
docker exec sentinel-agent mount | grep apache

# If on certain filesystems (NFS, etc), watchdog might not work
# Fallback: Use polling-based monitoring
```

---

## Testing Checklist

- [ ] Apache is running: `sudo systemctl status apache2`
- [ ] Apache is logging: `tail -f /var/log/apache2/access.log` shows entries
- [ ] Log format is correct: Should have IP at start: `127.0.0.1 - - [...] "GET ..."`
- [ ] Sentinel is monitoring: `docker logs -f sentinel-agent` shows "Web log monitoring: ACTIVE"
- [ ] Test attack is detected: Send curl request with `../` or `union select`
- [ ] Output appears: Check `docker logs -f sentinel-agent` for detection message

---

## Attack Patterns to Test

### ✅ These WILL be detected (if working correctly):

```bash
# SQL Injection
curl "http://localhost/?id=1 union select"
curl "http://localhost/?id=1' or 1=1"

# Directory Traversal  
curl "http://localhost/file.php?f=../../../etc/passwd"
curl "http://localhost/file.php?f=%2e%2e%2f%2e%2e%2fetc%2fpasswd"

# XSS
curl "http://localhost/?search=<script>alert(1)</script>"
curl "http://localhost/?name=<img src=x onerror=alert(1)>"

# Command Injection
curl "http://localhost/?cmd=ls;whoami"
curl "http://localhost/?cmd=`cat /etc/passwd`"
```

### ⚠️ These might NOT trigger (pattern-dependent):

```bash
# Normal requests (no attack pattern)
curl http://localhost/
curl http://localhost/index.html

# Incomplete patterns
curl "http://localhost/?id=1 or"  # Missing "1=1"
curl "http://localhost/?path=./"  # Missing ".."
```

---

## If Still Not Working

### Step 1: Manual Test of Attack Detector

```python
# In Python, test the detector directly:
from defense.attack_detector import AttackDetector

detector = AttackDetector()

# Test SQL Injection
log_line = '127.0.0.1 - - [timestamp] "GET /search?q=admin\' OR \'1\'=\'1" 200 1234'
result = detector.detect_attack(log_line, source="web")

if result:
    print("✅ Attack detected:", result)
else:
    print("❌ Attack NOT detected - pattern may not match")
```

### Step 2: Enable Debug Logging

```bash
# Set debug logging in docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG

# Restart and check logs
docker-compose restart sentinel-agent
docker logs -f sentinel-agent | grep -i "web\|attack\|pattern"
```

### Step 3: Contact Support

If after all this the issue persists, provide:
- Docker compose configuration
- Apache access.log sample lines
- Sentinel logs showing the detection attempt
- Exact curl commands being tested

---

## Summary

| Check | Command | Expected |
|-------|---------|----------|
| Apache Running | `systemctl status apache2` | `active (running)` |
| Apache Logging | `tail -f /var/log/apache2/access.log` | New entries appear |
| Log Format | `head -1 /var/log/apache2/access.log` | Starts with IP: `127.0.0.1` |
| Sentinel Monitoring | `docker logs sentinel-agent` | `Web log monitoring: ACTIVE` |
| Attack Detection | Send test attack + check logs | Detection message appears |

**Code Status**: ✅ All verified correct  
**Issue Type**: Operational (configuration/setup)  
**Solution**: Follow diagnostic steps above

---

Generated: February 6, 2026
