# Web Dashboard Database Initialization Issues & Solutions

**Last Updated:** February 15, 2026  
**Status:** ✅ FIXED - All issues resolved with proper path handling

---

## 🔴 Issue: "no such table: incidents"

### Symptoms
```
Error fetching incident summary: no such table: incidents
Error fetching blocked IPs: Execution failed on sql '...' : no such table: incidents
Error initializing database: [Errno 2] No such file or directory: ''
```

### Root Cause
1. **Database path mismatch** - web_dashboard.py was using `./data` while core modules use `/app/data`
2. **Missing initialization** - Database tables not created before dashboard starts
3. **Empty path variable** - Environment variables not properly set in container

---

## ✅ Fixes Applied (February 15, 2026)

### Fix #1: Database Path Alignment
**File:** `dashboard/web_dashboard.py` (Line 25-26)

**Before:**
```python
DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR") or "./data"
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH") or os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db")
```

**After:**
```python
DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR") or "/app/data"
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH") or os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db")
```

**Why:** Matches `data_engine.py` and `Dockerfile` which use `/app/data` in container

---

### Fix #2: Enhanced Database Initialization
**File:** `dashboard/web_dashboard.py` (Lines 63-123)

**Changes:**
- Added validation for empty paths
- Better error logging to diagnose issues
- Creates directories with proper error handling
- Logs full database path for debugging

**New Code:**
```python
def _ensure_database_initialized(self):
    """Ensure the database and tables exist"""
    try:
        # Verify database path is set
        if not self.db_path or self.db_path.isspace():
            self.logger.error(f"Invalid database path: {self.db_path}")
            self.db_path = DEFAULT_DB_PATH
        
        # Create directories
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            self.logger.info(f"Database directory ensured: {db_dir}")
        
        self.logger.info(f"Using database at: {self.db_path}")
        # ... table creation code ...
        self.logger.info(f"Database initialized successfully at {self.db_path}")
    except Exception as e:
        self.logger.error(f"Error initializing database: {e}")
        raise
```

---

### Fix #3: Main Function Error Handling
**File:** `dashboard/web_dashboard.py` (Lines 383-406)

**Changes:**
- Uses `DEFAULT_DB_PATH` instead of hardcoded value
- Try/catch with fallback to default path
- Better user feedback on initialization errors
- Shows full path in UI for debugging

**New Code:**
```python
def main():
    # Initialize session state with default database path
    if "db_path" not in st.session_state:
        st.session_state.db_path = DEFAULT_DB_PATH
    
    # ... sidebar code ...
    
    # Initialize data manager with proper error handling
    try:
        data_manager = DashboardDataManager(st.session_state.db_path or DEFAULT_DB_PATH)
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.info(f"Using default database path: {DEFAULT_DB_PATH}")
        try:
            data_manager = DashboardDataManager(DEFAULT_DB_PATH)
        except Exception as e2:
            st.error(f"Critical error: Cannot initialize database. {e2}")
            return
```

---

## 🚀 How to Deploy the Fix

### Option 1: Automatic (Recommended)
```bash
# Deploy updated code
git pull  # Get latest from repo

# Rebuild container
docker-compose down -v
docker-compose up -d --build && sleep 30

# Initialize database
docker exec -it sentinel-agent python3 init_database.py

# Run dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

### Option 2: Quick Fix (If container already running)
```bash
# Copy fixed file
scp dashboard/web_dashboard.py ubuntu@10.104.252.89:~/Project/dashboard/

# Restart container
ssh ubuntu@10.104.252.89 "cd ~/Project && docker-compose down && docker-compose up -d"
sleep 30

# Initialize database again
docker exec sentinel-agent python3 init_database.py

# Run dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

---

## 📋 Database Initialization Order

The database **MUST** be initialized before dashboard starts. This happens automatically via`docker-startup.sh`:

1. **Container Starts** → Runs `/usr/local/bin/docker-startup.sh`
2. **Database Init** → Executes `python3 init_database.py` ([line 19](docker-startup.sh#L19))
3. **Main Service** → Starts `python3 main.py` for monitoring  
4. **API Service** → Starts `python3 sentinel_api.py` for REST API
5. **Ready for Dashboard** → Web dashboard can now connect

### Manual Initialization
If database fails to initialize automatically:

```bash
# Inside container
python3 init_database.py

# Or via docker exec
docker exec -it sentinel-agent python3 init_database.py
```

---

## 🔍 Verify Fix

### Check if Database Exists
```bash
# Check file exists
docker exec sentinel-agent ls -lh /app/data/sentinel_intel.db

# Expected output:
# -rw-r--r-- 1 root root 48K Feb 15 19:38 /app/data/sentinel_intel.db
```

### Check Tables Created
```bash
# Connect to database
docker exec -it sentinel-agent sqlite3 /app/data/sentinel_intel.db ".tables"

# Expected output:
# actions   incidents  threat_intel
```

### Test Dashboard Directly
```bash
# Inside container Python
docker exec -it sentinel-agent python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/app/data/sentinel_intel.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM incidents")
print(f"Incidents in database: {cursor.fetchone()[0]}")
conn.close()
EOF
```

### View Dashboard Logs
```bash
# If dashboard is running
docker exec -it sentinel-agent docker logs sentinel-agent --tail=50

# Or check if dashboard started successfully
docker exec sentinel-agent curl -s http://localhost:8501
```

---

## 🆘 Still Having Issues?

### Symptom: Empty database path
```bash
# Check environment variables
docker exec sentinel-agent env | grep SENTINEL

# Should show:
# SENTINEL_LOG_DIR=/app/logs
# SENTINEL_DATA_DIR=/app/data
```

### Symptom: Permission denied on /app/data
```bash
# Fix permissions
docker exec sentinel-agent chmod -R 777 /app/data /app/logs
```

### Symptom: Database file but no tables
```bash
# Manually create tables
docker exec -it sentinel-agent python3 << 'EOF'
from data_engine import DataEngine
de = DataEngine()
print("Tables created successfully")
de.close()
EOF
```

### Symptom: Still seeing errors
```bash
# Complete reset
docker-compose down -v
rm -rf data/ logs/
docker-compose up -d --build
sleep 60
docker exec -it sentinel-agent python3 init_database.py
```

---

## 📊 Testing Checklist

- [ ] Database file exists at `/app/data/sentinel_intel.db`
- [ ] All 3 tables created: `incidents`, `actions`, `threat_intel`
- [ ] Web dashboard loads without errors
- [ ] Dashboard sidebar shows correct database path
- [ ] "INCIDENT FEED" tab shows "No recent incidents detected" (empty is OK)
- [ ] "Security Score" metric displays (e.g., 100%)
- [ ] Browser console shows no JavaScript errors

---

## 📚 Related Documentation

- [WEB_DASHBOARD_SETUP.md](WEB_DASHBOARD_SETUP.md) - Complete dashboard setup guide
- [TEST_GUIDE.md](TEST_GUIDE.md) - Testing guide with database info
- [data_engine.py](data_engine.py) - Database engine implementation
- [init_database.py](init_database.py) - Database initialization script
- [docker-startup.sh](docker-startup.sh) - Container startup sequence

---

## 🔐 Notes

- Database runs locally in container at `/app/data/sentinel_intel.db`
- All data persists via Docker volume: `./data:/app/data`
- Database is SQLite3 (lightweight, no server required)
- Multiple connections supported via `check_same_thread=False`
- Tables auto-created if missing (safe to run init multiple times)

