# Sentinel Agent - Health Check Fix

## Problem
The container was not becoming "healthy" because the `docker-compose.yml` file was missing a health check configuration.

## What Was Changed

### 1. Added Health Check to docker-compose.yml
Added a health check that tests the API endpoint every 10 seconds:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### 2. Improved sentinel_auto.py
- Increased wait time from 1 minute to 2 minutes (60 retries)
- Added helpful diagnostic message if container doesn't become healthy

### 3. Created Helper Scripts
- `fix-healthcheck.sh` - Rebuilds container with fixes
- `diagnose.sh` - Diagnoses container issues

## How to Fix (On Ubuntu)

### Option 1: Quick Fix (Recommended)
```bash
cd ~/Project

# Make scripts executable
chmod +x fix-healthcheck.sh diagnose.sh

# Run the fix script
./fix-healthcheck.sh

# Wait 30 seconds, then run setup
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

### Option 2: Manual Fix
```bash
cd ~/Project

# Stop and clean up
docker-compose down
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt data/*.json data/*.db

# Rebuild with new healthcheck
docker-compose build --no-cache
docker-compose up -d

# Wait for container to become healthy (check status)
watch -n 2 'docker-compose ps'
# Press Ctrl+C when you see "(healthy)"

# Get admin credentials
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"

# Run automated setup
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

### Troubleshooting

If the container still doesn't become healthy:

1. **Run diagnostics:**
   ```bash
   ./diagnose.sh
   ```

2. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   If not running, start it:
   ```bash
   ollama serve &
   ```

3. **Check container logs:**
   ```bash
   docker-compose logs -f sentinel-agent
   ```

4. **Verify the model is available:**
   ```bash
   ollama list
   # If llama3:8b is not listed:
   ollama pull llama3:8b
   ```

5. **Test API manually:**
   ```bash
   # Wait 60 seconds after container starts, then:
   curl http://localhost:8000/api/health
   ```

6. **Check if ports are available:**
   ```bash
   netstat -tuln | grep -E '8000|8501|11434'
   ```

## Expected Timeline

With the fixes:
- Container build: ~3 minutes
- Container startup: ~30-45 seconds
- Health check: ~10-20 seconds
- Total: ~4-5 minutes

## Next Steps After Fix

Once the container is healthy, you'll see:
```
✓ Container is healthy
✓ Admin password saved to .sentinel_password
✓ Login successful
✓ Token saved to .sentinel_token
```

Then you can:
- Access API: http://localhost:8000
- View Dashboard: http://localhost:8501
- Run attacks: `python3 sentinel_auto.py attack`
- View results: `python3 view_attacks.py`
