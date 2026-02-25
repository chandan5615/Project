# 🔒 Securing Dashboard Port 8501 - Local Network Only

**Date**: February 25, 2026  
**Issue**: Port 8501 currently exposed to public (0.0.0.0)  
**Goal**: Restrict dashboard to local network ONLY (192.168.31.0/24)

---

## ⚠️ Current Vulnerability

**Your docker-compose.yml (Line 95):**
```yaml
ports:
  - "${DASHBOARD_BIND_IP:-0.0.0.0}:8501:8501"  # ❌ EXPOSED TO PUBLIC!
```

**What this means:**
```
0.0.0.0:8501 → Binds to ALL network interfaces
├─ ✅ Localhost (127.0.0.1)
├─ ✅ Local network (192.168.31.91)
├─ ❌ Public internet (if server has public IP)
└─ ❌ ANY IP that can reach your server!

If your server has a public IP, ANYONE can access:
http://YOUR_PUBLIC_IP:8501
```

---

## 🛡️ Solution: Choose Your Security Level

### **Option 1: Localhost Only (Most Secure)** ⭐ Recommended if using SSH

**Best for**: Only access dashboard when SSH'd into server or via SSH tunnel

**Modify docker-compose.yml:**
```yaml
ports:
  - "127.0.0.1:8501:8501"  # ✅ LOCALHOST ONLY
```

**Access methods:**
```bash
# Method A: SSH into server, then browse locally
ssh ubuntu@192.168.31.91
firefox http://localhost:8501  # Or lynx/links

# Method B: SSH tunnel from your PC (BEST)
# On your Windows PC:
ssh -L 8501:localhost:8501 ubuntu@192.168.31.91
# Then browse: http://localhost:8501 on your PC
# Traffic is encrypted through SSH!
```

**Pros:**
- ✅ Maximum security - NO network exposure
- ✅ Even local network can't access
- ✅ SSH tunnel provides encryption
- ✅ Perfect for single-admin setup

**Cons:**
- ❌ Requires SSH tunnel setup
- ❌ Can't access from other LAN devices directly

---

### **Option 2: Local Network Only (Balanced)** ⭐ Recommended for LAN

**Best for**: Access from any device on your local network (192.168.31.0/24)

**Modify docker-compose.yml:**
```yaml
ports:
  - "192.168.31.91:8501:8501"  # ✅ LOCAL IP ONLY
```

**Access:**
```
✅ From any LAN device: http://192.168.31.91:8501
❌ From internet: Connection refused
```

**Pros:**
- ✅ Easy access from any LAN device
- ✅ No SSH tunnel needed
- ✅ Still blocks public internet
- ✅ Perfect for team on same network

**Cons:**
- ❌ Anyone on LAN can access (use authentication!)
- ❌ Vulnerable if someone joins your WiFi

---

### **Option 3: Firewall-Based Blocking (Advanced)** 

**Best for**: Keep Docker config flexible, use firewall for restriction

**Keep docker-compose.yml as-is, add firewall rule:**
```bash
# Block all external access to port 8501, allow only local network
sudo iptables -I INPUT -p tcp --dport 8501 ! -s 192.168.31.0/24 -j DROP

# Save rule permanently
sudo netfilter-persistent save
```

**Alternative - Allow only specific IPs:**
```bash
# Allow only your workstation (192.168.31.183)
sudo iptables -I INPUT -p tcp --dport 8501 -s 192.168.31.183 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 8501 -j DROP
```

**Pros:**
- ✅ Flexible - can change rules without rebuilding Docker
- ✅ Works even if Docker config changes
- ✅ Can whitelist specific IPs

**Cons:**
- ❌ More complex to manage
- ❌ Rules can be accidentally deleted
- ❌ Need to persist across reboots

---

## 🚀 Quick Fix - Apply Now

### **RECOMMENDED: Option 2 (Local Network Only)**

**Step 1: Update docker-compose.yml**
```bash
ssh ubuntu@192.168.31.91
cd ~/Project

# Edit docker-compose.yml
nano docker-compose.yml

# Find line 95, change:
# FROM:
- "${DASHBOARD_BIND_IP:-0.0.0.0}:8501:8501"

# TO:
- "192.168.31.91:8501:8501"

# Save: Ctrl+O, Enter, Ctrl+X
```

**Step 2: Rebuild and restart**
```bash
docker-compose down
docker-compose up -d
```

**Step 3: Verify it's locked down**
```bash
# From server (should work):
curl http://192.168.31.91:8501
# Expected: HTML response or "Streamlit app"

# Check what's listening:
sudo netstat -tulpn | grep 8501
# Expected: 192.168.31.91:8501 (NOT 0.0.0.0:8501)
```

**Step 4: Test from external network (if you have public IP)**
```bash
# From a device OUTSIDE your network (mobile hotspot, etc.):
curl http://YOUR_PUBLIC_IP:8501
# Expected: Connection timeout or refused ✅
```

---

## 📊 Port Binding Comparison

| Bind Address | Local Access | LAN Access | Internet Access | Security Level |
|--------------|--------------|------------|-----------------|----------------|
| `0.0.0.0:8501` | ✅ Yes | ✅ Yes | ⚠️ **YES** | ❌ **VULNERABLE** |
| `127.0.0.1:8501` | ✅ Yes | ❌ No | ❌ No | ✅ **MAXIMUM** |
| `192.168.31.91:8501` | ✅ Yes | ✅ Yes | ❌ No | ✅ **GOOD** |
| `0.0.0.0 + iptables` | ✅ Yes | ✅ Yes (filtered) | ❌ No | ✅ **GOOD** |

---

## 🔍 How to Check Current Exposure

**Check what IP Docker is bound to:**
```bash
ssh ubuntu@192.168.31.91
docker port sentinel-agent 8501
# Current output (vulnerable):
# 0.0.0.0:8501 -> 8501  ❌ BAD!

# After fix (secure):
# 192.168.31.91:8501 -> 8501  ✅ GOOD!
```

**Check with netstat:**
```bash
sudo netstat -tulpn | grep 8501

# Vulnerable output:
# tcp  0  0  0.0.0.0:8501  0.0.0.0:*  LISTEN  12345/docker-proxy  ❌

# Secure output (localhost):
# tcp  0  0  127.0.0.1:8501  0.0.0.0:*  LISTEN  12345/docker-proxy  ✅

# Secure output (LAN only):
# tcp  0  0  192.168.31.91:8501  0.0.0.0:*  LISTEN  12345/docker-proxy  ✅
```

**Check from external network:**
```bash
# From your Windows PC (or any LAN device):
nmap -p 8501 192.168.31.91

# Secure output:
# 8501/tcp open  streamlit-app

# From internet (if server has public IP):
nmap -p 8501 YOUR_PUBLIC_IP

# Secure output:
# 8501/tcp filtered  (connection blocked by firewall)
# or
# 8501/tcp closed  (port not listening on public interface)
```

---

## 🧪 Testing After Fix

**Test 1: Local access still works**
```bash
ssh ubuntu@192.168.31.91
curl http://192.168.31.91:8501
# Expected: HTTP 200 response ✅
```

**Test 2: LAN access works (from your Windows PC)**
```powershell
# On Windows:
curl http://192.168.31.91:8501
# Expected: HTTP response or browser loads page ✅
```

**Test 3: Internet access blocked**
```bash
# From mobile hotspot or external network:
curl --connect-timeout 5 http://YOUR_PUBLIC_IP:8501
# Expected: Connection timeout ✅
```

---

## 🔒 Additional Security Hardening

### **1. Combine Network Binding + Authentication**

Best practice: Use BOTH network restriction AND login

```yaml
# docker-compose.yml
ports:
  - "192.168.31.91:8501:8501"  # Network restriction ✅
```

**PLUS** authentication in web_dashboard.py (already implemented) ✅

**Result**: Defense in depth
- Layer 1: Network can't even reach the port ✅
- Layer 2: If they somehow do, login required ✅

---

### **2. Use UFW (Uncomplicated Firewall)**

**Install UFW:**
```bash
sudo apt install ufw

# Allow SSH first (don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow local network only for dashboard
sudo ufw allow from 192.168.31.0/24 to any port 8501

# Deny all other access to 8501
sudo ufw deny 8501/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

---

### **3. Port Knocking (Advanced)**

**Concept**: Port 8501 is closed by default, only opens after secret knock

```bash
# Install knockd
sudo apt install knockd

# Configure /etc/knockd.conf
[openDashboard]
    sequence    = 7000,8000,9000
    seq_timeout = 5
    command     = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 8501 -j ACCEPT
    tcpflags    = syn

[closeDashboard]
    sequence    = 9000,8000,7000
    seq_timeout = 5
    command     = /sbin/iptables -D INPUT -s %IP% -p tcp --dport 8501 -j ACCEPT
    tcpflags    = syn

# Usage:
# From your PC, knock to open port:
knock 192.168.31.91 7000 8000 9000
# Now access: http://192.168.31.91:8501
# When done, knock to close:
knock 192.168.31.91 9000 8000 7000
```

---

## 📖 FAQ

### **Q: Will this break the main website (port 8000)?**

**A:** No! Port 8000 can stay as `0.0.0.0:8000` if you want it public.

```yaml
ports:
  - "0.0.0.0:8000:8000"        # ✅ Public website (if desired)
  - "192.168.31.91:8501:8501"  # ✅ Private dashboard (LAN only)
```

### **Q: Can I use environment variable to switch binding?**

**A:** Yes! Already supported:

```bash
# In .env file or docker-compose.yml
DASHBOARD_BIND_IP=192.168.31.91

# Then in docker-compose.yml:
ports:
  - "${DASHBOARD_BIND_IP:-192.168.31.91}:8501:8501"
```

### **Q: How do I access from multiple local networks?**

**A:** Use VPN (Wireguard/OpenVPN):

```bash
# Install Wireguard
sudo apt install wireguard

# Configure VPN to connect home network + office network
# Dashboard accessible to all VPN clients
# Port still blocked from internet
```

### **Q: What if I accidentally lock myself out?**

**A:** Access via docker exec:

```bash
# From server console (not SSH):
docker exec -it sentinel-agent bash
apt update && apt install lynx
lynx http://localhost:8501
```

---

## ✅ Security Checklist

Before going to production:

- [ ] Changed docker-compose.yml to bind 8501 to local IP
- [ ] Verified `docker port sentinel-agent` shows local IP only
- [ ] Tested access from LAN works
- [ ] Tested access from internet FAILS (if applicable)
- [ ] Configured firewall rules (iptables/UFW)
- [ ] Enabled dashboard authentication
- [ ] Changed default admin password
- [ ] Documented who can access dashboard
- [ ] Set up SSH tunnel for remote admin (if needed)
- [ ] Configured monitoring for failed access attempts

---

## 🎯 Summary

**Your Goal**: Dashboard on local network only, NOT public

**Best Solution**: 
```yaml
# docker-compose.yml line 95:
- "192.168.31.91:8501:8501"  # ✅ LOCAL ONLY
```

**Combined with**:
- ✅ Authentication (already implemented)
- ✅ Firewall rules (optional but recommended)
- ✅ Regular security audits

**Access From**:
- ✅ Server itself: `http://localhost:8501`
- ✅ Your PC on LAN: `http://192.168.31.91:8501`
- ❌ Internet: Connection refused ✅ SECURE!

**This is the RIGHT security approach!** 🔒
