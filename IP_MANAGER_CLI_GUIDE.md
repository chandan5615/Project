# 🛡️ IP Manager CLI - Quick Reference Guide

**Standalone command-line tool for managing IP blocks on Linux servers**

---

## 📥 Installation

The tool is already installed at: `~/Project/ip_manager_cli.py`

Make it executable (already done):
```bash
chmod +x ~/Project/ip_manager_cli.py
```

---

## 🚀 Quick Start

### **Interactive Mode** (Recommended for beginners)
```bash
python3 ~/Project/ip_manager_cli.py
```

Then use commands like:
```
sentinel-ip> block 1.2.3.4
sentinel-ip> unblock 1.2.3.4
sentinel-ip> list
sentinel-ip> check 1.2.3.4
sentinel-ip> help
sentinel-ip> exit
```

---

## 📋 Command-Line Usage

### **Block a Single IP**
```bash
python3 ~/Project/ip_manager_cli.py block 1.2.3.4
```

### **Block Multiple IPs at Once**
```bash
python3 ~/Project/ip_manager_cli.py block 1.2.3.4 5.6.7.8 9.10.11.12
```

### **Block with Reason/Comment**
```bash
python3 ~/Project/ip_manager_cli.py block 1.2.3.4 --reason "Brute force attack"
```

### **Unblock a Single IP**
```bash
python3 ~/Project/ip_manager_cli.py unblock 1.2.3.4
```

### **Unblock Multiple IPs**
```bash
python3 ~/Project/ip_manager_cli.py unblock 1.2.3.4 5.6.7.8
```

### **List All Blocked IPs**
```bash
python3 ~/Project/ip_manager_cli.py list
```

### **List Blocked IPs (UFW only)**
```bash
python3 ~/Project/ip_manager_cli.py list
# Shows both UFW and iptables blocked IPs
```

### **Check if an IP is Blocked**
```bash
python3 ~/Project/ip_manager_cli.py check 1.2.3.4
```

### **Remove ALL Blocks** ⚠️ DANGEROUS!
```bash
python3 ~/Project/ip_manager_cli.py flush
```

---

## 🎯 Common Use Cases

### **Scenario 1: Block an Attacker IP**
```bash
# Check if already blocked
python3 ~/Project/ip_manager_cli.py check 203.0.113.50

# Block it
python3 ~/Project/ip_manager_cli.py block 203.0.113.50 --reason "SQL injection attempts"

# Verify it's blocked
python3 ~/Project/ip_manager_cli.py list
```

### **Scenario 2: Unblock a False Positive**
```bash
# Check status
python3 ~/Project/ip_manager_cli.py check 192.168.1.100

# Unblock if needed
python3 ~/Project/ip_manager_cli.py unblock 192.168.1.100

# Verify it's unblocked
python3 ~/Project/ip_manager_cli.py check 192.168.1.100
```

### **Scenario 3: Block Multiple IPs from Attack List**
```bash
# Block all at once
python3 ~/Project/ip_manager_cli.py block \
  203.0.113.10 \
  203.0.113.20 \
  203.0.113.30 \
  203.0.113.40 \
  --reason "Coordinated DDoS attack"
```

### **Scenario 4: View All Currently Blocked IPs**
```bash
python3 ~/Project/ip_manager_cli.py list
```

### **Scenario 5: Interactive Management Session**
```bash
# Start interactive mode
python3 ~/Project/ip_manager_cli.py

# Then use commands:
sentinel-ip> list
sentinel-ip> check 1.2.3.4
sentinel-ip> block 5.6.7.8
sentinel-ip> unblock 1.2.3.4
sentinel-ip> exit
```

---

## 🔧 Features

✅ **Dual Firewall Support**
- Works with both UFW and iptables
- Automatically detects which firewall is available
- Can use both simultaneously

✅ **IP Validation**
- Validates IP address format before blocking
- Prevents invalid entries
- Checks for existing blocks

✅ **Batch Operations**
- Block/unblock multiple IPs in one command
- Faster than Web dashboard for bulk operations

✅ **Color-Coded Output**
- ✓ Green for success
- ✗ Red for errors
- ⚠ Yellow for warnings
- ℹ Blue for information

✅ **Interactive Mode**
- User-friendly command prompt
- Built-in help system
- Command history support

✅ **Reason/Comment Support**
- Add comments when blocking IPs
- Track why IPs were blocked
- Useful for auditing

---

## 💡 Tips & Tricks

### **Create an Alias for Easy Access**
Add to your `~/.bashrc`:
```bash
echo "alias ipblock='python3 ~/Project/ip_manager_cli.py'" >> ~/.bashrc
source ~/.bashrc
```

Then use:
```bash
ipblock block 1.2.3.4
ipblock list
ipblock unblock 1.2.3.4
```

### **Block from Database Query**
Combine with database queries to block top attackers:
```bash
# Get top 5 attacking IPs from database
sqlite3 ~/Project/data/sentinel_intel.db \
  "SELECT DISTINCT source_ip FROM incidents 
   WHERE severity='HIGH' 
   ORDER BY timestamp DESC 
   LIMIT 5" | \
  xargs python3 ~/Project/ip_manager_cli.py block
```

### **Scheduled Cleanup**
Add to crontab to automatically flush old blocks:
```bash
# Flush blocks every Sunday at 2 AM
0 2 * * 0 python3 ~/Project/ip_manager_cli.py flush
```

### **Block from Log File**
Extract IPs from logs and block them:
```bash
# Example: Block all IPs with failed SSH attempts
grep "Failed password" /var/log/auth.log | \
  grep -oP '(\d{1,3}\.){3}\d{1,3}' | \
  sort -u | \
  xargs python3 ~/Project/ip_manager_cli.py block --reason "SSH brute force"
```

---

## 🆚 CLI Tool vs Web Dashboard

| Feature | CLI Tool | Web Dashboard |
|---------|----------|---------------|
| **Speed** | ⚡ Very fast | Moderate |
| **Batch operations** | ✅ Easy | Limited |
| **Remote access** | SSH only | Web browser |
| **Scriptable** | ✅ Yes | No |
| **Interactive** | ✅ Yes | ✅ Yes |
| **Visual feedback** | Text/Colors | Charts/Tables |
| **Best for** | Admins, scripts | Monitoring, analysis |

---

## 🔐 Permissions

**This tool requires sudo access** to modify firewall rules.

### **Setup Passwordless Sudo for Firewall Commands** (Optional)

For convenience, allow passwordless sudo for firewall commands:

```bash
sudo visudo
```

Add this line:
```
ubuntu ALL=(ALL) NOPASSWD: /usr/sbin/ufw, /usr/sbin/iptables
```

This allows the tool to run without password prompts.

---

## 🐛 Troubleshooting

### **"No firewall available" Error**
```bash
# Install UFW
sudo apt update
sudo apt install ufw -y
sudo ufw enable

# OR check if iptables is installed
sudo iptables -L
```

### **"Permission denied" Error**
```bash
# Run with sudo if needed
sudo python3 ~/Project/ip_manager_cli.py block 1.2.3.4
```

### **Check Firewall Status**
```bash
# UFW status
sudo ufw status numbered

# iptables status
sudo iptables -L -n -v
```

### **Verify IP is Actually Blocked**
```bash
# Try to ping from blocked IP
ping <your-server-ip>  # Should fail

# Or check with the tool
python3 ~/Project/ip_manager_cli.py check <IP>
```

---

## 📊 Integration with Sentinel

### **Block IPs from Dashboard Incidents**
```bash
# View recent attacks
python3 ~/Project/view_attacks.py --severity HIGH --limit 10

# Block specific IP from incidents
python3 ~/Project/ip_manager_cli.py block 203.0.113.50
```

### **Automated Blocking from Database**
Create a script to auto-block repeat offenders:
```bash
#!/bin/bash
# auto_block_top_attackers.sh

# Get IPs with more than 10 incidents
sqlite3 ~/Project/data/sentinel_intel.db \
  "SELECT source_ip, COUNT(*) as cnt FROM incidents 
   GROUP BY source_ip 
   HAVING cnt > 10" | \
  awk -F'|' '{print $1}' | \
  xargs python3 ~/Project/ip_manager_cli.py block --reason "Repeat offender (10+ incidents)"
```

---

## 📝 Example Session

```bash
ubuntu@sentinel:~/Project$ python3 ip_manager_cli.py
╔════════════════════════════════════════════════════════╗
║          SENTINEL IP MANAGER - CLI TOOL                ║
║        Block/Unblock IPs from Command Line             ║
╚════════════════════════════════════════════════════════╝

Interactive Mode - Type 'help' for commands

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

## ⚡ Advanced Usage

### **Combine with grep/awk/sed**
```bash
# Block all Chinese IPs from a range
for ip in 220.181.108.{1..255}; do
  python3 ~/Project/ip_manager_cli.py block $ip --reason "Suspicious Chinese IP range"
done
```

### **Export Blocked IPs to File**
```bash
python3 ~/Project/ip_manager_cli.py list > blocked_ips.txt
```

### **Import IPs from File**
```bash
cat blacklist.txt | xargs python3 ~/Project/ip_manager_cli.py block
```

### **Unblock All IPs Matching Pattern**
```bash
# Unblock all IPs from 192.168.x.x
python3 ~/Project/ip_manager_cli.py list | \
  grep "192.168." | \
  xargs python3 ~/Project/ip_manager_cli.py unblock
```

---

## 📞 Support

- **Tool location**: `~/Project/ip_manager_cli.py`
- **Documentation**: This file (`IP_MANAGER_CLI_GUIDE.md`)
- **Main documentation**: `~/Project/README.md`

---

## ✅ Summary

The IP Manager CLI provides a **fast, scriptable, and user-friendly** way to manage IP blocks directly from the Linux command line without needing to use the web dashboard.

**Key Benefits:**
- ⚡ **Faster** than web interface
- 🔄 **Scriptable** for automation
- 📦 **Batch operations** support
- 🎨 **Color-coded** output
- 💻 **Interactive mode** available
- 🔧 **Works with UFW and iptables**

**Best for:**
- System administrators
- Automated scripts
- Bulk IP management
- SSH-only access situations
- Quick manual blocks/unblocks

---

**Happy blocking! 🛡️**
