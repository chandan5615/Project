# 🚀 QUICK INSTALL REFERENCE

## Choose Your Installation (All are Clean & No-Mess!)

### 🪟 **Windows Users**

**Option 1: PowerShell (RECOMMENDED) ⭐**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\install.ps1
```

**Option 2: Command Prompt (CMD)**
```cmd
install.bat
```

### 🐧 **Linux/macOS Users**

```bash
chmod +x install.sh
./install.sh
```

### 🐍 **Any Platform (Python)**

```bash
python install.py
```

---

## What Each Installer Does

| Step | Action | Time |
|------|--------|------|
| 1️⃣ | Check Python 3.10+ installed | 5s |
| 2️⃣ | Check Ollama installed | 5s |
| 3️⃣ | Check system dependencies | 5s |
| 4️⃣ | Remove old venv (if exists) | 10s |
| 5️⃣ | Create new virtual environment | 30s |
| 6️⃣ | Upgrade pip & tools | 30s |
| 7️⃣ | Install all dependencies | 2-5 minutes |
| 8️⃣ | Initialize databases | 30s |
| | **Total Time:** | **3-6 minutes** |

---

## After Installation: Start the System

### Pre-Requirement: Start Ollama (Keep Running)
**Terminal 1:**
```bash
ollama serve
```

### Run Core System
**Terminal 2:**
```bash
# Activate environment
source venv/bin/activate        # Linux/macOS
# or
.\venv\Scripts\Activate.ps1     # Windows PowerShell

# Run system
python main.py
```

### Start REST API (Optional)
**Terminal 3:**
```bash
source venv/bin/activate
python sentinel_api.py
# Access: http://localhost:8000
```

### Start Dashboard (Optional)
**Terminal 4:**
```bash
source venv/bin/activate
streamlit run dashboard/web_dashboard.py
# Access: http://localhost:8501
```

---

## System Requirements

✅ **Must Have:**
- Python 3.10+
- Ollama (or install after setup)
- 4 GB RAM (8 GB recommended)
- 2 GB disk space
- Internet connection (for first install only)

---

## Troubleshooting (Most Common Issues)

| Issue | Solution |
|-------|----------|
| Python not found | Add Python to PATH, restart terminal |
| Ollama not found | Download from ollama.ai (not required for install) |
| PowerShell permissions error | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force` |
| Port already in use | Edit `.env` and change `API_PORT=8001` |
| Virtual env won't activate | Delete `venv` folder and reinstall |

---

## 📚 Full Documentation

For complete installation guide with all options and troubleshooting:
👉 **See [INSTALLATION.md](INSTALLATION.md)**

---

## ✅ Verify Installation Works

```bash
# Ensure venv is activated (check for (venv) in prompt)

# Test imports
python -c "import crewai, fastapi, streamlit; print('✅ Ready!')"

# Check databases created
ls data/          # Linux/macOS
dir data\         # Windows
```

---

## Ready to Go! 🎉

Your Sentinel Agent is installed and ready to use.

**Next Steps:**
1. Start Ollama: `ollama serve`
2. Start System: `python main.py`
3. Open API: `http://localhost:8000`
4. Read docs: `README.md` or `docs_markdown/INDEX.md`

**No mess, no problems!** 🎯
