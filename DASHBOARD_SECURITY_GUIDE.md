# [SECURE] Dashboard Security Guide - Sentinel Agent v2.3

**Critical Security Update: Dashboard Authentication**

---

## [WARNING] CRITICAL VULNERABILITY FIXED

### **Before v2.3.1 (VULNERABLE):**
```
[ERROR] Dashboard: http://YOUR_SERVER:8501
├─ No username/password required
├─ Anyone on network can access
├─ Can view ALL attack data
├─ Can unblock/block ANY IP
└─ ATTACKERS COULD UNBLOCK THEMSELVES!
```

### **After v2.3.1 (SECURE):**
```
[OK] Dashboard: http://YOUR_SERVER:8501
├─ Login page with username/password
├─ Session-based authentication
├─ Auto-logout after 24 hours inactivity
├─ Failed login attempts logged
└─ Only authenticated admins can access
```

---

## [DOCS] Quick Start: Enable Authentication

### **Step 1: Rebuild Docker Container**

```bash
cd Project/
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Step 2: Get Default Credentials**

**Option A: Check Docker Logs**
```bash
docker logs sentinel-agent | grep "DEFAULT ADMIN"

# You'll see:
# ======================================================================
# DEFAULT ADMIN CREDENTIALS (SAVE THESE NOW!):
#   Username: admin
#   Password: xY9mKp2Qr5vN8sL4
# CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!
# ======================================================================
```

**Option B: Check Credentials File**
```bash
docker exec sentinel-agent cat /app/data/INITIAL_CREDENTIALS.txt

# Output:
# Initial Admin Credentials
# Generated: 2026-02-25T11:30:00
# Username: admin
# Password: xY9mKp2Qr5vN8sL4
# 
# WARNING: Change password immediately!
# Delete this file after saving credentials.
```

### **Step 3: First Login**

1. Navigate to: `http://YOUR_SERVER:8501`
2. You'll see the login page ([SECURE] Sentinel Agent Login)
3. Enter credentials from Step 2
4. Click **[UNBLOCK] Login**
5. You're in! [SUCCESS]

### **Step 4: Change Password (CRITICAL)**

```bash
# Connect to container
docker exec -it sentinel-agent bash

# Run password change script
python3 -c "
from auth import DashboardAuthenticator
auth = DashboardAuthenticator()
auth.change_password('admin', 'OLD_PASSWORD', 'NEW_STRONG_PASSWORD')
print('Password changed successfully!')
"
```

---

## [PROTECT] Security Features

### **1. Session Management**
- Sessions expire after **24 hours** of inactivity
- Auto-logout when session expires
- Session tokens stored securely in database

### **2. Password Security**
- Passwords hashed using **bcrypt** (industry standard)
- Automatic salting (prevents rainbow table attacks)
- No plaintext passwords stored anywhere

### **3. Failed Login Protection**
- Failed attempts logged to `/var/log/sentinel/auth.log`
- Timestamps and IP addresses recorded
- Can implement rate limiting (see Advanced section)

### **4. Multi-User Support**
```python
# Create additional users via CLI
from auth import DashboardAuthenticator
auth = DashboardAuthenticator()

# Create analyst user (read-only)
auth.create_user("analyst", "SecurePass123!", "analyst")

# Create viewer user (view-only)
auth.create_user("viewer", "ViewerPass456!", "viewer")
```

---

## [CONFIG] Configuration Options

### **Option 1: Disable Authentication (Development Only)**

**[WARNING]: Only use on isolated/local networks!**

Edit `web_dashboard.py`:
```python
# Line ~1180 in main() function:
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True  # ← Set to True to bypass
```

Then rebuild:
```bash
docker-compose build
docker-compose up -d
```

### **Option 2: Change Session Timeout**

Edit `auth.py`:
```python
# Line ~157 in authenticate() function:
expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
#                                          ↑ Change 24 to desired hours
```

Examples:
- `hours=1` → Session expires after 1 hour
- `hours=168` → Session expires after 1 week
- `hours=24*365` → Session never expires (not recommended)

### **Option 3: IP Whitelist for Dashboard**

**Restrict dashboard access to specific IPs:**

```bash
# Allow only local network (192.168.31.0/24) to access port 8501
sudo iptables -A INPUT -p tcp --dport 8501 ! -s 192.168.31.0/24 -j DROP

# Allow only specific IP (e.g., admin's workstation)
sudo iptables -A INPUT -p tcp --dport 8501 ! -s 192.168.31.100 -j DROP

# Save rules
sudo netfilter-persistent save
```

### **Option 4: VPN-Only Access (Best Practice)**

**Setup Wireguard VPN:**
```bash
# Install Wireguard
sudo apt install wireguard

# Dashboard only accessible through VPN tunnel
sudo iptables -A INPUT -p tcp --dport 8501 ! -i wg0 -j DROP
```

---

## [ALERT] Emergency Access Recovery

### **Scenario 1: Forgot Password**

```bash
# Reset admin password to known value
docker exec -it sentinel-agent python3 -c "
from auth import DashboardAuthenticator
from security_manager import get_security_manager
import sqlite3

auth = DashboardAuthenticator()
new_password = 'TempPass2026!'
password_hash = auth.security.hash_password(new_password)

conn = sqlite3.connect('/app/data/auth.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', 
               (password_hash, 'admin'))
conn.commit()
conn.close()

print('Password reset to: TempPass2026!')
print('Login and change immediately!')
"
```

### **Scenario 2: Database Corrupted**

```bash
# Delete auth database (will recreate with default user)
docker exec sentinel-agent rm /app/data/auth.db
docker restart sentinel-agent

# Check logs for new credentials
docker logs sentinel-agent | grep "DEFAULT ADMIN"
```

### **Scenario 3: Locked Out Completely**

**Temporarily disable authentication:**
```bash
# Edit web_dashboard.py to bypass auth
docker exec -it sentinel-agent nano /app/dashboard/web_dashboard.py

# Find line with "if not st.session_state.authenticated"
# Comment it out:
#     # if not st.session_state.authenticated and st.session_state.auth_initialized:
#     #     _show_login_page()
#     #     return
st.session_state.authenticated = True  # Add this line

# Save and restart
docker restart sentinel-agent
```

---

## [STATS] Monitoring Authentication

### **Check Login Activity**

**View all sessions:**
```bash
docker exec sentinel-agent sqlite3 /app/data/auth.db \
  "SELECT u.username, s.created_at, s.expires_at 
   FROM sessions s 
   JOIN users u ON s.user_id = u.id 
   ORDER BY s.created_at DESC;"
```

**View last login for all users:**
```bash
docker exec sentinel-agent sqlite3 /app/data/auth.db \
  "SELECT username, role, last_login 
   FROM users 
   ORDER BY last_login DESC;"
```

**Count failed login attempts:**
```bash
docker exec sentinel-agent grep "Invalid username or password" \
  /var/log/sentinel/auth.log | wc -l
```

---

## [SECURE] Best Practices

### **1. Strong Passwords**
[OK] **DO:**
- Use passwords ≥ 16 characters
- Include uppercase, lowercase, numbers, symbols
- Use password manager (LastPass, 1Password, Bitwarden)

[ERROR] **DON'T:**
- Use `admin`, `password`, `123456`
- Reuse passwords from other systems
- Share credentials via email/chat

### **2. Network Security**
```bash
# [OK] Recommended: Dashboard only on local network
sudo ufw allow from 192.168.31.0/24 to any port 8501

# [ERROR] Avoid: Exposing dashboard to internet
sudo ufw allow 8501  # DANGEROUS!
```

### **3. Regular Audits**
```bash
# Check who accessed dashboard this week
docker exec sentinel-agent sqlite3 /app/data/auth.db \
  "SELECT username, last_login FROM users 
   WHERE last_login > datetime('now', '-7 days');"
```

### **4. Session Cleanup**
```bash
# Delete expired sessions (automatic, but can force):
docker exec sentinel-agent sqlite3 /app/data/auth.db \
  "DELETE FROM sessions WHERE expires_at < datetime('now');"
```

---

## [TOOLS] Advanced: Rate Limiting (Optional)

**Prevent brute-force attacks by limiting login attempts:**

Create `/app/dashboard/rate_limiter.py`:
```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_attempts=5, window_minutes=15):
        self.max_attempts = max_attempts
        self.window = timedelta(minutes=window_minutes)
        self.attempts = defaultdict(list)
    
    def allow_login(self, ip_address):
        now = datetime.now()
        # Remove old attempts
        self.attempts[ip_address] = [
            t for t in self.attempts[ip_address] 
            if now - t < self.window
        ]
        
        # Check if limit exceeded
        if len(self.attempts[ip_address]) >= self.max_attempts:
            return False
        
        # Record attempt
        self.attempts[ip_address].append(now)
        return True
```

Integrate into `web_dashboard.py`:
```python
# At top of file:
from rate_limiter import RateLimiter

# In _show_login_page():
if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)

# Before authentication:
if not st.session_state.rate_limiter.allow_login(st.session_state.get("client_ip", "unknown")):
    st.error("[BLOCKED] Too many failed attempts. Try again in 15 minutes.")
    return
```

---

## [DOCS] FAQ

### **Q: Can I use HTTPS instead of HTTP?**

**A:** Yes! Configure reverse proxy with SSL:

**Using Nginx:**
```nginx
# /etc/nginx/sites-available/sentinel
server {
    listen 443 ssl;
    server_name sentinel.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/sentinel.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sentinel.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### **Q: Can I integrate with LDAP/Active Directory?**

**A:** Yes, but requires custom modification:

```python
# In auth.py, modify authenticate():
import ldap

def authenticate_ldap(self, username, password):
    try:
        conn = ldap.initialize('ldap://your-domain-controller')
        conn.simple_bind_s(f'{username}@domain.com', password)
        return True, self._create_session(username)
    except ldap.INVALID_CREDENTIALS:
        return False, None
```

### **Q: How do I backup authentication database?**

```bash
# Backup
docker exec sentinel-agent sqlite3 /app/data/auth.db \
  ".backup /app/data/auth_backup_$(date +%Y%m%d).db"

# Copy to host
docker cp sentinel-agent:/app/data/auth_backup_*.db ./backups/

# Restore
docker cp ./backups/auth_backup_20260225.db sentinel-agent:/app/data/auth.db
docker restart sentinel-agent
```

---

## [TEST] Testing Authentication

### **Test 1: Verify Login Page Shows**
```bash
curl http://YOUR_SERVER:8501
# Should see "Sentinel Agent Login" page
```

### **Test 2: Verify Invalid Credentials Fail**
```python
from auth import DashboardAuthenticator
auth = DashboardAuthenticator()

success, token = auth.authenticate("admin", "WRONG_PASSWORD")
assert success == False  # Should fail
```

### **Test 3: Verify Valid Credentials Work**
```python
success, token = auth.authenticate("admin", "correct_password")
assert success == True
assert token is not None
```

### **Test 4: Verify Session Expires**
```bash
# Wait 24 hours (or modify timedelta to 1 minute for testing)
# Try to access dashboard with old session
# Should redirect to login page
```

---

## [OK] Security Checklist

Before deploying to production:

- [ ] Changed default admin password
- [ ] Deleted `/app/data/INITIAL_CREDENTIALS.txt`
- [ ] Configured firewall to restrict port 8501
- [ ] Enabled HTTPS with valid SSL certificate
- [ ] Set up regular database backups
- [ ] Configured session timeout appropriately
- [ ] Tested login/logout functionality
- [ ] Verified failed login attempts are logged
- [ ] Documented credentials in secure password manager
- [ ] Created backup admin account
- [ ] Tested emergency access recovery procedure

---

## [DEPLOY] Summary

**Before:**
- [ERROR] No authentication
- [ERROR] Public access if port exposed
- [ERROR] Attackers could manipulate firewall rules

**After:**
- [OK] Secure login with bcrypt hashing
- [OK] Session-based authentication
- [OK] Failed login logging
- [OK] Multi-user support
- [OK] Easy password reset

**Your dashboard is now SECURE! [SECURE]**

For support: Check logs in `/var/log/sentinel/auth.log`
