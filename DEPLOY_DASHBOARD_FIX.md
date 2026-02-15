# Quick Fix: Deploy Web Dashboard Database Initialization Fix

**For:** Web dashboard showing "no such table: incidents" errors  
**Time:** 5-10 minutes  
**Status:** ✅ Ready to deploy

---

## 🚀 Step-by-Step Deployment

### Step 1: Get Latest Code (2 minutes)
```bash
# On your dev machine (Windows)
cd "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project"
git pull
```

### Step 2: Deploy Fixed Files to Ubuntu (2 minutes)
```bash
# Copy the fixed web_dashboard.py
scp dashboard/web_dashboard.py ubuntu@10.104.252.89:~/Project/dashboard/

# Verify transfer completed
ssh ubuntu@10.104.252.89 "ls -l ~/Project/dashboard/web_dashboard.py"
```

### Step 3: Restart Container with new code (2 minutes)
```bash
ssh ubuntu@10.104.252.89 "cd ~/Project && docker-compose down && docker-compose up -d && sleep 30"

# Verify container is healthy
ssh ubuntu@10.104.252.89 "docker-compose ps"
# Should show: sentinel-agent   Up (healthy)
```

### Step 4: Initialize Database (1 minute)
```bash
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 init_database.py"

# Expected output:
# ✓ Data directory ready: /app/data
# ✓ Data Engine initialized (sentinel_intel.db created)
# ✓ Authentication module initialized (auth.db created)
# ... more initialization messages ...
```

### Step 5: Run Web Dashboard (1 minute)
```bash
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0"

# Expected output:
#   You can now view your Streamlit app in your browser.
#   Local URL: http://localhost:8501
#   Network URL: http://10.104.252.89:8501
```

### Step 6: Verify Dashboard (1 minute)
```bash
# Open browser to: http://10.104.252.89:8501
# 
# Should see:
# - "SENTINEL AGENT - SECURITY DASHBOARD" heading
# - Security Score metric (should show 100% initially)
# - Three tabs: "Wall of Shame", "Incident Feed", "Network Health"
# - No red error messages
```

---

## ✅ Verification Checklist

```bash
# Check database file exists
ssh ubuntu@10.104.252.89 "ls -lh ~/Project/data/sentinel_intel.db"
# Expected: -rw-r--r-- 1 ubuntu ubuntu 48K Feb 15 19:38 sentinel_intel.db

# Check tables created
ssh ubuntu@10.104.252.89 "docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db '.tables'"
# Expected output: actions   incidents  threat_intel

# Check environment variables
ssh ubuntu@10.104.252.89 "docker exec sentinel-agent env | grep SENTINEL"
# Expected:
# SENTINEL_LOG_DIR=/app/logs
# SENTINEL_DATA_DIR=/app/data

# View dashboard logs
ssh ubuntu@10.104.252.89 "docker exec sentinel-agent tail -30 /app/logs/dashboard.log"
```

---

## 🆘 If Something Goes Wrong

### Dashboard shows "Error initializing database"
```bash
# Re-initialize database
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 init_database.py"

# Check permissions
ssh ubuntu@10.104.252.89 "docker exec sentinel-agent chmod -R 777 /app/data /app/logs"

# Try dashboard again
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0"
```

### Still seeing "no such table: incidents"
```bash
# Complete reset
ssh ubuntu@10.104.252.89 "cd ~/Project && docker-compose down -v && rm -rf data/"
ssh ubuntu@10.104.252.89 "cd ~/Project && docker-compose up -d --build"
sleep 60

# Initialize and run
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 init_database.py"
ssh ubuntu@10.104.252.89 "docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0"
```

### Container won't start
```bash
# Check container logs
ssh ubuntu@10.104.252.89 "docker logs sentinel-agent --tail=100"

# Rebuild fresh
ssh ubuntu@10.104.252.89 "cd ~/Project && docker-compose down -v && docker-compose up -d --build"
```

---

## 📝 What Was Fixed

| File | Issue | Fix |
|------|-------|-----|
| `web_dashboard.py` Line 25 | Using `./data` instead of `/app/data` | Changed default to `/app/data` |
| `web_dashboard.py` Line 61 | Silent failures if path empty | Added validation and error checking |
| `web_dashboard.py` Line 383 | Using wrong session variable | Now properly uses `DEFAULT_DB_PATH` |

---

## 💡 Tips

- Dashboard needs **database already initialized** before it starts
- If adding test incidents, run: `docker exec sentinel-agent python3 test_attacks.py --auth-count 50`
- Dashboard auto-refreshes every 30 seconds (configurable in UI)
- All data persists in `./data/` volume on Ubuntu

---

## 🎯 Success Criteria

✅ Dashboard loads without errors  
✅ Browser shows "SENTINEL AGENT - SECURITY DASHBOARD"  
✅ Security Score shows 100% (no incidents initially)  
✅ All three tabs visible and clickable  
✅ Sidebar shows database path (e.g., `/app/data/sentinel_intel.db`)  

---

See [DATABASE_INIT_ISSUES.md](DATABASE_INIT_ISSUES.md) for detailed technical information.

