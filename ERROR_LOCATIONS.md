# ERROR LOCATIONS - VISUAL CODE MAP

## 📍 Error 1: Incomplete check_ip_threat() - Line 21 in tools.py

```python
# CURRENT STATE (BROKEN):
┌─ tools/tools.py ───────────────────────────────────────────
│
│ 18  """
│ 19  Sentinel Agent - Security Tools Module (Sudo Optimized)
│ 20  Provides CrewAI tools for threat intelligence...
│ 21  """
│ 22
│ 23  import subprocess
│ 24  import re
│ 25  from typing import Optional
│ 26  from pathlib import Path
│ 27
│ 28  try:
│ 29      from crewai_tools import tool
│ 30  except ImportError:
│ 31      from crewai.tools import tool
│ 32  import requests
│ 33  import json
│ 34
│ 35  # ... (check_ip_threat and get_system_context remain the same) ...  ❌ NOT REAL CODE
│ 36
│ 37  @tool("Verify Firewall Rule")
│ 38  def verify_firewall_rule(ip: str) -> str:
│
└────────────────────────────────────────────────────────────

PROBLEM:
  Line 35 is a COMMENT saying "remains the same"
  But the actual implementation code is MISSING
  
WHAT SHOULD BE THERE:
  @tool("Check IP Threat")
  def check_ip_threat(ip: str) -> str:
      # ... full implementation with 20-30 lines of code ...
  
  @tool("Get System Context") 
  def get_system_context() -> str:
      # ... full implementation with 20-30 lines of code ...
  
  @tool("Generate Firewall Rule")
  def generate_firewall_rule(ip: str, ...) -> str:
      # ... full implementation ...
  
  @tool("Extract IP from Log Line")
  def extract_ip_from_log(log_line: str) -> Optional[str]:
      # ... full implementation ...
  
  @tool("Check Web Logs for IP")
  def check_web_logs_for_ip(ip: str, ...) -> str:
      # ... full implementation ...
```

---

## 📍 Error 2: Incomplete kill_process() - Line 327 in tools.py

```python
# CURRENT STATE (BROKEN):
┌─ tools/tools.py ───────────────────────────────────────────
│
│ 316 @tool("Kill Process by Name or PID")
│ 317 def kill_process(process_name: str = None, pid: int = None, 
│ 318                  signal: str = "TERM") -> str:
│ 319     """
│ 320     Kill a process using sudo systemctl or sudo pkill.
│ 321     """
│ 322     result = {"success": False, "method": None, 
│ 323              "output": None, "error": None}
│ 324     
│ 325     try:
│ 326         if process_name:
│ 327             systemctl_result = subprocess.run(
│ 328                 ["sudo", "systemctl", "kill", ...],
│ 329                 capture_output=True, text=True, timeout=5
│ 330             )
│ 331             
│ 332             if systemctl_result.returncode == 0:
│ 333                 result["success"] = True
│ 334                 result["method"] = "systemctl"
│ 335             else:
│ 336                 pkill_result = subprocess.run(
│ 337                     ["sudo", "pkill", f"-{signal}", process_name],
│ 338                     capture_output=True, text=True, timeout=5
│ 339                 )
│ 340                 if pkill_result.returncode == 0:
│ 341                     result["success"] = True
│ 342                     result["method"] = "pkill"
│ 343         # ... (rest of the pid logic with sudo kill)  ❌ NOT REAL CODE
│ 344     except Exception as e:
│ 345         result["error"] = str(e)
│ 346     return json.dumps(result, indent=2)
│
└────────────────────────────────────────────────────────────

PROBLEM:
  Line 343 is a COMMENT saying "rest of the pid logic"
  But the PID handling code is MISSING
  
WHAT SHOULD BE THERE (Lines 343-353):
  elif pid:
      kill_result = subprocess.run(
          ["sudo", "kill", f"-{signal}", str(pid)],
          capture_output=True, text=True, timeout=5
      )
      if kill_result.returncode == 0:
          result["success"] = True
          result["method"] = "kill"
          result["output"] = f"Killed process {pid}"
      else:
          result["error"] = kill_result.stderr
  else:
      result["error"] = "Either process_name or pid must be provided"
```

---

## 📍 Error 3: Type Hint Python 3.9 Incompatibility - Line 7 in tasks.py

```python
# CURRENT STATE (BREAKS ON PYTHON 3.9):
┌─ tasks.py ─────────────────────────────────────────────────
│
│ 1  """
│ 2  Sentinel Agent - Security Playbooks (Tasks)
│ 3  Defines the workflow tasks for the AI crew.
│ 4  """
│ 5
│ 6  from crewai import Task
│ 7  from agents import ...
│ 8  import json
│ 9
│ 10 def create_security_incident_tasks(
│ 11     ip_address: str,
│ 12     log_line: str,
│ 13     attack_type: str = "unknown",
│ 14     severity: str = "medium"
│ 15 ) -> list[Task]:  ❌ PYTHON 3.10+ SYNTAX ONLY
│ 16     """
│ 17     Create a sequence of tasks for handling a security incident.
│
└────────────────────────────────────────────────────────────

PROBLEM:
  Python 3.9: list[Task] ❌ TypeError: 'type' object is not subscriptable
  Python 3.10+: list[Task] ✅ Works fine
  
FIX NEEDED:
  Line 1: Add import
    from typing import List
  
  Line 15: Change
    FROM: ) -> list[Task]:
    TO:   ) -> List[Task]:
```

---

## 📍 Error 4 & 5: Invalid IP Validation - Lines 105-115 and 115-125

### sensors/auth_sensor.py

```python
# CURRENT STATE (BROKEN):
┌─ sensors/auth_sensor.py ───────────────────────────────
│
│ 99  def _extract_ip(self, log_line: str) -> Optional[str]:
│ 100     """Extract IP address from a log line."""
│ 101     ip_patterns = [
│ 102         r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
│ 103         r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b',
│ 104     ]
│ 105     
│ 106     for pattern in ip_patterns:
│ 107         match = re.search(pattern, log_line)
│ 108         if match:
│ 109             ip = match.group(1) if match.groups() else match.group(0)
│ 110             try:
│ 111                 parts = ip.split('.')
│ 112                 if len(parts) == 4 and all(
│ 113                     0 <= int(p) <= 255 
│ 114                     for p in parts 
│ 115                     if p.isdigit()  ❌ FILTERS NON-DIGITS
│ 116                 ):
│ 117                     return ip  ❌ ACCEPTS INVALID IPs
│ 118             except ValueError:
│ 119                 continue
│ 120     
│ 121     return None
│
└─────────────────────────────────────────────────────────

PROBLEM:
  Condition: all(0 <= int(p) <= 255 for p in parts if p.isdigit())
  
  The "if p.isdigit()" FILTERS the iteration
  Only numeric parts are checked, non-numeric parts are SKIPPED
  
  Example:
    ip = "192.168.abc.1"
    parts = ["192", "168", "abc", "1"]
    
    The generator iterates:
      - p="192" -> isdigit()=True -> check range ✓
      - p="168" -> isdigit()=True -> check range ✓
      - p="abc" -> isdigit()=False -> SKIP (not checked!)
      - p="1" -> isdigit()=True -> check range ✓
    
    all() returns True even though "abc" is invalid!

FIX NEEDED (Lines 112-116):
  FROM:
    if len(parts) == 4 and all(
        0 <= int(p) <= 255 
        for p in parts 
        if p.isdigit()
    ):
    
  TO:
    if len(parts) == 4 and all(
        p.isdigit() and 0 <= int(p) <= 255 
        for p in parts
    ):
    
  This ensures:
    1. FIRST check p.isdigit() (must be digits)
    2. THEN check range (0-255)
    3. ALL parts must pass both checks (no filtering)
```

### sensors/web_sensor.py
Same issue at lines 115-125. Apply identical fix.

---

## 📍 Error 6: Nested JSON Parsing Fails - Lines 180-195 in main.py

```python
# CURRENT STATE (BROKEN):
┌─ main.py ──────────────────────────────────────────────
│
│ 170 def _extract_final_report(self, result, ip_address, ...):
│ 171     """Extract the final report from crew results."""
│ 172     report = {
│ 173         "ip_address": ip_address,
│ 174         "log_line": log_line,
│ 175         "action_required": False,
│ 176         "firewall_rule": None,
│ 177         "severity": "unknown",
│ 178         "threat_level": "unknown"
│ 179     }
│ 180     
│ 181     # Try to parse the result
│ 182     if hasattr(result, 'raw'):
│ 183         result_str = str(result.raw)
│ 184     else:
│ 185         result_str = str(result)
│ 186     
│ 187     try:
│ 188         # Find the last task's output
│ 189         json_match = re.search(
│ 190             r'\{[^{}]*"action_required"[^{}]*\}',  ❌ BREAKS ON NESTED JSON
│ 191             result_str, 
│ 192             re.DOTALL
│ 193         )
│
└────────────────────────────────────────────────────────

PROBLEM:
  Regex: \{[^{}]*"action_required"[^{}]*\}
  Means: "{ ... (no braces) ... "action_required" ... (no braces) ... }"
  
  When JSON has nested objects:
  {
    "action_required": true,      ✓ Matches start here
    "details": {                  
      "rule": "iptables -A...",   
      "reason": "block IP"        
    }                             ← Regex stops here because it sees }
  }                               ← Never reaches the outer }
  
  The pattern stops at the FIRST } it finds while looking for the end
  
FIX NEEDED:
  Replace regex with proper brace-counting algorithm:
  
  ```python
  try:
      json_start = result_str.find('{')
      if json_start == -1:
          raise ValueError("No JSON found")
      
      # Count braces to find matching closing brace
      brace_count = 0
      json_end = json_start
      for i in range(json_start, len(result_str)):
          if result_str[i] == '{':
              brace_count += 1
          elif result_str[i] == '}':
              brace_count -= 1
              if brace_count == 0:
                  json_end = i + 1
                  break
      
      json_str = result_str[json_start:json_end]
      parsed = json.loads(json_str)
      report.update(parsed)
  except json.JSONDecodeError as e:
      logger.warning(f"Could not parse JSON: {e}")
      report["raw_response"] = result_str
  ```
```

---

## 📍 Error 7: File Rotation Not Detected - Lines 48-71 in sensors

```python
# CURRENT STATE (VULNERABLE):
┌─ sensors/auth_sensor.py ────────────────────────────────
│
│ 48  def _process_new_lines(self):
│ 49      """Read and process new lines from the log file."""
│ 50      try:
│ 51          if not self.log_path.exists():
│ 52              return
│ 53          
│ 54          with open(self.log_path, 'r') as f:
│ 55              f.seek(self.last_position)  ❌ ASSUMES SAME FILE
│ 56              new_lines = f.readlines()
│ 57              self.last_position = f.tell()
│
└────────────────────────────────────────────────────────

PROBLEM:
  When logrotate runs:
    auth.log → auth.log.1 (old file moved)
    auth.log (new empty file created)
  
  Code still thinks it's the same file because path hasn't changed
  Seeks to old position in new file
  New empty file: seeking to position 1000 = seeks past EOF
  f.readlines() returns empty list
  Logs between rotation and next check are LOST
  
FIX NEEDED:
  Track file inode to detect when file is replaced:
  
  ```python
  def __init__(self, ...):
      self._last_inode = None  # Add this
  
  def _process_new_lines(self):
      try:
          if not self.log_path.exists():
              return
          
          # Check if file was rotated (inode changed)
          current_stat = self.log_path.stat()
          current_inode = current_stat.st_ino
          
          if self._last_inode is not None and current_inode != self._last_inode:
              # File was rotated!
              logger.info(f"Log file rotated. Starting from beginning.")
              self.last_position = 0
          
          self._last_inode = current_inode
          
          with open(self.log_path, 'r') as f:
              f.seek(self.last_position)
              new_lines = f.readlines()
              self.last_position = f.tell()
  ```
```

---

## 🎯 Summary Table with Exact Locations

| Error | File | Line(s) | What's Missing | How to Fix |
|-------|------|---------|-----------------|-----------|
| 1 | tools.py | 35 | check_ip_threat() impl | Add 25 lines of code |
| 2 | tools.py | 35 | get_system_context() impl | Add 25 lines of code |
| 3 | tools.py | 35 | generate_firewall_rule() impl | Add 20 lines of code |
| 4 | tools.py | 35 | extract_ip_from_log() impl | Add 20 lines of code |
| 5 | tools.py | 35 | check_web_logs_for_ip() impl | Add 20 lines of code |
| 6 | tools.py | 343 | kill_process() PID branch | Add 12 lines of code |
| 7 | tasks.py | 1, 15 | Import List, use List[Task] | 2 line change |
| 8 | auth_sensor.py | 115 | IP validation logic | Change 1 line |
| 9 | web_sensor.py | 115 | IP validation logic | Change 1 line |
| 10 | main.py | 189-193 | JSON regex to brace counting | Replace 30 lines |

---

**Total Code to Add/Fix:** ~150 lines  
**Estimated Effort:** 4-6 hours for experienced Python developer  
**Critical Path:** Lines 35 in tools.py (5 tools must be completed first)
