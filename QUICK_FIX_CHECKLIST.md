# Quick Reference - Error Checklist

## 🔴 CRITICAL ERRORS - MUST FIX BEFORE RUNNING

### [ ] 1. Complete `check_ip_threat()` in tools.py
- **Location:** tools/tools.py line 21
- **Status:** INCOMPLETE (only has comment placeholder)
- **Impact:** BLOCKING - Crew cannot initialize agents
- **Used by:** threat_intel_researcher agent

### [ ] 2. Complete `get_system_context()` in tools.py  
- **Location:** tools/tools.py line 63
- **Status:** INCOMPLETE (only has comment placeholder)
- **Impact:** BLOCKING - Multiple agents cannot function
- **Used by:** triage_analyst, incident_responder agents

### [ ] 3. Complete `generate_firewall_rule()` in tools.py
- **Location:** tools/tools.py line 144
- **Status:** INCOMPLETE (only has comment placeholder)
- **Impact:** BLOCKING - Response generation fails
- **Used by:** incident_responder agent

### [ ] 4. Complete `extract_ip_from_log()` in tools.py
- **Location:** tools/tools.py line 155
- **Status:** INCOMPLETE (only has comment placeholder)
- **Impact:** BLOCKING - Log analysis fails
- **Used by:** triage_analyst agent

### [ ] 5. Complete `check_web_logs_for_ip()` in tools.py
- **Location:** tools/tools.py line 185
- **Status:** INCOMPLETE (only has comment placeholder)
- **Impact:** BLOCKING - Cross-correlation cannot occur
- **Used by:** threat_intel_researcher agent

### [ ] 6. Complete `kill_process()` in tools.py
- **Location:** tools/tools.py line 327
- **Issue:** Missing elif branch for PID handling
- **Status:** INCOMPLETE (comment instead of code)
- **Impact:** BLOCKING - Process termination will fail
- **Current Code:**
  ```python
  if process_name:
      # ... code for process_name ...
  # ... (rest of the pid logic with sudo kill) ❌ NOT PYTHON CODE
  except Exception as e:
  ```
- **What's Missing:** elif block for pid parameter

---

## 🟡 HIGH PRIORITY ERRORS - FIX BEFORE PRODUCTION

### [ ] 7. Fix type hint in tasks.py line 7
- **Issue:** Uses `list[Task]` instead of `List[Task]`
- **Error on Python 3.9:** TypeError: 'type' object is not subscriptable
- **Fix:** `from typing import List` and change `list[Task]` → `List[Task]`
- **Impact:** Won't run on Python 3.9

### [ ] 8. Fix IP validation in sensors/auth_sensor.py lines 105-115
- **Issue:** Condition `all(0 <= int(p) <= 255 for p in parts if p.isdigit())`
- **Problem:** Accepts invalid IPs like "192.168.abc.1" 
- **Fix:** Change to `all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)`
- **Impact:** Invalid IPs bypass validation

### [ ] 9. Fix IP validation in sensors/web_sensor.py lines 115-125
- **Issue:** Same as #8
- **Problem:** Same as #8
- **Fix:** Same as #8
- **Impact:** Invalid IPs bypass validation

### [ ] 10. Fix JSON parsing in main.py lines 180-195
- **Issue:** Regex `\{[^{}]*"action_required"[^{}]*\}` fails on nested JSON
- **Problem:** Pattern breaks when JSON contains nested objects
- **Fix:** Use brace-counting algorithm instead of regex
- **Impact:** Reports with nested JSON structures are lost

---

## 🟠 MEDIUM PRIORITY - ROBUSTNESS IMPROVEMENTS

### [ ] 11. Add file rotation detection in sensors/auth_sensor.py
- **Location:** Around line 48-71
- **Issue:** Doesn't detect when logrotate rotates files
- **Solution:** Track inode number to detect rotation
- **Impact:** May miss logs after rotation

### [ ] 12. Add file rotation detection in sensors/web_sensor.py
- **Location:** Around line 48-71
- **Issue:** Same as #11
- **Solution:** Same as #11
- **Impact:** May miss logs after rotation

### [ ] 13. Add return type hint to agents.py line 25
- **Location:** `def get_ollama_url():`
- **Issue:** Missing `-> str` annotation
- **Impact:** Type checker warnings

---

## ✅ CODE QUALITY CHECKS

### Syntax Validation
- [x] agents.py - No syntax errors
- [x] main.py - No syntax errors
- [x] tasks.py - No syntax errors
- [x] view_attacks.py - No syntax errors
- [x] tools/tools.py - No syntax errors
- [x] defense/attack_detector.py - No syntax errors
- [x] defense/attack_logger.py - No syntax errors
- [x] sensors/auth_sensor.py - No syntax errors
- [x] sensors/web_sensor.py - No syntax errors

### Import Resolution
- [x] crewai - Required, in requirements.txt
- [x] langchain - Required, in requirements.txt
- [x] requests - Required, in requirements.txt
- [x] watchdog - Required, in requirements.txt
- [x] dotenv - Optional, gracefully handled

### Module Structure
- [x] defense/__init__.py exists
- [x] sensors/__init__.py exists
- [x] tools/__init__.py exists

---

## 📋 TESTING CHECKLIST

Before deploying, verify:

- [ ] All 5 missing tool implementations completed
- [ ] kill_process() PID handling added
- [ ] Type hints compatible with Python 3.9
- [ ] IP validation filters all invalid formats
- [ ] JSON parsing handles nested objects
- [ ] Log rotation detection implemented
- [ ] Unit tests pass for sensors
- [ ] Unit tests pass for tools
- [ ] Ollama server is running
- [ ] Ollama model (llama3:8b) is available
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Test with sample log lines
- [ ] Test with sample IPs

---

## 📊 SCORING

| Metric | Status | Details |
|--------|--------|---------|
| **Syntax Errors** | ✅ 0/9 files | All files are syntactically valid |
| **Critical Logic Errors** | 🔴 6 errors | 5 incomplete tools + 1 incomplete function |
| **High Priority Bugs** | 🟡 4 errors | Type hints, IP validation (2x), JSON parsing |
| **Medium Priority Issues** | 🟠 3 improvements | File rotation, type hints |
| **Code Quality** | 🟢 Good | Well-documented, structured properly |
| **Overall Status** | 🔴 NOT RUNNABLE | Cannot start without fixes |

---

## 🚀 FIX PRIORITY ORDER

**Phase 1 - CRITICAL (Days 1-2):**
1. Fix all 5 missing tool definitions in tools.py
2. Complete kill_process() function
3. Test imports - ensure no AttributeErrors

**Phase 2 - BLOCKING (Day 2-3):**
4. Fix type hints for Python 3.9 compatibility
5. Fix IP validation in both sensors
6. Test with sample logs

**Phase 3 - PRODUCTION (Day 3-4):**
7. Fix JSON parsing for nested objects
8. Add file rotation detection
9. Complete integration testing

**Phase 4 - OPTIONAL (Day 4+):**
10. Add missing type hints (code quality)
11. Add unit test suite
12. Performance optimization

---

## 📞 DEBUG COMMANDS

```bash
# Check Python version
python --version

# Verify imports
python -c "from tools.tools import check_ip_threat"

# Check Ollama
curl http://127.0.0.1:11434/api/tags

# Run with environment check
python main.py --skip-env-check

# Check syntax only
python -m py_compile agents.py main.py tasks.py

# Run specific sensor test
python -m sensors.auth_sensor
```

---

**Last Updated:** 2026-01-26  
**Status:** ANALYSIS COMPLETE - AWAITING FIXES
