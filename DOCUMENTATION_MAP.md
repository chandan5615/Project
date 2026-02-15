# Documentation Map - Sentinel Agent v2.2

**Quick Navigation:** Find the right document for your needs.

---

## 🎯 Getting Started (Choose One)

| Document | Best For | Time | Features |
|----------|----------|------|----------|
| [README.md](README.md) | Complete overview & quick start | 10 min | ✅ Zero interaction setup |
| [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) | Fastest automated setup | 3 min | ✅ One-command deployment |
| [WEB_DASHBOARD_SETUP.md](WEB_DASHBOARD_SETUP.md) | Web dashboard usage (LIVE) | 5 min | ✅ Interactive dashboards |
| [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) | Detailed step-by-step guide | 20 min | ✅ Full explanations |

**Recommendation:** Start with `README.md`, deploy with `docker-compose up -d --build`, then run `python3 sentinel_auto.py setup`.

---

## 🤖 Automation & Usage

| Document | Purpose |
|----------|---------|
| [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) | Complete automation guide for `sentinel_auto.py` |
| [WEB_DASHBOARD_SETUP.md](WEB_DASHBOARD_SETUP.md) | Web dashboard (Streamlit) setup and usage |
| [CODE_FIXES_2026_FEB_15.md](CODE_FIXES_2026_FEB_15.md) | Latest code fixes (auth, dashboard, API) |
| [PROJECT_STATUS_2026_FEB_15.md](PROJECT_STATUS_2026_FEB_15.md) | Complete project status and achievements |

**Key Scripts:**
- `sentinel_auto.py` - Main automation tool (setup, demo, status)
- `test_auth.py` - Authentication tester
- `test_attacks.py` - Manual attack generation
- `view_attacks.py` - View detected attacks

---

## 🔧 Troubleshooting

| Document | When to Use |
|----------|-------------|
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Container issues, authentication failures, common problems |
| [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) | Complete rebuild instructions |

---

## 🧪 Testing

| Document | Purpose |
|----------|---------|
| [TEST_GUIDE.md](TEST_GUIDE.md) | Complete testing guide - running tests, troubleshooting imports, CI/CD |

**Quick Test Commands:**
```bash
python3 -m pytest tests/ -v                  # Run all tests
python3 -m pytest tests/test_view_attacks.py # Run single test
python3 tests/test_view_attacks.py           # Direct execution
```

---

## 🆘 Quick Fixes

### Container Won't Start
```bash
# View logs
docker-compose logs --tail=100 sentinel-agent

# Rebuild
docker-compose down -v
docker-compose up -d --build
sleep 30
```

### Authentication Fails
```bash
# Re-run automated setup (10 seconds)
python3 sentinel_auto.py setup
```

### Token Expired
```bash
# Tokens last 24 hours - just re-run setup
python3 sentinel_auto.py setup
```

###Permission Denied (Data Cleanup)
```bash
# Docker creates files as root
docker-compose down -v
sudo rm -rf data/ logs/
docker-compose up -d --build
```

---

## 📚 Additional Documentation

### In `docs_markdown/` folder:

| Document | Topic |
|----------|-------|
| [ATTACK_TESTING_GUIDE.md](docs_markdown/ATTACK_TESTING_GUIDE.md) | How to test attack detection |
| [DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md) | Production deployment |
| [DOCKER_QUICKSTART.md](docs_markdown/DOCKER_QUICKSTART.md) | Docker-specific setup |
| [DOCKER_TROUBLESHOOTING.md](docs_markdown/DOCKER_TROUBLESHOOTING.md) | Docker-specific issues |
| [ENVIRONMENT.md](docs_markdown/ENVIRONMENT.md) | Environment configuration |
| [QUICK_REFERENCE.md](docs_markdown/QUICK_REFERENCE.md) | Command reference |
| [README_FEATURES.md](docs_markdown/README_FEATURES.md) | Feature documentation |
| [SECURITY_IMPLEMENTATION.md](docs_markdown/SECURITY_IMPLEMENTATION.md) | Security details |
| [USER_GUIDE.md](docs_markdown/USER_GUIDE.md) | End-user guide |

---

## 🔑 Key Files

### Configuration
- `docker-compose.yml` - Main Docker configuration
- `Dockerfile` - Container build instructions
- `requirements.txt` - Python dependencies

### Core Scripts
- `main.py` - Main agent orchestrator
- `sentinel_api.py` - REST API server
- `auth.py` - Authentication system
- `data_engine.py` - Data processing
- `agents.py` - AI agent definitions

### Automation
- `sentinel_auto.py` - **Main automation tool** ⭐
- `test_auth.py` - Authentication testing
- `test_attacks.py` - Manual attack generation
- `view_attacks.py` - View results

### Setup Scripts (Platform-specific)
- `setup.sh` / `setup.bat` - Environment setup
- `install.sh` / `install.bat` / `install.ps1` - Dependency installation
- `activate_env.sh` / `activate_env.bat` - Virtual environment activation

---

## 🚀 Recommended Reading Order

### For New Users
1. [README.md](README.md) - Get the overview
2. [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) - Deploy in 3 minutes
3. [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Learn all automation features

### For Troubleshooting
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
2. [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) - Complete rebuild guide
3. [DOCKER_TROUBLESHOOTING.md](docs_markdown/DOCKER_TROUBLESHOOTING.md) - Docker-specific issues

### For Production Deployment
1. [DEPLOYMENT_GUIDE.md](docs_markdown/DEPLOYMENT_GUIDE.md) - Production setup
2. [SECURITY_IMPLEMENTATION.md](docs_markdown/SECURITY_IMPLEMENTATION.md) - Security hardening
3. [ENVIRONMENT.md](docs_markdown/ENVIRONMENT.md) - Environment config

---

## 📖 Documentation Philosophy

**Zero Interaction Focused:**
- All guides emphasize automated setup
- No manual password management
- Token auto-saved to `.sentinel_token`
- One command deployment where possible

**Current Best Practice:**
```bash
# Complete deployment (zero interaction)
docker-compose up -d --build && sleep 30
python3 sentinel_auto.py setup
python3 sentinel_auto.py demo
python3 sentinel_auto.py status
```

---

## 🗑️ Removed/Obsolete Files

The following files have been removed as they are no longer needed:

### Temporary Fix Files (Replaced by CODE_FIXES_2026_FEB_15.md)
- ❌ COMPLETE_FIX_SUMMARY.md
- ❌ AUTH_FIX_GUIDE.md
- ❌ DATABASE_FIX_GUIDE.md
- ❌ DOCKER_FIXES_SUMMARY.md
- ❌ DATABASE_FIXES.md
- ❌ HEALTHCHECK_FIX.md
- ❌ HEALTHCHECK_DEBUG.md
- ❌ QUICK_FIX.md

### Temporary Status Files
- ❌ PROJECT_FINAL_VALIDATION.md
- ❌ GITHUB_UPLOAD_READY.md
- ❌ UPDATE_SUMMARY.md
- ❌ DOCS_UPDATE_SUMMARY.md
- ❌ UBUNTU_DIAGNOSTIC_REPORT.md
- ❌ SETUP_CHECKLIST.md

### Old Versions
- ❌ README_OLD_BACKUP.md
- ❌ FRESH_START_GUIDE_OLD.md
- ❌ DOCUMENTATION_MAP_OLD.md

### Temporary Scripts (Functionality moved to sentinel_auto.py)
- ❌ quick-rebuild.sh
- ❌ diagnose.sh
- ❌ diagnose_auth.sh
- ❌ diagnose_crash.sh
- ❌ fix-and-start.sh
- ❌ fix-healthcheck.sh
- ❌ quick-diagnose.sh
- ❌ docker-test.sh / docker-test.bat
- ❌ run_dashboard.sh / run_dashboard.bat / run_dashboard.py

---

**Last Updated:** February 15, 2026
**Version:** 2.2 (Zero Interaction Automation)
**Key Improvement:** All functionality consolidated into `sentinel_auto.py` for cross-platform compatibility

**Questions?**
1. Start with [README.md](README.md)
2. Try automated setup: `python3 sentinel_auto.py setup`
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise
