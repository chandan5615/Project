# ⚡ QUICK START - 2-Minute Setup

Copy & paste these commands. That's it!

> ⚠️ **Fresh Clone from GitHub?** First reset the database:
> ```bash
> docker-compose down
> rm -f data/auth.db data/INITIAL_CREDENTIALS.txt
> docker-compose build --no-cache
> docker-compose up -d
> sleep 5
> ```
> Then follow the steps below.
> 
> **📖 For complete guide:** See [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md)

---

## 🚀 Option A: Python (Recommended - All Systems)

```bash
# 1. Install dependency (one-time)
pip3 install requests

# 2. Complete setup + demo
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo

# 3. View results
python3 sentinel_auto.py status
```

---

## 🐚 Option B: Bash (Linux/macOS)

```bash
# 1. Make executable
chmod +x sentinel_setup.sh

# 2. Complete setup + demo
./sentinel_setup.sh setup
./sentinel_setup.sh demo

# 3. View results
./sentinel_setup.sh status
```

---

## 📊 What You'll See

**After setup:**
```
✓ Container is healthy
✓ Password extracted: s3cur3Rand0mP@ssw0rd123...
✓ API token obtained: eyJhbGc...
✓ Baseline captured (42 events, 3 threats)
```

**After demo (5-7 minutes later):**
```
✓ SSH brute force test completed (20 attempts)
✓ SQL injection test completed
✓ DDoS test completed (100 requests)
✓ Found 3 incidents
  • SSH Brute Force (HIGH) from 127.0.0.1
  • SQL Injection Attempt (CRITICAL) from 127.0.0.1
  • Rate Limit Exceeded (CRITICAL) from 127.0.0.1
```

**Status dashboard:**
```
System Health:
  Status: healthy
  Version: 2.2
  Uptime: 3600s

Detection Metrics:
  Total Events: 1542
  Threats Detected: 142
  Detection Rate: 9.2%
```

---

## 🎯 Individual Commands

```bash
# Get password only
python3 sentinel_auto.py password

# Get API token only
python3 sentinel_auto.py token

# Run SSH test only
python3 sentinel_auto.py test-ssh

# Run SQL injection test only
python3 sentinel_auto.py test-sql

# Run DDoS test only
python3 sentinel_auto.py test-ddos

# Check for detected incidents
python3 sentinel_auto.py check

# View status dashboard
python3 sentinel_auto.py status

# Help & all commands
python3 sentinel_auto.py help
```

---

## 📁 Files Created

After running setup:
```
.sentinel_password       ← Your admin password
.sentinel_token          ← API token for 24 hours
test_results/            ← All test results
  ├── baseline_metrics.json
  ├── incidents.json
  └── current_metrics.json
```

---

## ✅ What Gets Automated

| Task | Before | With Automation |
|------|--------|-----------------|
| Extract password | 5 manual steps | 10 seconds ⚡ |
| Get API token | `curl -X POST...` | Automatic |
| Run all attacks | 30+ manual commands | 1 command |
| Check results | Multiple API calls | 1 command |
| Generate report | Manual copy-paste | JSON files |
| **Total time** | **48 minutes** | **2 minutes** |

---

## 🆘 Troubleshooting

**"requests module not found"**
```bash
pip3 install requests
```

**"Permission denied"**
```bash
chmod +x sentinel_setup.sh
chmod +x sentinel_auto.py
```

**"Container not healthy"**
```bash
docker-compose up -d
docker-compose logs sentinel-agent
```

**"No incidents detected"**
```bash
# Make sure services are running
sudo systemctl start ssh
sudo systemctl start apache2

# Try again
python3 sentinel_auto.py test-ssh
sleep 60
python3 sentinel_auto.py check
```

---

## 📚 Read More

- **Automation details:** [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
- **Manual testing guide:** [docs_markdown/ATTACK_TESTING_GUIDE.md](docs_markdown/ATTACK_TESTING_GUIDE.md)
- **User features:** [docs_markdown/USER_GUIDE.md](docs_markdown/USER_GUIDE.md)

---

## 🎉 That's It!

Run this single line to test everything:

```bash
python3 sentinel_auto.py demo
```

Done! ✨
