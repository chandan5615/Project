# Docker Installation & Setup Guide for Sentinel Agent

This guide explains how to install Docker, Docker Compose, and all dependencies required to run the Sentinel Agent project.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Install Docker](#install-docker)
3. [Install Docker Compose](#install-docker-compose)
4. [Install Ollama (AI Model Server)](#install-ollama)
5. [Install Project Dependencies](#install-project-dependencies)
6. [Environment Configuration](#environment-configuration)
7. [Running the Project](#running-the-project)
8. [Verification & Troubleshooting](#verification--troubleshooting)

---

## System Requirements

### Minimum Hardware Specs:
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB+ recommended for Ollama + AI processing)
- **Disk Space**: 20GB minimum (30GB+ recommended)
- **Network**: Internet connection for initial setup

### Supported Operating Systems:
- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+
- **Windows**: Windows 10 Pro/Enterprise, Windows 11 (with WSL2)
- **macOS**: macOS 11+ (Intel or Apple Silicon)

#### Check Your OS:
```bash
# Linux/macOS
uname -a

# Windows PowerShell
[System.Environment]::OSVersion.VersionString
```

---

## Install Docker

Docker is a containerization platform that packages the entire Sentinel Agent application into a standardized container.

### Option 1: Linux (Ubuntu/Debian)

**Step 1: Update package list**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Step 2: Install Docker**
```bash
# Method A: Using Docker's official repository (recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

OR

```bash
# Method B: Using apt directly
sudo apt-get install -y docker.io
```

**Step 3: Verify installation**
```bash
docker --version
docker run hello-world
```

**Step 4: Manage Docker as non-root user (optional but recommended)**
```bash
# Create docker group
sudo groupadd docker

# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify
docker run hello-world
```

**Step 5: Enable Docker auto-start**
```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

### Option 2: Windows

**Prerequisites:**
- Windows 10 (version 1903+) or Windows 11
- WSL2 (Windows Subsystem for Linux 2) installed
- Virtualization enabled in BIOS

**Step 1: Enable WSL2**
```powershell
# Open PowerShell as Administrator
wsl --install
wsl --set-default-version 2
```

**Step 2: Download Docker Desktop**
- Visit: https://www.docker.com/products/docker-desktop
- Download "Docker Desktop for Windows"
- Run the installer (.msi file)

**Step 3: Complete installation**
- Follow the installation wizard
- Restart your computer when prompted
- Open Docker Desktop application

**Step 4: Verify installation**
```powershell
docker --version
docker run hello-world
```

**Step 5: Configure Docker Desktop (Optional)**
- Open Docker Desktop Settings
- Go to Resources → Advanced
- Increase CPUs and Memory allocation as needed
- Increase Disk image size to at least 50GB

---

### Option 3: macOS

**Prerequisites:**
- macOS 11 (Big Sur) or newer
- Apple Silicon (M1/M2/M3) or Intel processor

**Step 1: Download Docker Desktop**
- Visit: https://www.docker.com/products/docker-desktop
- Choose "Apple Silicon" (for M1/M2/M3) or "Intel Chip" version
- Download the .dmg file

**Step 2: Install**
- Open the .dmg file
- Drag Docker icon to Applications folder
- Launch Docker from Applications → Docker.app

**Step 3: Verify installation**
```bash
docker --version
docker run hello-world
```

**Step 4: Configure Docker Desktop (Optional)**
- Open Preferences (⌘ + ,)
- Go to Resources
- Increase CPU and Memory allocation as needed

---

## Install Docker Compose

Docker Compose lets you define and run multi-container applications using a YAML file.

### For Linux:

**Step 1: Download Docker Compose**
```bash
# Latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose
```

**Step 2: Verify installation**
```bash
docker-compose --version
```

Expected output: `Docker Compose version 2.x.x`

---

### For Windows & macOS:

Docker Compose comes pre-installed with Docker Desktop, no separate installation needed.

**Verify installation:**
```powershell
# Windows PowerShell
docker-compose --version

# macOS Terminal
docker-compose --version
```

---

## Install Ollama (AI Model Server)

Ollama is the AI model server that powers Sentinel Agent's intelligence (runs Llama 3:8b locally).

### Option 1: Linux

**Step 1: Download and install Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Step 2: Start Ollama service**
```bash
# If using systemd
sudo systemctl start ollama
sudo systemctl enable ollama

# Or run directly (for testing)
ollama serve
```

**Step 3: Download Llama 3:8b model**
```bash
# This downloads ~4.7GB
ollama pull llama2
# OR for Llama 3 (recommended)
ollama pull llama2:latest
```

**Step 4: Verify**
```bash
curl http://localhost:11434/api/tags
```

---

### Option 2: Windows (via WSL2)

**Step 1: Install WSL2 first** (see Docker installation)

**Step 2: Open WSL2 terminal**
```bash
# Open PowerShell and enter WSL
wsl
```

**Step 3: Inside WSL, install Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Step 4: Download model**
```bash
ollama pull llama2
```

**Step 5: Start Ollama**
```bash
ollama serve
```

---

### Option 3: macOS

**Step 1: Download installer**
- Visit: https://ollama.ai
- Click "Download for macOS"
- Open the .dmg file

**Step 2: Drag Ollama to Applications folder**

**Step 3: Launch Ollama**
- Open Applications → Ollama
- Or run: `ollama serve`

**Step 4: Download model**
```bash
ollama pull llama2
```

**Step 5: Verify**
```bash
curl http://localhost:11434/api/tags
```

---

## Install Project Dependencies

### Option 1: Using Automated Setup Scripts

**For Linux/macOS:**
```bash
cd ~/Project
chmod +x install.sh
./install.sh
```

**For Windows PowerShell:**
```powershell
cd ~/Project
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install.ps1
```

---

### Option 2: Manual Python Installation (if scripted doesn't work)

**Step 1: Verify Python 3.10+**
```bash
# Linux/macOS
python3 --version

# Windows PowerShell
python --version
```

If not installed, download from: https://www.python.org/downloads/

**Step 2: Create virtual environment (optional but recommended)**
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Step 3: Install project dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4: Verify**
```bash
python -c "import crewai; import fastapi; print('✓ All dependencies installed')"
```

---

## Environment Configuration

### Step 1: Create .env file

**On Linux/macOS:**
```bash
cd ~/Project
cp .env.example .env
```

**On Windows PowerShell:**
```powershell
cd ~/Project
cp .env.example .env
```

### Step 2: Edit environment variables

```bash
# Edit with your editor (nano, vim, VS Code, etc.)
nano .env
```

### Step 3: Set required variables

```ini
# Core Configuration
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
AUTH_LOG_PATH=/app/logs/auth.log
WEB_LOG_PATH=/app/logs/access.log

# Ollama Configuration (set to your host IP if on remote server)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# API Configuration
API_PORT=8001
API_HOST=0.0.0.0

# Security Configuration
SECURITY_PASSWORD=your-strong-password-here
DASHBOARD_PASSWORD=your-dashboard-password-here

# Optional: Slack integration
SLACK_WEBHOOK_URL=

# Optional: Remote logging
LOG_SERVER_HOST=
LOG_SERVER_PORT=
```

### Step 4: Verify configuration

```bash
# On your host machine, verify Ollama is accessible
curl http://localhost:11434/api/tags
```

---

## Running the Project

### Method 1: Docker Compose (Recommended)

**Step 1: Ensure Ollama is running**
```bash
# On Linux
sudo systemctl start ollama

# On Windows WSL
ollama serve  # Run in separate terminal

# On macOS
ollama serve  # Run in separate terminal
```

**Step 2: Start all services**
```bash
cd ~/Project
docker-compose up -d
```

**Step 3: Check if running**
```bash
docker-compose ps
```

Expected output:
```
NAME                 STATUS              PORTS
sentinel-agent       Up 2 seconds        0.0.0.0:8001->8001/tcp
```

**Step 4: View logs**
```bash
docker-compose logs -f sentinel-agent
```

**Step 5: Stop services**
```bash
docker-compose down
```

---

### Method 2: Manual Setup (Without Docker)

**Step 1: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Ensure Ollama is running**
```bash
ollama serve  # Run in separate terminal
```

**Step 3: Run Sentinel Agent**
```bash
python main.py
```

---

## Verification & Troubleshooting

### Check if everything is running

**Test Docker:**
```bash
docker --version
docker ps -a
docker-compose ps
```

**Test Ollama:**
```bash
curl http://localhost:11434/api/tags
```

**Test API endpoint:**
```bash
# Linux/macOS
curl http://localhost:8001/health

# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8001/health
```

**Test incident insertion:**
```bash
# Generate test attacks and check database
docker exec sentinel-agent python3 test_attacks.py --auth-count 3 --web-count 3

# Check logs for success
docker exec sentinel-agent tail -20 /app/logs/sentinel.log
```

---

### Common Issues & Solutions

#### 1. Docker daemon not running
**Error:** `Cannot connect to Docker daemon`

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker  # Linux
# Or open Docker Desktop app (Windows/macOS)
```

#### 2. Port already in use
**Error:** `Port 8001 is already allocated`

**Solution:**
```bash
# Find what's using port 8001
sudo lsof -i :8001  # Linux/macOS
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess  # Windows

# Stop the container and restart
docker-compose down
docker-compose up -d
```

#### 3. Ollama not found/not running
**Error:** `Failed to connect to Ollama at http://localhost:11434`

**Solution:**
```bash
# Ensure Ollama is installed
ollama --version

# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

#### 4. Insufficient disk space
**Error:** `no space left on device`

**Solution:**
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a  # Remove unused images and containers
docker system prune -a --volumes  # Also remove volumes
```

#### 5. Permission denied errors
**Error:** `Permission denied while trying to connect to Docker daemon`

**Solution (Linux):**
```bash
# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker
sudo systemctl restart docker
```

#### 6. Container keeps restarting
**Error:** Container exits immediately or restarts frequently

**Solution:**
```bash
# Check logs
docker-compose logs sentinel-agent

# Check system resources
docker stats

# Increase resources or reduce load
```

#### 7. LLM model not found
**Error:** `Model 'llama2' not found`

**Solution:**
```bash
# Pull the model
ollama pull llama2

# List available models
ollama list

# Verify it's loaded
curl http://localhost:11434/api/tags
```

---

### Health Check Commands

Run these commands to verify each component:

```bash
# 1. Docker
docker version

# 2. Docker Compose
docker-compose --version

# 3. Container is running
docker-compose ps

# 4. Ollama is accessible
curl http://localhost:11434/api/tags

# 5. API is responding
curl http://localhost:8001/health

# 6. Database is initialized
docker exec sentinel-agent ls -la /app/data/

# 7. Logs are being written
docker exec sentinel-agent tail -10 /app/logs/sentinel.log

# 8. Attack detection is working
docker exec sentinel-agent python3 test_attacks.py --auth-count 1 --web-count 1
```

---

## Quick Start Summary

**Complete setup in 5 steps:**

1. **Install Docker**: Run `curl -fsSL https://get.docker.com | sudo sh` (Linux)
2. **Install Docker Compose**: Already included with Docker Desktop
3. **Install Ollama**: Run `curl -fsSL https://ollama.ai/install.sh | sh`
4. **Download Llama model**: Run `ollama pull llama2`
5. **Start Sentinel**: Run `docker-compose up -d`

**Then access:**
- CLI Dashboard: `docker exec sentinel-agent python dashboard/cli_dashboard.py`
- API: `http://localhost:8001`
- Logs: `docker-compose logs -f`

---

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Guide**: https://docs.docker.com/compose/
- **Ollama Documentation**: https://ollama.ai
- **Sentinel Agent README**: See `README.md` in project root
- **Project Troubleshooting**: See `TROUBLESHOOTING.md`

---

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f sentinel-agent`
3. Check system resources: `docker stats`
4. Verify all components: Run health check commands above
5. Consult README.md for feature-specific issues

