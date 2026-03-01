# [CONFIG] Complete Troubleshooting Guide - Sentinel Agent

**Last Updated:** February 2026  
**Version:** 2.2

This guide covers **all known issues** and their solutions, plus potential future problems.

---

## Table of Contents

1. [[CRITICAL] Critical Issues](#-critical-issues)
2. [[DOCKER] Docker & Container Issues](#-docker--container-issues)
3. [[WEB] Network & Connectivity](#-network--connectivity)
4. [[AI] Ollama & AI Issues](#-ollama--ai-issues)
5. [[STATS] Dashboard Problems](#-dashboard-problems)
6. [[SECURE] Security & Permissions](#-security--permissions)
7. [[FAST] Performance Issues](#-performance-issues)
8. [[DB] Database Problems](#-database-problems)
9. [[FUTURE] Potential Future Issues](#-potential-future-issues)
10. [[TOOLS] Diagnostic Tools](#-diagnostic-tools)

---

## [CRITICAL] Critical Issues

### Issue 1: Ollama Connection Refused (MOST COMMON)

**Symptoms:**
```
[WARNING] Could not connect to Ollama server
   Tried: http://127.0.0.1:11434 and http://ollama:11434
WARNING:agents: Cannot reach Ollama server at http://127.0.0.1:11434
   Error: [Errno 111] Connection refused
```

**Root Cause:**  
Ollama service is listening only on `127.0.0.1:11434` (localhost interface). Docker containers in bridge network mode cannot reach the host's localhost - they need Ollama to be accessible on all network interfaces.

**Why This Happens:**
- Default Ollama installation binds to localhost only for security
- Docker bridge network isolates container networking
- `host.docker.internal` routes to host, but host isn't listening on that interface

**Complete Solution:**

**Step 1: Verify the problem**
```bash
# Check what interface Ollama is listening on
ss -tlnp | grep 11434

# If output shows:
# LISTEN 127.0.0.1:11434  <- PROBLEM (localhost only)
# If output shows:
# LISTEN *:11434          <- GOOD (all interfaces)
```

**Step 2: Configure Ollama to listen on all interfaces**
```bash
# Create systemd service override
sudo mkdir -p /etc/systemd/system/ollama.service.d/

sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

# Reload systemd daemon
sudo systemctl daemon-reload

# Restart Ollama with new configuration
sudo systemctl restart ollama

# Wait for Ollama to start
sleep 5

# Verify it's now listening on all interfaces
ss -tlnp | grep 11434
# Should show: LISTEN *:11434 or 0.0.0.0:11434
```

**Step 3: Test connectivity from container**
```bash
# Test from host
curl http://localhost:11434/api/tags

# Test from external IP (should work now)
curl http://192.168.31.91:11434/api/tags  # Replace with your IP

# Test from inside container
docker exec sentinel-agent curl http://host.docker.internal:11434/api/tags
```

**Step 4: Restart Sentinel container**
```bash
cd ~/Project
docker-compose restart sentinel-agent

# Watch logs for success message
docker-compose logs -f sentinel-agent | grep -E "(Ollama|SUCCESS)"
```

**Expected Success Output:**
```
Detecting Ollama server...
[SUCCESS] Found Ollama via host.docker.internal at http://host.docker.internal:11434
[SUCCESS] Model llama3:8b is available
[OK] Ollama server is reachable at http://host.docker.internal:11434
```

**Security Note:**  
Opening Ollama to `0.0.0.0` makes it accessible on your local network. If this is a concern:

```bash
# Option 1: Bind only to specific IP
Environment="OLLAMA_HOST=192.168.31.91:11434"

# Option 2: Use firewall rules
sudo ufw allow from 172.16.0.0/12 to any port 11434  # Docker subnet only
```

**Alternative: Docker Ollama (Isolated)**
```bash
# Edit docker-compose.yml - uncomment ollama service
nano docker-compose.yml

# Run with Docker Ollama profile
docker-compose --profile with-ollama up -d
```

---

### Issue 2: Line Endings (Windows Development)

**Symptoms:**
```
exec /usr/local/bin/docker-entrypoint.sh: no such file or directory
Container exits immediately with code 1
```

**Root Cause:**  
Script files edited on Windows have CRLF line endings (`\r\n`) instead of Unix LF (`\n`). Linux shells interpret the shebang as `#!/bin/bash\r` which is an invalid path.

**Detection:**
```bash
# Check for Windows line endings
file docker-entrypoint.sh
# Bad:  ASCII text, with CRLF line terminators
# Good: ASCII text
```

**Solutions:**

**Option 1: Automatic fix (Dockerfile already does this)**
```dockerfile
# The Dockerfile includes this fix:
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh
```

**Option 2: Manual fix on server**
```bash
cd ~/Project

# Convert line endings for all shell scripts
find . -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Option 3: Fix in Git (Development)**
```bash
# On Windows development machine
git config --global core.autocrlf input

# Re-clone repository
rm -rf Project/
git clone https://github.com/chandan5615/Project.git
```

**Prevention:**
```bash
# In repository, create .gitattributes file:
cat > .gitattributes <<EOF
* text=auto
*.sh text eol=lf
*.py text eol=lf
*.yml text eol=lf
EOF

git add .gitattributes
git commit -m "Fix line endings"
```

---

## [DOCKER] Docker & Container Issues

### Issue 3: Container Constantly Restarting

**Symptoms:**
```bash
docker-compose ps
# Shows: Restarting (1) Less than a second ago
```

**Diagnosis:**
```bash
# View recent logs
docker-compose logs --tail=200 sentinel-agent

# Check for crashed processes
docker-compose logs sentinel-agent | grep -E "(Error|Exception|Killed|Exited)"

# Check exit code
docker inspect sentinel-agent --format='{{.State.ExitCode}}'
```

**Common Causes & Fixes:**

**Cause 1: Missing dependencies**
```bash
# Rebuild with no cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Cause 2: Out of memory**
```bash
# Check memory
free -h

# Increase container memory limit (docker-compose.yml)
services:
  sentinel-agent:
    mem_limit: 4g  # Increase if needed
    mem_reservation: 2g
```

**Cause 3: Corrupted database**
```bash
# Backup and reset database
cp data/sentinel_intel.db data/sentinel_intel.db.backup
rm data/sentinel_intel.db

docker-compose restart sentinel-agent
```

---

### Issue 4: Docker Build Fails

**Symptoms:**
```
ERROR [internal] load metadata for docker.io/library/python:3.10-slim
failed to solve with frontend dockerfile.v0
```

**Solutions:**

**Network issues:**
```bash
# Add DNS to Docker daemon
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

sudo systemctl restart docker
```

**Disk space:**
```bash
# Check available space
df -h /var/lib/docker

# Clean Docker cache
docker system prune -a --volumes
```

**Docker daemon issues:**
```bash
# Restart Docker
sudo systemctl restart docker

# Check Docker status
sudo systemctl status docker
```

---

### Issue 5: Volume Permission Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/app/data/sentinel_intel.db'
```

**Solution:**
```bash
# Check volume ownership
ls -la ~/Project/data
ls -la ~/Project/logs

# Fix permissions (container runs as appuser)
sudo chown -R 1000:1000 ~/Project/data
sudo chown -R 1000:1000 ~/Project/logs
sudo chmod -R 755 ~/Project/data ~/Project/logs

# Restart
docker-compose restart sentinel-agent
```

---

## [WEB] Network & Connectivity

### Issue 6: Can't Access Dashboard from Remote Machine

**Symptoms:**
- Dashboard works on server: `http://localhost:8501` [OK]
- Dashboard fails from other devices: `http://SERVER_IP:8501` [ERROR]
- Browser error: "Connection refused" or "Timeout"

**Diagnosis:**
```bash
# Check port binding
docker-compose ps
# Look at PORTS column

# Check if port is listening
netstat -tlnp | grep 8501
# OR
ss -tlnp | grep 8501
```

**Causes & Solutions:**

**Cause 1: Wrong port binding in docker-compose.yml**
```yaml
# WRONG (only localhost):
ports:
  - "127.0.0.1:8501:8501"

# WRONG (may not work on all systems):
ports:
  - "8501:8501"

# CORRECT (specific IP for local network):
ports:
  - "192.168.31.91:8501:8501"  # Replace with YOUR server IP
```

**Cause 2: Firewall blocking**
```bash
# Check firewall status
sudo ufw status

# Allow port for local network
sudo ufw allow from 192.168.31.0/24 to any port 8501
sudo ufw allow from 192.168.31.0/24 to any port 8000
sudo ufw reload

# Or temporarily disable for testing
sudo ufw disable
```

**Cause 3: Wrong IP address used**
```bash
# Find your server's IP
ip addr show | grep "inet "

# Or
hostname -I

# Update docker-compose.yml with correct IP
nano docker-compose.yml
# Then restart
docker-compose down && docker-compose up -d
```

---

### Issue 7: Port Already in Use

**Symptoms:**
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :8000
sudo lsof -i :8501

# Kill the process
sudo kill -9 <PID>

# OR change Sentinel's port in docker-compose.yml
ports:
  - "YOUR_IP:9000:8000"  # External port 9000, internal 8000
  - "YOUR_IP:9501:8501"
```

---

### Issue 8: Container Can't Reach Internet

**Symptoms:**
```
Failed to establish connection to pypi.org
DNS resolution failed
```

**Solution:**
```bash
# Check Docker network
docker network ls
docker network inspect sentinel-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Check DNS in container
docker exec sentinel-agent cat /etc/resolv.conf

# Fix DNS (add to docker-compose.yml)
services:
  sentinel-agent:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

---

## [AI] Ollama & AI Issues

### Issue 9: Model Not Found

**Symptoms:**
```
[WARNING] Model llama3:8b not found
Model 'llama3:8b' not found
```

**Solution:**
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3:8b

# Wait for download (4.7GB)
# Verify
ollama list | grep llama3

# Restart container
docker-compose restart sentinel-agent
```

---

### Issue 10: AI Analysis Not Working (Expected Behavior)

**This is NORMAL for MEDIUM/LOW severity attacks!**

The system is optimized to conserve resources:
- [OK] **HIGH severity** → AI crew analysis (SQL injection, XSS, etc.)
- [DOCS] **MEDIUM/LOW severity** → Fast logging without AI (90% of attacks)

**Verify it's working correctly:**
```bash
# Generate HIGH severity test
python3 test_web_attacks.py --severity high

# Search for AI analysis in logs
docker-compose logs -f | grep -E "(HIGH SEVERITY|crew.kickoff|Agent analyzed)"

# Check database for analyzed incidents
sqlite3 data/sentinel_intel.db "SELECT severity, COUNT(*) FROM incidents GROUP BY severity;"
```

**Force AI analysis for testing:**
```python
# Edit main.py temporarily
if incident_data['severity'] in ['HIGH']:  # Remove 'MEDIUM'
    # AI analysis trigger
```

---

### Issue 11: Ollama Using Too Much Memory

**Symptoms:**
```
System becoming slow
Ollama consuming 8GB+ RAM
```

**Solution:**
```bash
# Unload models when not in use
ollama stop

# Load only when needed
ollama serve &

# Use smaller model (in docker-compose.yml)
environment:
  OLLAMA_MODEL: llama3:8b  # Default 4.7GB
  # OR
  OLLAMA_MODEL: llama2:7b  # Smaller
  # OR  
  OLLAMA_MODEL: phi:latest  # Tiny model for testing
```

---

## [STATS] Dashboard Problems

### Issue 12: Dashboard Shows No Data

**Diagnosis:**
```bash
# Check if database has data
sqlite3 data/sentinel_intel.db "SELECT COUNT(*) FROM incidents;"

# Check API endpoint
curl http://localhost:8000/api/summary

# Generate test data
python3 test_web_attacks.py --burst 50
```

**Solutions:**

**No incidents in database:**
```bash
# Check sensors are running
docker-compose logs sentinel-agent | grep "sensor started"

# Check log files exist
docker exec sentinel-agent ls -la /var/log/auth.log
docker exec sentinel-agent ls -la /var/log/apache2/access.log

# Generate test attacks
python3 test_web_attacks.py
```

**Dashboard not refreshing:**
```bash
# Check dashboard refresh rate (default 8 seconds)
# Press F5 or hard refresh browser

# Check web dashboard logs
docker-compose logs -f | grep streamlit
```

---

### Issue 13: Dashboard Authentication Fails

**Symptoms:**
- Login page appears but credentials don't work
- "Invalid username or password" with correct credentials

**Solution:**
```bash
# Verify credentials in docker-compose.yml
docker-compose config | grep -A 2 DASHBOARD

# Default is sentinel/sentinel

# Change credentials
nano docker-compose.yml
# Edit:
environment:
  DASHBOARD_USER: newusername
  DASHBOARD_PASS: newpassword

# Restart
docker-compose restart sentinel-agent

# Clear browser cache and retry
```

---

### Issue 14: CLI Dashboard Shows Garbled Text

**Symptoms:**
```
��[31m��[1m  <- Random characters
Box drawing characters don't display
```

**Cause:** Terminal doesn't support UTF-8 or Rich formatting

**Solutions:**
```bash
# Set locale
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Use different terminal (on SSH client)
# Windows: Use Windows Terminal (not cmd.exe)
# Mac: iTerm2
# Linux: GNOME Terminal, Konsole

# Fallback: Use web dashboard instead
# http://YOUR_SERVER_IP:8501
```

---

## [SECURE] Security & Permissions

### Issue 15: Permission Denied Errors

**File permissions:**
```bash
# Fix data directory
sudo chown -R $USER:$USER ~/Project/data
chmod -R 755 ~/Project/data

# Fix log files
sudo chmod 644 /var/log/auth.log
sudo chmod 644 /var/log/apache2/access.log
```

**Docker socket:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or
newgrp docker
```

---

### Issue 16: Firewall Blocking Container

**Symptoms:**
```
Container can't reach internet
pip install fails
```

**Solution:**
```bash
# Allow Docker subnet
sudo ufw allow from 172.16.0.0/12

# Check rules
sudo ufw status verbose

# Reload
sudo ufw reload
```

---

### Issue 17: Dashboard Exposed to Public Internet (SECURITY RISK)

**Check if exposed:**
```bash
# From external network, try to access
curl http://YOUR_PUBLIC_IP:8501

# Check port binding
netstat -tlnp | grep 8501
# Should show: 192.168.x.x:8501 (local IP)
# NOT: 0.0.0.0:8501 (all interfaces)
```

**Fix:**
```yaml
# docker-compose.yml
ports:
  - "192.168.31.91:8501:8501"  # Local network only
  # NOT "0.0.0.0:8501:8501" or "8501:8501"
```

**Additional protection:**
```bash
# Firewall rules
sudo ufw allow from 192.168.31.0/24 to any port 8501
sudo ufw deny 8501
sudo ufw enable
```

---

## [FAST] Performance Issues

### Issue 18: High CPU Usage

**Diagnosis:**
```bash
# Check container resources
docker stats sentinel-agent

# Check processes inside container
docker exec sentinel-agent top

# Check host system
htop
```

**Solutions:**

**Too many AI analyses:**
```bash
# Verify HIGH-severity-only optimization
docker-compose logs | grep "crew.kickoff" | wc -l
# Should be low (only HIGH severity)

# Check severity distribution
sqlite3 data/sentinel_intel.db "SELECT severity, COUNT(*) FROM incidents GROUP BY severity;"
```

**Log files too large:**
```bash
# Rotate logs
sudo logrotate -f /etc/logrotate.conf

# Limit log file size (in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

### Issue 19: Slow Dashboard Loading

**Solutions:**
```bash
# Limit database query results
sqlite3 data/sentinel_intel.db "DELETE FROM incidents WHERE timestamp < datetime('now', '-7 days');"

# Archive old data
sqlite3 data/sentinel_intel.db <<EOF
ATTACH DATABASE 'data/archive.db' AS archive;
CREATE TABLE archive.incidents AS SELECT * FROM incidents WHERE timestamp < datetime('now', '-30 days');
DELETE FROM incidents WHERE timestamp < datetime('now', '-30 days');
DETACH DATABASE archive;
EOF
```

---

## [DB] Database Problems

### Issue 20: Database Corruption

**Symptoms:**
```
sqlite3.DatabaseError: database disk image is malformed
Container crashing with DB errors
```

**Solution:**
```bash
# Backup current database
cp data/sentinel_intel.db data/sentinel_intel.db.corrupt

# Try to repair
sqlite3 data/sentinel_intel.db "PRAGMA integrity_check;"

# If corrupt, export/import
sqlite3 data/sentinel_intel.db .dump > backup.sql
mv data/sentinel_intel.db data/sentinel_intel.db.bad
sqlite3 data/sentinel_intel.db < backup.sql

# If still fails, start fresh (loses data)
rm data/sentinel_intel.db
docker-compose restart sentinel-agent
```

---

### Issue 21: Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Check for multiple connections
lsof data/sentinel_intel.db

# Restart container
docker-compose restart sentinel-agent

# If persistent, backup and recreate
```

---

## [FUTURE] Potential Future Issues

### Future Issue 1: Python Dependency Conflicts

**Potential Symptoms:**
```
ImportError: cannot import name 'X' from 'Y'
Incompatible library versions
```

**Prevention:**
```bash
# Pin all dependency versions in requirements.txt
pip freeze > requirements.txt.lock

# Regular dependency updates
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

**Solution if it occurs:**
```bash
# Rebuild with no cache
docker-compose build --no-cache --pull
```

---

### Future Issue 2: Docker Compose Version Changes

**Potential Symptoms:**
```
WARN: version is obsolete
```

**Solution:**
```yaml
# Remove version line from docker-compose.yml
# version: '3.9'  <- Delete this line

# Modern format doesn't need version
```

---

### Future Issue 3: Ollama API Changes

**Monitor for:**
- Ollama updates changing API endpoints
- Model format changes
- Authentication requirements

**Mitigation:**
```bash
# Pin Ollama version
sudo systemctl stop ollama
# Don't auto-update

# Test updates in staging first
```

---

### Future Issue 4: Large-Scale Attack Flood

**Scenario:** 10,000+ attacks/minute overwhelming system

**Solutions:**

**Rate limiting (add to web server):**
```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
```

**Database batching:**
```python
# Batch inserts every N seconds instead of per-attack
```

**Sampling:**
```python
# Only analyze every Nth attack during flood
if rand() < 0.1:  # 10% sampling
    analyze_attack()
```

---

### Future Issue 5: Insufficient Disk Space (Long-term)

**Monitor:**
```bash
# Set up disk monitoring
df -h | grep -E "/dev/sd|vg-"

# Alert if <10% free
```

**Solutions:**
```bash
# Automated log rotation
cat > /etc/logrotate.d/sentinel <<EOF
/var/lib/docker/volumes/sentinel_data/_data/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF

# Database archiving script
crontab -e
# Add: 0 2 * * * /path/to/archive_old_incidents.sh
```

---

### Future Issue 6: IPv6 Compatibility

**If your network enables IPv6:**

**Update docker-compose.yml:**
```yaml
networks:
  sentinel-network:
    enable_ipv6: true
    ipam:
      config:
        - subnet: fd00::/64
```

**Update firewall:**
```bash
sudo ufw allow from any to any port 8000 proto tcp
```

---

### Future Issue 7: Multi-Server Deployment

**When scaling to multiple servers:**

**Centralized database approach:**
```yaml
# Use PostgreSQL instead of SQLite
environment:
  DB_TYPE: postgresql
  DB_HOST: central-db-server
  DB_NAME: sentinel_multi
```

**Distributed logging:**
```yaml
# Use Elasticsearch or Loki
logging:
  driver: loki
  options:
    loki-url: "http://loki:3100/loki/api/v1/push"
```

---

## [TOOLS] Diagnostic Tools

### Complete Health Check Script

Save as `health_check.sh`:

```bash
#!/bin/bash
echo "==================================="
echo "Sentinel Agent Health Check"
echo "==================================="
echo ""

echo "1. Docker Status:"
docker-compose ps
echo ""

echo "2. Ollama Status:"
systemctl is-active ollama
ss -tlnp | grep 11434
curl -s http://localhost:11434/api/tags | head -n 5
echo ""

echo "3. Container Logs (last 20 lines):"
docker-compose logs --tail=20 sentinel-agent
echo ""

echo "4. Port Bindings:"
netstat -tlnp | grep -E "(8000|8501|11434)"
echo ""

echo "5. Database Status:"
sqlite3 data/sentinel_intel.db "SELECT 
    (SELECT COUNT(*) FROM incidents) as total_incidents,
    (SELECT COUNT(*) FROM incidents WHERE severity='HIGH') as high_severity,
    (SELECT COUNT(*) FROM actions) as total_actions;"
echo ""

echo "6. Disk Usage:"
df -h | grep -E "Filesystem|/$|docker"
echo ""

echo "7. Memory Usage:"
free -h
echo ""

echo "8. API Health:"
curl -s http://localhost:8000/api/health
echo ""

echo "Health check complete!"
```

Run it:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

### Log Analysis Commands

**Find errors:**
```bash
docker-compose logs sentinel-agent | grep -i error
docker-compose logs sentinel-agent | grep -i exception
docker-compose logs sentinel-agent | grep -i fail
```

**Watch live logs:**
```bash
docker-compose logs -f sentinel-agent | grep -E "(HIGH|CRITICAL|ERROR)"
```

**Count attack types:**
```bash
sqlite3 data/sentinel_intel.db "SELECT attack_type, COUNT(*) as count FROM incidents GROUP BY attack_type ORDER BY count DESC;"
```

---

### Performance Monitoring

**Container resource usage:**
```bash
docker stats sentinel-agent --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

**Database size:**
```bash
du -sh data/*.db
```

**Log processing speed:**
```bash
# Watch detection rate
tail -f /var/log/auth.log | while read line; do echo "$(date +%T) - Auth event"; done
```

---

## [SUPPORT] Support Escalation

If issues persist after trying these solutions:

1. **Collect diagnostics:**
   ```bash
   ./health_check.sh > diagnostic_report.txt
   docker-compose logs sentinel-agent > container_logs.txt
   ```

2. **GitHub Issues:**  
   https://github.com/chandan5615/Project/issues
   
   Include:
   - OS version (`lsb_release -a`)
   - Docker version (`docker --version`)
   - Docker Compose version (`docker-compose --version`)
   - Error logs (diagnostic_report.txt)

3. **Emergency Recovery:**
   ```bash
   # Complete clean reinstall
   cd ~/Project
   docker-compose down -v
   rm -rf data/ logs/
   sudo ./AUTO_INSTALL.sh
   ```

---

**Document Version:** 2.2  
**Last Updated:** February 22, 2026  
**Maintainer:** Sentinel Agent Team

**Contributions welcome!** Found a fix for a new issue? Submit a pull request!
