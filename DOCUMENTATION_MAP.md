# Documentation Map - Sentinel Agent v2.2

**Quick Navigation:** Find the right document for your needs.

---

## 🎯 Getting Started (Choose One)

| Document | Best For | Time |
|----------|----------|------|
| [README.md](README.md) | Overview & 3-command setup | 5 min |
| [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) | Automated setup scripts | 5 min |
| [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) | Complete step-by-step guide | 20 min |

**Recommendation:** Start with `README.md`, use `quick-rebuild.sh` script for easiest setup.

---

## 🔧 Troubleshooting & Fixes

| Document | Purpose |
|----------|---------|
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common problems and solutions |
| [COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md) | All recent fixes (password hashing, permissions) |
| [DATABASE_FIX_GUIDE.md](DATABASE_FIX_GUIDE.md) | Database initialization issues |
| [AUTH_FIX_GUIDE.md](AUTH_FIX_GUIDE.md) | Authentication fixes |

**Quick Diagnostic Scripts:**
- `diagnose_crash.sh` - Container crash diagnostics
- `diagnose_auth.sh` - Authentication diagnostics  
- `test_auth.py` - Python auth tester

---

## 🆘 When Things Go Wrong

**Container won't start:**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
→ Run `./diagnose_crash.sh`

**Authentication fails:**
→ [AUTH_FIX_GUIDE.md](AUTH_FIX_GUIDE.md)
→ Run `./diagnose_auth.sh`

**Database errors:**
→ [DATABASE_FIX_GUIDE.md](DATABASE_FIX_GUIDE.md)
→ [COMPLETE_FIX_SUMMARY.md](COMPLETE_FIX_SUMMARY.md)

**Permission denied:**
→ Use `sudo rm -rf data/ logs/` then run `./quick-rebuild.sh`

---

**Last Updated:** February 2026
**Version:** 2.2 (Simplified setup, automated scripts)
