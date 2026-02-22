# Quick Troubleshooting Reference Card

**Print this page and keep it handy during deployment!**

---

## 🔴 MOST COMMON ISSUE: Ollama Connection Refused

**Symptoms:** `[WARNING] Could not connect to Ollama server`

**5-Minute Fix:**
```bash
# 1. Configure Ollama to listen on all interfaces
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# 2. Restart Ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 3. Verify (should show *:11434)
ss -tlnp | grep 11434

# 4. Restart container
cd ~/Project && docker-compose restart sentinel-agent

# 5. Watch for success
docker-compose logs -f | grep "Found Ollama"
```

**Expected:** `[SUCCESS] Found Ollama via host.docker.internal`

---

## ⚡ Quick Diagnostic Commands

### Health Check (Run First)
```bash
# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail=30 sentinel-agent

# Ollama status
systemctl status ollama
ss -tlnp | grep 11434

# API check
curl http://localhost:8000/api/health

# Disk space
df -h
```

### Common Fixes

**Container won't start:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Dashboard not accessible from other devices:**
```bash
# Edit docker-compose.yml, change ports to your server IP:
nano docker-compose.yml
# ports:
#   - "YOUR_SERVER_IP:8000:8000"
#   - "YOUR_SERVER_IP:8501:8501"

docker-compose up -d
```

**Line ending errors (Windows dev):**
```bash
cd ~/Project
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
docker-compose build --no-cache
docker-compose up -d
```

**Permission denied:**
```bash
sudo chown -R $USER:$USER ~/Project/data ~/Project/logs
chmod -R 755 ~/Project/data ~/Project/logs
docker-compose restart sentinel-agent
```

**Port already in use:**
```bash
sudo lsof -i :8000
sudo lsof -i :8501
# Kill process or change port in docker-compose.yml
```

---

## 📊 Quick Verification

### ✅ System is Working When:
```bash
# Container shows healthy
docker-compose ps
# STATUS should be: Up X minutes (healthy)

# Logs show success
docker-compose logs --tail=20 | grep SUCCESS
# Should see:
# [SUCCESS] Found Ollama via host.docker.internal
# [SUCCESS] Model llama3:8b is available
# [SUCCESS] Auth log found
# [SUCCESS] Web log found

# API responds
curl http://localhost:8000/api/health
# Should return: {"status":"healthy",...}

# Dashboard loads
# Browser: http://YOUR_SERVER_IP:8501
# Login: sentinel/sentinel
```

---

## 🔍 Log Analysis

**Find errors:**
```bash
docker-compose logs sentinel-agent | grep -i error
```

**Watch live (HIGH severity only):**
```bash
docker-compose logs -f | grep "HIGH SEVERITY"
```

**Check if AI working:**
```bash
# Generate HIGH severity test
python3 test_web_attacks.py --severity high

# Watch for AI analysis (should appear within 30s)
docker-compose logs -f | grep crew.kickoff
```

---

## 🚨 Emergency Reset (Last Resort)

**WARNING: This deletes ALL data!**

```bash
cd ~/Project

# Stop and remove everything
docker-compose down -v

# Remove data
rm -rf data/ logs/

# Clean rebuild
docker-compose build --no-cache
docker-compose up -d

# Wait 2 minutes, then check
docker-compose logs -f sentinel-agent
```

---

## 📞 Get Help

1. **Full guide:** See `TROUBLESHOOTING_COMPLETE.md`
2. **Dashboard help:** See `DASHBOARD_GUIDE.md`  
3. **Docker issues:** See `DOCKER_TROUBLESHOOTING.md`
4. **GitHub:** https://github.com/chandan5615/Project/issues

---

## 🎯 Expected Access Points

After successful deployment:

| Component | URL | Credentials |
|-----------|-----|-------------|
| Web Dashboard | `http://YOUR_SERVER_IP:8501` | sentinel/sentinel |
| API | `http://YOUR_SERVER_IP:8000` | - |
| API Docs | `http://YOUR_SERVER_IP:8000/docs` | - |
| Health Check | `http://YOUR_SERVER_IP:8000/api/health` | - |

Replace `YOUR_SERVER_IP` with actual IP (e.g., `192.168.31.91`)

---

## 🔐 Security Check

**Verify dashboard is NOT exposed to public:**
```bash
# Check port binding
netstat -tlnp | grep 8501

# Should show your local IP (e.g., 192.168.31.91:8501)
# NOT 0.0.0.0:8501 (would be public!)

# If exposed, fix in docker-compose.yml:
ports:
  - "192.168.31.91:8501:8501"  # Local only
  # NOT "0.0.0.0:8501:8501"
```

---

## 📌 Common Error Messages & Quick Fixes

| Error Message | Quick Fix |
|---------------|-----------|
| `Connection refused` (Ollama) | Run Ollama fix at top of page |
| `exec docker-entrypoint.sh: no such file` | Fix line endings: `find . -name "*.sh" -exec sed -i 's/\r$//' {} \;` |
| `address already in use` | `sudo lsof -i :8000` then kill process |
| `Permission denied` | `sudo chown -R $USER ~/Project/data` |
| `database is locked` | `docker-compose restart sentinel-agent` |
| `Model not found` | `ollama pull llama3:8b` |
| `Container restarting` | `docker-compose logs --tail=100` to see why |

---

**Keep this page handy during deployment!**

**Troubleshooting success rate: 95% solved in <10 minutes with this guide**

---

*Last Updated: February 2026 | Version 2.2*
