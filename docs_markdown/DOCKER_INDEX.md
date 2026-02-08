# Docker Documentation Index - Sentinel Agent v2.2

Complete navigation guide for Docker-related documentation and tools.

---

##  Documentation Files

### Quick Start Guides

| File | Purpose | Time | For |
|------|---------|------|-----|
| [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) | **5-minute quick start** | 5 min | Everyone starting out |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | **Comprehensive deployment guide** | 30 min | In-depth understanding |

### Advanced Topics

| File | Purpose | For |
|------|---------|-----|
| [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) | Solutions to 14+ common Docker issues | Debugging & problem-solving |
| [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) | Scaling, monitoring, security configs | Advanced deployments |

---

##  Tools & Scripts

### System Preparation

| File | Purpose | Platform |
|------|---------|----------|
| `docker-test.sh` | Docker installation & health checks | Linux/macOS |
| `docker-test.bat` | Docker installation & health checks | Windows |

**Usage:**
```bash
# Linux/macOS
chmod +x docker-test.sh
./docker-test.sh

# Windows
docker-test.bat
```

---

##  Core Docker Files

| File | Purpose | For |
|------|---------|-----|
| `Dockerfile` | Container image definition | Building the application |
| `docker-compose.yml` | Service orchestration | Starting services |
| `docker-compose.prod.yml` | Production configuration | Production deployments |
| `docker-entrypoint.sh` | Container startup script | Service initialization |
| `nginx.conf` | Reverse proxy configuration | SSL/TLS & load balancing |
| `.dockerignore` | Build optimization | Reducing image size |

---

##  Quick Reference

### Installation Methods

```bash
# ⭐ RECOMMENDED: Host Ollama (Production - Best Performance)
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Deploy Sentinel Agent
git clone <repo> && cd sentinel-agent
docker-compose up -d  # Starts in 10 seconds!

# Alternative: Docker Ollama (Containerized everything)
# Uncomment ollama and ollama-pull services in docker-compose.yml
docker-compose --profile with-ollama up -d

# Production with SSL/TLS
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Essential Commands

```bash
# Service Management
docker-compose up -d              # Start with host Ollama
docker-compose down               # Stop services
docker-compose ps                 # View status
docker-compose logs -f            # Follow logs

# Verify Setup
curl http://localhost:8000/api/health    # API health check
curl http://localhost:11434/api/tags     # Ollama health check

# Debugging
docker-compose exec sentinel-agent bash
docker stats
docker-compose config --quiet     # Validate YAML

# Advanced
docker-compose build --no-cache
docker-compose -p instance1 up -d
docker system prune -a
```

### Troubleshooting

```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 sentinel-agent

# Test API
curl http://localhost:8000/api/health

# Access container
docker-compose exec sentinel-agent bash

# Reset everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

##  Reading Guide by Role

### For Developers

**Order:**
1. [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Get started immediately
2. [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Advanced patterns
3. Modify `docker-compose.yml` for your needs

**Key Commands:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose exec sentinel-agent bash
```

---

### For DevOps / Operators

**Order:**
1. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Complete deployment guide
2. [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Profiles & scaling
3. [DOCKER_TROUBLESHOOTING.md](#docker_troubleshooting.md) - Problem resolution

**Key Files:**
- `docker-compose.prod.yml` - Production configuration
- `nginx.conf` - Reverse proxy setup
- `docker-test.sh` - Health checks

---

### For New Users

**Order:**
1. [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Start here
2. Run `./docker-test.sh` - Verify Docker setup
3. `docker-compose --profile with-ollama up -d` - Deploy

**Key Concepts:**
- Profiles control which services run
- `docker-compose.yml` defines the application
- Ports map internal→external (8000:8000)
- Volumes persist data (./data/)

---

### For System Administrators

**Order:**
1. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Installation & setup
2. [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Monitoring & security
3. [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Maintenance

**Key Responsibilities:**
- Set up Docker on system servers
- Configure SSL certificates (in `certs/`)
- Monitor resource usage (`docker stats`)
- Manage backups (`./data/`, `./logs/`)
- Handle updates (`git pull` + rebuild)

---

##  Common Tasks

### Task: Deploy in 30 Seconds
→ See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Quick Start section

### Task: Run in Production
→ See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Production Checklist

### Task: Something is Broken
→ See [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Find your symptom

### Task: Multiple Instances
→ See [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Scaling section

### Task: Custom Configuration
→ See [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Environment Configuration

### Task: SSL/HTTPS Setup
→ See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Production Deployment

---

## ❓ FAQ

### Q: Which deployment option should I use?

**For Development:**
```bash
docker-compose --profile with-ollama up -d
```
Simple, self-contained, everything in Docker.

**For Production:**
```bash
# Terminal 1: Host Ollama
ollama pull llama3:8b && ollama serve

# Terminal 2: Sentinel Agent
docker-compose up -d
```
Better performance, shared Ollama, production-ready.

**For Enterprise:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
SSL/TLS, reverse proxy, monitoring, backup automation.

---

### Q: What if something doesn't work?

1. **Check Status:** `docker-compose ps`
2. **View Logs:** `docker-compose logs -f sentinel-agent`
3. **Find Solution:** Search [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
4. **Reset:** `docker-compose down -v && docker-compose build --no-cache && docker-compose up -d`

---

### Q: How do I backup my data?

```bash
# Manual backup
tar czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Restore
tar xzf backup-20240101.tar.gz
docker-compose restart
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Data Persistence section.

---

### Q: Can I use a different LLM model?

Yes! Edit `docker-compose.yml`:

```yaml
environment:
  OLLAMA_MODEL: mistral:7b  # or any model Ollama supports
```

Then restart:
```bash
docker-compose restart
```

---

### Q: How do I access the API?

```bash
# Health check
curl http://localhost:8000/api/health

# Other endpoints
curl http://localhost:8000/api/threats
curl http://localhost:8000/api/attacks

# See API docs
open http://localhost:8000/docs
```

---

### Q: What if I need more resources?

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '8'        # More CPU
      memory: 16G      # More RAM
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

##  File Organization

```
sentinel-agent/
├── README.md                              # Main readme (mentions Docker)
├── INSTALLATION.md                        # Installation guide
│
├── Dockerfile                             # Container definition
├── docker-compose.yml                     # Service configuration
├── docker-compose.prod.yml                # Production version
├── docker-entrypoint.sh                   # Startup script
├── nginx.conf                             # Reverse proxy
├── .dockerignore                          # Build optimization
│
├── docker-test.sh                         # Health check (Linux/macOS)
├── docker-test.bat                        # Health check (Windows)
│
├── docs_markdown/
│   ├── DOCKER_QUICKSTART.md              # Quick start (5 min)
│   ├── DOCKER_DEPLOYMENT.md              # Full guide
│   ├── DOCKER_TROUBLESHOOTING.md         # Problem solving
│   ├── DOCKER_PROFILES_ADVANCED.md       # Advanced configs
│   └── DOCKER_INDEX.md                   # This file
│
└── data/                                  # Persistent storage
    ├── *.db                              # Databases
    └── attack_records.json
```

---

##  Next Steps

1. **Start Immediately:** Run `./docker-test.sh` then quick start command
2. **Learn Basics:** Read [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
3. **Go Deeper:** Study [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
4. **Handle Issues:** Reference [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
5. **Advanced Teams:** See [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md)

---

##  Support

- **Quick Issues:** See [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- **Setup Help:** See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Configuration:** See [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md)
- **General Help:** See [README.md](../README.md)

---

## ⏱️ Time Estimates

| Task | Time | Guide |
|------|------|-------|
| Initial setup | 5 min | [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) |
| Full deployment | 30 min | [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) |
| Troubleshooting | varies | [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) |
| Learning all | 2 hours | All guides |

---

##  Version Information

- **Sentinel Agent:** v2.2
- **Docker Compose:** v3.9 (compatible with Docker 20.10+)
- **Base Image:** python:3.10-slim
- **Last Updated:** 2024

---

**Happy Deploying! **
