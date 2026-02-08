# Sentinel Agent - Automation Tools

Complete automation for setup, testing, and monitoring. No manual commands needed!

> **⚠️ Fresh Clone?** If you just cloned this repo, reset the database first:
> ```bash
> docker-compose down
> rm -f data/auth.db data/INITIAL_CREDENTIALS.txt
> docker-compose build --no-cache
> docker-compose up -d
> sleep 5
> ```
> Then proceed below. See [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) for complete instructions.

---

## 🚀 Quick Start (5 Minutes)

### **Option 1: Python (Easiest - All Systems)**

```bash
# Install dependency (one-time)
pip install requests

# Run complete setup and demo
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
python3 sentinel_auto.py status
```

### **Option 2: Bash (Linux/macOS)**

```bash
# Make script executable
chmod +x sentinel_setup.sh

# Run complete setup and demo
./sentinel_setup.sh setup
./sentinel_setup.sh demo
./sentinel_setup.sh status
```

---

## 📋 What Gets Automated

| Task | Manual | Automated | Time Saved |
|------|--------|-----------|-----------|
| Extract password from logs | `docker-compose logs \| grep...` | ✅ Automatic | 5 min |
| Get API token | `curl -X POST...` | ✅ Automatic | 3 min |
| Verify container health | Check 10+ times | ✅ Auto-wait | 10 min |
| Run SSH brute force test | 20 manual commands | ✅ Loop | 10 min |
| Run SQL injection test | 5-10 manual requests | ✅ All payloads | 5 min |
| Run DDoS test | Manual concurrent requests | ✅ 100 requests | 5 min |
| Check for incidents | Manual API calls | ✅ Auto check + wait | 10 min |
| Generate report | Copy/paste results | ✅ JSON files | 5 min |
| **TOTAL** | **48 Minutes** | **2 Minutes** | **96% Time Saved!** |

---

## 📂 Available Tools

### **Python Tool: sentinel_auto.py**

**Best for:** All systems (Windows, Linux, macOS) - simpler syntax

```bash
python3 sentinel_auto.py [COMMAND]
```

**Commands:**
```bash
setup          # Extract password & get token
demo           # Run ALL attacks and get results
status         # Show live dashboard
test-ssh       # SSH brute force only
test-sql       # SQL injection only
test-ddos      # DDoS attack only
check          # Check for incidents
help           # Show help
```

**Examples:**

```bash
# First time: Get password and token
python3 sentinel_auto.py setup

# Run everything automatically
python3 sentinel_auto.py demo

# View live status dashboard
python3 sentinel_auto.py status

# Check for detected incidents
python3 sentinel_auto.py check
```

---

### **Bash Tool: sentinel_setup.sh**

**Best for:** Linux/macOS developers who prefer bash

```bash
./sentinel_setup.sh [COMMAND]
```

**Commands:**
```bash
setup          # Extract password & get token
demo           # Run ALL attacks and get results
status         # Show live dashboard
test-ssh       # SSH brute force only
test-sql       # SQL injection only
test-ddos      # DDoS attack only
check          # Check for incidents
help           # Show help
```

**Examples:**

```bash
chmod +x sentinel_setup.sh
./sentinel_setup.sh setup
./sentinel_setup.sh demo
./sentinel_setup.sh status
```

---

## 🎯 Common Workflows

### **Workflow 1: First-Time Setup**

```bash
# Python
python3 sentinel_auto.py setup

# OR Bash
chmod +x sentinel_setup.sh
./sentinel_setup.sh setup
```

**What happens:**
1. ✅ Waits for container to be healthy
2. ✅ Extracts admin password from logs
3. ✅ Authenticates and gets API token
4. ✅ Gets baseline metrics
5. ✅ Saves everything to files

**Output files:**
- `.sentinel_password` - Your admin password
- `.sentinel_token` - 24-hour API token
- `test_results/baseline_metrics.json` - Starting metrics

---

### **Workflow 2: Run Full Detection Demo**

```bash
python3 sentinel_auto.py demo
```

**What happens (5-7 minutes):**
1. ✅ Gets baseline metrics
2. ✅ Simulates 20 SSH brute force attacks
3. ✅ Tests 4 SQL injection payloads
4. ✅ Sends 100 concurrent DDoS requests
5. ✅ Waits for analysis
6. ✅ Checks for detected incidents
7. ✅ Generates report with results

**Example Output:**
```
Baseline captured (42 events, 3 threats)
SSH brute force test completed (20 attempts)
SQL injection test completed
DDoS test completed (100 requests)
✓ Found 3 incidents
  • SSH Brute Force (HIGH) from 127.0.0.1
  • SQL Injection Attempt (CRITICAL) from 127.0.0.1
  • Rate Limit Exceeded (CRITICAL) from 127.0.0.1
```

---

### **Workflow 3: Individual Attack Tests**

```bash
# Test SSH brute force only
python3 sentinel_auto.py test-ssh

# Test SQL injection only
python3 sentinel_auto.py test-sql

# Test DDoS only
python3 sentinel_auto.py test-ddos

# Check if attacks were detected
python3 sentinel_auto.py check
```

---

### **Workflow 4: Live Status Dashboard**

```bash
python3 sentinel_auto.py status
```

**Shows:**
- System health (status, version, uptime)
- Detection metrics (events analyzed, threats detected, rate)
- Recent incidents (last 3)
- IP lists (whitelisted/blacklisted count)

**Refresh every 30 seconds:**
```bash
watch -n 30 'python3 sentinel_auto.py status'
```

---

## 📊 Output Files

### **Location:** `test_results/` directory

```
test_results/
├── baseline_metrics.json      # Initial system state
├── incidents.json             # All detected incidents
├── current_metrics.json       # Latest metrics
└── [timestamp]_report.json    # Full test report
```

**Example baseline_metrics.json:**
```json
{
  "total_events_analyzed": 42,
  "threats_detected": 3,
  "detection_rate": 0.071,
  "most_common_threat": "SSH Brute Force",
  "avg_analysis_time_ms": 45
}
```

**Example incidents.json:**
```json
[
  {
    "id": "INC-2024-00150",
    "timestamp": "2024-02-07T15:30:00Z",
    "type": "SSH Brute Force",
    "source_ip": "127.0.0.1",
    "severity": "HIGH",
    "fail_count": 20,
    "status": "Flagged"
  },
  {
    "id": "INC-2024-00151",
    "timestamp": "2024-02-07T15:31:00Z",
    "type": "SQL Injection Attempt",
    "source_ip": "127.0.0.1",
    "severity": "CRITICAL",
    "payload_detected": "OR '1'='1",
    "status": "Blocked"
  }
]
```

---

## 🔧 Installation & Setup

### **Python Requirements**

```bash
# Check Python version
python3 --version
# Should be 3.7 or higher

# Install requests library (one-time)
pip3 install requests

# Verify installation
python3 -c "import requests; print('✓ requests installed')"
```

### **Bash Requirements**

- Linux or macOS
- `bash`, `curl`, `jq`, `docker-compose`
- All usually pre-installed

```bash
# Verify tools
which docker-compose curl jq
```

---

## 📍 Where to Run

**From project root directory:**

```bash
cd ~/Project  # or wherever you cloned it

# Python tool
python3 sentinel_auto.py setup

# OR Bash tool
./sentinel_setup.sh setup
```

**Files created in:**
- `.sentinel_password` - Project root
- `.sentinel_token` - Project root
- `test_results/` - Project root directory

---

## 🔐 Security

**Passwords are readable files!**

```bash
# The scripts save password/token to files for convenience
# In production, use environment variables:

echo "YOUR_PASSWORD" > .env
source .env
# Keep .env in .gitignore
```

**Tokens expire in 24 hours:**
```bash
# Old token expired? Get a new one:
python3 sentinel_auto.py setup
```

---

## 🛠️ Troubleshooting

### **Problem: "requests module not found"**

```bash
# Python tool needs the requests library
pip3 install requests

# Or for system Python
sudo pip3 install requests
```

### **Problem: "Container not healthy"**

```bash
# Is Sentinel running?
docker-compose ps

# Start it
docker-compose up -d

# Check logs
docker-compose logs sentinel-agent
```

### **Problem: "No incidents detected"**

Possible reasons:
- Log files don't exist (need Apache & SSH running)
- Insufficient time for analysis (wait 60+ seconds)
- Attacks didn't trigger patterns
- Check logs: `docker-compose logs sentinel-agent`

**Solution:**
```bash
# Make sure SSH is running
sudo systemctl start ssh

# Make sure Apache is running
sudo systemctl start apache2

# Then try again
python3 sentinel_auto.py test-ssh
sleep 60
python3 sentinel_auto.py check
```

### **Problem: "Permission denied" on .sentinel_token**

```bash
# Fix permissions
chmod 600 .sentinel_token
chmod 600 .sentinel_password
```

### **Problem: "API token is unauthorized (401)"**

```bash
# Token expired or invalid - get a new one
python3 sentinel_auto.py setup

# This extracts new password and gets new token
```

---

## 📈 Advanced Usage

### **Continuous Monitoring**

Watch dashboard every 30 seconds:
```bash
watch -n 30 'python3 sentinel_auto.py status'
```

### **Scheduled Testing**

Test daily at 2 AM (cron):
```bash
# Add to crontab
0 2 * * * cd /home/user/Project && python3 sentinel_auto.py demo >> test_log.txt 2>&1
```

### **Custom Attack Parameters**

Edit `.py` or `.sh` file:

```python
# In sentinel_auto.py, change:
def test_ssh_brute_force(attempts: int = 20) -> bool:
    # Change 20 to higher number for more attacks
```

```bash
# In sentinel_setup.sh, change:
ATTEMPTS=20
# Change to higher number
```

### **Integration with CI/CD**

```bash
#!/bin/bash
# Called by GitHub Actions/Jenkins/GitLab CI

python3 sentinel_auto.py setup
python3 sentinel_auto.py demo

# Check if incidents were found
if [ -f "test_results/incidents.json" ]; then
    COUNT=$(jq 'length' test_results/incidents.json)
    if [ "$COUNT" -gt 0 ]; then
        echo "✓ Tests passed: Detected $COUNT incidents"
        exit 0
    fi
fi

echo "✗ Tests failed: No incidents detected"
exit 1
```

---

## 📚 Additional Resources

- **USER_GUIDE.md** - End-user features
- **ATTACK_TESTING_GUIDE.md** - Detailed attack examples
- **DEPLOYMENT_GUIDE.md** - Full deployment info
- **API Docs** - http://localhost:8000/docs

---

## 💡 Tips & Tricks

### **Batch Testing**

```bash
# Run 5 demos in sequence
for i in {1..5}; do
  echo "Run $i of 5"
  python3 sentinel_auto.py demo
  sleep 300  # Wait 5 minutes between runs
done
```

### **Performance Testing**

```bash
# Increase attack intensity
# Edit and change:
# - test_ssh_brute_force(attempts=50)
# - test_ddos(requests_count=500)
```

### **Export Results**

```bash
# Convert to CSV for analysis
python3 << 'EOF'
import json
incidents = json.load(open("test_results/incidents.json"))
print("Type,Severity,Source IP,Status")
for inc in incidents:
    print(f"{inc['type']},{inc['severity']},{inc['source_ip']},{inc['status']}")
EOF
```

---

## ⚡ Performance

Typical execution times:

| Command | Time |
|---------|------|
| `setup` | 30-60 sec |
| `demo` | 5-7 min |
| `status` | < 1 sec |
| `check` | 30 sec |

---

## 🚀 Summary

**With automation tools:**
- ✅ No manual password extraction
- ✅ No manual token generation
- ✅ No manual attack scripting
- ✅ Automated result checking
- ✅ JSON report generation
- ✅ Single command testing

**From 48 minutes → 2 minutes!**

---

**Version:** 2.0 | **Updated:** February 2024
