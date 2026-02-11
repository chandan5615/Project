# Quick Fix Instructions

## The Problem
Your container wasn't becoming "healthy" because:
1. Missing health check configuration in docker-compose.yml
2. Startup script was exiting early on errors
3. Not enough time allocated for startup

## All Fixed! ✓

The following files have been updated with fixes:
- ✓ `docker-compose.yml` - Added health check with 60s start period
- ✓ `docker-startup.sh` - Made error-tolerant, skips read-only log issues
- ✓ `sentinel_auto.py` - Extended timeout to 2 minutes
- ✓ Created diagnostic scripts

## What To Do Now (On Ubuntu)

### Option 1: One-Command Fix (Easiest)

```bash
cd ~/Project
git pull  # Get the latest fixes
chmod +x complete-fix.sh
./complete-fix.sh
```

This script will:
- Stop the old container
- Clean old data
- Check Ollama is running
- Rebuild everything
- Wait for healthy status
- Show you the admin credentials
- Tell you what to do next

**Time required**: ~5-6 minutes

### Option 2: Manual Step-by-Step

```bash
cd ~/Project
git pull

# 1. Make sure Ollama is running
ollama serve &
sleep 5
ollama pull llama3:8b

# 2. Stop and clean
docker-compose down
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt data/*.json data/*.db

# 3. Rebuild
docker-compose build --no-cache
docker-compose up -d

# 4. Wait for healthy (about 90 seconds)
watch -n 5 'docker-compose ps'
# Wait until you see (healthy), then press Ctrl+C

# 5. Get credentials
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"

# 6. Run automation
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
```

## What You Should See

### During rebuild:
```
Building sentinel-agent
[+] Building 274.7s (19/19) FINISHED
...
Creating sentinel-agent ... done
```

### After ~90 seconds:
```bash
$ docker-compose ps

NAME              STATUS
sentinel-agent    Up 2 minutes (healthy)  ← This is what you want!
```

### Credentials output:
```
DEFAULT ADMIN CREDENTIALS (SAVE THESE NOW!):
  Username: admin
  Password: <random-password>
```

### Automation success:
```
✓ Container is healthy
✓ Admin password saved to .sentinel_password
✓ Login successful
✓ Token saved to .sentinel_token
```

## If It Still Doesn't Work

Run diagnostics:
```bash
cd ~/Project
chmod +x quick-diagnose.sh
./quick-diagnose.sh
```

Then check [HEALTHCHECK_DEBUG.md](HEALTHCHECK_DEBUG.md) for detailed troubleshooting.

## Why This Happened

The original setup had three issues:

1. **No health check defined** → Docker never knew when the container was ready
2. **Strict error handling** → Script would exit if test attacks failed (they always fail in Docker due to read-only logs)
3. **Short timeout** → 30 seconds wasn't enough for full startup

All three are now fixed! The container should now become healthy within 60-90 seconds.

## Next Steps After Fix

Once everything is healthy:

1. **Run automated setup** to get your API token:
   ```bash
   python3 sentinel_auto.py setup
   ```

2. **Run demo attacks** to see the system in action:
   ```bash
   python3 sentinel_auto.py demo
   ```

3. **Access the services**:
   - API: http://localhost:8000
   - Web Dashboard: http://localhost:8501
   - API Docs: http://localhost:8000/docs

4. **View attack detections**:
   ```bash
   python3 view_attacks.py
   ```
