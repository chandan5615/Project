# Archived: OUTPUT_EXAMPLES.md
This file has been archived and moved to `archive/docs-legacy/OUTPUT_EXAMPLES.md` on 2026-01-30.

(If you need the original content restored, copy the archived file back into the repository root.)

---

# Sentinel Agent v2.1 - Output Examples & Visual Guide

**Date**: January 26, 2026  
**Version**: 2.1 (Professional Output)  
**Purpose**: Showcase professional output formatting without icons

---

## Complete Workflow Examples

### Example 1: Brute Force Attack Detection & Response

#### Step 1: System Startup

```
====================================================================================================
                        SENTINEL AGENT v2.0 INITIALIZATION
====================================================================================================

  SYSTEM CONFIGURATION
  --------------------

  Authentication Log   : /var/log/auth.log
  Web Access Log       : /var/log/apache2/access.log
  AI Engine            : Ollama Local LLM (llama3:8b)
  Analysis Mode        : Multi-Agent AI Investigation
  Multi-Vector Support : Enabled
  Human-in-Loop        : Enabled

```

#### Step 2: Attack Detection

```
----------------------------------------------------------------------------------------------------
                           SECURITY ALERT DETECTED
----------------------------------------------------------------------------------------------------

  Threat Source        : 192.168.1.105
  Attack Classification: Brute Force Attack
  Severity Level       : CRITICAL
  Event Source         : AUTH

  Log Reference        :
  Failed password for root from 192.168.1.105 port 22 ssh2

----------------------------------------------------------------------------------------------------
                     INITIALIZING AI INVESTIGATION CREW
----------------------------------------------------------------------------------------------------

  Status: All agents are being assembled and coordinated
  Operation: Sequential analysis chain execution
  Mode: Verbose reporting enabled

```

#### Step 3: AI Analysis

```
  INITIATING AI ANALYSIS
  ----------------------

  Threat Target        : 192.168.1.105
  Threat Category      : Brute Force Attack
  Analysis Type        : Multi-Agent AI Investigation
  Start Time           : 2026-01-26 15:45:32

  
  [PROCESSING] Triage Analyst              | Analyzing attack pattern and severity
  [PROCESSING] Threat Intelligence Researcher | Checking IP reputation database
  [PROCESSING] Incident Response Specialist    | Generating response plan
  [PROCESSING] Enforcer Agent              | Preparing firewall rules

```

#### Step 4: Final Report

```
====================================================================================================
                        ANALYSIS COMPLETE - FINAL REPORT
====================================================================================================

  THREAT INTELLIGENCE
  -------------------

  Target IP Address    : 192.168.1.105
  Threat Severity      : CRITICAL
  Threat Level         : CRITICAL
  Confidence Score     : 99%

  THREAT ANALYSIS
  ---------------

  The IP address 192.168.1.105 has attempted 156 failed SSH login attempts in 8 minutes.
  Pattern analysis indicates automated brute force attack targeting root account.
  Previous reputation checks show this IP associated with 47 other incidents.
  Immediate blocking is strongly recommended.

  RECOMMENDED ACTIONS
  -------------------

  1. Block IP address via firewall rules (PRIORITY: IMMEDIATE)
  2. Review SSH logs for successful breaches
  3. Check password policy and implement account lockout
  4. Enable multi-factor authentication
  5. Monitor for additional attacks from this IP range

  FIREWALL RULE
  ---------------

  Command: iptables -A INPUT -s 192.168.1.105 -j DROP

  DECISION
  --------

  Status: ACTION REQUIRED
  Timestamp: 2026-01-26 15:45:45

====================================================================================================

```

#### Step 5: Approval & Execution

```
----------------------------------------------------------------------------------------------------
                    SECURITY ACTION REQUIRES APPROVAL
----------------------------------------------------------------------------------------------------

  Target IP Address    : 192.168.1.105
  Firewall Command     : iptables -A INPUT -s 192.168.1.105 -j DROP

  This action will block the IP address using iptables rules.

====================================================================================================

  Execute this firewall rule? (yes/no): yes

  SUCCESS
  -------

  Firewall Rule Successfully Applied

  Blocked IP Address: 192.168.1.105
  Rule Command: iptables -A INPUT -s 192.168.1.105 -j DROP
  Status: Active and Verified

```

---

### Example 2: SQL Injection Detection

#### Attack Alert

```
----------------------------------------------------------------------------------------------------
                           SECURITY ALERT DETECTED
----------------------------------------------------------------------------------------------------

  Threat Source        : 203.45.67.89
  Attack Classification: SQL Injection
  Severity Level       : HIGH
  Event Source         : WEB

  Log Reference        :
  GET /search.php?q=1' OR '1'='1'-- HTTP/1.1 200

```

#### Analysis Report

```
====================================================================================================
                        ANALYSIS COMPLETE - FINAL REPORT
====================================================================================================

  THREAT INTELLIGENCE
  -------------------

  Target IP Address    : 203.45.67.89
  Threat Severity      : HIGH
  Threat Level         : HIGH
  Confidence Score     : 96%

  THREAT ANALYSIS
  ---------------

  SQL injection payload detected in web application query parameter.
  Payload: 1' OR '1'='1'-- (classic OR-based SQL injection)
  Target appears to be search functionality in website.
  Suggests automated vulnerability scanning or targeted attack.

  RECOMMENDED ACTIONS
  -------------------

  1. Block IP immediately using firewall
  2. Review web application logs for compromise
  3. Implement input validation and prepared statements
  4. Conduct web application security audit
  5. Enable Web Application Firewall (WAF) rules

  FIREWALL RULE
  ---------------

  Command: iptables -A INPUT -s 203.45.67.89 -j DROP

  DECISION
  --------

  Status: ACTION REQUIRED
  Timestamp: 2026-01-26 16:22:15

====================================================================================================

```

---

### Example 3: Attack Records Viewer

#### Main Menu

```
====================================================================================================
                              ATTACK RECORDS ANALYSIS
====================================================================================================

  RECENT ATTACKS DETAILED
  ----------------------

  ID    Date & Time         IP Address       Attack Type          Severity  Source
  --    -----------         ----------       -----------          --------  ------
  1     2026-01-26 15:45    192.168.1.105    Brute Force Attack   CRITICAL  AUTH
  2     2026-01-26 16:22    203.45.67.89     SQL Injection        HIGH      WEB
  3     2026-01-26 16:45    10.0.0.50        Failed Password      MEDIUM    AUTH
  4     2026-01-26 17:01    172.16.10.25     XSS Reflected        MEDIUM    WEB
  5     2026-01-26 17:15    192.168.1.110    Credential Stuffing   HIGH      AUTH
  6     2026-01-26 17:32    203.100.50.10    Command Injection    CRITICAL  WEB
  7     2026-01-26 17:48    10.20.30.40      Directory Traversal   MEDIUM    WEB
  8     2026-01-26 18:00    192.168.2.75     CSRF Attack          LOW       WEB
  9     2026-01-26 18:15    172.31.0.100     Session Hijacking    HIGH      AUTH
  10    2026-01-26 18:30    203.50.25.15     Brute Force Attack   CRITICAL  AUTH

  STATISTICS
  ----------

  Total Attacks Recorded: 10

  ATTACKS BY SEVERITY

  CRITICAL: ========== (3)
  HIGH    : ======== (4)
  MEDIUM  : ======= (3)

  TOP ATTACK TYPES

  Brute Force Attack           : 3
  SQL Injection                : 1
  Failed Password              : 1
  Credential Stuffing          : 1
  Command Injection            : 1
  Directory Traversal          : 1
  XSS Reflected                : 1
  CSRF Attack                  : 1
  Session Hijacking            : 1

====================================================================================================

  INTERACTIVE VIEWER OPTIONS
  ----------------------------

  1. View full details of a record
  2. Search by IP address
  3. Filter by attack type
  4. Filter by severity
  5. Exit

  Select option (1-5):
```

#### Record Details View

```
====================================================================================================
                              ATTACK RECORD DETAILS
====================================================================================================

  INCIDENT INFORMATION
  --------------------

  Record ID            : 1
  Date & Time          : 2026-01-26 15:45:32
  Attacker IP          : 192.168.1.105

  ATTACK DETAILS
  ---------------

  Attack Type          : Brute Force Attack
  Severity Level       : CRITICAL
  Detection Source     : AUTH
  Description          : Multiple failed SSH login attempts detected targeting root account

  LOG REFERENCE
  ---------------

  Failed password for root from 192.168.1.105 port 22 ssh2

  RESPONSE ACTIONS
  ----------------

  1. [SUCCESS] Firewall Block
     Details: IP blocked in iptables successfully

  2. [SUCCESS] Attack Logged
     Details: Incident recorded in attack database

  3. [PENDING] Monitoring
     Details: System is actively monitoring for additional indicators

====================================================================================================

```

---

## Output Elements Reference

### Headers

**Main Header (100 characters):**
```
====================================================================================================
                                 SECTION TITLE
====================================================================================================
```

**Subheader (100 characters):**
```
----------------------------------------------------------------------------------------------------
                              SUBSECTION TITLE
----------------------------------------------------------------------------------------------------
```

**Section Title:**
```
  SECTION NAME
  -----------
```

---

### Data Fields

**Single Field:**
```
  Field Name          : Value
```

**Multiple Related Fields:**
```
  Target IP Address   : 192.168.1.100
  Attack Type         : Brute Force
  Severity Level      : CRITICAL
  Detection Time      : 2026-01-26 15:45:32
```

**Table Format:**
```
  Column 1          Column 2            Column 3
  --------          --------            --------
  Value 1           Value 2              Value 3
  Another Value     Another Value        Another
```

---

### Status Indicators

**Processing:**
```
  [PROCESSING] Agent Name              | Status message
```

**Success:**
```
  [SUCCESS] Action Type
  Details: Information about what succeeded
```

**Pending:**
```
  [PENDING] Action Type
  Details: Information about what is pending
```

**Failed:**
```
  [FAILED] Action Type
  Details: Information about what failed
```

---

### Alert Levels

**Critical Alert:**
```
Threat Source        : IP Address
Attack Classification: Attack Type
Severity Level       : CRITICAL
```

**High Severity:**
```
Severity Level       : HIGH
```

**Medium Severity:**
```
Severity Level       : MEDIUM
```

**Low Severity:**
```
Severity Level       : LOW
```

---

## Professional Formatting Guidelines

### 1. Alignment
All field names should align at the same column. Use spaces to align values:

**Good:**
```
  Field Name      : Value
  Longer Field    : Value
  Another One     : Value
```

**Avoid:**
```
  Field Name: Value
  Longer Field: Value
  Another One: Value
```

### 2. Spacing
- Use 2 spaces for indentation
- One blank line between major sections
- One blank line before prompts

**Good:**
```
  SECTION 1
  ---------

  Field: Value

  SECTION 2
  ---------

  Field: Value
```

### 3. Width
- Main content uses approximately 100 characters width
- Consider readability on standard terminals (80-120 chars)
- Don't exceed 100 characters for best appearance

### 4. Hierarchy
Clear visual hierarchy with:
- Main headers (100 char separator)
- Subheaders (dash separator)
- Section titles (dash underline)
- Content (indented fields)

---

## User Experience Features

### 1. Clear Information Flow
- Problem statement first
- Analysis details next
- Actions and decisions last

### 2. Easy Scanning
- Section titles clearly visible
- Field names aligned
- Values easy to locate

### 3. Complete Information
- All relevant details included
- Timestamps for reference
- Status clearly indicated

### 4. Professional Appearance
- No informal language
- Proper capitalization
- Consistent formatting
- Clean presentation

---

## Color Support (Optional)

For terminals that support ANSI colors, the formatter can optionally use:

```python
# Available but optional colors
OutputFormatter.BOLD       # For emphasis
OutputFormatter.UNDERLINE  # For highlighting
OutputFormatter.RED        # For errors
OutputFormatter.GREEN      # For success
OutputFormatter.YELLOW     # For warnings
OutputFormatter.CYAN       # For information
```

By default, all output is text-based for maximum compatibility.

---

## Accessibility Features

### 1. No Special Characters
- All output uses standard ASCII
- Works on any terminal
- No platform-specific issues

### 2. Screen Reader Friendly
- Clear structure and hierarchy
- Consistent formatting
- Descriptive field names

### 3. Copy-Paste Friendly
- Clean formatting for copying
- Easy to include in reports
- Professional appearance when exported

---

## Integration Examples

### Running the System
```bash
$ sudo python main.py
# Professional startup and monitoring output
```

### Viewing Records
```bash
$ python view_attacks.py
# Clean, easy-to-read attack records
```

### Output in Logs
All formatted output is also logged:
```bash
$ tail -f system_logs.txt
# Professional formatted messages in logs
```

---

## Summary

Sentinel Agent v2.1 provides professional, fancy, and easy-to-understand output formatting featuring:

✅ **No Icons** - Pure text-based professional appearance  
✅ **Clear Layout** - Well-organized sections and fields  
✅ **Professional** - Enterprise-grade presentation  
✅ **Easy to Read** - Proper spacing and alignment  
✅ **Consistent** - Same style throughout  
✅ **Informative** - All details clearly displayed  
✅ **Accessible** - Works on any terminal  

The system transforms complex security events into clear, understandable, and professional displays.

---

**Version**: 2.1  
**Status**: Complete and Ready  
**Last Updated**: January 26, 2026
