# Auto-Unblocking & Whitelist Protection Features

**Release Date**: February 25, 2026  
**Version**: 2.3  
**Status**: [OK] Implemented & Deployed

---

## [DOCS] Overview

This document describes three new security features added to Sentinel Agent v2.2:

1. **Temporary Ban Logic (Auto-Expiry)** - Automatic IP unblocking after configurable time
2. **Whitelist Protection (Admin God-Mode)** - Prevent blocking of admin/local network
3. **Progressive Punishment** - Escalating penalties for repeat offenders

These features prevent permanent lockouts of genuine users/admins while maintaining strong security.

---

## [UNBLOCK] Feature 1: Temporary Ban Logic (Auto-Expiry)

### Problem Solved
Previously, blocked IPs would remain blocked indefinitely, risking permanent lockout of:
- Legitimate users with bad passwords
- Misconfigured services
- Temporary network issues
- Administrative mistakes

### How It Works

#### Database Schema
```sql
CREATE TABLE blocked_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE,
    blocked_at TEXT,              -- When the block was applied
    banned_until TEXT,            -- When the ban expires
    offense_count INTEGER,        -- Number of previous offenses
    ban_duration_minutes INTEGER, -- How long to ban
    reason TEXT,                  -- Why they were blocked
    status TEXT DEFAULT 'active'  -- 'active' or 'expired'
)
```

#### Auto-Unblock Process

1. **Background Cleanup Thread** (runs every 60 seconds)
   ```python
   # Checks for expired bans
   data_engine.get_expired_ips()
   
   # Auto-unblocks each expired IP:
   iptables -D INPUT -s {ip} -j DROP
   
   # Marks status as 'expired' in database
   data_engine.mark_ip_unblocked(ip)
   ```

2. **Progressive Ban Durations** (see Feature 3)
   - 1st offense: 15 minutes
   - 2nd offense: 2 hours
   - 3rd+ offense: 24 hours
   - CRITICAL severity: 24 hours (always)

3. **Logging**
   ```
   [OK] Auto-unblocked 203.0.113.45 (ban expired)
   [UNBLOCK] Found 3 expired IP blocks - auto-unblocking...
   ```

### Configuration
- **Check Interval**: 60 seconds (hardcoded, can be tuned)
- **Ban Duration**: Set by progressive punishment logic
- **Thread Type**: Daemon thread (exits when main process exits)

### Code Location
- **main.py**: `_cleanup_expired_blocks()`, `_unblock_ip()`, `_start_cleanup_thread()`
- **data_engine.py**: `block_ip()`, `get_expired_ips()`, `mark_ip_unblocked()`

---

## [PROTECT] Feature 2: Whitelist Protection (Admin God-Mode)

### Problem Solved
Prevents the system from "suicide-blocking" the administrator or local network due to:
- Misconfigured authentication
- False positive detections
- Testing gone wrong
- Legitimate but suspicious activity

### How It Works

#### Database Schema
```sql
CREATE TABLE safe_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE,
    reason TEXT,
    added_at TEXT,
    auto_detected INTEGER DEFAULT 0  -- 1 if auto-detected on startup
)
```

#### Auto-Detection on Startup

```python
# tools/tools.py
get_admin_ips()  # Returns list of safe IPs including:
├── 127.0.0.1          # Localhost IPv4
├── ::1                 # Localhost IPv6
├── {local_ip}          # Server's primary IP
└── {local_network}     # Local network (e.g., 192.168.1.0/24)
```

#### Check-Before-Block Rule

In `_handle_remediation()`:
```python
if data_engine.is_whitelisted(ip_address):
    logger.warning(f"[WHITE] WHITELIST PROTECTION: IP {ip} is whitelisted - SKIPPING BLOCK")
    data_engine.insert_action(incident_id, "whitelist_skip", ...)
    return  # Do NOT block
```

#### Startup Initialization

```
[SECURE] Initializing Whitelist Protection...
  [OK] 127.0.0.1 (already whitelisted)
  [OK] 192.168.31.91 (added to whitelist)
  [OK] 192.168.31.0/24 (added to whitelist)
[OK] Auto-unblock cleanup thread started (checks every 60 seconds)
```

### Functions
| Function | Purpose |
|----------|---------|
| `add_safe_ip(ip, reason, auto_detected)` | Add IP to whitelist |
| `is_whitelisted(ip)` | Check if IP is safe |
| `get_all_whitelisted_ips()` | List all safe IPs |
| `remove_from_whitelist(ip)` | Remove from whitelist |
| `get_local_ip()` | Detect server IP |
| `get_local_network()` | Detect local network |
| `get_admin_ips()` | Get all safe IPs to add |

### Code Location
- **data_engine.py**: `add_safe_ip()`, `is_whitelisted()`, `get_all_whitelisted_ips()`, `remove_from_whitelist()`
- **tools/tools.py**: `get_local_ip()`, `get_local_network()`, `get_admin_ips()`
- **main.py**: `start()` initialization, `_handle_remediation()` check

---

## [BALANCE] Feature 3: Progressive Punishment

### Problem Solved
First-time offenders (users who made a mistake) shouldn't receive the same penalty as repeat attackers:
- Genuine users with typos get 15-minute cooldown
- Persistent attackers get escalating penalties
- Repeat offenders get hard 24-hour bans

### How It Works

#### Punishment Schedule
```
Offense #  | Ban Duration | Severity Level | Rationale
-----------|--------------|----------------|----------
1st        | 15 minutes   | Any            | Cooldown for mistakes
2nd        | 2 hours      | Any            | Escalated warning
3rd+       | 24 hours     | Any            | Hard ban - repeat attacker
ANY*       | 24 hours     | CRITICAL       | Override all (immediate hard ban)

*CRITICAL severity overrides all logic
```

#### Offense Tracking
```python
data_engine.get_offense_count(ip)  # Returns count of previous offenses

Progressive punishment applied in _calculate_ban_duration():
- If count=0: 15 min ban
- If count=1: 120 min ban (2 hours)
- If count≥2: 1440 min ban (24 hours)
```

#### Database Tracking
```
Each block adds offense_count in blocked_ips table:
IP 203.0.113.45 blocked 3 times = offense_count = 3
```

#### Logging
```
[BALANCE]  1st offense → 15 minute ban for 203.0.113.45
[BALANCE]  2nd offense → 2 hour ban for 203.0.113.45
[BALANCE]  3rd offense → 24 hour HARD BAN for 203.0.113.45
[WARNING]  CRITICAL severity → 24 hour HARD BAN for 203.0.113.45
```

### Code Location
- **main.py**: `_calculate_ban_duration()`, `_handle_remediation()` (calls it)
- **data_engine.py**: `block_ip()` (increments offense_count), `get_offense_count()`

---

## [CONFIG] Implementation Details

### Files Modified
1. **data_engine.py** (↑55 lines)
   - Added 2 new tables: `blocked_ips`, `safe_ips`
   - Added 8 new methods for managing blocks and whitelist

2. **main.py** (↑120 lines)
   - Added cleanup thread: `_start_cleanup_thread()`, `_cleanup_expired_blocks()`, `_unblock_ip()`
   - Added punishment logic: `_calculate_ban_duration()`
   - Modified `__init__()` to initialize thread
   - Modified `start()` to initialize whitelist
   - Modified `_handle_remediation()` to check whitelist + apply progressive punishment

3. **tools/tools.py** (↑70 lines)
   - Added 3 new functions: `get_local_ip()`, `get_local_network()`, `get_admin_ips()`

### Backward Compatibility
[OK] **Fully compatible** - All existing code continues to work:
- Old `incidents` table unchanged
- Old `actions` table unchanged
- Whitelist check is transparent (if IP not in list, proceeds normally)

### Performance Impact
- **Minimal**: Cleanup thread checks every 60 seconds
- **Negligible**: Whitelist lookup is O(1) database query
- **No impact on blocking**: Progressive punishment calculated once per block

---

## [STATS] Usage Examples

### Example 1: First-Time Offender Gets 15-Minute Ban
```
20:30:15 | [ERROR] Attack detected: 203.0.113.45 (suspicious auth)
20:30:16 | [BALANCE]  1st offense → 15 minute ban for 203.0.113.45
20:30:17 | [SECURE] Firewall rule: iptables -I INPUT -s 203.0.113.45 -j DROP
20:30:18 | [OK] IP 203.0.113.45 blocked until 20:45:15
---
20:45:15 | [UNBLOCK] Found 1 expired IP blocks - auto-unblocking...
20:45:16 | [OK] Auto-unblocked 203.0.113.45 (ban expired)
20:45:17 | [UNBLOCK] Firewall rule removed for 203.0.113.45
```

### Example 2: Repeat Attacker Gets 24-Hour Ban
```
19:00:00 | [ERROR] Attack detected: 192.0.2.1 (1st time)
19:00:01 | [BALANCE]  1st offense → 15 minute ban
---
(15 minutes later)
19:15:01 | [UNBLOCK] Auto-unblocked 192.0.2.1
---
19:20:00 | [ERROR] Attack detected: 192.0.2.1 (2nd time!)
19:20:01 | [BALANCE]  2nd offense → 2 hour ban
---
(2 hours later)
21:20:01 | [UNBLOCK] Auto-unblocked 192.0.2.1
---
21:25:00 | [ERROR] Attack detected: 192.0.2.1 (3rd time!!!)
21:25:01 | [BALANCE]  3rd offense → 24 hour HARD BAN
---
(24 hours later)
21:25:01 Next day | [UNBLOCK] Auto-unblocked 192.0.2.1
```

### Example 3: Admin IP Protected
```
14:30:00 | [ERROR] Attack detected: 192.168.31.91 (config mistake)
14:30:01 | [WHITE] WHITELIST PROTECTION: IP 192.168.31.91 is whitelisted - SKIPPING BLOCK
14:30:02 | ℹ️  No action taken - risk of admin lockout prevented
```

### Example 4: Startup Initialization
```
SENTINEL AGENT v2.2 - Security Monitoring Active
=========================================================
[SECURE] Initializing Whitelist Protection...
  [OK] 127.0.0.1 (already whitelisted)
  [OK] 192.168.31.91 (added to whitelist)
  [OK] 192.168.31.0/24 (added to whitelist)
[OK] Auto-unblock cleanup thread started (checks every 60 seconds)

[OK] Monitoring active: Auth + Web logs | Cross-correlation enabled
Press Ctrl+C to stop
```

---

## [TEST] Testing

### Manual Test 1: Auto-Unblocking
```bash
# Simulate blocking an IP for 15 seconds (for testing)
python -c "
from data_engine import DataEngine
db = DataEngine()
db.block_ip('192.0.2.100', ban_duration_minutes=0.25, reason='test')  # 15 sec
print('IP blocked until expiry in 15 seconds...')
import time; time.sleep(15)
expired = db.get_expired_ips()
print(f'Expired IPs: {len(expired)}')
"
```

### Manual Test 2: Whitelist Check
```bash
python -c "
from data_engine import DataEngine
db = DataEngine()
db.add_safe_ip('192.0.2.1', 'Test whitelist')
print(f'Is 192.0.2.1 whitelisted? {db.is_whitelisted(\"192.0.2.1\")}')
print(f'Is 10.0.0.1 whitelisted? {db.is_whitelisted(\"10.0.0.1\")}')
"
```

### Manual Test 3: Progressive Punishment
```bash
python -c "
from data_engine import DataEngine
db = DataEngine()
# Simulate 3 blocks
db.block_ip('203.0.113.10', 15, 'Test 1st')
db.block_ip('203.0.113.10', 120, 'Test 2nd')
db.block_ip('203.0.113.10', 1440, 'Test 3rd')
print(f'Offense count: {db.get_offense_count(\"203.0.113.10\")}')
"
```

---

## [DEPLOY] Deployment

### Files Deployed
- [OK] `main.py` (modified)
- [OK] `data_engine.py` (modified)
- [OK] `tools/tools.py` (modified)

### Docker Rebuild
```bash
ssh ubuntu@192.168.31.91 "cd ~/Project && docker-compose down && \
  docker-compose build --no-cache && docker-compose up -d"
```

### Verification
```bash
# Check logs
docker-compose logs sentinel-agent | grep -E "Whitelist|Auto-unblock|Progressive"

# Check database
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT * FROM blocked_ips LIMIT 5;"
```

---

## [CONFIG] Configuration

### Adjustable Parameters

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| Cleanup interval | `_cleanup_expired_blocks()` | 60s | How often to check for expired bans |
| 1st offense ban | `_calculate_ban_duration()` | 15 min | First-time offender penalty |
| 2nd offense ban | `_calculate_ban_duration()` | 120 min | Second-time offender penalty |
| 3rd+ offense ban | `_calculate_ban_duration()` | 1440 min | Hard ban duration |
| Local network mask | `get_local_network()` | /24 | Subnet for local network protection |

### Tuning Examples

**More lenient (shorter bans)**:
```python
# In _calculate_ban_duration()
ban_minutes = 5    # 1st offense
ban_minutes = 30   # 2nd offense
ban_minutes = 120  # 3rd offense
```

**Stricter (longer bans)**:
```python
# In _calculate_ban_duration()
ban_minutes = 30   # 1st offense
ban_minutes = 480  # 2nd offense (8 hours)
ban_minutes = 2880 # 3rd offense (48 hours)
```

---

## [DATA] Monitoring

### Key Metrics to Track
1. **Auto-unblock rate**: How many IPs auto-unblocked vs still blocked
2. **Offense distribution**: Are most IPs 1st-time or repeaters?
3. **False positive prevention**: How many whitelisted IPs were protected?
4. **Ban effectiveness**: Do 2nd/3rd offenses have lower attack rates?

### Database Queries
```sql
-- Count active blocks
SELECT COUNT(*) FROM blocked_ips WHERE status='active';

-- Find repeat offenders
SELECT ip, COUNT(*) as attempts FROM blocked_ips 
GROUP BY ip HAVING COUNT(*) > 1;

-- Check whitelist coverage
SELECT COUNT(*) FROM safe_ips;

-- Find expired but not cleaned
SELECT COUNT(*) FROM blocked_ips 
WHERE status='active' AND banned_until < datetime('now');
```

---

## [BUG] Troubleshooting

### Issue: Cleanup thread not running
**Check**: `docker logs sentinel-agent | grep "Auto-unblock cleanup thread"`  
**Fix**: Ensure `_start_cleanup_thread()` is called in `start()` method

### Issue: IPs not auto-unblocking
**Possible causes**:
1. Cleanup thread crashed (check logs)
2. iptables rule syntax error (check firewall)
3. Permission denied (running as non-root)

**Debug**:
```bash
docker exec sentinel-agent ps aux | grep cleanup
docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db \
  "SELECT * FROM blocked_ips WHERE banned_until < datetime('now');"
```

### Issue: Whitelist not preventing blocks
**Check**: `data_engine.is_whitelisted(ip)` returns True  
**Debug**:
```bash
docker exec sentinel-agent python -c "
from data_engine import DataEngine
db = DataEngine()
print('Safe IPs:', db.get_all_whitelisted_ips())
"
```

---

## [DOCS] Future Enhancements

Potential v2.4 improvements:
1. **Manual whitelist management**: Add CLI commands to manage whitelist
2. **Temporary whitelist**: Time-limited whitelist entries ("disable block for 1 hour")
3. **Context-aware punishment**: Different ban lengths based on attack type
4. **Redemption system**: Forgive old offenses after long periods
5. **Backup retention**: Keep history of unblocked IPs for forensics

---

## [SUPPORT] Support

For issues or questions:
1. Check logs: `docker-compose logs sentinel-agent`
2. Review database: `docker exec sentinel-agent sqlite3 /app/data/sentinel_intel.db`
3. Test features manually using examples above
4. Check this document's troubleshooting section

---

**Version**: 2.3  
**Last Updated**: February 25, 2026  
**Status**: [OK] Production Ready
