# 🎨 Sentinel Agent Dashboard Guide

Complete guide to running both web and CLI dashboards for monitoring your security system.

---

## 🚀 Quick Start (5 Minutes)

### **If System Already Running (Docker):**

```bash
# Option 1: Web Dashboard (browser-based)
# Already running automatically at:
http://192.168.31.91:8501
# Login: sentinel/sentinel

# Option 2: CLI Dashboard (terminal-based)
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Option 3: Both at the same time (multiple terminals)
# Terminal 1: Web dashboard (already running)
# Terminal 2: CLI dashboard
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py
# Terminal 3: Logs
docker-compose logs -f sentinel-agent | grep -E "(HIGH|ALERT)"
```

---

## 🌐 Web Dashboard (Streamlit)

### **What It Is:**
- Browser-based graphical interface
- Real-time metrics and charts
- Interactive IP management
- Responsive design (works on mobile)
- Professional dark theme

### **How to Start:**

#### **Method 1: Via Docker (Recommended)**

```bash
# Already running with main system
# Just open your browser:
http://192.168.31.91:8501

# Or if on same machine:
http://localhost:8501

# Login with:
Username: sentinel
Password: sentinel
```

#### **Method 2: Standalone on Your PC/Laptop**

```bash
# 1. Clone the project
git clone https://github.com/chandan5615/Project.git
cd Project

# 2. Install dependencies
pip install -r requirements.txt
# or just dashboards:
pip install streamlit pandas plotly rich requests

# 3. Copy database from server (optional, creates demo data locally)
mkdir -p data
scp ubuntu@192.168.31.91:~/Project/data/sentinel_intel.db ./data/

# 4. Run dashboard
streamlit run dashboard/web_dashboard.py

# 5. Opens automatically in browser:
# http://localhost:8501
```

#### **Method 3: SSH Tunnel (From Anywhere)**

```bash
# Terminal 1: Create SSH tunnel
ssh -L 8501:localhost:8501 ubuntu@192.168.31.91

# Terminal 2: Open browser
# http://localhost:8501

# Now you can access dashboard from any network!
```

### **Features:**

#### **Dashboard Home:**
- Security score (% safe)
- Total threats detected
- Incidents this hour
- System status indicator
- Real-time threat feed

#### **Metrics Tab:**
- 📊 Attacks over time (line chart)
- 📊 Attack types distribution (pie chart)
- 📊 Severity breakdown (stacked bar)
- 📊 Top 10 attackers (bar chart)

#### **IP Management Tab:**
- View all blocked IPs
- View whitelist
- Add new IPs to whitelist
- Unblock previously blocked IPs
- Edit IP notes/descriptions

#### **Logs Tab:**
- All incident logs
- Filter by severity
- Filter by attack type
- Search by IP
- Download as CSV

#### **Settings Tab:**
- Change password
- Configure refresh interval
- Export data
- System configuration

### **Keyboard Shortcuts:**
| Key | Action |
|-----|--------|
| `R` | Refresh all data |
| `I` | Jump to IP Management |
| `L` | Jump to Logs |
| `M` | Jump to Metrics |
| `S` | Jump to Settings |
| `?` | Show help |

### **Configuration:**

```bash
# Create .env file in project root:
DASHBOARD_PORT=8501
DASHBOARD_USER=sentinel
DASHBOARD_PASS=sentinel
DASHBOARD_THEME=dark          # or 'light'
DASHBOARD_REFRESH=8           # seconds
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
```

---

## 💻 CLI Dashboard (Rich Terminal UI)

### **What It Is:**
- Terminal-based text interface
- Perfect for SSH sessions
- Live updates every 5 seconds
- Minimal bandwidth requirement
- No authentication needed
- Color-coded for quick scanning

### **How to Start:**

#### **Method 1: From Server via SSH**

```bash
# SSH into server
ssh ubuntu@192.168.31.91

# Navigate to project
cd ~/Project

# Run CLI dashboard
python3 dashboard/cli_dashboard.py

# Press Ctrl+C to exit
```

#### **Method 2: Inside Docker Container**

```bash
# Interactive terminal inside container
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Auto-refreshes with live incident data
# Press Ctrl+C to exit
```

#### **Method 3: Remote SSH Execution**

```bash
# Run from your PC, output streams to your terminal
ssh ubuntu@192.168.31.91 "cd ~/Project && python3 dashboard/cli_dashboard.py"

# Works great with tmux or screen for persistent sessions
tmux new-session -d -s sentinel sudo sshubuntu@192.168.31.91 \
  "cd ~/Project && python3 dashboard/cli_dashboard.py"

# Later, attach to session:
tmux attach -t sentinel
```

### **Display Layout:**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SENTINEL AGENT DASHBOARD - CLI MODE                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🔴 SECURITY STATE: CRITICAL (5 HIGH severity incidents)                   ║
║  📊 Updates: Every 5 seconds  |  Database: sentinel_intel.db               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ RECENT INCIDENTS (Last 24 Hours)                                            ║
╠════════════════┬──────────────┬──────────────┬────────┬────────────────────╣
║ Time           │ IP Address   │ Attack Type  │ Status │ Details            ║
╠════════════════┼──────────────┼──────────────┼────────┼────────────────────╣
║ 2026-02-22     │ 192.168.1.50 │ SQL Inject   │ Blocked│ admin' OR '1'='1   ║
║ 14:45:23       │              │              │        │                    ║
╠────────────────┼──────────────┼──────────────┼────────┼────────────────────╣
║ 2026-02-22     │ 10.0.0.100   │ XSS          │ Blocked│ <script>alert(...)║
║ 14:43:12       │              │              │        │                    ║
╠────────────────┼──────────────┼──────────────┼────────┼────────────────────╣
║ 2026-02-22     │ 203.0.113.45 │ SSH Brute    │ Blocked│ Failed attempts: 5 ║
║ 14:40:56       │              │              │        │                    ║
╚════════════════┴──────────────┴──────────────┴────────┴────────────────────╝

╠══════════════════════════════════════════════════════════════════════════════╣
║ TOP ATTACKERS (This Week)                                                   ║
╠════════════════┬────────┬──────────────────────────────────────────────────╣
║ IP Address     │ Count  │ Last Seen (Latest Attack)                        ║
╠════════════════┼────────┼──────────────────────────────────────────────────╣
║ 192.168.1.50   │   27   │ 14:45 SQL Injection attempt                      ║
║ 203.0.113.45   │   15   │ 14:40 SSH brute force                            ║
║ 10.0.0.100     │   12   │ 14:43 XSS payload                                ║
║ 172.16.0.5     │    8   │ 14:30 Path traversal                             ║
║ 192.0.2.200    │    5   │ 14:15 Directory scan                             ║
╚════════════════┴────────┴──────────────────────────────────────────────────╝

╠══════════════════════════════════════════════════════════════════════════════╣
║ ATTACK TYPES SUMMARY                                                         ║
║                                                                              ║
║  SQL Injection:    ████████████░░░░░ 12  |  40%  🔴 HIGH                  ║
║  Brute Force:      ████████░░░░░░░░░ 8   |  27%  🟡 MEDIUM                ║
║  XSS Attacks:      ██████░░░░░░░░░░░ 6   |  20%  🟡 MEDIUM                ║
║  Path Traversal:   ███░░░░░░░░░░░░░░ 3   |  10%  🟡 MEDIUM                ║
║  Other:            ░░░░░░░░░░░░░░░░░ 1   |  3%   🟢 LOW                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ SYSTEM RESOURCES                                                             ║
║                                                                              ║
║  CPU Usage:    ▓▓▓▓░░░░░░ 42%  |  Memory: ▓▓▓▓▓░░░░░ 52%  |  Disk: 68%  ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Status: ✓ Connected | Refresh: 5 seconds | Next update: 4s                ║
║ Press Ctrl+C to exit                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### **Keyboard Controls:**

| Key | Action |
|-----|--------|
| `Q` | Quit dashboard |
| `Ctrl+C` | Exit (also works) |
| `F5` | Force refresh |
| `C` | Clear screen |
| `S` | Sort by (time/IP/type) |
| `?` | Show help |

### **Features:**

✅ **Real-time Updates** - Every 5 seconds automatically  
✅ **Color Coding** - Red (HIGH), Yellow (MEDIUM), Cyan (LOW)  
✅ **Top Attackers** - Ranked by incident count  
✅ **Attack Statistics** - Types, frequencies, patterns  
✅ **System Monitoring** - CPU, Memory, Disk usage  
✅ **Anti-Spam** - Avoids duplicate alerts  
✅ **Size-Aware** - Adapts to terminal size  
✅ **No Auth** - Direct access, no login needed  

### **Configuration:**

```bash
# Environment variables
CLI_REFRESH_INTERVAL=5           # seconds between updates
CLI_MAX_INCIDENTS=20             # rows to show
CLI_SHOW_STATS=true              # show statistics
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
```

---

## 🔄 Running Multiple Dashboards

### **Scenario 1: Web + CLI Monitoring**

```bash
# Terminal 1: SSH into server
ssh ubuntu@192.168.31.91
cd ~/Project

# Terminal 2: Open web dashboard in browser
# http://192.168.31.91:8501

# Terminal 3: Run CLI dashboard
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Terminal 4: Monitor raw logs
docker-compose logs -f sentinel-agent | grep -E "(HIGH|BLOCKED|ALERT)"

# Now you have:
# - Visual dashboard in browser
# - Live terminal updates in CLI
# - Raw logs in separate terminal
```

### **Scenario 2: Headless Server (SSH Only)**

```bash
# All from terminal, no browser needed
ssh ubuntu@192.168.31.91

# Run CLI dashboard
cd ~/Project
python3 dashboard/cli_dashboard.py

# In another SSH terminal:
# Monitor logs in real-time
docker-compose logs -f sentinel-agent | tail -50

# In a third SSH terminal:
# Check API directly
curl http://localhost:8000/api/health
```

### **Scenario 3: Full Stack Development**

```bash
# Terminal 1: API Server
docker-compose up -d

# Terminal 2: Web Dashboard
streamlit run dashboard/web_dashboard.py --logger.level=debug

# Terminal 3: CLI Dashboard
python3 dashboard/cli_dashboard.py

# Terminal 4: Test attacks
python3 test_web_attacks.py --burst 5

# Now develop/test with all views active
```

---

## 🔐 Security Notes

### **Authentication:**
- **Web Dashboard**: Requires HTTP Basic Auth (username/password)
- **CLI Dashboard**: No auth (terminal access required)
- **API**: Basic auth on endpoints
- **Credentials**: `sentinel/sentinel` (change in .env)

### **Network Access:**
- **Web**: Bound to `192.168.31.91` (local network only)
- **CLI**: Local terminal access only
- **API**: `192.168.31.91:8000` (local network only)

### **Best Practices:**
1. Change default credentials in production
2. Use SSH key auth instead of password
3. Run dashboards behind VPN or firewall
4. Rotate credentials regularly
5. Monitor audit logs

---

## 🐛 Troubleshooting

### **Dashboard Not Loading**

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs sentinel-agent

# Restart container
docker-compose restart sentinel-agent

# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **CLI Dashboard Shows No Data**

```bash
# Check database exists
ls -la ~/Project/data/sentinel_intel.db

# Generate test data
python3 test_web_attacks.py

# Check database connection
sqlite3 ~/Project/data/sentinel_intel.db "SELECT COUNT(*) FROM incidents;"

# Check permissions
chmod 666 ~/Project/data/sentinel_intel.db
```

### **Web Dashboard Slow**

```bash
# Check resources
docker stats sentinel-agent

# Clear old data
sqlite3 ~/Project/data/sentinel_intel.db "DELETE FROM incidents WHERE timestamp < datetime('now', '-30 days');"

# Rebuild index
sqlite3 ~/Project/data/sentinel_intel.db "VACUUM; ANALYZE;"
```

### **Can't Connect to Remote Dashboard**

```bash
# Check if port is open
sudo netstat -tlnp | grep 8501

# Check firewall
sudo ufw status

# SSH tunnel instead
ssh -L 8501:localhost:8501 ubuntu@192.168.31.91

# Then use:
# http://localhost:8501
```

---

## 📊 Dashboard Comparison

| Feature | Web Dashboard | CLI Dashboard |
|---------|:----------:|:----------:|
| **Interface** | Graphical (Streamlit) | Terminal (Rich TUI) |
| **Refresh Rate** | 8 seconds | 5 seconds |
| **IP Management** | ✅ Interactive | ❌ View only |
| **Charts** | ✅ Interactive | ❌ Table-based |
| **Mobile Friendly** | ✅ Yes | ❌ No |
| **SSH Access** | ❌ Needs browser | ✅ Full support |
| **Bandwidth** | ~500KB/refresh | ~10KB/refresh |
| **Authentication** | ✅ Basic auth | ❌ Terminal auth |
| **Dark Theme** | ✅ Yes | ✅ Default |
| **Export Data** | ✅ CSV/JSON | ✅ Copy/Paste |
| **Performance** | 🟡 Medium | 🟢 Lightweight |
| **Settings** | ✅ UI Configurable | ✅ Env variables |

---

## 📚 Additional Resources

- **Dashboard Code**: `dashboard/` directory
- **API Docs**: `http://192.168.31.91:8000/docs`
- **Configuration**: `docker-compose.yml` & `.env`
- **Database**: `data/sentinel_intel.db` (SQLite3)
- **Logs**: `docker-compose logs -f`

---

**💡 Tip:** Use web dashboard for presentations and monitoring, use CLI dashboard for daily terminal work!
