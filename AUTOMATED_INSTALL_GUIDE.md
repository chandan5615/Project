# 🚀 SENTINEL AGENT v2.2 - AUTOMATED INSTALLATION GUIDE

## ✨ **ONE-CLICK INSTALLATION - NO MANUAL SETUP REQUIRED!**

This guide shows how to deploy Sentinel Agent on any fresh system using fully automated installers.

---

## 📋 **What Gets Installed Automatically**

The automated installer handles EVERYTHING:

✅ **Docker & Docker Compose** - Container orchestration  
✅ **System Dependencies** - Python, Apache, networking tools  
✅ **Ollama LLM** - Local AI engine with llama3:8b model  
✅ **Sentinel Agent** - All security monitoring components  
✅ **Database Setup** - SQLite databases for incidents, metrics, etc.  
✅ **Firewall Configuration** - UFW rules (optional enable)  
✅ **Service Startup** - Containers auto-start on boot  

---

## 🐧 **LINUX/UBUNTU INSTALLATION (RECOMMENDED)**

### **Method 1: Direct Installation on Server**

1. **Upload project files to server:**
   ```bash
   scp -r * ubuntu@YOUR_SERVER_IP:~/Project/
   ```

2. **SSH into server:**
   ```bash
   ssh ubuntu@YOUR_SERVER_IP
   cd ~/Project
   ```

3. **Run one-click installer:**
   ```bash
   chmod +x AUTO_INSTALL.sh
   sudo ./AUTO_INSTALL.sh
   ```

4. **Wait 10-15 minutes** while the installer:
   - Installs Docker
   - Sets up Ollama and downloads llama3:8b model
   - Builds containers
   - Initializes databases
   - Starts all services

5. **Access Sentinel Agent:**
   - Dashboard: `http://YOUR_SERVER_IP:8501`
   - API: `http://YOUR_SERVER_IP:8000`
   - Login: `sentinel` / `sentinel`

**That's it!** The system is fully operational.

---

### **Method 2: Remote Installation from Windows**

1. **On Windows machine**, double-click:
   ```
   AUTO_INSTALL_WINDOWS.bat
   ```

2. **Enter server details** when prompted:
   - Server IP: `192.168.31.91`
   - Username: `ubuntu`

3. **The script automatically:**
   - Copies all files to server
   - Runs the Linux installer remotely
   - Shows you access URLs when complete

---

## 🪟 **WINDOWS (FOR TESTING ONLY)**

Windows is supported for **attack testing** and **development**, but production deployment requires Linux.

1. **Double-click:**
   ```
   AUTO_INSTALL_WINDOWS.bat
   ```

2. **The script will:**
   - Check prerequisites (Python, Git, Docker)
   - Install Python packages
   - Help you connect to remote Linux server
   - OR set up local testing environment

3. **Test attacks from Windows:**
   ```powershell
   python test_web_attacks.py
   python continuous_attacks.py --interval 10 --duration 5
   ```

---

## 🎯 **POST-INSTALLATION**

### **Verify Installation**

```bash
# Check containers running
docker-compose ps

# View live logs
docker-compose logs -f sentinel-agent

# Test API health
curl http://localhost:8000/api/health
```

### **Generate Test Attacks**

From **Windows** (attacking the server):
```powershell
python test_web_attacks.py
```

From **Server** itself:
```bash
python3 test_attacks.py --auth-count 20 --web-count 20
```

### **Access Dashboard**

1. Open browser: `http://YOUR_SERVER_IP:8501`
2. Login: `sentinel` / `sentinel`
3. View:
   - Real-time attack feed
   - Security score
   - Wall of Shame (attacker IPs)
   - Network health charts
   - **IP Management** - Block/unblock IPs
   - **Log Viewer** - Auto-refreshing every 8 seconds

---

## 🔧 **IMPORTANT FEATURES**

### **🚀 AI Optimization (NEW!)**

AI crew analysis **ONLY runs for HIGH severity attacks**. This optimizes system resources:

- **HIGH severity** → Full AI analysis with Ollama LLM
- **MEDIUM/LOW severity** → Logged and blocked automatically without AI

This saves ~90% of LLM resources while maintaining security!

### **🔄 Auto-Refresh Dashboard**

- **Logs**: Update every 8 seconds
- **Traffic**: Update every 5 seconds
- **IP Status**: Update every 15 seconds
- **Metrics**: Update every 10 seconds

### **🛡️ IP Management**

- **Block IP**: Click "Block IP" button, enter IP address
- **Unblock IP**: Click ❌ button next to blocked IP
- **View Status**: Real-time blocked/whitelisted IP lists

---

## 📊 **SYSTEM REQUIREMENTS**

### **Minimum (Works Fine)**
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space
- Ubuntu 20.04+ or Debian 11+

### **Recommended (Better Performance)**
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space
- Ubuntu 22.04 LTS

---

## 🔄 **MANAGEMENT COMMANDS**

### **Container Management**
```bash
docker-compose ps           # Status
docker-compose logs -f      # Live logs
docker-compose restart      # Restart all
docker-compose down         # Stop all
docker-compose up -d        # Start all
```

### **Rebuild After Updates**
```bash
cd ~/Project
docker-compose down
docker-compose up -d --build
```

### **View Specific Logs**
```bash
docker logs -f sentinel-agent                    # Main application
docker-compose logs -f sentinel-agent | grep SQL # Only SQL attacks
docker-compose logs -f sentinel-agent | grep XSS # Only XSS attacks
```

### **Database Access**
```bash
# Enter container
docker exec -it sentinel-agent bash

# Access SQLite databases
cd /app/data
sqlite3 sentinel_intel.db
```

---

## 🐛 **TROUBLESHOOTING**

### **Error: "Cannot connect to Docker daemon"**

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### **Error: "Port already in use"**

```bash
# Check what's using ports
sudo netstat -tlnp | grep -E '8000|8501'

# Stop conflicting services
sudo systemctl stop apache2  # If on port 8000
```

### **Ollama not working**

```bash
# Check Ollama status
ps aux | grep ollama

# Start Ollama
ollama serve &

# Test Ollama
ollama list
curl http://localhost:11434/api/tags
```

### **Dashboard not showing logs**

1. **Check API endpoint:**
   ```bash
   curl http://localhost:8000/api/logs?limit=10
   ```

2. **Generate test attacks:**
   ```bash
   python3 test_attacks.py --web-count 10
   ```

3. **Check container logs:**
   ```bash
   docker-compose logs dashboard
   ```

### **AI crew not running**

This is NORMAL for MEDIUM/LOW severity attacks! AI only runs for HIGH severity.

To test AI:
1. Generate HIGH severity attacks (SQL injection, XSS)
2. Check logs for: `⚡ HIGH SEVERITY ATTACK - Activating AI Crew Analysis`

---

## 🔐 **SECURITY NOTES**

### **Change Default Password**
```bash
# TODO: Add password change instructions when implemented
```

### **Enable Firewall**
```bash
sudo ufw enable
sudo ufw status
```

### **SSL/HTTPS (Optional)**
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com
```

---

## 📚 **ADDITIONAL RESOURCES**

### **Files Created by Installer**
- `/home/ubuntu/Project/` - All application files
- `/app/data/` - Databases (in container)
- `/app/logs/` - Application logs (in container)
- `.env` - Environment configuration

### **Useful Links**
- Ollama Docs: https://ollama.ai/docs
- Docker Docs: https://docs.docker.com/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

## 🎓 **EDUCATIONAL USE**

This tool is designed for:
- ✅ Learning cybersecurity concepts
- ✅ Testing your own systems
- ✅ Security research in controlled environments
- ❌ Attacking systems you don't own (ILLEGAL!)

---

## 🆘 **GETTING HELP**

If the automated installer fails:

1. **Check the error message** - most issues are shown clearly
2. **Review logs:**
   ```bash
   docker-compose logs
   ```
3. **Re-run installer:**
   ```bash
   sudo ./AUTO_INSTALL.sh
   ```
4. **Manual recovery:**
   ```bash
   docker-compose down -v  # Clear everything
   sudo ./AUTO_INSTALL.sh  # Fresh install
   ```

---

## ✅ **SUCCESS CHECKLIST**

After installation, verify:

- [ ] Containers running: `docker-compose ps`
- [ ] Dashboard accessible: `http://SERVER_IP:8501`
- [ ] API responding: `curl http://SERVER_IP:8000/api/health`
- [ ] Ollama working: `ollama list`
- [ ] Logs monitoring: Check `docker-compose logs -f`
- [ ] Can generate attacks: `python3 test_attacks.py`
- [ ] Dashboard shows attacks after testing
- [ ] Can block/unblock IPs from dashboard
- [ ] Logs auto-refresh in dashboard

---

## 🎉 **YOU'RE READY!**

Your Sentinel Agent is now:
- ✅ Monitoring for attacks 24/7
- ✅ Automatically responding to threats
- ✅ Using AI for critical threats only
- ✅ Providing real-time dashboard insights
- ✅ Logging everything to databases

**Happy monitoring!** 🛡️

