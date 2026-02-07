# Docker Commands Cheat Sheet - Sentinel Agent v2.2

Quick reference for common Docker and docker-compose commands.

---

## 🚀 Getting Started

```bash
# Navigate to project
cd sentinel-agent

# Option 1: With Docker Ollama (Easiest)
docker-compose --profile with-ollama up -d

# Option 2: With Host Ollama (Fastest)
ollama pull llama3:8b && ollama serve
docker-compose up -d

# Option 3: Production Setup
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📊 Service Management

### Start Services
```bash
# Start in background
docker-compose up -d

# Start with specific profile
docker-compose --profile with-ollama up -d

# Start with custom env file
docker-compose --env-file .env.prod up -d

# Start and view logs
docker-compose up
```

### Stop Services
```bash
# Stop services (keep data)
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v

# Stop just one service
docker-compose stop sentinel-agent

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart sentinel-agent
```

---

## 📋 View Status & Logs

### Status
```bash
# List running services
docker-compose ps

# List services with more details
docker-compose ps -a

# Show service details
docker inspect sentinel-agent

# Check resource usage
docker stats

# View network
docker network ls
docker network inspect sentinel-network
```

### Logs
```bash
# Follow logs in real-time
docker-compose logs -f sentinel-agent

# View last 100 lines
docker-compose logs --tail=100 sentinel-agent

# View logs with timestamps
docker-compose logs --timestamps sentinel-agent

# View logs for all services
docker-compose logs -f

# View Ollama logs
docker-compose logs -f ollama

# Save logs to file
docker-compose logs sentinel-agent > debug.log
```

---

## 🔧 Container Interaction

### Access Container Shell
```bash
# Interactive bash shell
docker-compose exec sentinel-agent bash

# Execute command
docker-compose exec sentinel-agent python script.py

# Check environment variables
docker-compose exec sentinel-agent env

# Check running processes
docker-compose exec sentinel-agent ps aux

# Check listening ports
docker-compose exec sentinel-agent netstat -tulpn
```

### Copy Files
```bash
# Copy FROM container
docker-compose exec sentinel-agent cat /app/config.json > config.json

# Copy TO container
docker cp ./config.json container-name:/app/config.json

# OR edit in container
docker-compose exec sentinel-agent nano /app/config.json
```

---

## 🏗️ Building & Images

### Build Image
```bash
# Build image
docker-compose build

# Build without cache (fresh)
docker-compose build --no-cache

# Build verbose
docker-compose build --verbose

# Build specific service
docker-compose build sentinel-agent
```

### Image Management
```bash
# List images
docker images

# View image details
docker inspect sentinel-agent:2.2

# Remove image
docker rmi sentinel-agent:2.2

# Remove unused images
docker image prune -a

# Tag image
docker tag sentinel-agent:2.2 myrepo/sentinel-agent:latest
```

---

## 🌐 API & Testing

### Health Check
```bash
# Test API health
curl http://localhost:8000/api/health

# Verbose output
curl -v http://localhost:8000/api/health

# With response code
curl -w "%{http_code}" http://localhost:8000/api/health

# From container
docker-compose exec sentinel-agent curl http://127.0.0.1:8000/api/health
```

### API Endpoints
```bash
# Get threats
curl http://localhost:8000/api/threats

# Get attacks
curl http://localhost:8000/api/attacks

# Get metrics
curl http://localhost:8000/api/metrics

# Authentication (if enabled)
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/threats
```

### Test Connectivity
```bash
# Test from container to Ollama
docker-compose exec sentinel-agent curl http://127.0.0.1:11434/api/tags

# Test DNS resolution
docker-compose exec sentinel-agent nslookup ollama

# Test internet connection
docker-compose exec sentinel-agent curl https://api.github.com
```

---

## 💾 Data Management

### Backup
```bash
# Backup data and logs
tar czf backup-$(date +%Y%m%d-%H%M%S).tar.gz data/ logs/

# Backup from outside container
docker-compose exec -T sentinel-agent tar czf - /app/data > data_backup.tar.gz

# View backup size
ls -lh backup*.tar.gz
```

### Restore
```bash
# Stop services first
docker-compose down

# Extract backup
tar xzf backup-20240101-120000.tar.gz

# Start services
docker-compose up -d
```

### Data Inspection
```bash
# List data files
docker-compose exec sentinel-agent ls -la /app/data/

# Check database
docker-compose exec sentinel-agent sqlite3 /app/data/sentinel_intel.db ".tables"

# View database size
docker-compose exec sentinel-agent du -sh /app/data/

# Check disk usage
docker-compose exec sentinel-agent df -h
```

---

## 🧹 Cleanup & Maintenance

### Clean Up
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Everything at once (be careful!)
docker system prune -a

# Force remove container
docker rm -f container-name
```

### Check System Usage
```bash
# Docker disk usage
docker system df

# Detailed breakdown
docker system df --verbose

# Find large images
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | sort -k2 -h
```

---

## 🔍 Debugging & Troubleshooting

### Diagnostic Commands
```bash
# Show full configuration after processing
docker-compose config

# Check for errors in compose file
docker-compose config --quiet

# Show which files are being used
docker-compose config --resolve-image-digests

# List all services
docker-compose config --services
```

### Container Debugging
```bash
# View container logs with errors
docker-compose logs --tail=200 sentinel-agent | grep -i error

# Check specific service
docker ps -a | grep sentinel

# View last command
docker-compose logs sentinel-agent | tail -20

# Check exit code
docker-compose ps -a
```

### Network Debugging
```bash
# List networks
docker network ls

# Inspect network
docker network inspect sentinel-network

# Check container IP
docker inspect -f '{{.NetworkSettings.Networks.sentinel-network.IPAddress}}' sentinel-agent

# Test network connectivity
docker-compose exec sentinel-agent ping ollama
```

### Port Debugging
```bash
# Check port mapping
docker-compose ps

# Check if port is in use (Linux)
lsof -i :8000
netstat -tulpn | grep 8000

# Check if port is in use (Windows)
netstat -ano | findstr :8000

# Find process using port and kill it
fuser -k 8000/tcp
```

---

## 📦 Profiles & Variations

### Using Profiles
```bash
# Start with Ollama profile
docker-compose --profile with-ollama up -d

# List available profiles
docker-compose config --profiles

# Start with multiple profiles
docker-compose --profile with-ollama --profile monitoring up -d

# Stop only specific services
docker-compose --profile with-ollama down
```

### Multiple Instances
```bash
# Same compose, different projects
docker-compose -p instance1 up -d
docker-compose -p instance2 up -d
docker-compose -p instance3 up -d

# Access each
curl http://localhost:8000/api/health   # instance1
curl http://localhost:8001/api/health   # instance2
curl http://localhost:8002/api/health   # instance3
```

---

## 🔒 Security Commands

### Check Security
```bash
# List running containers
docker ps

# Check container privileges
docker inspect sentinel-agent | grep -A 20 "Capabilities"

# View security options
docker inspect sentinel-agent | grep -i security

# Check volume permissions
docker-compose exec sentinel-agent ls -la /app/
```

### User Management
```bash
# Check current user in container
docker-compose exec sentinel-agent whoami

# Run as different user
docker-compose exec -u root sentinel-agent whoami

# Fix file permissions
docker-compose exec sentinel-agent chmod 755 /app/logs
```

---

## 🚨 Common Issues Quick Fixes

### Service Won't Start
```bash
# Check logs
docker-compose logs sentinel-agent

# Full restart
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
```

### API Not Responding
```bash
# Test from container
docker-compose exec sentinel-agent curl http://127.0.0.1:8000/api/health

# Check port
docker-compose ps | grep 8000

# Restart service
docker-compose restart sentinel-agent
```

### Ollama Not Found
```bash
# Check if Ollama is running
docker-compose exec sentinel-agent curl http://ollama:11434/api/tags

# Start Docker Ollama
docker-compose --profile with-ollama up -d

# Or start host Ollama
ollama serve
```

### Out of Disk Space
```bash
# Check usage
docker system df

# Clean up
docker system prune -a

# Remove old images
docker image prune -a
```

---

## 📚 Help & Documentation

### Get Help
```bash
# Docker compose help
docker-compose help

# Specific command help
docker-compose help up

# View full documentation
docker-compose config --help
```

### Find Documentation
```bash
# Docker documentation
docker docs               # (if installed)

# Project documentation
see docs_markdown/DOCKER_QUICKSTART.md
see docs_markdown/DOCKER_DEPLOYMENT.md
see docs_markdown/DOCKER_TROUBLESHOOTING.md
```

---

## 📋 Command By Purpose

### "I want to start the application"
```bash
docker-compose up -d
# or with Ollama:
docker-compose --profile with-ollama up -d
```

### "Something's broken, help!"
```bash
docker-compose logs -f --tail=100 sentinel-agent
# Then find solution in DOCKER_TROUBLESHOOTING.md
```

### "Check if it's working"
```bash
docker-compose ps
curl http://localhost:8000/api/health
```

### "Get into the container"
```bash
docker-compose exec sentinel-agent bash
```

### "Backup my data"
```bash
tar czf backup-$(date +%Y%m%d).tar.gz data/ logs/
```

### "Clean everything and restart fresh"
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### "Update the application"
```bash
git pull origin main
docker-compose build --no-cache
docker-compose restart
```

### "Monitor what's happening"
```bash
docker stats                # Resource usage
docker-compose logs -f      # Real-time logs
docker-compose ps           # Service status
```

---

## 🎯 One-Liners

```bash
# Quick health check
docker-compose exec sentinel-agent curl http://127.0.0.1:8000/api/health && echo "OK" || echo "FAILED"

# View all API endpoints
curl -s http://localhost:8000/docs | grep -o '"path":"[^"]*"'

# Container resource usage
docker stats --no-stream | grep sentinel-agent

# Backup and verify
tar czf backup.tar.gz data/ && tar tzf backup.tar.gz | head -10

# Search logs for errors
docker-compose logs | grep -i "error\|warning\|fail"

# Reset everything (careful!)
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d

# Check all containers running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 📞 Quick Links

- **Quick Start:** `docs_markdown/DOCKER_QUICKSTART.md`
- **Full Guide:** `docs_markdown/DOCKER_DEPLOYMENT.md`
- **Troubleshooting:** `docs_markdown/DOCKER_TROUBLESHOOTING.md`
- **Advanced:** `docs_markdown/DOCKER_PROFILES_ADVANCED.md`
- **Navigation:** `docs_markdown/DOCKER_INDEX.md`

---

**Last Updated:** 2024  
**Version:** Sentinel Agent v2.2
