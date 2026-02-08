# Sentinel Agent v2.2 - Attack Simulation & Testing Guide

Complete guide to test Sentinel Agent features by simulating real-world attacks and verifying detection.

---

## Table of Contents
1. [Overview](#overview)
2. [Pre-Test Setup](#pre-test-setup)
3. [Attack Types & Simulation](#attack-types--simulation)
4. [Verification Methods](#verification-methods)
5. [Expected Results](#expected-results)
6. [Troubleshooting Tests](#troubleshooting-tests)
7. [Performance Testing](#performance-testing)

---

## Overview

This guide helps you verify that Sentinel Agent correctly detects and responds to various attack types:

| Attack Type | Severity | Detection Source | Expected Response |
|-------------|----------|------------------|------------------|
| **SSH Brute Force** | HIGH | `/var/log/auth.log` | IP flagged, logged, scored |
| **SQL Injection** | CRITICAL | `/var/log/apache2/access.log` | Blocked, threat recorded |
| **DDoS Attack** | CRITICAL | `/var/log/apache2/access.log` | Rate limiting, IP blacklist |
| **Port Scanning** | MEDIUM | `/var/log/auth.log` | Anomaly alert |
| **Failed Logins** | MEDIUM | `/var/log/auth.log` | Pattern detection |
| **Web Fuzzing** | MEDIUM | `/var/log/apache2/access.log` | WEB attack flagged |
| **Malware Detection** | CRITICAL | Local analysis | Threat database match |

---

## Pre-Test Setup

### Verify Sentinel Agent is Running

```bash
# Check container status
docker-compose ps
# Should show: sentinel-agent   Up (healthy)

# Check API health
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"2.2"}

# Get API token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=YOUR_PASSWORD" | jq -r '.token')

# Verify token works
curl -H "X-API-Key: $TOKEN" http://localhost:8000/api/health
```

### Baseline Metrics (Before Testing)

```bash
# Record baseline stats
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/detection > baseline_metrics.json

curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent > baseline_incidents.json

# Count incidents
cat baseline_incidents.json | jq 'length'
```

---

## Attack Types & Simulation

### 1. SSH Brute Force Attack

**What it is:** Multiple failed login attempts on SSH port 22

**Why it matters:** Attackers use automated tools to guess passwords

**How to simulate:**

#### Method 1: Using sshpass (Simple)
```bash
# Install sshpass
sudo apt-get install sshpass -y

# Simulate 10 failed login attempts
for i in {1..10}; do
  sshpass -p "wrongpassword" ssh -o StrictHostKeyChecking=no user@localhost 2>/dev/null
  echo "Attempt $i - Failed login"
done
```

#### Method 2: Using hydra (Advanced - More realistic)
```bash
# Install hydra
sudo apt-get install hydra -y

# Create password list
cat > passwords.txt << EOF
wrongpass1
wrongpass2
wrongpass3
EOF

# Run attack simulation (30 attempts against local SSH)
hydra -l ubuntu -P passwords.txt -t 5 localhost ssh 2>/dev/null
```

#### Method 3: Manual failure (No extra tools)
```bash
# Connect with wrong password multiple times
for i in {1..15}; do
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 wrong_user@localhost 2>/dev/null || true
done
```

**What Sentinel Should Detect:**

After 1-2 minutes, check:

```bash
# View detected incidents
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | jq '.[] | select(.type=="SSH Brute Force")'

# Expected output:
# {
#   "id": "INC-2024-00150",
#   "type": "SSH Brute Force",
#   "source_ip": "127.0.0.1",
#   "severity": "HIGH",
#   "fail_count": 15,
#   "status": "Flagged"
# }

# Check threat score
curl -s -X POST http://localhost:8000/api/anomaly/score \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "127.0.0.1",
    "attack_type": "ssh_brute_force",
    "severity": "high",
    "fail_count": 15
  }' | jq '.anomaly_score'

# Should be > 0.8 (high risk)
```

**Success Criteria:**
- ✅ Attack logged with timestamp
- ✅ Source IP identified
- ✅ High severity assigned
- ✅ Anomaly score > 0.8
- ✅ Logs show failed attempts count

---

### 2. SQL Injection Attack

**What it is:** Malicious SQL code in web request parameters

**Why it matters:** Can access/modify database directly

**How to simulate:**

#### Method 1: Simple curl request
```bash
# Standard attack payload
PAYLOAD="1' OR '1'='1"
curl "http://localhost/search.php?q=${PAYLOAD}"

# Alternative payloads
curl "http://localhost/login.php?user=admin'--&pass=anything"
curl "http://localhost/api/users?id=1 UNION SELECT * FROM users--"
curl "http://localhost/product?id=1; DROP TABLE users--"
```

#### Method 2: Using sqlmap (Automated)
```bash
# Install sqlmap
sudo apt-get install sqlmap -y

# Test local web server (if available)
sqlmap -u "http://localhost/search.php?q=test" --batch
```

#### Method 3: Multiple attempts
```bash
# Simulate attacker trying different payloads
PAYLOADS=(
  "1' OR '1'='1"
  "admin'--"
  "1 UNION SELECT NULL--"
  "' OR 1=1--"
  "1; DROP TABLE users--"
)

for payload in "${PAYLOADS[@]}"; do
  curl -s "http://localhost/search.php?q=${payload}" > /dev/null
  echo "Tested: $payload"
done
```

**What Sentinel Should Detect:**

```bash
# View SQL injection incidents
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("SQL"))'

# Expected:
# {
#   "id": "INC-2024-00151",
#   "type": "SQL Injection Attempt",
#   "source_ip": "127.0.0.1",
#   "severity": "CRITICAL",
#   "payload_detected": "OR '1'='1",
#   "url": "/search.php?q=..."
# }

# Check logs
docker-compose logs sentinel-agent | grep -i "sql injection"
```

**Success Criteria:**
- ✅ SQL injection pattern detected
- ✅ Marked as CRITICAL severity
- ✅ Request logged with payload
- ✅ Source IP recorded
- ✅ Quick detection (< 5 seconds)

---

### 3. DDoS Attack (Distributed Denial of Service)

**What it is:** Flooding server with high volume of requests

**Why it matters:** Makes service unavailable to legitimate users

**How to simulate:**

#### Method 1: Using Apache Bench (Simple)
```bash
# Install apache2-utils
sudo apt-get install apache2-utils -y

# Send 1000 requests from single client (simulates local DDoS)
ab -n 1000 -c 50 http://localhost/

# Output shows requests per second
```

#### Method 2: Using wrk (Better for concurrency)
```bash
# Install wrk
sudo apt-get install wrk -y

# Generate high concurrency load (50 concurrent connections for 10 seconds)
wrk -t4 -c50 -d10s http://localhost/

# Output: requests/sec, latency stats
```

#### Method 3: Using hping3 (Network-level)
```bash
# Install hping3
sudo apt-get install hping3 -y

# HTTP flood (flood from single IP - WARNING: system may be slow)
sudo hping3 -S --flood -p 80 127.0.0.1
# Press Ctrl+C after 10 seconds
```

#### Method 4: Bash loop (Simple DDoS)
```bash
# Create heavy load with curl
for i in {1..500}; do
  curl -s http://localhost/ > /dev/null &
done
wait

echo "Sent 500 concurrent requests"
```

**What Sentinel Should Detect:**

```bash
# View DDoS/rate limit incidents
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("DDoS|Rate"))'

# Expected:
# {
#   "id": "INC-2024-00152",
#   "type": "DDoS Attack",
#   "source_ip": "127.0.0.1",
#   "severity": "CRITICAL",
#   "requests_per_sec": 450,
#   "normal_baseline": 10,
#   "spike_factor": "45x"
# }

# Check metrics
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/detection | \
  jq '.throughput_anomalies'
```

**Success Criteria:**
- ✅ High request rate detected
- ✅ Marked as CRITICAL severity
- ✅ Source IP rate-limited or blocked
- ✅ Spike detected vs baseline
- ✅ Auto-mitigation triggered

---

### 4. Brute Force - Web Login

**What it is:** Multiple failed login attempts on web application

**Why it matters:** Gains unauthorized access to accounts

**How to simulate:**

#### Method 1: Using curl loop
```bash
# Simulate 20 failed login attempts
for i in {1..20}; do
  curl -s -X POST http://localhost/login \
    -d "username=admin&password=wrongpass${i}" \
    -H "Content-Type: application/x-www-form-urlencoded" > /dev/null
  echo "Failed attempt $i"
  sleep 0.5
done
```

#### Method 2: Using hydra (Realistic)
```bash
# Create password list
echo -e "admin\nPassword1\nTest123\nWrongPass" > webpass.txt

# Attack web login form
hydra -l admin -P webpass.txt http-post-form \
  "localhost/login:username=^USER^&password=^PASS^:F=404" -t 5 -v
```

#### Method 3: Different usernames
```bash
# Try common usernames
USERS=("admin" "root" "test" "user" "administrator")
PASS="wrongpass"

for user in "${USERS[@]}"; do
  for i in {1..5}; do
    curl -s -X POST "http://localhost/login" \
      -d "username=${user}&password=${PASS}" > /dev/null
  done
done
```

**What Sentinel Should Detect:**

```bash
# View brute force incidents
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("Brute"))'

# Expected:
# {
#   "id": "INC-2024-00153",
#   "type": "Web Brute Force",
#   "source_ip": "127.0.0.1",
#   "severity": "HIGH",
#   "failed_attempts": 20,
#   "target_accounts": ["admin", "root", "test"],
#   "status": "Blocked"
# }
```

**Success Criteria:**
- ✅ Failed attempts counted
- ✅ Marked as HIGH/CRITICAL severity
- ✅ Multiple accounts detected
- ✅ Source IP blocked after threshold
- ✅ Incident logged with details

---

### 5. Port Scanning

**What it is:** Attacker probes open ports to find services

**Why it matters:** Reconnaissance for later attacks

**How to simulate:**

#### Method 1: Using nmap
```bash
# Install nmap
sudo apt-get install nmap -y

# Scan common ports on localhost
nmap -sS -p 22,25,80,443,3306,5432 localhost

# More aggressive scan
nmap -sS -A -T4 localhost
```

#### Method 2: Using hping3
```bash
sudo hping3 -S -p 22,80,443,3306 -c 10 127.0.0.1
```

#### Method 3: Manual TCP connections
```bash
# Attempt connections to various ports
PORTS=(21 22 23 25 80 443 3306 5432 8080 9000)

for port in "${PORTS[@]}"; do
  timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/$port" 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: CLOSED"
done
```

**What Sentinel Should Detect:**

```bash
# View port scan incidents
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("Scan|Probe"))'

# Expected:
# {
#   "id": "INC-2024-00154",
#   "type": "Port Scanning",
#   "source_ip": "127.0.0.1",
#   "severity": "MEDIUM",
#   "ports_scanned": [21, 22, 23, 25, 80, 443],
#   "total_probes": 10,
#   "status": "Detected"
# }
```

**Success Criteria:**
- ✅ Multiple port attempts detected
- ✅ Pattern recognized as scan
- ✅ Source IP logged
- ✅ Medium severity assigned
- ✅ Timeline of attempts recorded

---

### 6. XSS (Cross-Site Scripting)

**What it is:** Malicious JavaScript injected into web pages

**Why it matters:** Steals user sessions and cookies

**How to simulate:**

```bash
# XSS payload examples
PAYLOADS=(
  "<script>alert('XSS')</script>"
  "';alert('XSS');//"
  "<img src=x onerror=alert('XSS')>"
  "<svg onload=alert('XSS')>"
)

# Send via search parameter
for payload in "${PAYLOADS[@]}"; do
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''${payload}'''))")
  curl -s "http://localhost/search?q=${ENCODED}" > /dev/null
done
```

**What Sentinel Should Detect:**

```bash
# View XSS attempts
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("XSS"))'
```

---

### 7. Path Traversal

**What it is:** Accessing files outside intended directory (../../../etc/passwd)

**Why it matters:** Exposes sensitive system files

**How to simulate:**

```bash
# Path traversal payloads
curl "http://localhost/page.php?file=../../../../etc/passwd"
curl "http://localhost/api/files?path=../../config.php"
curl "http://localhost/download?file=../../../etc/shadow"

# Loop of attempts
for i in {1..10}; do
  curl -s "http://localhost/files?path=$(printf '../%.0s' {1..50})etc/passwd" > /dev/null
done
```

**What Sentinel Should Detect:**

```bash
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent | \
  jq '.[] | select(.type | contains("Path|Traversal"))'
```

---

## Verification Methods

### Method 1: Check Incidents API (Real-time)

```bash
# Get incidents from last hour
curl -s -H "X-API-Key: $TOKEN" \
  "http://localhost:8000/api/incidents/recent?hours=1" | jq .

# Get specific incident
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/INC-2024-00150
```

### Method 2: View Docker Logs

```bash
# Real-time logs
docker-compose logs -f sentinel-agent

# Last 100 lines
docker-compose logs --tail 100 sentinel-agent

# Search for specific attack
docker-compose logs sentinel-agent | grep -i "brute force"
docker-compose logs sentinel-agent | grep -i "sql injection"
```

### Method 3: Check Metrics

```bash
# Detection statistics
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/detection | jq .

# Response metrics
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/response | jq .
```

### Method 4: Check Threat Database

```bash
# Get all threat patterns
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/threats/patterns | jq .

# Check if IP was added to threat list
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/lists/blacklisted-ips | jq .
```

### Method 5: Dashboard (Web UI)

```bash
# If dashboard enabled at http://localhost:8501
# 1. Open browser
# 2. Go to http://localhost:8501
# 3. Login with (admin/password)
# 4. View real-time incident charts
# 5. Check top attacking IPs
```

---

## Expected Results

### Successful Detection Results

```json
{
  "Test": "SSH Brute Force (15 attempts)",
  "Result": "✅ PASS",
  "Details": {
    "time_to_detect": 45,
    "severity": "HIGH",
    "anomaly_score": 0.87,
    "action_taken": "IP flagged",
    "incident_logged": "INC-2024-00150"
  }
}
```

### Test Summary Template

Create file: `test_results.json`

```bash
cat > test_results.json << 'EOF'
{
  "test_date": "2024-02-07",
  "sentinel_version": "2.2",
  "tests": [
    {
      "attack_type": "SSH Brute Force",
      "status": "PASS",
      "detected": true,
      "time_to_detect_sec": 45,
      "severity": "HIGH",
      "incidents_created": 1
    },
    {
      "attack_type": "SQL Injection",
      "status": "PASS",
      "detected": true,
      "time_to_detect_sec": 2,
      "severity": "CRITICAL",
      "incidents_created": 1
    },
    {
      "attack_type": "DDoS",
      "status": "PASS",
      "detected": true,
      "time_to_detect_sec": 8,
      "severity": "CRITICAL",
      "incidents_created": 1
    }
  ],
  "summary": {
    "total_tests": 3,
    "passed": 3,
    "failed": 0,
    "detection_rate": 1.0
  }
}
EOF

# View results
jq . test_results.json
```

---

## Troubleshooting Tests

### Issue: Attack not detected

**Troubleshoot:**

```bash
# 1. Check if Sentinel Agent is running
docker-compose ps
# Should show: sentinel-agent   Up (healthy)

# 2. Verify logs are being monitored
docker-compose logs sentinel-agent | head -20

# 3. Check if log files exist
docker-compose exec sentinel-agent ls -la /var/log/auth.log
docker-compose exec sentinel-agent ls -la /var/log/apache2/access.log

# 4. Manually test log entry
docker-compose exec sentinel-agent bash -c 'echo "Test log entry" >> /var/log/auth.log'

# 5. Check if AI can analyze
curl -s -X POST http://localhost:8000/api/anomaly/score \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"127.0.0.1","attack_type":"test","severity":"high"}' | jq .
```

### Issue: False Positives

**Reduce false positives:**

```bash
# 1. Whitelist legitimate IPs
curl -X POST http://localhost:8000/api/lists/whitelist-ip \
  -H "X-API-Key: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "127.0.0.1",
    "reason": "Testing system - ignore alerts",
    "added_by": "admin"
  }'

# 2. Check baseline metrics
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/detection | jq '.false_positive_rate'
```

### Issue: Slow Detection

**Speed up tests:**

```bash
# 1. Check Ollama latency
curl http://localhost:11434/api/tags

# 2. View API logs
docker-compose logs sentinel-agent | grep -i "latency"

# 3. Check system resources
docker stats sentinel-agent
# If CPU is high, reduce concurrent tests

# 4. Increase timeout
for i in {1..30}; do
  ssh -o StrictHostKeyChecking=no wrong@localhost 2>/dev/null || true
  sleep 0.2  # Add delay between attempts
done
```

---

## Performance Testing

### Load Test: Multiple Simultaneous Attacks

```bash
#!/bin/bash
# test_full_load.sh - Run multiple attacks concurrently

TOKEN="your_token"

# Function 1: SSH attacks
ssh_attacks() {
  for i in {1..20}; do
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=1 wrong@localhost 2>/dev/null || true
  done
}

# Function 2: Web requests
web_attacks() {
  for i in {1..100}; do
    curl -s "http://localhost/search?q=1' OR '1'='1" > /dev/null &
  done
  wait
}

# Function 3: API calls to check detection
check_detection() {
  sleep 5
  curl -s -H "X-API-Key: $TOKEN" \
    http://localhost:8000/api/metrics/detection | jq '.total_events_analyzed'
}

# Run all concurrently
ssh_attacks &
SSH_PID=$!
web_attacks &
WEB_PID=$!

wait $SSH_PID $WEB_PID

echo "Attacks completed. Checking detection..."
check_detection
```

**Expected Performance:**
- Detection time: < 2 seconds for SQL injection
- Detection time: 30-60 seconds for pattern-based attacks
- Throughput: 100+ API calls/second
- False positive rate: < 5%

---

## Cleanup After Testing

```bash
# Remove test whitelisting
curl -X DELETE http://localhost:8000/api/lists/remove-ip \
  -H "X-API-Key: $TOKEN" \
  -d '{"ip":"127.0.0.1"}'

# Clear incident logs (optional)
# Note: No API endpoint - must stop container and clear database
docker-compose down
rm -rf data/*.db  # WARNING: Deletes all data
docker-compose up -d

# Export test results
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/incidents/recent > test_incidents.json
curl -s -H "X-API-Key: $TOKEN" \
  http://localhost:8000/api/metrics/dashboard > test_metrics.json
```

---

## Test Checklist

Use this checklist to verify all attack types are detected:

```
Attack Type                Status     Time    Severity   Notes
────────────────────────────────────────────────────────────────
☐ SSH Brute Force          [ ]       ___s    [H/C]      _______
☐ SQL Injection            [ ]       ___s    [H/C]      _______
☐ DDoS/Rate Limit          [ ]       ___s    [H/C]      _______
☐ Web Brute Force          [ ]       ___s    [H/C]      _______
☐ Port Scanning            [ ]       ___s    [H/C]      _______
☐ XSS Attack               [ ]       ___s    [H/C]      _______
☐ Path Traversal           [ ]       ___s    [H/C]      _______

Legend: H=High, C=Critical, ___s=seconds to detect
```

---

## Additional Resources

- [USER_GUIDE.md](USER_GUIDE.md) - End-user features
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment and setup
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Troubleshooting
- **API Docs:** http://localhost:8000/docs

---

**Last Updated:** February 2024 | **Version:** 2.2 | **Status:** Production Ready
