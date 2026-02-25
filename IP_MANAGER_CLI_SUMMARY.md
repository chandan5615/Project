# 🛡️ IP Manager CLI - Feature Addition Summary

## ✅ What Was Added

A **standalone command-line tool** for blocking/unblocking IPs directly from the Linux terminal without needing the web dashboard.

---

## 📁 New Files Created

### **1. ip_manager_cli.py** (17 KB)
**Location:** `~/Project/ip_manager_cli.py`

**Purpose:** Interactive and scriptable IP blocking/unblocking tool for Linux CLI

**Features:**
- ✅ Block/unblock single or multiple IPs
- ✅ List all currently blocked IPs
- ✅ Check if an IP is blocked
- ✅ Interactive mode with command prompt
- ✅ Batch operations support
- ✅ Works with both UFW and iptables
- ✅ IP address validation
- ✅ Color-coded terminal output
- ✅ Reason/comment support for blocks
- ✅ Flush all blocks (with confirmation)

**Usage Examples:**
```bash
# Interactive mode
python3 ip_manager_cli.py

# Block an IP
sudo python3 ip_manager_cli.py block 1.2.3.4

# Block multiple IPs
sudo python3 ip_manager_cli.py block 1.2.3.4 5.6.7.8 9.10.11.12

# Unblock an IP
sudo python3 ip_manager_cli.py unblock 1.2.3.4

# List blocked IPs
sudo python3 ip_manager_cli.py list

# Check if IP is blocked
sudo python3 ip_manager_cli.py check 1.2.3.4
```

---

### **2. IP_MANAGER_CLI_GUIDE.md** (11 KB)
**Location:** `~/Project/IP_MANAGER_CLI_GUIDE.md`

**Purpose:** Complete user guide for the IP Manager CLI tool

**Contents:**
- Installation instructions
- Quick start guide
- All command examples
- Common use cases
- Tips & tricks
- Integration with Sentinel
- Troubleshooting
- Advanced usage (scripting, automation)

---

## 📝 Documentation Updates

### **README.md Updated**
Added IP Manager CLI documentation to:

1. **Utility Scripts Section:**
   - Added `ip_manager_cli.py` as first entry (starred as new feature)
   - Marked with ⭐ to highlight it's new

2. **Command-Line Reference Section:**
   - Added complete `IP Manager CLI` section with:
     - All commands documented
     - All options explained
     - 10+ usage examples
     - Feature checklist
     - Reference to detailed guide

3. **Documentation Files Section:**
   - Added `IP_MANAGER_CLI_GUIDE.md` to dashboard & features

---

## 🎯 Key Features

### **1. Dual Firewall Support**
Works with both UFW and iptables automatically:
- Detects which firewall is available
- Uses appropriate commands
- Can manage both simultaneously

### **2. Interactive Mode**
User-friendly command prompt:
```bash
sentinel-ip> block 1.2.3.4
✓ Blocked 1.2.3.4 using UFW

sentinel-ip> list
ℹ Found 5 blocked IPs in UFW:
  1. 1.2.3.4
  2. 5.6.7.8
  ...

sentinel-ip> exit
```

### **3. Batch Operations**
Block/unblock multiple IPs in one command:
```bash
sudo python3 ip_manager_cli.py block 1.2.3.4 5.6.7.8 9.10.11.12
```

### **4. Color-Coded Output**
- ✓ **Green** for success
- ✗ **Red** for errors
- ⚠ **Yellow** for warnings
- ℹ **Blue** for information

### **5. IP Validation**
Validates IP addresses before blocking:
- Checks format (xxx.xxx.xxx.xxx)
- Validates octets (0-255)
- Prevents invalid entries

### **6. Scriptable**
Easy to integrate into automation:
```bash
# Get top attacking IPs and block them
sqlite3 ~/Project/data/sentinel_intel.db \
  "SELECT DISTINCT source_ip FROM incidents WHERE severity='HIGH' LIMIT 10" | \
  xargs sudo python3 ~/Project/ip_manager_cli.py block
```

---

## 🆚 CLI Tool vs Web Dashboard

| Feature | CLI Tool | Web Dashboard |
|---------|----------|---------------|
| **Speed** | ⚡ Very fast | Moderate |
| **Batch operations** | ✅ Easy (one command) | Limited |
| **Remote access** | SSH only | Web browser |
| **Scriptable** | ✅ Yes | No |
| **Interactive** | ✅ Yes | ✅ Yes |
| **Visual feedback** | Text/Colors | Charts/Tables |
| **Authentication** | SSH/sudo | HTTP Basic Auth |
| **Best for** | Admins, scripts, automation | Monitoring, analysis, visualization |

---

## 💡 Use Cases

### **1. Quick Manual Block**
```bash
sudo python3 ip_manager_cli.py block 203.0.113.50 --reason "Brute force attack"
```

### **2. Batch Block from File**
```bash
cat blacklist.txt | xargs sudo python3 ip_manager_cli.py block
```

### **3. Automated Blocking Script**
```bash
#!/bin/bash
# Block top 10 attackers daily

sqlite3 ~/Project/data/sentinel_intel.db \
  "SELECT source_ip, COUNT(*) as cnt FROM incidents 
   GROUP BY source_ip 
   HAVING cnt > 10" | \
  awk -F'|' '{print $1}' | \
  xargs sudo python3 ~/Project/ip_manager_cli.py block --reason "Repeat offender"
```

### **4. Emergency Response**
```bash
# Quick interactive session to block attackers
sudo python3 ip_manager_cli.py
> list
> check 203.0.113.10
> block 203.0.113.10
> exit
```

### **5. Unblock False Positives**
```bash
sudo python3 ip_manager_cli.py unblock 192.168.1.100
```

---

## 🚀 Installation Status

### **Local (Windows)**
✅ Files created in: `c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\`
- ✅ ip_manager_cli.py
- ✅ IP_MANAGER_CLI_GUIDE.md

### **Remote (Ubuntu Server)**
✅ Files uploaded to: `~/Project/`
- ✅ ip_manager_cli.py (executable)
- ✅ IP_MANAGER_CLI_GUIDE.md

### **Documentation**
✅ README.md updated with:
- ✅ Utility scripts section
- ✅ Command-line reference section
- ✅ Documentation files section

---

## 🔧 Requirements

**System:**
- Linux (Ubuntu/Debian/CentOS)
- Python 3.6+
- sudo access

**Firewall:**
- UFW (recommended) OR
- iptables

**No additional Python packages required!** Uses only standard library.

---

## 📋 Quick Start

### **1. Make executable** (already done)
```bash
chmod +x ~/Project/ip_manager_cli.py
```

### **2. Run interactive mode**
```bash
sudo python3 ~/Project/ip_manager_cli.py
```

### **3. Try commands**
```bash
sentinel-ip> list
sentinel-ip> block 1.2.3.4
sentinel-ip> check 1.2.3.4
sentinel-ip> unblock 1.2.3.4
sentinel-ip> help
sentinel-ip> exit
```

### **4. Create alias for easy access** (optional)
```bash
echo "alias ipblock='sudo python3 ~/Project/ip_manager_cli.py'" >> ~/.bashrc
source ~/.bashrc

# Then use:
ipblock list
ipblock block 1.2.3.4
ipblock unblock 1.2.3.4
```

---

## 🎓 Example Session

```bash
ubuntu@sentinel:~/Project$ sudo python3 ip_manager_cli.py
╔════════════════════════════════════════════════════════╗
║          SENTINEL IP MANAGER - CLI TOOL                ║
║        Block/Unblock IPs from Command Line             ║
╚════════════════════════════════════════════════════════╝

Interactive Mode - Type 'help' for commands

sentinel-ip> help

Available Commands:
  block <ip> [<ip2> ...]     - Block one or more IPs
  unblock <ip> [<ip2> ...]   - Unblock one or more IPs
  list                       - List all blocked IPs
  check <ip>                 - Check if an IP is blocked
  flush                      - Remove all blocks (dangerous!)
  help                       - Show this help
  exit / quit / q            - Exit interactive mode

sentinel-ip> list
╔════════════════════════════════════════════════════════╗
║          SENTINEL IP MANAGER - CLI TOOL                ║
║        Block/Unblock IPs from Command Line             ║
╚════════════════════════════════════════════════════════╝

=== UFW BLOCKED IPs ===
ℹ Found 3 blocked IPs in UFW:
  1. 203.0.113.10
  2. 203.0.113.20
  3. 198.51.100.50

sentinel-ip> check 203.0.113.10
╔════════════════════════════════════════════════════════╗
║          SENTINEL IP MANAGER - CLI TOOL                ║
║        Block/Unblock IPs from Command Line             ║
╚════════════════════════════════════════════════════════╝
ℹ IP 203.0.113.10 is BLOCKED by: UFW

sentinel-ip> block 192.0.2.100
╔════════════════════════════════════════════════════════╗
║          SENTINEL IP MANAGER - CLI TOOL                ║
║        Block/Unblock IPs from Command Line             ║
╚════════════════════════════════════════════════════════╝
ℹ Attempting to block 1 IP(s)...

✓ Blocked 192.0.2.100 using UFW

ℹ Results: 1 blocked, 0 failed

sentinel-ip> exit
ℹ Goodbye!
```

---

## 🔐 Permissions

The tool requires **sudo** to modify firewall rules.

### **Option 1: Run with sudo** (simpler)
```bash
sudo python3 ip_manager_cli.py block 1.2.3.4
```

### **Option 2: Passwordless sudo** (more convenient)
For automated scripts or frequent use:

```bash
sudo visudo
```

Add this line:
```
ubuntu ALL=(ALL) NOPASSWD: /usr/sbin/ufw, /usr/sbin/iptables
```

Then you can run without password:
```bash
python3 ip_manager_cli.py block 1.2.3.4
```

---

## 📊 Comparison with Existing Tools

| Tool | Purpose | Best For |
|------|---------|----------|
| **ip_manager_cli.py** (NEW!) | Manual IP management | Quick blocks, scripting, automation |
| **web_dashboard.py** | Visual monitoring + IP management | Analysis, visualization, reports |
| **clear_database.py** | Database cleanup | Data management |
| **view_attacks.py** | Attack viewing | Incident review |
| **main.py** | Automated detection + blocking | Production monitoring |

---

## 🎉 Benefits

### **For System Administrators:**
- ⚡ **Faster than web interface** for quick blocks
- 🔄 **Scriptable** for automation
- 📦 **Batch operations** for bulk management
- 💻 **Works over SSH** without X11/GUI

### **For Security Teams:**
- 🛡️ **Emergency response** capability
- 📝 **Audit trail** with reason codes
- 🔍 **Quick IP checks** during investigations
- 📊 **Integration** with existing workflows

### **For Developers:**
- 🐍 **Python-based** (easy to modify)
- 📖 **Well-documented** code
- 🔌 **Easy to integrate** into other tools
- 🧪 **No dependencies** beyond stdlib

---

## 📖 Documentation

**Complete documentation available:**
- **Quick Reference:** This file
- **Detailed Guide:** [IP_MANAGER_CLI_GUIDE.md](IP_MANAGER_CLI_GUIDE.md)
- **README Section:** [README.md - IP Manager CLI](README.md#-ip-manager-cli-new)

---

## ✅ Testing Status

**Tested on:**
- ✅ Ubuntu 22.04 LTS
- ✅ With UFW firewall
- ✅ Basic operations (block, unblock, list, check)
- ✅ Interactive mode
- ✅ Batch operations

**Known to work with:**
- UFW (Ubuntu Uncomplicated Firewall)
- iptables (direct)

---

## 🔄 Integration Examples

### **1. Block Top Attackers from Database**
```bash
sqlite3 ~/Project/data/sentinel_intel.db \
  "SELECT DISTINCT source_ip FROM incidents WHERE severity='HIGH' LIMIT 10" | \
  xargs sudo python3 ~/Project/ip_manager_cli.py block --reason "Top attacker"
```

### **2. Block IPs from Log File**
```bash
grep "Failed password" /var/log/auth.log | \
  grep -oP '(\d{1,3}\.){3}\d{1,3}' | \
  sort -u | \
  xargs sudo python3 ~/Project/ip_manager_cli.py block --reason "SSH brute force"
```

### **3. Scheduled Block Review**
```bash
# Add to crontab
# Review and cleanup blocks every Sunday at 2 AM
0 2 * * 0 sudo python3 ~/Project/ip_manager_cli.py list > /tmp/blocked_ips_$(date +\%Y\%m\%d).txt
```

---

## 🚀 Future Enhancements

Potential improvements (not yet implemented):
- [ ] Database integration (log blocks to Sentinel DB)
- [ ] Temporary blocks with auto-expiry
- [ ] Import/export block lists
- [ ] Integration with threat intelligence feeds
- [ ] Web API endpoint for remote management
- [ ] Whitelist management
- [ ] Block statistics and reports

---

## 📞 Support

**Documentation:**
- Guide: `IP_MANAGER_CLI_GUIDE.md`
- README: See "IP Manager CLI" section
- Help: Run `python3 ip_manager_cli.py` and type `help`

**Location:**
- Local: `c:\Users\kchan\OneDrive\Desktop\6 sem\AIML\Project\ip_manager_cli.py`
- Server: `~/Project/ip_manager_cli.py`

---

## 🎯 Summary

**Added:** Standalone CLI tool for IP blocking/unblocking  
**Type:** Python script (no dependencies)  
**Size:** 17 KB (400+ lines)  
**Status:** ✅ Fully functional and documented  
**Location:** `~/Project/ip_manager_cli.py`  
**Guide:** `~/Project/IP_MANAGER_CLI_GUIDE.md`  

**Key Benefit:** Now you can block/unblock IPs directly from the Linux command line without using the web dashboard! 🎉

---

**Created:** 2026-02-25  
**Version:** 1.0  
**Status:** 🟢 Production Ready
