# Sentinel Agent Dashboard - Enhanced Features

## 🎉 New Features Added

### 1. 📄 Log File Viewer
**Tab: Log Viewer**

- **Real-time log viewing** from multiple sources
- **Supported logs:**
  - Auth Log (`/var/log/auth.log`)
  - Apache Access Log (`/var/log/apache2/access.log`)
  - Custom log paths
- **Features:**
  - Tail last N lines (10-500 configurable)
  - Search/filter log content
  - Download log content as text file
  - Real-time updates

**Usage:**
1. Select log file type from dropdown
2. Adjust number of lines to display
3. Use search box to filter specific patterns
4. Download filtered results if needed

---

### 2. 🌐 Apache Server Traffic Analysis
**Tab: Apache Traffic**

- **Comprehensive traffic monitoring**
- **Metrics displayed:**
  - Total requests
  - Unique IP addresses
  - Error count (4xx/5xx)
  - Error rate percentage
  - HTTP status code distribution
  - HTTP method usage (GET, POST, etc.)
  - Top client IPs
  - Most requested URLs
  - User agent statistics
  - Recent error requests details

**Features:**
- Configurable log path
- Adjustable analysis window (100-10,000 lines)
- Parse Apache Combined Log Format
- Real-time analysis on button click
- Detailed error request breakdown

**Usage:**
1. Enter Apache access.log path (default: `/var/log/apache2/access.log`)
2. Set number of log lines to analyze
3. Click "Analyze Traffic" button
4. Review comprehensive statistics and charts

---

### 3. 🚫 IP Blocking/Unblocking Controls
**Tab: IP Blocking**

- **Manual IP management** with firewall integration
- **Supported firewalls:**
  - UFW (Uncomplicated Firewall)
  - iptables

**Features:**
- Block IP addresses manually
- Unblock IP addresses
- View currently blocked IPs
- IP address validation
- Real-time firewall rule updates
- Support for both UFW and iptables

**Usage:**

**To Block an IP:**
1. Select firewall type (UFW or iptables)
2. Enter IP address in "Block New IP" field
3. Click "Block IP" button
4. Confirmation message shows success/failure

**To Unblock an IP:**
1. Enter IP address in "Unblock IP" field
2. Click "Unblock IP" button
3. Confirmation message shows success/failure

**To View Blocked IPs:**
1. Click "Refresh Blocked IPs List" button
2. View table of currently blocked IPs with firewall type

**Requirements:**
- Sudo privileges for firewall commands
- UFW or iptables installed
- May require passwordless sudo or manual password entry

---

### 4. 🎯 Attack Patterns Analysis
**Tab: Attack Patterns**

- **Visualize attack trends** over time
- **Analysis features:**
  - Attack types distribution (last 7 days)
  - Hourly attack patterns (last 24 hours)
  - Bar charts and line graphs
  - Automatic pattern detection

**Insights:**
- Identify most common attack types
- Detect attack time patterns
- Spot anomalies in traffic
- Plan defense strategies

---

### 5. 📊 Export Reports
**Tab: Export Reports**

- **Export security data** for analysis and archival
- **Export formats:**
  - CSV for incidents
  - JSON for threat intelligence

**Export Options:**

**Incident Reports:**
- Time ranges: Last Hour, 24 Hours, 7 Days, 30 Days, All Time
- Format: CSV
- Includes all incident fields

**Threat Intelligence:**
- Export all threat intel data
- Format: JSON
- Includes IP reputation scores and details

**Database Statistics:**
- Total incidents count
- Total actions count
- Threat intelligence records
- Database file size (MB)

**Usage:**
1. Select time range for incident export
2. Click export button
3. Download button appears with generated file
4. Files named with timestamp for tracking

---

### 6. 💻 System Information
**Tab: System Info**

- **Monitor system health** metrics
- **Displayed information:**
  - System uptime
  - Load average (1m, 5m)
  - Disk usage (total, used, available)
  - Disk usage percentage with progress bar

**Use cases:**
- Monitor system resource usage
- Detect performance issues
- Plan capacity upgrades
- Troubleshoot system problems

---

## 🚀 Quick Start Guide

### Running the Enhanced Dashboard

**Inside Docker (Recommended):**
```bash
docker exec -it sentinel-agent streamlit run dashboard/web_dashboard.py --server.address 0.0.0.0 --server.port 8501
```

**Standalone (Development):**
```bash
streamlit run dashboard/web_dashboard.py
```

**With Custom Database:**
```bash
SENTINEL_DB_PATH=/path/to/db.sqlite streamlit run dashboard/web_dashboard.py
```

### Access URLs
- Local: `http://localhost:8501`
- LAN: `http://YOUR_SERVER_IP:8501`

---

## ⚙️ Configuration

### Environment Variables

```bash
# Database configuration
SENTINEL_DB_PATH=/app/data/sentinel_intel.db
SENTINEL_DATA_DIR=/app/data

# Log file paths
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# Dashboard settings
DASHBOARD_PORT=8501
```

### Required Permissions

For IP blocking functionality:
```bash
# Add user to sudoers for firewall commands (optional)
sudo visudo

# Add line (replace 'username'):
username ALL=(ALL) NOPASSWD: /usr/sbin/ufw, /usr/sbin/iptables
```

### Log File Access

Ensure dashboard has read access to log files:
```bash
# For Docker containers
docker run -v /var/log:/var/log:ro ...

# For host system
sudo chmod +r /var/log/auth.log
sudo chmod +r /var/log/apache2/access.log
```

---

## 📋 Feature Summary Table

| Feature | Tab | Key Capabilities | Requirements |
|---------|-----|------------------|--------------|
| Log Viewer | 📄 Log Viewer | Tail, search, download logs | Read access to log files |
| Apache Traffic | 🌐 Apache Traffic | Traffic stats, error analysis | Apache access.log file |
| IP Blocking | 🚫 IP Blocking | Block/unblock IPs | Sudo, UFW/iptables |
| Attack Patterns | 🎯 Attack Patterns | Visualize attack trends | Database with incidents |
| Export Reports | 📊 Export Reports | CSV/JSON exports | Database access |
| System Info | 💻 System Info | Uptime, load, disk usage | /proc filesystem access |

---

## 🔒 Security Considerations

### IP Blocking
- IP blocking requires sudo privileges
- All blocks are logged in firewall rules
- Use caution when blocking IPs (verify first!)
- Blocked IPs can cause legitimate traffic loss

### Log Access
- Dashboard reads logs in read-only mode
- No log file modifications
- Sensitive data may be visible in logs
- Restrict dashboard access appropriately

### System Commands
- Firewall commands execute with sudo
- Commands are validated before execution
- Failed commands show error messages
- Check firewall rules after changes

---

## 🐛 Troubleshooting

### Log Viewer Shows "File Not Found"
- Verify log file path exists
- Check read permissions
- For Docker: ensure volume mount includes `/var/log`

### Apache Traffic Shows "Could Not Parse"
- Verify Apache Combined Log Format
- Check log file path is correct
- Ensure log file has recent entries

### IP Blocking Fails
- Verify sudo privileges
- Check UFW/iptables is installed
- Try running firewall command manually
- Check for existing conflicting rules

### System Info Not Available
- Requires Linux `/proc` filesystem
- May not work on all systems (Windows, macOS)
- Normal behavior on non-Linux platforms

---

## 📝 Usage Examples

### Example 1: Investigating Suspicious IPs
1. Go to "Wall of Shame" tab - find suspicious IP
2. Check "Apache Traffic" tab - verify requests from that IP
3. Review "Log Viewer" - search for IP in auth.log
4. Go to "IP Blocking" tab - block the IP
5. Export data from "Export Reports" for records

### Example 2: Analyzing Attack Patterns
1. Check "Attack Patterns" tab for trends
2. Review "Incident Feed" for recent attacks
3. Check "Apache Traffic" for error patterns
4. Export incident report for analysis
5. Block recurring attacker IPs

### Example 3: System Health Check
1. Review "System Info" for resource usage
2. Check "Network Health" for traffic spikes
3. Review "Database Statistics" for growth
4. Export reports for historical tracking
5. Plan capacity if needed

---

## 🎯 Best Practices

1. **Regular Monitoring:** Check dashboard daily for new threats
2. **Export Reports:** Backup incident data weekly
3. **Verify Before Blocking:** Check logs before blocking IPs
4. **Monitor System Resources:** Watch disk and memory usage
5. **Review Attack Patterns:** Identify trends and adjust defenses
6. **Test Firewall Rules:** Verify blocks work as expected
7. **Keep Logs Rotating:** Prevent disk space issues
8. **Document Actions:** Export reports when blocking IPs

---

## 🔄 Updates and Maintenance

### Dashboard Updates
- All features auto-refresh based on sidebar settings
- Click refresh buttons for on-demand updates
- Database updates reflect immediately
- Firewall changes require manual refresh

### Data Retention
- Incidents stored in SQLite database
- Logs managed by system log rotation
- Export old data before cleanup
- Monitor database size growth

---

## 📚 Additional Resources

### Related Files
- `web_dashboard.py` - Main dashboard code
- `clear_database.py` - Database cleanup utility
- `README.md` - Project documentation
- `docker-compose.yml` - Container configuration

### Log Formats
- **Apache Combined Log:** Standard web server format
- **Auth Log:** System authentication events
- **Sentinel Database:** SQLite custom schema

### Firewall Tools
- **UFW:** Ubuntu's simplified firewall
- **iptables:** Linux kernel firewall
- Both supported for IP blocking

---

## ✨ Feature Highlights

- **9 Comprehensive Tabs** with specialized views
- **Real-time Monitoring** with auto-refresh
- **Export Capabilities** for reporting and archival  
- **Manual IP Control** for immediate threat response
- **Traffic Analysis** for Apache web servers
- **Attack Visualization** for pattern detection
- **System Health** monitoring integration
- **Log Management** with search and filter

---

**Dashboard Version:** 2.0 (Enhanced)  
**Last Updated:** February 2026  
**Sentinel Agent:** v2.2+
