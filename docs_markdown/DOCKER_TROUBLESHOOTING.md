# Docker Troubleshooting Guide - Sentinel Agent

## Common Issues & Solutions

---

## 1. SERVICE WON'T START

### Symptom
```bash
docker-compose up -d
docker-compose ps  # Shows "Exit 1" or "Exited"
```

### Solution

**Step 1: Check Logs**
```bash
docker-compose logs sentinel-agent
# Look for error messages
```

**Step 2: Common Error Messages**

#### "Cannot connect to Ollama"
```bash
# Check if Ollama is running (host mode)
ollama serve

# Or use Docker Ollama
docker-compose --profile with-ollama up -d

# Wait 5 minutes for model download
docker-compose logs ollama-pull
```

#### "Port already in use"
```bash
# Find what's using the port
lsof -i :8000
netstat -tulpn | grep 8000

# Either:
# 1. Kill the process using the port
# 2. Change the port in docker-compose.yml
```

#### "Out of memory"
```bash
# Check current usage
docker stats

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

**Step 3: Full Reset**
```bash
# Stop and remove everything
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Check status
docker-compose logs -f sentinel-agent
```

---

## 2. API NOT RESPONDING

### Symptom
```bash
curl http://localhost:8000/api/health
# Connection refused or timeout
```

### Solution

**Step 1: Verify Container is Running**
```bash
docker-compose ps

# Should show: sentinel-agent    Up (healthy) ...
```

**Step 2: Check Container Logs**
```bash
docker-compose logs --tail=50 sentinel-agent

# Look for startup errors
```

**Step 3: Verify Port Mapping**
```bash
docker-compose ps

# Check PORTS column shows: 0.0.0.0:8000->8000/tcp
```

**Step 4: Test from Within Container**
```bash
# Connect to container shell
docker-compose exec sentinel-agent bash

# Test locally
curl http://127.0.0.1:8000/api/health
curl -v http://127.0.0.1:8000/api/health

# Check listening ports
netstat -tulpn | grep 8000
```

**Step 5: Restart Service**
```bash
docker-compose restart sentinel-agent

# Wait 10 seconds for startup
sleep 10

# Test again
curl http://localhost:8000/api/health
```

---

## 3. OLLAMA CONNECTION FAILED

### Symptom
```
WARNING: Could not connect to Ollama server
```

### Solution

**Option A: Using Docker Ollama (Easiest)**
```bash
# Stop current setup
docker-compose down

# Start with Ollama profile
docker-compose --profile with-ollama up -d

# Wait for model to download (5-10 minutes)
docker-compose logs -f ollama-pull

# Verify
curl http://localhost:11434/api/tags
```

**Option B: Using Host Ollama**
```bash
# On your host machine
ollama pull llama3:8b
ollama serve

# In docker-compose.yml, set:
# OLLAMA_BASE_URL: http://127.0.0.1:11434

# Start sentinel
docker-compose up -d

# Verify
curl http://localhost:8000/api/health
```

**Option C: Different Model**
```bash
# Pull different model
ollama pull mistral:7b

# Update docker-compose.yml
environment:
  OLLAMA_MODEL: mistral:7b

# Restart
docker-compose restart
```

**Diagnose Ollama Issues**
```bash
# Check if Ollama container exists
docker ps -a | grep ollama

# View Ollama logs
docker-compose logs ollama

# Test Ollama directly
docker-compose exec ollama curl http://127.0.0.1:11434/api/tags

# List available models
docker-compose exec ollama ollama list
```

---

## 4. DISK SPACE ISSUES

### Symptom
```
No space left on device
Docker error: insufficient space
```

### Solution

**Check Disk Usage**
```bash
# Overall Docker usage
docker system df

# Directory usage
du -sh /var/lib/docker/*

# Current directory usage
du -sh .
```

**Free Up Space**

**Option 1: Clean Unused Images** (Recommended)
```bash
# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove unused volumes
docker volume prune

# All at once (be careful!)
docker system prune -a
```

**Option 2: Clear Old Logs**
```bash
# Stop services
docker-compose down

# Clear logs
rm -rf logs/*

# Clear cached databases
rm -rf data/*

# Start fresh
docker-compose up -d
```

**Option 3: Export and Delete Data**
```bash
# Backup important data first
tar czf backup.tar.gz data/

# Remove old model
docker rmi sentinel-agent:2.2

# Delete old Ollama models (on host)
rm -rf ~/.ollama/models

# Re-download fresh model
ollama pull llama3:8b
```

**Option 4: Move Docker to Different Disk**
```bash
# Check current Docker location
docker info | grep "Docker Root Dir"

# Move to larger disk (requires Docker restart)
# See Docker documentation for your OS
```

---

## 5. MEMORY ISSUES

### Symptom
```
Killed (OOMKilled)
Out of memory error
Container constantly restarting
```

### Solution

**Check Current Memory Usage**
```bash
docker stats sentinel-agent

# Watch in real-time for memory spikes
docker stats --no-stream
```

**Increase Memory Limit**

**In docker-compose.yml:**
```yaml
sentinel-agent:
  deploy:
    resources:
      limits:
        memory: 8G      # Increase from 4G
        cpus: '4'       # Also increase CPU
```

**Then restart:**
```bash
docker-compose down
docker-compose up -d
```

**Understanding Memory Usage**
```bash
# Check what's consuming memory
docker-compose exec sentinel-agent ps aux --sort=-%mem

# Monitor over time
docker stats --no-trunc
```

**Optimize Application**
```bash
# Reduce model size
docker-compose.yml: OLLAMA_MODEL: llama2:7b  # Smaller model

# Or disable features
docker-compose.yml: DEBUG: "false"
```

---

## 6. NETWORK CONNECTIVITY

### Symptom
```
Cannot resolve container names
Services can't communicate
Network errors in logs
```

### Solution

**Check Network Status**
```bash
# List networks
docker network ls
docker network inspect sentinel-network

# Test connectivity from container
docker-compose exec sentinel-agent ping ollama

# Check DNS resolution
docker-compose exec sentinel-agent nslookup ollama
```

**Recreate Network**
```bash
# Stop services
docker-compose down

# Remove network
docker network rm sentinel-network

# Restart (network will be recreated)
docker-compose up -d
```

**Network Configuration Issues**
```bash
# If using custom network, verify in docker-compose
networks:
  sentinel-network:
    driver: bridge

# Check network settings
docker-compose config | grep -A 5 "networks:"
```

---

## 7. LOG PROBLEMS

### Symptom
```
Logs not being written
"Permission denied" when viewing logs
```

### Solution

**Check Log Permissions**
```bash
# View log file permissions
ls -la logs/

# Fix permissions
chmod 755 logs/
chmod 644 logs/*

# From inside container
docker-compose exec sentinel-agent chmod 755 /app/logs
```

**View Logs Effectively**
```bash
# Latest 100 lines
docker-compose logs --tail=100 sentinel-agent

# Follow in real-time
docker-compose logs -f sentinel-agent

# Save to file
docker-compose logs sentinel-agent > logs.txt

# Filter by service
docker-compose logs -f sentinel-agent

# With timestamps
docker-compose logs --timestamps sentinel-agent
```

**Log File Location Issues**
```bash
# Check where logs are being written
docker-compose exec sentinel-agent ls -la /app/logs/

# Check full path
docker-compose exec sentinel-agent pwd
docker-compose exec sentinel-agent mount | grep logs
```

---

## 8. BUILD PROBLEMS

### Symptom
```
docker-compose build fails
Image build hangs
Build errors in logs
```

### Solution

**Rebuild from Scratch**
```bash
# Force rebuild without cache
docker-compose build --no-cache

# Increase build timeout
docker-compose build --no-cache --build-arg BUILDKIT_INLINE_CACHE=1
```

**Check Build Logs**
```bash
# See verbose build output
docker-compose build --no-cache --verbose

# Or just rebuild the main image
docker build --no-cache -t sentinel-agent:2.2 .
```

**Common Build Errors**

**"pip: command not found"**
```bash
# Ensure Python is in path
# Check Dockerfile PYTHONPATH
# Rebuild
docker-compose build --no-cache
```

**"Network timeout"**
```bash
# Check internet connectivity
docker-compose exec sentinel-agent ping 8.8.8.8

# Rebuild with increased timeout
docker-compose build --no-cache --build-arg PIP_DEFAULT_TIMEOUT=100
```

---

## 9. DATABASE ISSUES

### Symptom
```
"Database locked" error
Database corruption
Missing tables
```

### Solution

**Check Database Status**
```bash
# List database files
docker-compose exec sentinel-agent ls -la /app/data/

# Check database integrity
docker-compose exec sentinel-agent sqlite3 /app/data/sentinel_intel.db ".tables"

# Backup before trying fixes
cp -r data/ data_backup/
```

**Reset Database**
```bash
# Stop services
docker-compose down

# Backup current data
tar czf data_backup_$(date +%s).tar.gz data/

# Delete databases
rm -f data/*.db

# Start services (databases will be recreated)
docker-compose up -d
```

**Recover from Backup**
```bash
# Stop services
docker-compose down

# Remove corrupted data
rm -rf data/

# Restore from backup
tar xzf data_backup_*.tar.gz

# Start services
docker-compose up -d
```

---

## 10. PERFORMANCE ISSUES

### Symptom
```
Slow API responses
High CPU usage
Container running slow
```

### Solution

**Monitor Performance**
```bash
# Real-time stats
docker stats sentinel-agent

# Check CPU/Memory limits
docker inspect sentinel-agent | grep -A 10 "Resources"

# Process list
docker-compose exec sentinel-agent ps aux
```

**Increase Resources**
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'        # Increase from 2
      memory: 8G       # Increase from 4G
```

**Enable Profiling**
```bash
# Check what's consuming CPU
docker-compose exec sentinel-agent top -b -n 1

# Memory breakdown
docker-compose exec sentinel-agent free -m
```

---

## 11. PORT CONFLICTS

### Symptom
```
bind: address already in use
Cannot map ports
```

### Solution

**Find What's Using Ports**
```bash
# Linux
lsof -i :8000
lsof -i :8501
lsof -i :11434

# Windows
netstat -ano | findstr :8000

# macOS  
lsof -i :8000
```

**Change Ports in docker-compose.yml**
```yaml
services:
  sentinel-agent:
    ports:
      - "8888:8000"  # Use port 8888 instead of 8000
```

**Stop Conflicting Service**
```bash
# Kill process using the port
kill -9 <PID>

# Or stop entire Docker service
docker-compose down
```

---

## 12. HEALTH CHECK FAILING

### Symptom
```
docker-compose ps shows "unhealthy"
Health check timeout
```

### Solution

**Check Health Manually**
```bash
# Direct test
docker-compose exec sentinel-agent curl -v http://127.0.0.1:8000/api/health

# Verbose output
curl -v http://localhost:8000/api/health

# Check response code
curl -w "%{http_code}" http://localhost:8000/api/health
```

**Review Health Check Config**
```bash
# In docker-compose.yml, check:
healthcheck:
  test: ["CMD", "curl", ...]
  interval: 60s       # Check every 60s
  timeout: 10s        # Wait 10s for response
  retries: 3          # Fail after 3 failed checks

# Increase timeouts if slow
interval: 120s
timeout: 20s
```

**Increase Health Check Tolerance**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/api/health"]
  interval: 120s      # Increased to 2 minutes
  timeout: 20s        # Increased to 20 seconds
  retries: 5          # Allow more retries
  start_period: 60s   # Grace period for startup
```

---

## 13. ENVIRONMENT VARIABLE ISSUES

### Symptom
```
Environment variables not being picked up
Wrong configuration applied
```

### Solution

**Verify Variables Are Set**
```bash
# Check environment inside container
docker-compose exec sentinel-agent env | grep OLLAMA

# Check what docker-compose sees
docker-compose config | grep -A 20 "environment:"
```

**Using .env File**
```bash
# Create .env in project root
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3:8b
LOG_LEVEL=DEBUG

# docker-compose will auto-load it
docker-compose up -d

# Verify
docker-compose exec sentinel-agent env | grep -i sentinel
```

**Override Variables on Command Line**
```bash
# Set variable when starting
LOG_LEVEL=DEBUG docker-compose up -d

# Or in commands
docker-compose -e LOG_LEVEL=DEBUG up -d
```

---

## 14. IMAGE ISSUES

### Symptom
```
Image cannot be found
Image corrupted  
Different versions running
```

### Solution

**Check Images**
```bash
# List all images
docker images | grep sentinel

# Show detailed info
docker inspect sentinel-agent:2.2

# Check image size
docker images --no-trunc
```

**Rebuild Image**
```bash
# Remove old image
docker rmi sentinel-agent:2.2

# Rebuild
docker build -t sentinel-agent:2.2 .

# Or via compose
docker-compose build --no-cache
```

**Pull Latest Update**
```bash
# Update code
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart
docker-compose up -d
```

---

## STILL STUCK?

### Diagnostic Steps

1. **Collect Information**
   ```bash
   docker --version
   docker-compose --version
   docker info
   docker ps -a
   docker-compose logs > diagnostics.log
   ```

2. **Check System Resources**
   ```bash
   df -h              # Disk space
   free -m            # Memory
   docker stats       # Container stats
   ```

3. **Validate Configuration**
   ```bash
   docker-compose config > config_check.yml
   docker-compose config --quiet
   ```

4. **Check Connectivity**
   ```bash
   docker-compose exec sentinel-agent ping 8.8.8.8
   docker-compose exec sentinel-agent curl https://api.github.com
   ```

### Get Help

- Check **DOCKER_DEPLOYMENT.md** for detailed documentation
- Review **docker-compose.yml** comments for configuration options
- See **INSTALLATION.md** for general setup help
- Check logs: `docker-compose logs -f sentinel-agent`

---

**Last Updated**: 2024  
**Version**: Sentinel Agent v2.2
