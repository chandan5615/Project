# QUICK TEST COMMANDS - CrewAI Tool Fix

**Purpose**: Verify the CrewAI tool invocation fixes  
**Date**: January 28, 2026  

---

## What Was Fixed

Tool invocation errors where agents were wrapping parameters in metadata dicts instead of passing simple values.

---

## Test Commands

### 1. Run Full System Test
```bash
# Navigate to project
cd "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project"

# Run with sudo (for firewall operations)
sudo python main.py

# Monitor for proper tool invocation - look for:
# ✅ Tool Input: {"ip": "10.26.103.210"}
# ✅ Tool Output: Valid JSON response
# ❌ NOT seeing: Pydantic validation errors
# ❌ NOT seeing: Arguments validation failed
```

### 2. Quick Verification of Changes
```bash
# Verify tasks.py was updated
grep -n "IMPORTANT: When using tools" "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\tasks.py"

# Should show 4 lines (one for each task):
# Line ~24: IMPORTANT: When using tools, pass parameters as simple values
# Line ~49: IMPORTANT: Use the available tools correctly
# Line ~83: IMPORTANT: When using tools:
# Line ~125: IMPORTANT: When using tools, pass parameters correctly
```

### 3. Check Fix Documentation
```bash
# View the comprehensive fix document
cat "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\CREWAI_TOOL_FIX.md"
```

---

## What to Watch For

### Success Indicators ✅
```
Tool Name: Check IP Threat
Tool Input: {"ip": "10.26.103.210"}
Tool Output: { "ip": "10.26.103.210", "threat_level": "low", ... }
```

### Error Indicators ❌
```
Arguments validation failed: 1 validation error for Checkipthreat
Input should be a valid string [type=string_type, input_value={'description': 'None', ...}]
```

```
Action 'None' don't exist
```

---

## Expected Behavior After Fix

### Before (Broken)
```
Agent: Using tool: Check IP Threat
Tool Input: {"ip": {"description": "None", "type": "str", "value": "10.26.103.210"}}
ERROR: Arguments validation failed...
Agent: I forgot the Action name...
```

### After (Fixed)
```
Agent: Using tool: Check IP Threat
Tool Input: {"ip": "10.26.103.210"}
Tool Output: {"ip": "10.26.103.210", "threat_level": "low", ...}
Agent: Continuing with analysis...
```

---

## Detailed Testing Steps

### Step 1: Start the System
```bash
cd "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project"
sudo python main.py
```

### Step 2: Monitor Initial Output
Watch for:
- ✅ System initialization completes
- ✅ Sensors start successfully
- ✅ Ready to detect events

### Step 3: Trigger a Security Event
(In another terminal, or system generates alert)

### Step 4: Monitor Agent Execution
Look for patterns:

**Task 1 - Triage Analysis:**
```
# Agent: Senior SOC Analyst
## Using tool: Extract IP from Log Line
## Tool Input: {"log_line": "10.26.103.210 - - [28/Jan/2026:..."}  ✅
```

**Task 2 - Threat Intelligence:**
```
# Agent: Cyber Intelligence Expert
## Using tool: Check IP Threat
## Tool Input: {"ip": "10.26.103.210"}  ✅
## Using tool: Check Web Logs for IP
## Tool Input: {"ip": "10.26.103.210", "log_path": "..."}  ✅
```

**Task 3 - Incident Response:**
```
# Agent: System Defense Engineer
## Using tool: Generate Firewall Rule
## Tool Input: {"ip": "10.26.103.210", "protocol": "tcp", "port": "all"}  ✅
```

**Task 4 - Enforcement:**
```
# Agent: Security Enforcer
## Using tool: Execute Iptables Rule
## Tool Input: {"rule": "iptables -A INPUT -s 10.26.103.210 -j DROP"}  ✅
```

### Step 5: Verify Completion
Check for:
- ✅ All 4 tasks complete without validation errors
- ✅ JSON reports generated
- ✅ Firewall rule proposed (if action required)
- ✅ No agent confusion ("forgetting action names")

---

## PowerShell Test Commands

```powershell
# Navigate to project
cd "c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project"

# Check if changes were applied
Select-String "IMPORTANT: When using tools" tasks.py

# Should output 4 matches if fix applied correctly
# Output:
#   24: IMPORTANT: When using tools, pass parameters as simple values
#   49: IMPORTANT: Use the available tools correctly
#   83: IMPORTANT: When using tools:
#   125: IMPORTANT: When using tools, pass parameters correctly
```

---

## If Issues Persist

### Issue: Still seeing validation errors

**Diagnosis:**
```bash
# Check if tasks.py was properly updated
grep -A 2 "IMPORTANT: When using tools" tasks.py
# Should show the fix is present
```

**Solution:**
1. Verify the file was saved: `ls -la tasks.py`
2. Check file encoding is UTF-8: `file tasks.py`
3. Restart Python process: Stop and re-run `sudo python main.py`

### Issue: Agent still confused about action names

**Diagnosis:**
```bash
# Check agents.py has correct tool assignments
grep -A 5 "tools=\[" agents.py
```

**Solution:**
1. Verify agents have correct tools in their definition
2. Check CrewAI version compatibility: `pip list | grep crewai`
3. Reinstall CrewAI: `pip install --upgrade crewai`

### Issue: Tools returning empty or error responses

**Diagnosis:**
```bash
# Check if tools.py implementations are correct
python -c "from tools.tools import check_ip_threat; print(check_ip_threat('10.26.103.210'))"
```

**Solution:**
1. Verify tools.py has proper implementations
2. Check log paths exist: `ls /var/log/auth.log /var/log/apache2/access.log`
3. Verify permissions: `ls -la /var/log/auth.log`

---

## Success Checklist

After applying the fix, verify:

- [ ] tasks.py has 4 "IMPORTANT: When using tools" sections
- [ ] Running `sudo python main.py` starts without errors
- [ ] Agent tool inputs are simple dicts with string values
- [ ] NO pydantic validation errors appear
- [ ] NO "Arguments validation failed" errors appear
- [ ] Agent completes all 4 tasks successfully
- [ ] JSON reports are generated
- [ ] Firewall rule is proposed (if applicable)

---

## Summary

**Fix Applied:** Enhanced task descriptions with explicit tool invocation guidance  
**Files Modified:** tasks.py (4 task descriptions updated)  
**Expected Result:** Agents properly invoke tools with correct parameters  
**Status:** ✅ Ready for testing  

**To Test:**
1. Run: `sudo python main.py`
2. Monitor: Tool invocations for proper parameter format
3. Verify: No validation errors, all tasks complete

---

**Questions?** See `CREWAI_TOOL_FIX.md` for detailed explanation.
