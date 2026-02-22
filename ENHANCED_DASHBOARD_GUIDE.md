# Enhanced Sentinel Dashboard Guide

## 🎨 New Features Overview

The Sentinel dashboard has been completely redesigned with powerful new features for comprehensive security monitoring and management.

## ✨ Features Added

### 1. **Detailed Log Viewing** 📋
- View complete log details for each incident
- Raw log display with timestamp and context
- Filter logs by severity (High/Medium/Low)
- Monospace formatting for easy reading
- Color-coded severity indicators

### 2. **IP Address Management** 🚫
- **Block IPs**: Click to instantly blacklist malicious IPs
- **Unblock IPs**: Remove IPs from blacklist with one click
- Visual IP badges showing blocked/whitelisted status
- Bulk management interface
- Reason tracking for blocked IPs

### 3. **Real-Time Traffic Monitoring** 📊
- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption tracking
- **Disk Usage**: Storage monitoring
- **Network Traffic**: Bytes sent/received
- **Active Connections**: Current network connections count
- Visual gauge bars with color coding
- Auto-refresh every 5 seconds

### 4. **Enhanced Analytics** 📈
- Total incidents counter
- High-severity alerts tracker
- Recent activity (last hour)
- Active network connections
- Top attack types visualization
- Top attacker IPs ranking
- Attack timeline trends

### 5. **Modern UI/UX** 🎨
- Beautiful gradient design
- Responsive card layout
- Smooth animations
- Color-coded severity levels
- Font Awesome icons
- Real-time status indicators
- Professional dark theme accents

### 6. **Additional Features** ⚡
- Auto-refresh every 10 seconds
- WebSocket real-time updates
- Interactive Plotly charts
- Severity filtering
- One-click IP blocking from incident table
- HTTP Basic Authentication
- Sticky table headers
- Smooth transitions and hover effects

---

## 🚀 Access the Dashboard

### URL:
```
http://192.168.31.91:8501
```

### Credentials:
```
Username: sentinel
Password: sentinel
```

*(Set via environment variables `DASHBOARD_USER` and `DASHBOARD_PASS`)*

---

## 📊 Dashboard Sections

### **Header Stats**
- **Total Incidents**: All-time incident count
- **Blocked IPs**: Currently blacklisted addresses
- **High Severity**: Critical threats detected

### **Metric Cards** (Top Row)
1. **Incidents (Last Hour)**: Recent activity indicator
2. **Active Connections**: Current network traffic
3. **CPU Usage**: Server processor load
4. **Memory Usage**: RAM utilization

### **Server Traffic & Resources**
Real-time monitoring with visual gauge bars:
- CPU percentage
- Memory percentage  
- Disk usage
- Network bytes sent
- Network bytes received
- Manual refresh button

### **IP Address Management**
- Input field to enter IP addresses
- **Block IP** button to add to blacklist
- List of currently blocked IPs with unblock buttons
- List of whitelisted IPs
- Color-coded badges (red for blocked, purple for whitelisted)

### **Charts**
1. **Incidents Timeline**: Line chart showing attack trends over time
2. **Severity Distribution**: Donut chart of severity levels
3. **Top Attack Types**: Bar chart of most common attack vectors

### **Recent Log Details**
- Filterable by severity
- Shows complete log entries with:
  - Source IP address
  - Attack type
  - Timestamp
  - Raw log content
  - Severity badge
- Scrollable container for many logs

### **Recent Incidents Table**
- ID, Timestamp, Source IP, Attack Type, Severity
- **Action Buttons**: Quick-block malicious IPs
- Sortable and scrollable
- Color-coded severity tags

---

## 🔧 API Endpoints

### Traffic Monitoring
```http
GET /api/traffic
```
Returns CPU, memory, disk, network stats, and active connections.

### Log Details
```http
GET /api/logs?limit=100&severity=high
```
Get detailed log entries with optional severity filtering.

### Block IP
```http
POST /api/ip/block
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "reason": "Malicious activity detected"
}
```

### Unblock IP
```http
POST /api/ip/unblock
Content-Type: application/json

{
  "ip": "192.168.1.100"
}
```

### IP Status
```http
GET /api/ip/status
```
Returns lists of blacklisted and whitelisted IPs.

### Dashboard Metrics
```http
GET /api/metrics/dashboard
```
Returns comprehensive metrics for dashboard overview.

---

## 💡 Usage Examples

### Block an IP Address
1. Enter IP in the input field (e.g., `203.0.113.75`)
2. Click **Block IP** button
3. IP appears in "Blocked IPs" list
4. Confirmation alert shows success

### Unblock an IP Address
1. Find IP in "Blocked IPs" list
2. Click the × button next to the IP
3. Confirm the action
4. IP is removed from blacklist

### Filter Logs by Severity
1. Use dropdown in "Recent Log Details" section
2. Select: All Severities / High / Medium / Low
3. Logs automatically filter

### Monitor Server Health
1. View metric cards at top
2. Check "Server Traffic & Resources" section
3. Click refresh button for instant update
4. Gauge bars show current status

### Identify Top Attackers
1. Scroll to "Recent Incidents" table
2. Click "Block" button next to suspicious IPs
3. Check "Top Attack Types" chart for patterns
4. Review timeline for attack trends

---

## 🎯 Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| 🟢 Green Badge | High Severity | Critical threat |
| 🟡 Yellow Badge | Medium Severity | Moderate threat |
| 🟢 Green Badge | Low Severity | Minor issue |
| 🔴 Red IP Badge | Blocked | Blacklisted IP |
| 🟣 Purple IP Badge | Whitelisted | Trusted IP |
| 🟢 Green Dot | System Online | Dashboard active |
| 🟡 Yellow Dot | Warning | Attention needed |

---

## 🔄 Auto-Refresh Rates

- **Dashboard Metrics**: Every 10 seconds
- **Traffic Monitoring**: Every 5 seconds
- **IP Status**: Every 15 seconds
- **WebSocket Updates**: Real-time (instant)

---

## 🛡️ Security Features

- **HTTP Basic Authentication**: Username/password required
- **Internal-Only Access**: Binds to 127.0.0.1
- **Session Tokens**: Time-limited WebSocket tokens
- **HTTPS Ready**: Works with SSL/TLS
- **Credential Hiding**: No credentials in URLs

---

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop browsers (1920x1080+)
- Laptops (1366x768+)
- Tablets (iPad, Android tablets)
- Mobile devices (with horizontal scroll)

---

## 🐛 Troubleshooting

### Dashboard Not Loading
```bash
# Check if dashboard is running
docker ps | grep sentinel

# Check logs
docker logs sentinel-agent | grep dashboard

# Restart container
docker-compose restart
```

### Authentication Failing
```bash
# Verify credentials
echo $DASHBOARD_USER
echo $DASHBOARD_PASS

# Or use default: sentinel / sentinel
```

### No Data Showing
```bash
# Check if incidents exist
curl http://192.168.31.91:8000/api/incidents/recent

# Run attack tests
python3 test_web_attacks.py
```

### Traffic Gauges Not Updating
```bash
# Ensure psutil is installed
pip install psutil

# Check if psutil works
python3 -c "import psutil; print(psutil.cpu_percent())"
```

---

## 🚀 Performance Tips

1. **Limit Log Query**: Don't set limit too high (max 100-200)
2. **Filter Logs**: Use severity filters to reduce data
3. **Close Unused Tabs**: Dashboard auto-refreshes consume resources
4. **Disable Auto-Refresh**: If needed, comment out setInterval() calls
5. **Use Chrome/Firefox**: Best browser compatibility

---

## 📊 Metrics Explained

### CPU Usage
Percentage of CPU cores being utilized. >80% indicates high load.

### Memory Usage  
RAM consumption. >85% may cause slowdowns.

### Disk Usage
Storage capacity used. Monitor to prevent disk full errors.

### Active Connections
Number of established network connections. Spikes may indicate DDoS or scan.

### Incidents (Last Hour)
Recent attack activity. Baseline for comparison.

---

## 🎓 Best Practices

1. **Regular Monitoring**: Check dashboard 2-3 times daily
2. **Investigate High Severity**: Immediate action required
3. **Review Blocked IPs**: Periodically audit blacklist
4. **Export Data**: Use API endpoints for external analysis
5. **Update Whitelist**: Add legitimate IPs to prevent false positives
6. **Monitor Trends**: Look for patterns in attack types
7. **Resource Alerts**: Set up alerts for CPU/Memory >80%
8. **Log Retention**: Archive old logs to save space

---

## 🔗 Integration

### Export to CSV
```javascript
// Copy this into browser console while on dashboard
const data = await fetch('/api/records?limit=1000', {credentials: 'include'}).then(r => r.json());
const csv = [['ID','Timestamp','IP','Type','Severity'], ...data.map(r => [r.id, r.timestamp, r.source_ip, r.attack_type, r.severity])].map(r => r.join(',')).join('\\n');
const blob = new Blob([csv], {type: 'text/csv'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'sentinel-incidents.csv';
a.click();
```

### API Integration
```python
import requests

# Get traffic data
response = requests.get(
    'http://localhost:8501/api/traffic',
    auth=('sentinel', 'sentinel')
)
traffic = response.json()
print(f"CPU: {traffic['cpu_percent']}%")
```

---

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [README.md](README.md)
3. Check Docker logs: `docker logs sentinel-agent`
4. Verify API health: `curl http://localhost:8000/api/health`

---

## 🎉 Enjoy Your Enhanced Dashboard!

The new Sentinel SOC Dashboard provides enterprise-grade security monitoring with an intuitive, modern interface. Use it to stay ahead of threats and maintain a strong security posture.

**Stay Safe! 🛡️**
