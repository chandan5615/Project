# Sentinel Agent - Docker Deployment Guide

Complete guide for deploying Sentinel Agent using Docker and Docker Compose on Linux servers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running with Docker Compose](#running-with-docker-compose)
6. [Running with Docker](#running-with-docker)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+, or similar)
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 1.29 or higher (or Docker Compose V2)
- **Disk Space**: At least 10GB free space (for LLM model)
- **Memory**: Minimum 8GB RAM recommended (16GB for larger models)
- **Permissions**: Root or sudo access
- **Optional**: NVIDIA GPU for faster inference

### Install Docker and Docker Compose

**Ubuntu/Debian:**

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

**CentOS/RHEL:**

```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version
```

**Add user to docker group (optional):**

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Verify
docker ps
```

---

## Quick Start

### 1. Clone or Download Project

```bash
# Clone repository
git clone <repository-url>
cd Sentinel-Agent

# OR download and extract
# Navigate to project directory
cd /path/to/Sentinel-Agent
```

### 2. Set Up Environment Variables (Optional)

```bash
# Create .env file (optional - defaults work out of the box)
cat > .env << EOF
# Ollama model (default: llama3:8b)
OLLAMA_MODEL=llama3:8b

# Log paths (defaults shown)
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
EOF

# Secure the file
chmod 600 .env
```

### 3. Build and Run

```bash
# Build and start containers
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

---

## Installation

### Step 1: Prepare Project Directory

```bash
# Create project directory
mkdir -p /opt/sentinel-agent
cd /opt/sentinel-agent

# Copy project files
cp -r /path/to/Sentinel-Agent/* .

# Create necessary directories
mkdir -p data logs
```

### Step 2: Create Environment File (Optional)

```bash
# Create .env file (optional - defaults work out of the box)
cat > .env << EOF
# Ollama model to use (default: llama3:8b)
# Smaller: llama3.2:3b (faster, less RAM)
# Larger: llama3:70b (slower, more accurate)
OLLAMA_MODEL=llama3:8b

# Log file paths (adjust based on your system)
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# Optional: Custom paths for different distributions
# AUTH_LOG_PATH=/var/log/secure          # CentOS/RHEL
# WEB_LOG_PATH=/var/log/nginx/access.log # Nginx
EOF

# Secure the file
chmod 600 .env
```

### Step 3: Build Docker Image

```bash
# Build the image
docker compose build

# OR build manually
docker build -t sentinel-agent:latest .

# Verify image was created
docker images | grep sentinel-agent
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Ollama model (default: llama3:8b)
OLLAMA_MODEL=llama3:8b

# Log paths (defaults shown)
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log

# For Nginx
# WEB_LOG_PATH=/var/log/nginx/access.log
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  sentinel-agent:
    environment:
      - OLLAMA_BASE_URL=http://127.0.0.1:11434
      - OLLAMA_MODEL=${OLLAMA_MODEL:-llama3:8b}
      - AUTH_LOG_PATH=${AUTH_LOG_PATH:-/var/log/auth.log}
      - WEB_LOG_PATH=${WEB_LOG_PATH:-/var/log/apache2/access.log}
    volumes:
      # Adjust paths based on your system
      - /var/log:/var/log:ro
      - ./data:/app/data
      - ./logs:/app/logs
```

### Log File Paths

**For Apache:**
```yaml
WEB_LOG_PATH=/var/log/apache2/access.log
```

**For Nginx:**
```yaml
WEB_LOG_PATH=/var/log/nginx/access.log
```

**For Custom Locations:**
```yaml
WEB_LOG_PATH=/var/log/custom/web.log
```

---

## Running with Docker Compose

### Start Services

```bash
# Start in detached mode (background)
docker compose up -d

# Start with logs visible
docker compose up

# Start and rebuild if needed
docker compose up -d --build
```

### View Logs

```bash
# View all logs
docker compose logs

# Follow logs (like tail -f)
docker compose logs -f

# View logs for specific service
docker compose logs -f sentinel-agent

# View last 100 lines
docker compose logs --tail=100
```

### Stop Services

```bash
# Stop services
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers, volumes, and images
docker compose down -v --rmi all
```

### Check Status

```bash
# Check container status
docker compose ps

# Check container health
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"

# View container details
docker inspect sentinel-agent
```

### Restart Services

```bash
# Restart services
docker compose restart

# Restart specific service
docker compose restart sentinel-agent
```

---

## Running with Docker

### Build Image

```bash
# Build image
docker build -t sentinel-agent:latest .

# Build with custom tag
docker build -t sentinel-agent:v1.0.0 .
```

### Run Container

**Note:** It's recommended to use `docker compose` as it manages both Ollama and Sentinel Agent together.

```bash
# Basic run (requires Ollama running separately on host)
docker run -d \
  --name sentinel-agent \
  --privileged \
  --network host \
  -e OLLAMA_BASE_URL="http://127.0.0.1:11434" \
  -e OLLAMA_MODEL="llama3:8b" \
  -e AUTH_LOG_PATH="/var/log/auth.log" \
  -e WEB_LOG_PATH="/var/log/apache2/access.log" \
  -v /var/log:/var/log:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  sentinel-agent:latest \
  python main.py --auth-log /var/log/auth.log --web-log /var/log/apache2/access.log

# Run with .env file
docker run -d \
  --name sentinel-agent \
  --privileged \
  --network host \
  --env-file .env \
  -v /var/log:/var/log:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  sentinel-agent:latest
```

### View Container Logs

```bash
# View logs
docker logs sentinel-agent

# Follow logs
docker logs -f sentinel-agent

# View last 100 lines
docker logs --tail=100 sentinel-agent
```

### Stop and Remove Container

```bash
# Stop container
docker stop sentinel-agent

# Remove container
docker rm sentinel-agent

# Stop and remove
docker stop sentinel-agent && docker rm sentinel-agent
```

---

## Production Deployment

### Step 1: Create Production Directory Structure

```bash
# Create production directory
sudo mkdir -p /opt/sentinel-agent/{data,logs,config}
cd /opt/sentinel-agent

# Set ownership
sudo chown -R $USER:$USER /opt/sentinel-agent
```

### Step 2: Copy Project Files

```bash
# Copy all project files
cp -r /path/to/Sentinel-Agent/* /opt/sentinel-agent/

# Create .env file (optional)
cat > /opt/sentinel-agent/.env << EOF
OLLAMA_MODEL=llama3:8b
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
EOF

chmod 600 /opt/sentinel-agent/.env
```

### Step 3: Create Systemd Service

```bash
sudo nano /etc/systemd/system/sentinel-agent.service
```

Add the following:

```ini
[Unit]
Description=Sentinel Agent - Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/sentinel-agent
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable sentinel-agent

# Start service
sudo systemctl start sentinel-agent

# Check status
sudo systemctl status sentinel-agent

# View logs
sudo journalctl -u sentinel-agent -f
```

### Step 4: Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/sentinel-agent
```

Add:

```
/opt/sentinel-agent/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    sharedscripts
    postrotate
        docker compose -f /opt/sentinel-agent/docker-compose.yml restart sentinel-agent > /dev/null 2>&1 || true
    endscript
}
```

### Step 5: Set Up Backup

```bash
# Create backup script
cat > /opt/sentinel-agent/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/sentinel-agent"
mkdir -p $BACKUP_DIR
cp /opt/sentinel-agent/data/attack_records.json "$BACKUP_DIR/attack_records_$(date +%Y%m%d_%H%M%S).json"
find $BACKUP_DIR -name "attack_records_*.json" -mtime +30 -delete
EOF

chmod +x /opt/sentinel-agent/backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/sentinel-agent/backup.sh") | crontab -
```

### Step 6: Monitor Health

```bash
# Create health check script
cat > /opt/sentinel-agent/healthcheck.sh << 'EOF'
#!/bin/bash
if ! docker ps | grep -q sentinel-agent; then
    echo "ALERT: Sentinel Agent container is not running"
    systemctl restart sentinel-agent
fi
EOF

chmod +x /opt/sentinel-agent/healthcheck.sh

# Add to crontab (check every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/sentinel-agent/healthcheck.sh") | crontab -
```

---

## Troubleshooting

### Issue 1: Container Won't Start

**Symptoms:**
```
Error: Container failed to start
```

**Solutions:**
```bash
# Check logs
docker compose logs

# Check if ports are available
docker compose ps

# Check Docker daemon
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

### Issue 2: Permission Denied Reading Logs

**Symptoms:**
```
Permission denied: /var/log/auth.log
```

**Solutions:**
```bash
# Check log file permissions
ls -la /var/log/auth.log

# Run container with proper user mapping
# Edit docker-compose.yml to add:
user: "0:0"  # Run as root (not recommended for production)

# OR ensure log files are readable
sudo chmod 644 /var/log/auth.log
```

### Issue 3: Ollama Connection Failed

**Symptoms:**
```
Cannot reach Ollama server at http://127.0.0.1:11434
```

**Solutions:**
```bash
# Check if Ollama container is running
docker compose ps ollama

# Check Ollama logs
docker compose logs ollama

# Test Ollama API
curl http://localhost:11434/api/tags

# Restart Ollama container
docker compose restart ollama

# Check if model is downloaded
docker compose exec ollama ollama list

# Pull model manually if needed
docker compose exec ollama ollama pull llama3:8b
```

### Issue 4: iptables Not Working

**Symptoms:**
```
iptables command not found
Permission denied for iptables
```

**Solutions:**
```bash
# Ensure container runs with --privileged
# Check docker-compose.yml has:
privileged: true

# Verify iptables in container
docker compose exec sentinel-agent iptables --version

# Check capabilities
docker inspect sentinel-agent | grep -i privileged
```

### Issue 5: Log Files Not Found

**Symptoms:**
```
Log file /var/log/apache2/access.log does not exist
```

**Solutions:**
```bash
# Verify log file exists on host
ls -la /var/log/apache2/access.log

# Check volume mount
docker inspect sentinel-agent | grep -A 10 Mounts

# Verify volume configuration in docker-compose.yml
# Should have: - /var/log:/var/log:ro

# Test volume mount
docker compose exec sentinel-agent ls -la /var/log/apache2/
```

### Issue 6: Container Keeps Restarting

**Symptoms:**
```
Container status: Restarting
```

**Solutions:**
```bash
# Check logs for errors
docker compose logs --tail=50 sentinel-agent

# Check exit code
docker inspect sentinel-agent | grep -i exitcode

# Check health status
docker compose ps

# Review container configuration
docker compose config
```

### Issue 7: Out of Disk Space

**Symptoms:**
```
No space left on device
```

**Solutions:**
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a

# Clean up old logs
docker compose logs --tail=0  # Clear logs

# Remove unused volumes
docker volume prune
```

---

## Maintenance

### Update Container

```bash
# Pull latest changes
git pull

# Rebuild image
docker compose build --no-cache

# Restart with new image
docker compose up -d
```

### View Attack Records

```bash
# Access container shell
docker compose exec sentinel-agent bash

# View attack records
cat /app/data/attack_records.json | python -m json.tool

# OR from host
cat data/attack_records.json | python -m json.tool

# Use view_attacks.py
docker compose exec sentinel-agent python view_attacks.py
```

### Backup Data

```bash
# Backup attack records
cp data/attack_records.json backup/attack_records_$(date +%Y%m%d).json

# Backup entire data directory
tar -czf backup/sentinel-data-$(date +%Y%m%d).tar.gz data/

# Restore from backup
cp backup/attack_records_20240115.json data/attack_records.json
```

### Monitor Resource Usage

```bash
# View container stats
docker stats sentinel-agent

# View disk usage
docker system df

# View container resource limits
docker inspect sentinel-agent | grep -i memory
```

### Clean Up

```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Remove images
docker rmi sentinel-agent:latest

# Clean up everything
docker system prune -a --volumes
```

---

## Security Considerations

### 1. Local LLM Security

- Ollama runs locally - no API keys or external calls needed
- Model data is stored in Docker volume
- No sensitive data leaves your network

### 2. Container Security

- Run with minimal privileges when possible
- Use read-only volumes for logs
- Keep Docker and images updated
- Scan images for vulnerabilities

### 3. Network Security

- Use `network_mode: host` only when necessary
- Consider using bridge network with port mapping
- Restrict container network access

### 4. Data Security

- Encrypt attack records at rest
- Secure backup storage
- Implement access controls
- Regular security audits

---

## Quick Reference

### Essential Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose stop

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Rebuild and restart
docker compose up -d --build

# Check status
docker compose ps

# Access container shell
docker compose exec sentinel-agent bash

# View attack records
docker compose exec sentinel-agent python view_attacks.py
```

### File Locations

- **Project Directory**: `/opt/sentinel-agent`
- **Attack Records**: `./data/attack_records.json`
- **Container Logs**: `./logs/`
- **Configuration**: `.env`
- **Docker Compose**: `docker-compose.yml`

---

## Advanced Configuration

### Custom Dockerfile

If you need to customize the build:

```dockerfile
FROM python:3.10-slim

# Add custom dependencies
RUN apt-get update && apt-get install -y \
    your-custom-package

# Copy custom scripts
COPY custom-scripts/ /app/custom-scripts/

# Rest of Dockerfile...
```

### Multi-Stage Build Optimization

The Dockerfile uses multi-stage builds to minimize image size. To further optimize:

```bash
# Build with buildkit
DOCKER_BUILDKIT=1 docker build -t sentinel-agent:latest .

# Use .dockerignore effectively
# Already configured in .dockerignore file
```

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  sentinel-agent:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## Conclusion

This guide provides comprehensive instructions for deploying Sentinel Agent using Docker and Docker Compose. Follow the steps carefully, test thoroughly, and monitor regularly for best results.

For additional information:
- `PROJECT_DOCUMENTATION.md` - Complete project documentation
- `SETUP_GUIDE_WEB_APPLICATIONS.md` - Web application setup guide
- `README.md` - General project information
