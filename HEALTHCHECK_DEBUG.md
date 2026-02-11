# Container Health Check - Complete Fix Guide

## Changes Made (Already Applied)

### ✓ 1. Added Health Check to docker-compose.yml
- Tests `/api/health` endpoint every 10 seconds
- Allows 60 seconds for initial startup
- Retries 5 times before marking unhealthy

### ✓ 2. Fixed docker-startup.sh
- Changed from `set -e` to `set +e` (errors don't stop startup)
- Added error handling for each step
- Skips test attack generation in Docker (logs are read-only)
- Uses `exec` for API to ensure proper signal handling

### ✓ 3. Improved sentinel_auto.py
- Extended wait time to 2 minutes (60 retries)
- Added helpful diagnostic message

### ✓ 4. Created Diagnostic Scripts
- `quick-diagnose.sh` - Fast problem identification
- `test_api_startup.py` - Test API components

## Fix Steps for Ubuntu

### Option 1: Quick Rebuild (Recommended)

```bash
cd ~/Project

# Make sure you're using the latest code
git pull

# Stop everything
docker-compose down

# Clean old data
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt data/*.json data/*.db

# Make scripts executable
chmod +x quick-diagnose.sh test_api_startup.py

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# Wait for health check (about 90 seconds)
echo "Waiting for container to become healthy..."
sleep 90

# Check status
docker-compose ps
```

### Option 2: Debug First, Then Fix

```bash
cd ~/Project

# Run quick diagnostics on current container
chmod +x quick-diagnose.sh
./quick-diagnose.sh

# Look for errors in output, common issues:
# - "Connection refused" on port 8000 = API not started
# - "ModuleNotFoundError" = Missing dependencies  
# - "Permission denied" = Database/file access issues
```

## What to Look For

### ✓ Success Looks Like:
```
docker-compose ps

NAME              STATUS
sentinel-agent    Up X minutes (healthy)
```

### ✗ Failure Looks Like:
```
sentinel-agent    Up X minutes (unhealthy)
```

## Debugging Unhealthy Container

If container is still unhealthy after rebuild:

### Step 1: Check Logs
```bash
# See last 100 lines
docker-compose logs --tail=100 sentinel-agent

# Look for these errors:
# - Module import errors
# - Database connection failures
# - Port already in use
# - Ollama connection issues
```

### Step 2: Test Inside Container
```bash
# Run API startup test
docker exec sentinel-agent python test_api_startup.py

# Check if API is running
docker exec sentinel-agent ps aux | grep python

# Manual health check
docker exec sentinel-agent curl http://localhost:8000/api/health
```

### Step 3: Check Port Availability
```bash
# On host machine
sudo netstat -tulpn | grep -E '8000|8501'

# If port 8000 is in use by another process:
sudo fuser -k 8000/tcp
```

### Step 4: Verify Ollama
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve &

# Pull model if needed:
ollama pull llama3:8b
```

## Common Issues & Solutions

### Issue 1: "Connection refused" on localhost:8000
**Cause**: API failed to start  
**Solution**:
```bash
# Check why API failed
docker-compose logs sentinel-agent | grep -i error

# Test API startup
docker exec sentinel-agent python test_api_startup.py
```

### Issue 2: "Port 8000 already in use"
**Cause**: Another process is using the port  
**Solution**:
```bash
# Find and kill the process
sudo lsof -i :8000
sudo fuser -k 8000/tcp

# Restart container
docker-compose restart sentinel-agent
```

### Issue 3: "ModuleNotFoundError"
**Cause**: Dependencies not installed  
**Solution**:
```bash
# Rebuild with fresh install
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue 4: Container starts but stays unhealthy for 2 minutes
**Cause**: Ollama connection taking too long  
**Solution**:
```bash
# Make sure Ollama is ready
ollama list
curl http://localhost:11434/api/tags

# Check if container can reach Ollama
docker exec sentinel-agent curl http://localhost:11434/api/tags
```

## Expected Timeline

| Step | Time | What's Happening |
|------|------|------------------|
| Build | 3-5 min | Installing dependencies |
| Container Start | 5-10 sec | Starting services |
| Database Init | 5-10 sec | Creating/checking database |
| Main.py Start | 5 sec | Starting monitoring agent |
| API Start | 5-10 sec | Starting FastAPI server |
| Health Check | 10-20 sec | Waiting for first successful check |
| **Total** | **4-6 min** | From build to healthy |

## Verification Commands

After container is healthy:

```bash
# 1. Check container status
docker-compose ps
# Should show: sentinel-agent (healthy)

# 2. Test API endpoint
curl http://localhost:8000/api/health
# Should return: {"status":"healthy",...}

# 3. Extract admin credentials
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"

# 4. Run automation
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

## Still Not Working?

If the container is still unhealthy after following all steps:

1. **Capture full diagnostics**:
   ```bash
   ./quick-diagnose.sh > diagnostics.txt 2>&1
   docker-compose logs sentinel-agent > container-logs.txt
   ```

2. **Check these files for clues**:
   - `diagnostics.txt` - System state
   - `container-logs.txt` - Container output
   - `logs/sentinel.log` - Application logs

3. **Try minimal startup**:
   ```bash
   # Start container without automatic startup
   docker-compose run --rm sentinel-agent /bin/bash
   
   # Inside container, run step by step:
   python init_database.py
   python test_api_startup.py
   python sentinel_api.py
   ```
