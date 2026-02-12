# Authentication Fix Guide

## Issue Identified

The authentication was failing because the FastAPI endpoint wasn't properly configured to accept form data. 

**Error seen:**
```
✗ Failed to authenticate
```

## Root Cause

The `/api/auth/login` endpoint was expecting parameters differently than how `sentinel_auto.py` was sending them.

## Fix Applied

### 1. Updated API Endpoint ([sentinel_api.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\sentinel_api.py))
- Added `Form` parameter support for form data
- Added `pydantic.BaseModel` for structured requests
- Created dual endpoints: `/api/auth/login` (form) and `/api/auth/login-json` (JSON)

### 2. Enhanced Automation Script ([sentinel_auto.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\sentinel_auto.py))
- Added better error handling and logging
- Shows actual HTTP status codes
- Displays password being used (masked)
- Better retry logic with connection error handling

### 3. Created Diagnostic Tools
- **[test_auth.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\test_auth.py)** - Python script to test authentication
- **[diagnose_auth.sh](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\diagnose_auth.sh)** - Complete diagnostic script

## How to Test on Ubuntu

### Quick Test (Recommended)
```bash
cd ~/Project

# Run comprehensive diagnostics
chmod +x diagnose_auth.sh
./diagnose_auth.sh
```

This script will:
1. ✓ Check container status
2. ✓ Verify API is responding
3. ✓ Extract admin password
4. ✓ Check database exists
5. ✓ Verify admin user in DB
6. ✓ Test authentication
7. ✓ Generate and save API token
8. ✓ Test API access with token

### Manual Test
```bash
cd ~/Project

# Test with Python script
python3 test_auth.py
```

### Using Automation (Should work now)
```bash
cd ~/Project

# Setup (gets token)
python3 sentinel_auto.py setup

# If that works, run demo
python3 sentinel_auto.py demo
```

## What Changed in Code

### Before (Broken):
```python
# API endpoint expected query params
@app.post("/api/auth/login")
def login(username: str, password: str, ...):
    ...

# Script sent form data
requests.post(url, data={"username": "admin", "password": pw})
# ❌ Mismatch!
```

### After (Fixed):
```python
# API accepts form data
@app.post("/api/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    ...
):
    ...

# Script sends form data
requests.post(url, data={"username": "admin", "password": pw})
# ✅ Works!
```

## Troubleshooting

### If authentication still fails:

#### 1. Check the password is correct
```bash
# Extract password from logs
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"
```

#### 2. Test manually with curl
```bash
# Get the password
PASSWORD=$(docker-compose logs sentinel-agent | grep "Password:" | tail -1 | awk -F': ' '{print $NF}')

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" \
  -d "password=$PASSWORD"
```

Should return:
```json
{"token":"...", "type":"bearer", "expires_in":86400}
```

#### 3. Check database was initialized
```bash
docker exec sentinel-agent ls -la /app/data/
# Should show auth.db, sentinel_intel.db, etc.
```

#### 4. Verify admin user exists
```bash
docker exec sentinel-agent /opt/venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('/app/data/auth.db')
cursor = conn.cursor()
cursor.execute('SELECT username, role FROM users')
print(cursor.fetchall())
"
```

Should show: `[('admin', 'admin')]`

#### 5. Check API logs
```bash
docker-compose logs sentinel-agent | grep -i auth
```

#### 6. Restart container with fresh database
```bash
# Complete reset
docker-compose down
rm -rf data/
docker-compose up -d

# Wait 60 seconds for health check
sleep 60

# Get new password
docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"

# Test again
python3 test_auth.py
```

## Expected Flow After Fix

```
1. Container starts
   └─> Initializes databases
   └─> Creates admin user with random password
   └─> Logs password to console

2. sentinel_auto.py setup
   └─> Waits for container to be healthy
   └─> Extracts password from logs
   └─> Calls /api/auth/login with form data
   └─> Receives JWT token
   └─> Saves token to .sentinel_token

3. sentinel_auto.py demo
   └─> Reads token from .sentinel_token
   └─> Makes authenticated API calls
   └─> Runs attack simulations
   └─> Shows results
```

## Files Modified

1. **[sentinel_api.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\sentinel_api.py#L1-L6)** - Added Form import and LoginRequest model
2. **[sentinel_api.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\sentinel_api.py#L349-L390)** - Updated login endpoints
3. **[sentinel_auto.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\sentinel_auto.py#L115-L160)** - Enhanced error handling

## Files Created

1. **[test_auth.py](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\test_auth.py)** - Authentication test script
2. **[diagnose_auth.sh](c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\diagnose_auth.sh)** - Complete diagnostic shell script
3. **AUTH_FIX_GUIDE.md** - This guide

## Verification

After applying fixes, run on Ubuntu:

```bash
cd ~/Project
chmod +x diagnose_auth.sh
./diagnose_auth.sh
```

Expected output:
```
✓ Container is running
✓ Container is healthy  
✓ API is responding
✓ Password extracted
✓ Auth database exists
✓ Admin user exists in database
✓ Authentication SUCCESSFUL!
✓ Token saved to .sentinel_token
✓ API access working!
```

Then you can run:
```bash
python3 sentinel_auto.py demo
```

## Summary

✅ **API endpoint fixed** to accept form data properly  
✅ **Automation script enhanced** with better error messages  
✅ **Diagnostic tools created** for troubleshooting  
✅ **Complete testing workflow** documented

The authentication should now work reliably!
