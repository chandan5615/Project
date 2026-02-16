# Web Dashboard Setup Guide

## 🎯 Problem
Streamlit needs to run **inside the Docker container**, not on the Ubuntu host.

---

## ✅ Solution

### Option 1: Run Dashboard Inside Container (Recommended)

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Ensure container is running
cd ~/Project
docker-compose ps
# Should show: sentinel-agent   Up (healthy)

# Terminal 3: Run Streamlit inside container
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

**Then access:** http://localhost:8501

---

### Option 2: Use CLI Dashboard (No Streamlit Required)

```bash
# Simple command - works everywhere
python3 sentinel_auto.py status

# Or direct Python command
python3 dashboard/cli_dashboard.py
```

---

### Option 3: Install Streamlit in Container (Permanent Fix)

**Edit `requirements.txt` to add/ensure Streamlit:**
```
streamlit>=1.35.0
```

**Rebuild container:**
```bash
docker-compose down -v
docker-compose up -d --build
sleep 30

# Verify
docker exec sentinel-agent python3 -c "import streamlit; print(f'Streamlit {streamlit.__version__} ready')"
```

**Then run dashboard:**
```bash
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

---

## 📊 Three Dashboard Options

### 1. Quick Status (CLI) ⭐ Recommended
```bash
python3 sentinel_auto.py status
```
**Features:** Health, metrics, incidents, IP lists  
**Requires:** Nothing extra  
**Works:** Windows SSH, Linux native  

### 2. Rich Terminal Dashboard
```bash
python3 dashboard/cli_dashboard.py
```
**Features:** Interactive, formatted output  
**Requires:** Nothing extra  
**Works:** Linux/Mac terminals

### 3. Web Dashboard
```bash
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```
**Features:** Web-based, interactive plots  
**Requires:** Streamlit in container  
**Access:** http://localhost:8501

---

## 🐳 One-Liner Web Dashboard Setup

```bash
# Full setup from scratch
docker-compose up -d --build && sleep 30 && \
docker exec -it sentinel-agent bash -c \
'pip install -q streamlit && python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0'
```

---

## ✨ Quick Start

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Dashboard  
ssh ubuntu@10.104.252.89 'cd ~/Project && docker-compose ps && docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0'

# Terminal 3: Access
# Open browser to http://10.104.252.89:8501
```

---

## 🔍 Troubleshooting

### Database Errors: "no such table: incidents"
**Cause:** Database not initialized before dashboard starts  
**Fix:**
```bash
# Initialize database first
docker exec -it sentinel-agent python3 init_database.py

# Then run dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

### No incidents showing in dashboard
**Cause:** Sensors read `/var/log/*` but test attacks were written to `/app/logs/*`  
**Fix:** Generate attacks to `/app/logs` and let sensors use the same path:
```bash
docker exec -it sentinel-agent bash -lc "cd /app && python3 test_attacks.py \
  --auth-log /app/logs/auth.log \
  --web-log /app/logs/access.log \
  --auth-count 50 --web-count 50"
```

### Can the container access host web pages?
**Yes.** This setup uses `network_mode: host`, so the container can access host services at:
- `http://localhost:<port>`
- `http://<host-ip>:<port>`

### "Error initializing database: [Errno 2] No such file or directory: ''"
**Cause:** Database path is empty or misconfigured  
**Fix:**
```bash
# Verify database directory exists
docker exec sentinel-agent ls -la /app/data/

# Restart container (automatically initializes DB)
docker-compose restart
sleep 10

# Then run dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

### "streamlit: command not found"
**Cause:** Running on host instead of container  
**Fix:** Use `docker exec` to run inside container

### "Permission denied /var/lib/dpkg/lock"
**Cause:** Trying to apt install on host  
**Fix:** Don't install on host - use Docker container

### "externally-managed-environment" error
**Cause:** PEP 668 prevents pip install on system Python  
**Fix:** Use Docker container instead

### Container exits after Streamlit starts
**Cause:** Streamlit needs interactive terminal  
**Fix:** Use `-it` flag: `docker exec -it ...`

---

## 📝 Recommended Approach

For **production/scripts:**
```bash
python3 sentinel_auto.py status
```

For **development/interactive:**
```bash
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

---

**Key Point:** All Python tools must run either inside the container (via `docker exec`) or use the automated `sentinel_auto.py` which handles everything.
