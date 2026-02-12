# ⚡ QUICK START - 5-Minute Setup

**Easiest way to get Sentinel Agent running!**

---

## 🎯 Method 1: One-Command Setup (Recommended)

```bash
# 1. Start Ollama (in separate terminal)
ollama serve

# 2. Run quick rebuild script
chmod +x quick-rebuild.sh
./quick-rebuild.sh

# 3. Test authentication
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

**Done!** System fully operational in ~5 minutes. ✅

---

## 📋 What Gets Automated

### quick-rebuild.sh ⭐
- ✅ Stops old containers
- ✅ Cleans data (handles sudo for Docker files)
- ✅ Rebuilds with all dependencies
- ✅ Starts fresh with new credentials
- ✅ Shows admin password

### sentinel_auto.py setup
- ✅ Waits for container health
- ✅ Extracts password from logs
- ✅ Authenticates and saves token

### sentinel_auto.py demo
- ✅ Generates 40+ attacks
- ✅ Shows AI analysis
- ✅ Displays performance metrics

---

## 🛠️ Method 2: Manual Setup

```bash
# 1. Start Ollama
ollama serve  # Terminal 1

# 2. Clean and rebuild (Terminal 2)
docker-compose down -v
sudo rm -rf data/ logs/
docker-compose build --no-cache
docker-compose up -d

# 3. Wait for healthy
sleep 60
docker-compose ps  # Should show "healthy"

# 4. Get password
docker-compose logs sentinel-agent | grep "Password:"

# 5. Authenticate
python3 sentinel_auto.py setup
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
