# Archived: OUTPUT_FORMATTING.md
This file has been archived and moved to `archive/docs-legacy/OUTPUT_FORMATTING.md` on 2026-01-30.

(If you need the original content restored, copy the archived file back into the repository root.)

---

# Sentinel Agent v2.0 - Professional Output Formatting

**Version**: 2.1 (Enhanced Output)  
**Date**: January 26, 2026  
**Status**: Complete with Professional Styling

---

## Overview

Sentinel Agent v2.1 features a completely redesigned output system that provides professional, fancy, and easy-to-understand formatting. All output is clean, structured, and professional—without using icons or emojis.

---

## Output Formatting Enhancements

### 1. Security Alert Display

**Before:**
```
🚨 Suspicious activity detected: IP 192.168.1.100 (Source: auth)
   Attack Type: failed_password
   Severity: medium
   Log line: Failed password for user admin from 192.168.1.100 port 22
```

**After:**
```
----------------------------------------------------------------------------------------------------
                           SECURITY ALERT DETECTED
----------------------------------------------------------------------------------------------------

  Threat Source        : 192.168.1.100
  Attack Classification: Failed Password
  Severity Level       : MEDIUM
  Event Source         : AUTH

  Log Reference        :
  Failed password for user admin from 192.168.1.100 port 22

```

**Features:**
- Clean, structured format with proper alignment
- Professional field labels
- Easy to scan and understand
- No icons or emojis

---

### 2. AI Analysis Initialization

**Before:**
```
🤖 Starting AI crew analysis...
```

**After:**
```
----------------------------------------------------------------------------------------------------
                     INITIALIZING AI INVESTIGATION CREW
----------------------------------------------------------------------------------------------------

  Status: All agents are being assembled and coordinated
  Operation: Sequential analysis chain execution
  Mode: Verbose reporting enabled

  INITIATING AI ANALYSIS
  ----------------------

  Threat Target        : 192.168.1.100
  Threat Category      : Brute Force Attack
  Analysis Type        : Multi-Agent AI Investigation
  Start Time           : 2026-01-26 14:32:21

```

**Features:**
- Clear explanation of what's happening
- Displays threat information
- Professional headers and separators
- Timestamp included

---

### 3. Analysis Complete Report

**Before:**
```
📊 ANALYSIS RESULTS
IP: 192.168.1.100
Severity: high
Threat Level: critical
Recommendation: Block IP
Firewall Rule: iptables -A INPUT -s 192.168.1.100 -j DROP
```

**After:**
```
====================================================================================================
                        ANALYSIS COMPLETE - FINAL REPORT
====================================================================================================

  THREAT INTELLIGENCE
  -------------------

  Target IP Address    : 192.168.1.100
  Threat Severity      : HIGH
  Threat Level         : CRITICAL
  Confidence Score     : 95%

  THREAT ANALYSIS
  ---------------

  Multiple failed SSH login attempts detected. IP has been flagged as potential brute force attacker.
  Recommend immediate blocking and ongoing monitoring.

  RECOMMENDED ACTIONS
  -------------------

  1. Block IP address via firewall rules
  2. Review authentication logs for other affected accounts
  3. Enable account lockout protection
  4. Monitor for additional suspicious activity

  FIREWALL RULE
  ---------------

  Command: iptables -A INPUT -s 192.168.1.100 -j DROP

  DECISION
  --------

  Status: ACTION REQUIRED
  Timestamp: 2026-01-26 14:32:27

====================================================================================================

```

**Features:**
- Comprehensive report layout
- Multiple analysis sections
- Clear decision indicators
- Professional spacing and alignment
- Full firewall command displayed

---

### 4. Human-in-the-Loop Approval

**Before:**
```
🛡️  SECURITY ACTION REQUIRES APPROVAL
IP to block: 192.168.1.100
Command: iptables -A INPUT -s 192.168.1.100 -j DROP
Do you want to execute this firewall rule? (yes/no):
```

**After:**
```
----------------------------------------------------------------------------------------------------
                    SECURITY ACTION REQUIRES APPROVAL
----------------------------------------------------------------------------------------------------

  Target IP Address    : 192.168.1.100
  Firewall Command     : iptables -A INPUT -s 192.168.1.100 -j DROP

  This action will block the IP address using iptables rules.

====================================================================================================

  Execute this firewall rule? (yes/no):
```

**Features:**
- Clear information layout
- Firewall command prominently displayed
- Professional approval request
- Easy to understand consequences

---

### 5. Firewall Execution Success

**Before:**
```
✅ Successfully blocked IP: 192.168.1.100
```

**After:**
```
  SUCCESS
  -------

  Firewall Rule Successfully Applied

  Blocked IP Address: 192.168.1.100
  Rule Command: iptables -A INPUT -s 192.168.1.100 -j DROP
  Status: Active and Verified

```

**Features:**
- Success confirmation with details
- All relevant information displayed
- Professional formatting
- Clear status indication

---

### 6. Attack Records Viewer

**Before:**
```
[#1] 2026-01-26 14:32:10
  IP: 192.168.1.100
  Attack Type: failed_password
  Severity: medium
  Actions: 1
    [SUCCESS] firewall_block: IP blocked in iptables
```

**After:**
```
====================================================================================================
                              ATTACK RECORDS ANALYSIS
====================================================================================================

  RECENT ATTACKS DETAILED
  ----------------------

  ID    Date & Time         IP Address       Attack Type          Severity  Source
  --    -----------         ----------       -----------          --------  ------
  1     2026-01-26 14:32    192.168.1.100    Failed Password      MEDIUM    AUTH
  2     2026-01-26 14:35    192.168.1.101    SQL Injection        HIGH      WEB
  3     2026-01-26 14:38    192.168.1.102    Brute Force Attack   CRITICAL  AUTH

```

**Features:**
- Professional table format
- All information easily scannable
- Proper column alignment
- Clear severity indication
- Timestamp and source visible

---

### 7. Attack Details View

**Example:**
```
====================================================================================================
                              ATTACK RECORD DETAILS
====================================================================================================

  INCIDENT INFORMATION
  --------------------

  Record ID            : 1
  Date & Time          : 2026-01-26 14:32:10
  Attacker IP          : 192.168.1.100

  ATTACK DETAILS
  ---------------

  Attack Type          : Failed Password
  Severity Level       : MEDIUM
  Detection Source     : AUTH
  Description          : Failed SSH login attempt detected

  LOG REFERENCE
  ---------------

  Failed password for invalid user root from 192.168.1.100 port 22 ssh2

  RESPONSE ACTIONS
  ----------------

  1. [SUCCESS] Firewall Block
     Details: IP blocked in iptables successfully

  2. [PENDING] Monitoring
     Details: System is actively monitoring for additional indicators

====================================================================================================

```

**Features:**
- Complete record information
- Organized sections
- Action history with status
- Professional layout

---

## Output Categories

### 1. Alert Messages

**Format:**
```
  CATEGORY
  --------

  Information here
```

**Used for:**
- Security alerts
- System events
- Attack detection

**Example:**
```
  SECURITY ALERT DETECTED
  -----------------------

  Threat Source        : 192.168.1.100
  Attack Classification: SQL Injection
```

---

### 2. Headers

**Main Header:**
```
====================================================================================================
                                SECTION TITLE HERE
====================================================================================================
```

**Subheader:**
```
----------------------------------------------------------------------------------------------------
                                SUBSECTION TITLE
----------------------------------------------------------------------------------------------------
```

**Section Header:**
```
  SECTION NAME
  -----------
```

---

### 3. Data Display

**Key-Value Pairs:**
```
  Field Name          : Value
  Another Field       : Value with alignment
```

**Tables:**
```
  Column1       Column2       Column3
  --------      --------      --------
  Value1        Value2        Value3
```

**Lists:**
```
  1. First item
  2. Second item
  3. Third item
```

---

### 4. Status Messages

**Success:**
```
  SUCCESS
  -------

  Message describing success
  Additional details
```

**Error:**
```
  ERROR ENCOUNTERED
  -----------------

  Title: Brief error description
  Details: More detailed information
```

**Information:**
```
  INFORMATION
  -----------

  Title: Important information
  Details: Supporting information
```

---

## Professional Features

### 1. Consistent Spacing
- 2-space indentation for all content
- Proper alignment of field names
- Clean separation between sections

### 2. Clear Hierarchy
- Main headers use full width separators
- Subheaders use lighter separators
- Section headers are clearly labeled

### 3. Easy Reading
- Generous white space
- Logical grouping of information
- Consistent formatting throughout

### 4. No Icons or Emojis
- All information conveyed through text
- Professional appearance suitable for enterprise
- No platform compatibility issues

---

## Output Formatter API

### Main Functions

#### Header Display
```python
from output_formatter import OutputFormatter, print_header

# Create a main header
print(OutputFormatter.header("SYSTEM ALERT"))

# Or use convenience function
print_header("SYSTEM ALERT")
```

#### Security Alerts
```python
from output_formatter import OutputFormatter, print_alert

# Format security alert
alert = OutputFormatter.alert_event(
    ip_address="192.168.1.100",
    attack_type="brute_force",
    severity="high",
    source="auth",
    log_line="Failed password for user root..."
)
print(alert)

# Or use convenience function
print_alert("192.168.1.100", "brute_force", "high", "auth")
```

#### Analysis Reports
```python
from output_formatter import OutputFormatter, print_report

# Format analysis report
report = {
    'severity': 'high',
    'threat_level': 'critical',
    'description': 'Multiple failed attempts detected',
    'action_required': True,
    'firewall_rule': 'iptables -A INPUT -s 192.168.1.100 -j DROP'
}

print_report(report, ip_address="192.168.1.100")
```

#### Status Messages
```python
from output_formatter import print_success, print_error, print_info

# Success message
print_success(
    "Firewall Rule Applied",
    ["IP blocked successfully", "Rule is active"]
)

# Error message
print_error("Operation Failed", "Details about what went wrong")

# Info message
print_info("System Update", ["Information line 1", "Information line 2"])
```

#### Attack Records
```python
from output_formatter import OutputFormatter

# Table format
table = OutputFormatter.attack_record_table(records_list)
print(table)

# Detailed view
detail = OutputFormatter.attack_record_detail(single_record)
print(detail)
```

---

## Integration Points

### 1. Main Application (main.py)
- Security alert detection and display
- AI analysis initialization
- Remediation approval and execution
- Final report display

### 2. Attack Viewer (view_attacks.py)
- Attack record listing
- Interactive search and filtering
- Detailed record display
- Statistics presentation

### 3. Defense Module (defense/)
- Attack logging with formatted output
- Defense strategy display

---

## Color Support (Optional)

The OutputFormatter includes optional ANSI color codes for terminal output:

```python
# Available colors (can be used if terminal supports it)
OutputFormatter.HEADER    # Magenta
OutputFormatter.BLUE      # Blue
OutputFormatter.CYAN      # Cyan
OutputFormatter.GREEN     # Green
OutputFormatter.YELLOW    # Yellow
OutputFormatter.RED       # Red
OutputFormatter.BOLD      # Bold
OutputFormatter.UNDERLINE # Underline
OutputFormatter.END       # Reset colors
```

**Example with colors:**
```python
print(f"{OutputFormatter.BOLD}Important:{OutputFormatter.END} This is bold text")
```

---

## Best Practices

### 1. Use Descriptive Field Names
```python
# Good
print(f"  Target IP Address    : {ip}")

# Avoid
print(f"  IP: {ip}")
```

### 2. Align Field Values
```python
# Good (aligned)
f"  Field Name          : Value"
f"  Another Field       : Another Value"

# Avoid (misaligned)
f"  Field Name: Value"
f"  Another Field: Another Value"
```

### 3. Use Appropriate Separators
```python
# Header: Use full width separator
print("=" * 100)

# Subheader: Use medium width separator
print("-" * 100)

# Section: Use dashes for titles
print("  SECTION NAME")
print("  -----------")
```

### 4. Group Related Information
```python
# Good: Organize by logical sections
print(OutputFormatter.section("THREAT INFORMATION"))
print(f"  Field 1: {value1}")
print(f"  Field 2: {value2}")

# Avoid: Random ordering
print(f"  Field 1: {value1}")
print(f"  Other 1: {other1}")
print(f"  Field 2: {value2}")
```

---

## Example Outputs

### Complete Attack Detection Workflow

**1. Alert Received:**
```
----------------------------------------------------------------------------------------------------
                           SECURITY ALERT DETECTED
----------------------------------------------------------------------------------------------------

  Threat Source        : 192.168.1.100
  Attack Classification: Brute Force Attack
  Severity Level       : HIGH
  Event Source         : AUTH

  Log Reference        :
  Failed password for user root from 192.168.1.100 port 22 ssh2

```

**2. Analysis Started:**
```
----------------------------------------------------------------------------------------------------
                     INITIALIZING AI INVESTIGATION CREW
----------------------------------------------------------------------------------------------------

  Status: All agents are being assembled and coordinated
  Operation: Sequential analysis chain execution
  Mode: Verbose reporting enabled

  INITIATING AI ANALYSIS
  ----------------------

  Threat Target        : 192.168.1.100
  Threat Category      : Brute Force Attack
  Analysis Type        : Multi-Agent AI Investigation
  Start Time           : 2026-01-26 14:32:21

```

**3. Analysis Complete:**
```
====================================================================================================
                        ANALYSIS COMPLETE - FINAL REPORT
====================================================================================================

  THREAT INTELLIGENCE
  -------------------

  Target IP Address    : 192.168.1.100
  Threat Severity      : HIGH
  Threat Level         : CRITICAL
  Confidence Score     : 98%

  THREAT ANALYSIS
  ---------------

  The IP address 192.168.1.100 has attempted 47 failed SSH login attempts in the last 5 minutes.
  This is consistent with an automated brute force attack. Immediate action is recommended.

  RECOMMENDED ACTIONS
  -------------------

  1. Block IP address via firewall immediately
  2. Review all authentication logs for this IP
  3. Check for successful breaches
  4. Enable multi-factor authentication
  5. Monitor for additional similar attacks

  FIREWALL RULE
  ---------------

  Command: iptables -A INPUT -s 192.168.1.100 -j DROP

  DECISION
  --------

  Status: ACTION REQUIRED
  Timestamp: 2026-01-26 14:32:27

====================================================================================================

```

**4. Approval:**
```
----------------------------------------------------------------------------------------------------
                    SECURITY ACTION REQUIRES APPROVAL
----------------------------------------------------------------------------------------------------

  Target IP Address    : 192.168.1.100
  Firewall Command     : iptables -A INPUT -s 192.168.1.100 -j DROP

  This action will block the IP address using iptables rules.

====================================================================================================

  Execute this firewall rule? (yes/no): yes

```

**5. Execution:**
```
  SUCCESS
  -------

  Firewall Rule Successfully Applied

  Blocked IP Address: 192.168.1.100
  Rule Command: iptables -A INPUT -s 192.168.1.100 -j DROP
  Status: Active and Verified

```

---

## Summary

Sentinel Agent v2.1 provides:

✅ **Professional Output** - No icons, clean formatting  
✅ **Easy to Understand** - Clear sections and field labels  
✅ **Fancy Styling** - Nice layout with proper spacing  
✅ **Enterprise-Ready** - Suitable for production systems  
✅ **Consistent Format** - Uniform styling throughout  
✅ **Rich Information** - All details clearly displayed  

The new output system transforms the Sentinel Agent into a truly professional security tool with beautiful, informative displays that are easy to read and understand.

---

**Version**: 2.1  
**Status**: Complete and Ready for Production  
**Last Updated**: January 26, 2026
