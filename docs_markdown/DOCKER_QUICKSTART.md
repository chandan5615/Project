# Docker Quick Start - Sentinel Agent v2.2

##  Installation (Choose One)

### Option A: Host Ollama (Production - Recommended) ⭐
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Sentinel Agent
cd sentinel-agent
docker-compose up -d
```

### Option B: Docker Ollama (Alternative)
```bash
cd sentinel-agent
# Uncomment ollama and ollama-pull services in docker-compose.yml
docker-compose --profile with-ollama up -d
```

### Option C: Production (with SSL/Nginx)
```bash
cd sentinel-agent
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## ✅ Verify Installation

```bash
# Check all services running
docker-compose ps

# Test API health (ports directly accessible via host network)
curl http://localhost:8000/api/health

# Check Ollama connectivity
curl http://localhost:11434/api/tags

# View logs
docker-compose logs -f sentinel-agent
```

---

##  Accessing the Application

When using `network_mode: host`, ports are **directly accessible** without port forwarding:

| Service | URL | Access |
|---------|-----|--------|
| API | `http://localhost:8000` | REST API endpoints |
| Health Check | `http://localhost:8000/api/health` | Health status |
| Dashboard | `http://localhost:8501` | Web interface (if running) |
| Ollama | `http://localhost:11434` | LLM engine |

---

##  Essential Commands

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start services in background |
| `docker-compose down` | Stop all services |
| `docker-compose ps` | List running services |
| `docker-compose logs -f` | Follow logs in real-time |
| `docker-compose exec sentinel-agent bash` | Access container shell |
| `docker-compose restart` | Restart all services |
| `docker-compose build --no-cache` | Rebuild images |

---

##  Configuration

### Update Environment Variables

**Option 1: Edit `docker-compose.yml`**
```yaml
environment:
  LOG_LEVEL: DEBUG
  OLLAMA_MODEL: mistral:7b
```

**Option 2: Use `.env` file**
```
OLLAMA_MODEL=mistral:7b
LOG_LEVEL=INFO
```

**Note**: With `network_mode: host`, ports cannot be customized - they're bound directly to the host (8000 for API, 8501 for Dashboard).

---

##  Data Management

```bash
# Backup
tar czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Restore
tar xzf backup-20240101.tar.gz
docker-compose restart

# View disk usage
docker system df

# Clean up
docker system prune -a
```

---

##  Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs sentinel-agent

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't Connect to API
```bash
# Test from container
docker-compose exec sentinel-agent curl http://127.0.0.1:8000/api/health

# Check port
docker-compose ps

# View network
docker network inspect sentinel-network
```

### Ollama Connection Failed
```bash
# Check Ollama status
docker-compose exec sentinel-agent curl http://ollama:11434/api/tags

# View Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama
```

### Container Out of Memory
```bash
# Check memory usage
docker stats

# Increase in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

---

##  Common Tasks

### Run Custom Script
```bash
docker-compose exec sentinel-agent python script.py
```

### View Application Logs
```bash
docker-compose logs --tail=100 sentinel-agent
```

### Access Container Shell
```bash
docker-compose exec sentinel-agent bash
```

### Restart Specific Service
```bash
docker-compose restart sentinel-agent
```

### Scale Multiple Instances
```bash
docker-compose -p instance1 up -d
docker-compose -p instance2 up -d
```

---

##  Security

### Enable HTTPS (Production)
```bash
# Place SSL certificates
mkdir certs
cp your.crt certs/sentinel.crt
cp your.key certs/sentinel.key

# Use production compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Credentials
- Create `.env` with sensitive variables
- Never commit `.env` to git
- Use strong passwords for authentication
- Rotate credentials regularly

---

##  Docker Images

### View Images
```bash
docker images
```

### Remove Old Images
```bash
docker image prune -a
```

### Manual Build
```bash
docker build -t sentinel-agent:2.2 .
```

---

## 🆘 Getting Help

**Docker Compose Validation Errors?**
```bash
# Validate configuration
docker-compose config --quiet

# If you see "volumes.dashboard" or "depends_on.required" errors,
# see: DOCKER_TROUBLESHOOTING.md#0-docker-compose-validation-errors
```

**Check Logs First:**
```bash
docker-compose logs --tail=200 sentinel-agent > debug.log
```

**See Documentation:**
- Full guide: `docs_markdown/DOCKER_DEPLOYMENT.md`
- Troubleshooting: `docs_markdown/DOCKER_TROUBLESHOOTING.md`
- Installation: `INSTALLATION.md`
- Configuration: Review `docker-compose.yml` comments

**Manual Troubleshooting:**
```bash
# System info
docker version
docker-compose version

# Container inspection
docker inspect sentinel-agent

# Network diagnostics
docker network inspect sentinel-network
```

---

##  Startup Checklist

- [ ] Docker and Docker Compose installed
- [ ] Sufficient disk space (10GB+)
- [ ] Ports 8000, 8501 available
- [ ] Git and project cloned
- [ ] docker-compose.yml reviewed
- [ ] Environment variables set
- [ ] Data backup created (if updating existing installation)
- [ ] Services started and running
- [ ] API health check passing
- [ ] Logs showing no errors

---

##  Next Steps

1. **Configure**: Edit `docker-compose.yml` as needed
2. **Start**: Run `docker-compose up -d`
3. **Verify**: Test with `curl http://localhost:8000/api/health`
4. **Monitor**: Check logs with `docker-compose logs -f`
5. **Backup**: Create regular backups of `data/` folder

---

**Latest Version**: Sentinel Agent v2.2  
**Docker Version**: 3.9 compose format (Docker 20.10+)  
**For detailed guide**: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
