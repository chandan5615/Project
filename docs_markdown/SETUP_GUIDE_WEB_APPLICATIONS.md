# Sentinel Agent - Complete Setup Guide for Websites and Web Applications

This guide provides detailed, step-by-step instructions for setting up Sentinel Agent to protect your websites and web applications.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Web Server Configuration](#web-server-configuration)
4. [Log File Setup](#log-file-setup)
5. [Configuration](#configuration)
6. [Testing the Setup](#testing-the-setup)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+, or similar)
- **Python**: Version 3.10 or higher
- **Web Server**: Apache 2.4+ or Nginx 1.18+
- **Permissions**: Root or sudo access for log reading and firewall management
- **Internet**: Connection for API calls (Google Gemini API)

### Required Software

```bash
# Check Python version
python3 --version  # Should be 3.10 or higher

# Check if web server is installed
apache2 -v  # For Apache
# OR
nginx -v   # For Nginx

# Check if iptables is available
iptables --version
```

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (you'll need it later)

---

## Installation

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Sentinel-Agent

# OR download and extract the project files
# Navigate to your project directory
cd /path/to/Sentinel-Agent
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Set Up Google API Key

**Option A: Environment Variable (Recommended for Testing)**

```bash
# Set API key for current session
export GOOGLE_API_KEY="your-api-key-here"

# Verify it's set
echo $GOOGLE_API_KEY
```

**Option B: .env File (Recommended for Production)**

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your-api-key-here
EOF

# Secure the file
chmod 600 .env
```

**Option C: System-wide Environment Variable**

```bash
# Add to ~/.bashrc or ~/.profile
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Web Server Configuration

### Apache Configuration

#### Step 1: Locate Apache Log Files

```bash
# Find Apache log directory
apache2ctl -V | grep SERVER_CONFIG_FILE
# Usually: /etc/apache2/apache2.conf

# Common log locations:
# - /var/log/apache2/access.log
# - /var/log/apache2/error.log
# - /var/log/httpd/access_log (CentOS/RHEL)
```

#### Step 2: Verify Log File Permissions

```bash
# Check current permissions
ls -la /var/log/apache2/access.log

# If permission denied, add your user to adm group
sudo usermod -aG adm $USER

# OR run Sentinel Agent with sudo
```

#### Step 3: Configure Apache Log Format (Optional but Recommended)

Edit Apache configuration to use a detailed log format:

```bash
# Edit Apache configuration
sudo nano /etc/apache2/apache2.conf
# OR
sudo nano /etc/httpd/conf/httpd.conf  # CentOS/RHEL
```

Add or modify the log format:

```apache
# Custom log format for better attack detection
LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined
CustomLog /var/log/apache2/access.log combined
```

Restart Apache:

```bash
# Ubuntu/Debian
sudo systemctl restart apache2

# CentOS/RHEL
sudo systemctl restart httpd
```

### Nginx Configuration

#### Step 1: Locate Nginx Log Files

```bash
# Find Nginx configuration
nginx -t

# Common log locations:
# - /var/log/nginx/access.log
# - /var/log/nginx/error.log
```

#### Step 2: Verify Log File Permissions

```bash
# Check current permissions
ls -la /var/log/nginx/access.log

# Add user to nginx group (if exists)
sudo usermod -aG nginx $USER

# OR run Sentinel Agent with sudo
```

#### Step 3: Configure Nginx Log Format (Optional but Recommended)

Edit Nginx configuration:

```bash
sudo nano /etc/nginx/nginx.conf
```

Ensure access log is configured:

```nginx
http {
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/access.log detailed;
    error_log /var/log/nginx/error.log;
    
    # ... rest of configuration
}
```

Test and reload Nginx:

```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Log File Setup

### Step 1: Identify Your Log File Locations

**For Apache:**
```bash
# Check Apache configuration
grep -r "CustomLog\|ErrorLog" /etc/apache2/
# OR
grep -r "CustomLog\|ErrorLog" /etc/httpd/
```

**For Nginx:**
```bash
# Check Nginx configuration
grep -r "access_log\|error_log" /etc/nginx/
```

### Step 2: Test Log File Access

```bash
# Test reading access log
sudo tail -n 10 /var/log/apache2/access.log
# OR
sudo tail -n 10 /var/log/nginx/access.log

# If you can read it, Sentinel Agent can monitor it
```

### Step 3: Create Test Log Entries (Optional)

To test Sentinel Agent, you can manually add test entries:

```bash
# For Apache
echo '192.168.1.100 - - [$(date +"%d/%b/%Y:%H:%M:%S %z")] "GET /test.php?id=1'"'"' OR 1=1--" 200' | sudo tee -a /var/log/apache2/access.log

# For Nginx
echo '192.168.1.100 - - [$(date +"%d/%b/%Y:%H:%M:%S %z")] "GET /test.php?id=1'"'"' OR 1=1--" 200' | sudo tee -a /var/log/nginx/access.log
```

---

## Configuration

### Step 1: Configure Sentinel Agent

Create a configuration file or use command-line arguments:

**Using Command-Line Arguments:**

```bash
# For Apache
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log

# For Nginx
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/nginx/access.log

# Custom paths
sudo python main.py --auth-log /var/log/secure --web-log /var/log/custom/web.log
```

### Step 2: Create a Startup Script

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/sentinel-agent.service
```

Add the following content (adjust paths as needed):

```ini
[Unit]
Description=Sentinel Agent - AI SOC Analyst
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/Sentinel-Agent
Environment="PATH=/path/to/Sentinel-Agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="GOOGLE_API_KEY=your-api-key-here"
ExecStart=/path/to/Sentinel-Agent/venv/bin/python /path/to/Sentinel-Agent/main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important:** Replace:
- `/path/to/Sentinel-Agent` with your actual project path
- `your-api-key-here` with your actual API key
- `/var/log/apache2/access.log` with your actual web log path

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable sentinel-agent

# Start service
sudo systemctl start sentinel-agent

# Check status
sudo systemctl status sentinel-agent

# View logs
sudo journalctl -u sentinel-agent -f
```

### Step 3: Create a Simple Startup Script (Alternative)

If you prefer a simple script:

```bash
cat > start_sentinel.sh << 'EOF'
#!/bin/bash
cd /path/to/Sentinel-Agent
source venv/bin/activate
export GOOGLE_API_KEY="your-api-key-here"
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
EOF

chmod +x start_sentinel.sh
```

Run it:
```bash
./start_sentinel.sh
```

---

## Testing the Setup

### Step 1: Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "from crewai import Agent; print('CrewAI OK')"
python -c "from defense.attack_detector import AttackDetector; print('Attack Detector OK')"
python -c "from defense.attack_logger import AttackLogger; print('Attack Logger OK')"

# Check API key
python -c "import os; print('API Key:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
```

### Step 2: Test Attack Detection

**Test SQL Injection Detection:**

```bash
# Add a test SQL injection attempt to web log
echo '192.168.1.200 - - [$(date +"%d/%b/%Y:%H:%M:%S %z")] "GET /login.php?id=1'"'"' OR 1=1--" 200' | sudo tee -a /var/log/apache2/access.log
```

**Test Brute Force Detection:**

```bash
# Add a test failed login to auth log
echo "$(date '+%b %d %H:%M:%S') $(hostname) sshd[12345]: Failed password for user admin from 192.168.1.200 port 22" | sudo tee -a /var/log/auth.log
```

### Step 3: Run Sentinel Agent

```bash
# Activate virtual environment
source venv/bin/activate

# Set API key if not in .env
export GOOGLE_API_KEY="your-api-key-here"

# Run Sentinel Agent
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
```

You should see output like:
```
Starting Sentinel Defense Module...
Monitoring auth log: /var/log/auth.log
Monitoring web log: /var/log/apache2/access.log
AI Crew ready with Google Gemini API (gemini-1.5-flash)
Multi-Vector Ingestion: Active
Sentinel Defense Module is now monitoring for security events...
```

### Step 4: Verify Attack Detection

After adding test entries, Sentinel Agent should:
1. Detect the attack
2. Log it to `attack_records.json`
3. Analyze it with AI agents
4. Propose defensive actions

View detected attacks:
```bash
python view_attacks.py
```

---

## Production Deployment

### Step 1: Security Hardening

**Secure API Key:**
```bash
# Use .env file with restricted permissions
chmod 600 .env
chown root:root .env  # If running as root
```

**Secure Attack Records:**
```bash
# Restrict access to attack records
chmod 600 attack_records.json
```

**Firewall Rules:**
```bash
# Ensure iptables is properly configured
sudo iptables -L -n -v
```

### Step 2: Log Rotation Configuration

Configure log rotation to prevent disk space issues:

**For Apache:**
```bash
sudo nano /etc/logrotate.d/apache2
```

Ensure it includes:
```
/var/log/apache2/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload apache2 > /dev/null 2>&1 || true
    endscript
}
```

**For Nginx:**
```bash
sudo nano /etc/logrotate.d/nginx
```

### Step 3: Monitoring and Alerts

**Set up log monitoring:**
```bash
# Monitor Sentinel Agent logs
sudo journalctl -u sentinel-agent -f

# Monitor attack records
watch -n 5 'tail -20 attack_records.json'
```

**Create alert script:**
```bash
cat > check_attacks.sh << 'EOF'
#!/bin/bash
ATTACKS=$(python view_attacks.py | grep "Total Attacks" | awk '{print $4}')
if [ "$ATTACKS" -gt 10 ]; then
    echo "ALERT: High number of attacks detected: $ATTACKS"
    # Add email notification or other alert mechanism
fi
EOF

chmod +x check_attacks.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/check_attacks.sh") | crontab -
```

### Step 4: Backup Configuration

**Backup attack records:**
```bash
# Create backup script
cat > backup_attacks.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/sentinel-agent"
mkdir -p $BACKUP_DIR
cp attack_records.json "$BACKUP_DIR/attack_records_$(date +%Y%m%d_%H%M%S).json"
# Keep only last 30 days
find $BACKUP_DIR -name "attack_records_*.json" -mtime +30 -delete
EOF

chmod +x backup_attacks.sh

# Add to crontab (daily backup)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup_attacks.sh") | crontab -
```

---

## Troubleshooting

### Issue 1: Permission Denied Reading Logs

**Symptoms:**
```
Permission denied reading /var/log/apache2/access.log
```

**Solutions:**
```bash
# Option 1: Add user to adm group
sudo usermod -aG adm $USER
newgrp adm

# Option 2: Run with sudo
sudo python main.py

# Option 3: Change log file permissions (not recommended)
sudo chmod 644 /var/log/apache2/access.log
```

### Issue 2: API Key Not Found

**Symptoms:**
```
ValueError: GOOGLE_API_KEY environment variable is not set
```

**Solutions:**
```bash
# Check if API key is set
echo $GOOGLE_API_KEY

# Set it
export GOOGLE_API_KEY="your-key"

# OR create .env file
echo "GOOGLE_API_KEY=your-key" > .env
```

### Issue 3: Log File Not Found

**Symptoms:**
```
Log file /var/log/apache2/access.log does not exist
```

**Solutions:**
```bash
# Find actual log location
sudo find /var/log -name "*access*" -type f

# Update configuration with correct path
python main.py --web-log /actual/path/to/access.log
```

### Issue 4: iptables Command Not Found

**Symptoms:**
```
iptables command not found
```

**Solutions:**
```bash
# Install iptables
sudo apt-get install iptables  # Ubuntu/Debian
sudo yum install iptables      # CentOS/RHEL

# Verify installation
which iptables
```

### Issue 5: Virtual Environment Issues

**Symptoms:**
```
ModuleNotFoundError: No module named 'crewai'
```

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep crewai
```

### Issue 6: Web Server Not Logging

**Symptoms:**
No entries appearing in access logs

**Solutions:**
```bash
# Check if logging is enabled in Apache
grep -i "CustomLog\|LogLevel" /etc/apache2/apache2.conf

# Check if logging is enabled in Nginx
grep -i "access_log" /etc/nginx/nginx.conf

# Test by accessing your website
curl http://localhost

# Check if log entry appears
sudo tail -f /var/log/apache2/access.log
```

### Issue 7: Attack Not Detected

**Symptoms:**
Attack added to log but not detected

**Solutions:**
```bash
# Verify log file is being monitored
# Check Sentinel Agent output for "Monitoring" messages

# Verify attack pattern matches
# Check defense/attack_detector.py for patterns

# Test with known attack pattern
echo '192.168.1.100 - - [15/Jan/2024:14:30:25 +0000] "GET /test.php?id=1'"'"' OR 1=1--" 200' | sudo tee -a /var/log/apache2/access.log
```

---

## Best Practices

### 1. Log File Management

- **Enable log rotation** to prevent disk space issues
- **Monitor log file sizes** regularly
- **Archive old logs** for compliance and analysis
- **Use centralized logging** for multiple servers

### 2. Security

- **Never commit API keys** to version control
- **Use .env files** with restricted permissions
- **Regularly rotate API keys**
- **Monitor attack records** for patterns
- **Keep attack_records.json secure**

### 3. Performance

- **Monitor system resources** (CPU, memory, disk)
- **Adjust log monitoring frequency** if needed
- **Use log rotation** to manage file sizes
- **Consider log aggregation** for high-traffic sites

### 4. Monitoring

- **Set up alerts** for critical attacks
- **Regularly review attack records**
- **Monitor Sentinel Agent service** status
- **Track false positives** and adjust patterns

### 5. Maintenance

- **Update dependencies** regularly
- **Review and update attack patterns**
- **Backup attack records** regularly
- **Test detection** after updates
- **Document custom configurations**

### 6. Integration

- **Integrate with SIEM systems** for centralized monitoring
- **Export attack data** for analysis tools
- **Set up email/SMS alerts** for critical attacks
- **Create dashboards** for visualization

---

## Common Web Application Setups

### WordPress

**Log Location:**
```bash
# Apache
/var/log/apache2/access.log

# Nginx
/var/log/nginx/access.log
```

**Common Attack Patterns:**
- SQL injection in wp-admin
- XSS in comments
- Brute force on wp-login.php
- Directory traversal in wp-content

**Configuration:**
```bash
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
```

### Laravel/PHP Applications

**Log Location:**
```bash
# Application logs (if configured)
/var/www/html/storage/logs/laravel.log

# Web server logs
/var/log/apache2/access.log
```

**Configuration:**
```bash
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
```

### Node.js Applications

**Log Location:**
```bash
# If using Nginx reverse proxy
/var/log/nginx/access.log

# Application logs (if configured)
/var/log/nodejs/app.log
```

**Configuration:**
```bash
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/nginx/access.log
```

### Django/Python Applications

**Log Location:**
```bash
# Web server logs
/var/log/apache2/access.log
# OR
/var/log/nginx/access.log
```

**Configuration:**
```bash
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log
```

---

## Quick Reference

### Essential Commands

```bash
# Start Sentinel Agent
sudo python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log

# View attack records
python view_attacks.py

# Check service status
sudo systemctl status sentinel-agent

# View logs
sudo journalctl -u sentinel-agent -f

# Test attack detection
echo '192.168.1.100 - - [...] "GET /test.php?id=1'"'"' OR 1=1--" 200' | sudo tee -a /var/log/apache2/access.log
```

### File Locations

- **Attack Records**: `attack_records.json`
- **Configuration**: `.env` (API key)
- **Logs**: `/var/log/apache2/access.log` or `/var/log/nginx/access.log`
- **Service**: `/etc/systemd/system/sentinel-agent.service`

### Important Paths

- **Project Directory**: `/path/to/Sentinel-Agent`
- **Virtual Environment**: `/path/to/Sentinel-Agent/venv`
- **Main Script**: `/path/to/Sentinel-Agent/main.py`

---

## Support and Resources

### Documentation Files

- `PROJECT_DOCUMENTATION.md` - Complete project documentation
- `ATTACK_DEFENSE.md` - Attack detection details
- `DEFENSE_MODULE.md` - Defense module documentation
- `README.md` - General project information

### Getting Help

1. Check troubleshooting section above
2. Review log files for error messages
3. Verify all prerequisites are met
4. Test with sample attack patterns
5. Check system resources and permissions

---

## Conclusion

This guide provides comprehensive instructions for setting up Sentinel Agent to protect your websites and web applications. Follow the steps carefully, test thoroughly, and monitor regularly for best results.

Remember:
- Always test in a development environment first
- Keep API keys secure
- Regularly review attack records
- Update attack patterns as needed
- Monitor system resources

For additional information, refer to the other documentation files in the project.
