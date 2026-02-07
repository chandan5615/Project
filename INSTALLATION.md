#  Sentinel Agent - Complete Installation Guide

## Quick Start (2 Minutes)

### Choose Your Installation Method

#### 🪟 **Windows (Recommended: PowerShell)**
```powershell
# Right-click PowerShell → Run As Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1
```

#### 🪟 **Windows (Alternative: Batch)**
```cmd
install.bat
```

####  **Linux/macOS**
```bash
chmod +x install.sh
./install.sh
```

####  **Cross-Platform (Python)**
```bash
python install.py
```

---

## Installation Methods Explained

### Method 1: PowerShell Script (Recommended for Windows)
**File:** `install.ps1`

**Features:**
- ✅ Comprehensive error checking
- ✅ Colored output for clarity
- ✅ Virtual environment management
- ✅ Automatic dependency verification
- ✅ Database initialization

**Prerequisites:**
- PowerShell 5.0+
- Python 3.10+
- Admin privileges (recommended)

**How to Run:**
```powershell
# Option 1: If you get execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1

# Option 2: Bypass execution policy for this run only
PowerShell -ExecutionPolicy Bypass -File .\install.ps1

# Optional flags
.\install.ps1 -SkipOllamaCheck  # Skip Ollama check
.\install.ps1 -Dev              # Development mode
```

---

### Method 2: Batch Script (Windows)
**File:** `install.bat`

**Features:**
- ✅ Traditional Windows batch file
- ✅ No execution policy issues
- ✅ Works on all Windows versions
- ✅ Color-coded output

**How to Run:**
```cmd
# Simply double-click install.bat OR run:
install.bat
```

---

### Method 3: Shell Script (Linux/macOS)
**File:** `install.sh`

**Features:**
- ✅ Full Linux/macOS support
- ✅ Automatic dependency detection
- ✅ System package checking
- ✅ POSIX compliant

**How to Run:**
```bash
chmod +x install.sh
./install.sh
```

**For macOS with Homebrew:**
```bash
# Install Python 3.10+ if needed
brew install python@3.10

# Run installer
./install.sh
```

---

### Method 4: Python Script (Cross-Platform)
**File:** `install.py`

**Features:**
- ✅ Works on Windows, Linux, macOS
- ✅ No shell script issues
- ✅ Platform detection
- ✅ Detailed error messages

**How to Run:**
```bash
python install.py
# or
python3 install.py
```

**Advanced Options:**
```bash
python install.py --help                    # Show all options
python install.py --skip-ollama            # Skip Ollama check
python install.py --skip-python-check      # Skip Python version check
python install.py --dev                    # Development mode
```

---

## System Requirements

### Minimum Requirements
| Component | Requirement | Notes |
|-----------|------------|-------|
| **OS** | Windows 10+, Ubuntu 18.04+, macOS 10.14+ | Any 64-bit OS works |
| **Python** | 3.10+ | Check: `python --version` |
| **RAM** | 4 GB | 8 GB recommended |
| **Disk Space** | 2 GB | For venv + dependencies |
| **Ollama** | Latest | Required for AI features |
| **Ollama Model** | llama3:8b | Auto-downloaded (~4GB) |

### Network
- Internet connection for first-time dependency download
- Ollama must be accessible (default: `localhost:11434`)

### Optional Tools
- Git (for version control)
- Docker (for containerized deployment)
- WSL2 (for Windows, Linux-like experience)

---

## Pre-Installation Checklist

Before running the installer, verify you have:

- [ ] Python 3.10 or higher installed
- [ ] Ollama downloaded and ready (https://ollama.ai)
- [ ] At least 2 GB free disk space
- [ ] Internet connection (for package downloads)
- [ ] Administrator access (optional but recommended)

### Check Python Installation
```bash
python --version
# Should show: Python 3.10.x or higher
```

### Check Ollama Installation
```bash
ollama --version
# Should show version number
```

---

## Step-by-Step Installation

### Step 1: Prepare Environment
```bash
# Navigate to project directory
cd path/to/Sentinel-Agent

# Verify Python installation
python --version

# Verify Ollama is installed
ollama --version
```

### Step 2: Run Appropriate Installer

**For Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1
```

**For Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**For any platform (Python):**
```bash
python install.py
```

### Step 3: Wait for Installation
The installer will:
1. ✅ Check Python version (3.10+)
2. ✅ Check Ollama installation
3. ✅ Create virtual environment (`venv`)
4. ✅ Upgrade pip/setuptools
5. ✅ Install all dependencies from `requirements.txt`
6. ✅ Initialize databases
7. ✅ Create `.env` configuration file
8. ✅ Verify installation

**Estimated Time:** 3-5 minutes (depends on internet speed)

### Step 4: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

### Step 5: Verify Installation
```bash
# Test that all modules can be imported
python -c "import crewai, fastapi, streamlit; print('✅ All modules imported successfully')"

# Check installed packages
pip list | grep -E "crewai|fastapi|streamlit"
```

---

## Post-Installation Setup

### Start Ollama Server

Open a **new terminal** and start Ollama:

```bash
ollama serve
```

You should see output like:
```
Starting Ollama server...
 Ollama is running on 127.0.0.1:11434
```

### Pull Required Model (First Time Only)

Open **another new terminal** and download the AI model:

```bash
ollama pull llama3:8b
```

This downloads a 4 GB model. Wait for completion.

### Verify .env Configuration

Check `.env` file was created:

```bash
# Windows (PowerShell)
Get-Content .env

# Unix/Linux/macOS
cat .env
```

You should see configuration for:
- Ollama model (`llama3:8b`)
- API port (8000)
- Dashboard port (8501)

---

## Starting the System

Once installation is complete, follow this order in separate terminals:

### Terminal 1: Start Ollama (Keep Running)
```bash
ollama serve
# Keep this running in background
```

### Terminal 2: Run Core System
```bash
# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Start the system
python main.py
```

You should see:
```
 Sentinel Agent Starting...
 Initializing data engine...
 Starting threat intelligence system...
✅ All systems initialized
```

### Terminal 3: Start REST API (Optional)
```bash
source venv/bin/activate

python sentinel_api.py
```

Access at: `http://localhost:8000`

### Terminal 4: Start Dashboard (Optional)
```bash
source venv/bin/activate

streamlit run dashboard/web_dashboard.py
```

Access at: `http://localhost:8501`

---

## Troubleshooting

### ❌ Python Not Found
**Error:** `'python' is not recognized` or `command not found: python`

**Solution:**
- Windows: Reinstall Python, check "Add Python to PATH" during installation
- Mac/Linux: Install Python 3.10+ using `brew install python@3.10` or apt
- Verify: `python --version` should show 3.10+

### ❌ Ollama Not Found
**Error:** `'ollama' is not recognized` or `command not found: ollama`

**Solution:**
- Download Ollama from https://ollama.ai
- Add Ollama to PATH or restart terminal after installation
- Verify: `ollama --version` should show version number
- Installation can continue without Ollama, but AI features won't work

### ❌ Permission Denied (Linux/macOS)
**Error:** `Permission denied: './install.sh'`

**Solution:**
```bash
chmod +x install.sh
./install.sh
```

### ❌ PowerShell Execution Policy (Windows)
**Error:** `PowerShell cannot execute scripts...`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1
```

### ❌ Port Already in Use
**Error:** `Address already in use: 127.0.0.1:8000`

**Solution:**
Edit `.env` and change the port:
```
API_PORT=8001  # or another unused port
```

### ❌ Virtual Environment Won't Activate
**Windows PowerShell Error:** `execution disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### ❌ Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'crewai'`

**Solution:**
```bash
# Make sure virtual environment is activated (check for (venv) prefix)
# If activated, reinstall requirements:
pip install --upgrade --force-reinstall -r requirements.txt
```

### ❌ Database Initialization Failed
**Warning:** Database initialization reported errors

**Solution:**
- This is usually OK, databases will be created on first run
- Check `data/` folder has been created
- If issues persist, delete `data/` folder and database files, system will recreate them

### ❌ SSL Certificate Errors
**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution (macOS):**
```bash
# Install SSL certificates
/Applications/Python\ 3.10/Install\ Certificates.command
```

**Solution (Windows PowerShell):**
```powershell
pip install --upgrade certifi
```

---

## Directory Structure After Installation

```
Sentinel-Agent/
├── venv/                          # Virtual environment (created)
│   └── [Python packages]
├── data/                          # Database files (created)
│   ├── threat_intel.db
│   ├── auth.db
│   ├── lists.db
│   ├── metrics.db
│   └── anomalies.db
├── .env                           # Configuration (created)
├── main.py                        # Core system
├── sentinel_api.py                # REST API
├── install.ps1                    # PowerShell installer
├── install.bat                    # Batch installer
├── install.sh                     # Bash installer
├── install.py                     # Python installer
├── requirements.txt               # Dependencies
├── README.md                      # Project documentation
├── INSTALLATION.md                # This file
└── docs_markdown/                 # Detailed guides
    ├── INDEX.md
    ├── DEPLOYMENT_GUIDE.md
    ├── FEATURE_INTEGRATION.md
    └── [25+ more guides]
```

---

## Uninstallation

To completely remove Sentinel Agent:

### Windows
```powershell
# Remove virtual environment
Remove-Item -Recurse -Force venv

# Remove data and configuration
Remove-Item -Recurse -Force data
Remove-Item -Force .env

# Remove Python packages from global Python (if needed)
# Re-run only if you want to remove from global environment
```

### Linux/macOS
```bash
# Remove virtual environment
rm -rf venv

# Remove data and configuration
rm -rf data
rm -f .env

# That's it!
```

---

## Verification After Installation

Run these commands to verify everything is working:

```bash
# Activate virtual environment
source venv/bin/activate  # on Windows: .\venv\Scripts\Activate.ps1

# Test Python environment
python --version

# Test imports
python -c "print('Testing imports...'); import crewai; import fastapi; import streamlit; print('✅ All imports successful!')"

# Check databases
ls -la data/  # or dir data\ on Windows

# Verify configuration
cat .env
```

---

## Support and Documentation

After successful installation, refer to:

- **Quick Start:** [README.md](README.md)
- **API Docs:** [docs_markdown/FEATURE_INTEGRATION.md](docs_markdown/FEATURE_INTEGRATION.md)
- **Deployment:** [docs_markdown/DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md)
- **Troubleshooting:** [docs_markdown/TROUBLESHOOTING.md](docs_markdown/TROUBLESHOOTING.md)
- **Documentation Index:** [docs_markdown/INDEX.md](docs_markdown/INDEX.md)

---

## Quick Reference

### After Installation
| Action | Command |
|--------|---------|
| Activate venv | `source venv/bin/activate` |
| Start system | `python main.py` |
| Start API | `python sentinel_api.py` |
| Start dashboard | `streamlit run dashboard/web_dashboard.py` |
| View logs | `tail -f logs/sentinel.log` |
| Check status | `curl http://localhost:8000/api/health` |

---

**Installation Complete! **

Your Sentinel Agent system is now ready to use. Follow the "Starting the System" section above to begin!
