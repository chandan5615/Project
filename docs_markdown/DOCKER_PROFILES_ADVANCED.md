# Docker Profiles & Advanced Configuration

Advanced Docker deployment patterns for Sentinel Agent v2.2

---

## Profiles

Profiles allow you to selectively enable services. Use `--profile` flag:

### Basic Profiles

#### Profile: `with-ollama`
Includes Docker-based Ollama service. Use this for:
- **Development** - Self-contained, no host dependencies
- **Testing** - Isolated environment
- **Learning** - Everything in Docker

```bash
docker-compose --profile with-ollama up -d
```

**What It Includes:**
- Ollama container (LLM engine)
- ollama-pull service (auto-downloads model)
- Sentinel Agent
- Shared network for communication

**Disk Space:** ~4GB for llama3:8b model  
**Start Time:** 5-10 minutes on first run  
**Performance:** Good for development, slower than host Ollama for production

---

#### Profile: `default` (No Profile)
Uses external/host Ollama. Use this for:
- **Production** - Maximum performance
- **Shared Ollama** - Multiple projects using same Ollama
- **Minimal footprint** - Only sentinel-agent runs in Docker

```bash
# Make sure Ollama is running on host first
ollama pull llama3:8b
ollama serve

# In another terminal
docker-compose up -d
```

**What It Includes:**
- Sentinel Agent container
- Connects to host Ollama on port 11434
- No Ollama container

**Start Time:** 2-3 minutes  
**Performance:** Fastest, best for production

---

## Deployment Patterns

### Pattern 1: Quick Development

```bash
# Complete setup in one command
docker-compose --profile with-ollama up -d
```

**Best for:**
- Getting started quickly
- Testing new features
- Development environment

**Files Used:**
```
docker-compose.yml (with-ollama profile enabled)
```

---

### Pattern 2: Production with Host Ollama

**Setup:**

Terminal 1:
```bash
# Install Ollama (one-time)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama (keep running)
ollama pull llama3:8b
ollama serve
```

Terminal 2:
```bash
cd sentinel-agent
docker-compose up -d
```

**Best for:**
- Production servers
- Shared Ollama across projects
- Maximum performance
- Dedicated hardware for Ollama

**Files Used:**
```
docker-compose.yml (default profile)
```

---

### Pattern 3: Production with Nginx & SSL

```bash
# Prerequisites: SSL certificates
mkdir certs
cp /path/to/your.crt certs/sentinel.crt
cp /path/to/your.key certs/sentinel.key

# Deploy with production config
docker-compose -f docker-compose.yml \
                -f docker-compose.prod.yml up -d
```

**What's Included:**
- Nginx reverse proxy (SSL/TLS)
- Resource limits (2 CPU, 4GB RAM)
- Advanced logging
- Monitoring support (Prometheus optional)
- Automated backups (optional)

**Files Used:**
```
docker-compose.yml
docker-compose.prod.yml
nginx.conf
docker-entrypoint.sh
```

---

### Pattern 4: Multi-Instance Load Balancing

Run multiple Sentinel Agent instances:

```bash
# Create compose project names
docker-compose -p sentinel-1 up -d
docker-compose -p sentinel-2 up -d
docker-compose -p sentinel-3 up -d
```

**API Endpoints:**
- Instance 1: `http://localhost:8000/api/health`
- Instance 2: `http://localhost:8001/api/health` (change port in .env)
- Instance 3: `http://localhost:8002/api/health`

**Benefits:**
- High availability
- Load distribution
- Fault tolerance

---

### Pattern 5: Microservices Architecture

Uncomment optional services in docker-compose.yml:

```yaml
# In docker-compose.yml, uncomment:
services:
  sentinel-api:      # Separate API service
  sentinel-dashboard: # Separate dashboard service
```

**Benefits:**
- Independent scaling per service
- Separate monitoring
- Easier debugging
- Resource isolation

---

## Environment Configuration

### Basic Configuration (`.env`)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3:8b

# Logging
LOG_LEVEL=INFO
SENTINEL_LOG_DIR=/app/logs
SENTINEL_DATA_DIR=/app/data

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8501

# Security
DISABLE_AUTH=false
SESSION_TIMEOUT=3600
```

### Production Configuration (`.env.prod`)

```env
# Production Ollama
OLLAMA_BASE_URL=http://ollama-server.internal:11434
OLLAMA_MODEL=llama3:8b

# Logging - Production Settings
LOG_LEVEL=WARNING
SENTINEL_LOG_DIR=/app/logs
SENTINEL_DATA_DIR=/app/data

# API - Production
API_HOST=127.0.0.1
API_PORT=8000
DASHBOARD_PORT=8501

# Security - Strict
DISABLE_AUTH=false
SESSION_TIMEOUT=1800  # 30 minutes
MAX_LOGIN_ATTEMPTS=3
REQUIRE_HTTPS=true

# Performance
WORKER_THREADS=4
MAX_CONNECTIONS=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

**Usage:**
```bash
docker-compose --env-file .env.prod up -d
```

---

## Advanced Docker Compose

### Custom Network Configuration

```yaml
version: '3.9'

services:
  sentinel-agent:
    networks:
      - sentinel-net
    environment:
      OLLAMA_BASE_URL: http://ollama:11434

  ollama:
    networks:
      - sentinel-net

networks:
  sentinel-net:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br_sentinel
      com.docker.driver.mtu: 1500
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Volume Management

```yaml
services:
  sentinel-agent:
    volumes:
      # Persistent data
      - sentinel-data:/app/data:rw
      - sentinel-logs:/app/logs:rw
      
      # Read-only system access
      - /proc:/proc:ro
      - /sys:/sys:ro
      - /var/log:/var/log:ro
      
      # Custom mounts
      - ./config:/app/config:ro
      - ./scripts:/app/scripts:ro

volumes:
  sentinel-data:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
  
  sentinel-logs:
    driver: local
```

### Resource Management

```yaml
services:
  sentinel-agent:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
          memswap: 10G  # Including swap
        reservations:
          cpus: '2'
          memory: 4G
      
      # Restart policy
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5
        window: 120s
```

### Logging Configuration

```yaml
services:
  sentinel-agent:
    logging:
      driver: json-file
      options:
        max-size: 100m        # 100MB per file
        max-file: 10          # Keep 10 files
        labels: "sentinel=true"
        env: "LOG_LEVEL,OLLAMA_MODEL"
```

---

## Scaling Configurations

### Small Scale (Development)

```yaml
sentinel-agent:
  environment:
    WORKER_THREADS: 2
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 2G
```

### Medium Scale (Single Server Production)

```yaml
sentinel-agent:
  environment:
    WORKER_THREADS: 4
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
```

### Large Scale (Cluster/Multi-Server)

```yaml
# Run multiple instances
# Use docker stack deploy instead of docker-compose

# Terminal 1:
docker swarm init
docker stack deploy -c docker-compose.prod.yml sentinel

# Terminal 2:
docker stack services sentinel
docker service update --replicas 3 sentinel_sentinel-agent
```

---

## Monitoring & Observability

### Built-in Health Checks

```yaml
services:
  sentinel-agent:
    healthcheck:
      test: ["CMD", "curl", "-f", "-s", "http://127.0.0.1:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Prometheus Integration (Optional)

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    depends_on:
      - sentinel-agent

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:
```

---

## Security Configurations

### Network Isolation

```yaml
services:
  sentinel-agent:
    networks:
      - sentinel-secure
    ports:
      - "8000:8000"  # API
    labels:
      - "firewall=enabled"

  ollama:
    networks:
      - sentinel-secure
    expose:          # No ports exposed, internal only
      - 11434

networks:
  sentinel-secure:
    driver: bridge
    driver_opts:
      # Disable inter-container ping
      --icc: "false"
```

### User & Permission Management

```yaml
services:
  sentinel-agent:
    user: "1000:1000"  # Run as non-root
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_ADMIN      # Only what's needed
```

### Environment Secrets

```bash
# Create Docker secret (Swarm mode)
echo "mysecretpassword" | docker secret create db_password -

# Use in compose
services:
  sentinel-agent:
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    external: true
```

---

## Backup & Recovery

### Automated Backup Service

```yaml
services:
  backup:
    image: alpine:latest
    volumes:
      - sentinel-data:/data:ro
      - ./backups:/output
    entrypoint: |
      sh -c 'while true; do
        tar czf /output/backup-$(date +%s).tar.gz /data
        find /output -name "backup-*.tar.gz" -mtime +7 -delete
        sleep 86400
      done'
    restart: always
```

### Restore from Backup

```bash
# Find backup
ls -lR backups/

# Stop services
docker-compose down

# Extract backup
tar xzf backups/backup-1234567890.tar.gz

# Verify files
ls data/

# Start services
docker-compose up -d
```

---

## Performance Tuning

### Limits & Reservations

```yaml
services:
  sentinel-agent:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2.5'
          memory: 5G
```

### Memory Optimization

```yaml
# Reduce Ollama model size
environment:
  OLLAMA_MODEL: mistral:7b  # 5GB instead of 13GB

# Optimize Python
environment:
  PYTHONHASHSEED: random
```

### I/O Optimization

```yaml
volumes:
  sentinel-data:
    driver: local
    driver_opts:
      type: btrfs    # Better for Docker
```

---

## Troubleshooting Advanced Setup

### Check Compose Configuration

```bash
# Validate syntax
docker-compose config

# Show processed config
docker-compose config > actual-config.yml

# Check specific service
docker-compose config --services
```

### Network Debugging

```bash
# Check network
docker network ls
docker network inspect sentinel-network

# Test connectivity
docker-compose exec sentinel-agent \
  nslookup ollama

# View network traffic
docker-compose exec sentinel-agent \
  tcpdump -i eth0 -n
```

### Volume Debugging

```bash
# List volumes
docker volume ls
docker volume inspect sentinel_sentinel-data

# Check mount points
docker-compose exec sentinel-agent mount | grep data
```

---

## Best Practices

1. **Always Use Named Volumes**
   ```yaml
   volumes:
     sentinel-data:
       driver: local
   ```

2. **Set Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4'
         memory: 8G
   ```

3. **Enable Health Checks**
   ```yaml
   healthcheck:
     test: [...]
     interval: 30s
   ```

4. **Use Environment Files**
   ```bash
   docker-compose --env-file .env.prod up -d
   ```

5. **Keep Logs Manageable**
   ```yaml
   logging:
     options:
       max-size: 100m
       max-file: 10
   ```

6. **Version Your Images**
   ```bash
   docker build -t sentinel-agent:2.2.1 .
   ```

7. **Document Changes**
   ```bash
   # Before updating
   git add docker-compose.yml
   git commit -m "Updated resource limits"
   ```

---

**Last Updated**: 2024  
**Version**: Sentinel Agent v2.2  
**Compatibility**: Docker 20.10+, Docker Compose 1.29+
