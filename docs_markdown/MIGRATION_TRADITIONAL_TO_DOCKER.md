# Migration Guide: Traditional Setup → Docker

Guide for migrating from traditional Python virtual environment setup to Docker containerized setup.

---

##  Overview

| Aspect | Traditional | Docker |
|--------|-----------|--------|
| **Setup Time** | 6+ minutes | 30 seconds |
| **Dependencies** | Manual Python, Ollama, venv | All in container |
| **Persistence** | Local directories | Named volumes |
| **Scaling** | Single instance | Multiple instances |
| **Isolation** | System-wide dependencies | Containerized |
| **Backup/Restore** | Filesystem sync | Volume snapshots |
| **Production** | Manual HTTPS setup | Nginx automated |

---

##  Quick Migration (5 Minutes)

### Step 1: Backup Existing Data
```bash
# Current traditional setup
cp -r data/ data_backup/
cp -r logs/ logs_backup/

# Or create tar archive
tar czf traditional-backup-$(date +%Y%m%d).tar.gz data/ logs/
```

### Step 2: Keep Traditional Installation (Optional)
```bash
# Traditional setup can stay alongside Docker
# No conflicts - Docker uses container environment
```

### Step 3: Start Docker Version
```bash
# Using Docker Ollama
docker-compose --profile with-ollama up -d

# Or using host Ollama (if running)
docker-compose up -d
```

### Step 4: Migrate Data (If Needed)
```bash
# Copy data from traditional to Docker volume
docker cp data_backup/ sentinel-agent:/app/data/

# Or restore from backup
tar xzf traditional-backup-*.tar.gz
docker-compose restart
```

### Step 5: Verify Docker Version Works
```bash
# Check status
docker-compose ps

# Test API
curl http://localhost:8000/api/health

# Check logs
docker-compose logs -f sentinel-agent
```

### Done! 

---

##  Data Migration Strategies

### Strategy 1: Fresh Start (Recommended for Development)

**When to use:** 
- Development environment
- Testing new features
- No critical data to preserve

**Steps:**
```bash
# Stop traditional version
pkill -f "python main.py"

# Start Docker version fresh
docker-compose --profile with-ollama up -d

# Let it initialize new databases
sleep 5

# Verify
docker-compose ps
curl http://localhost:8000/api/health
```

**Advantages:**
- Clean start
- No data conflicts
- Fresh performance

---

### Strategy 2: Import Existing Data (Recommended for Production)

**When to use:**
- Production migration
- Data continuity required
- Preserve attack records

**Steps:**

```bash
# 1. Stop traditional version
pkill -f "python main.py"
pkill -f "python sentinel_api.py"

# 2. Backup existing data
tar czf backup-before-docker.tar.gz data/ logs/

# 3. Start Docker version (will create new volumes)
docker-compose up -d

# 4. Copy data into Docker volumes
docker cp data/. sentinel-agent:/app/data/
docker cp logs/. sentinel-agent:/app/logs/

# 5. Restart Docker to reload data
docker-compose restart

# 6. Verify
docker-compose ps
curl http://localhost:8000/api/health
docker-compose logs sentinel-agent
```

---

### Strategy 3: Parallel Run (Safest)

**When to use:**
- Critical systems
- Validation needed
- Gradual transition

**Steps:**

```bash
# 1. Change Docker API port (so no conflict)
# Edit docker-compose.yml:
ports:
  - "8001:8000"  # Use 8001 instead of 8000

# 2. Start Docker version alongside traditional
docker-compose up -d

# 3. Test Docker version
curl http://localhost:8001/api/health

# 4. Run both for comparison period
# Traditional on :8000
# Docker on :8001

# 5. Once verified, migrate completely
# Stop traditional
pkill -f "python main.py"

# 6. Change Docker back to standard port
# Edit docker-compose.yml:
ports:
  - "8000:8000"

# 7. Restart Docker
docker-compose restart

# 8. Verify
curl http://localhost:8000/api/health
```

---

## ️ Database Migration

### Automatic Migration
Docker automatically handles database initialization. If migration is needed:

```bash
# Check databases in traditional setup
ls -la data/*.db

# Copy to Docker container
for db in data/*.db; do
  docker cp "$db" sentinel-agent:/app/data/
done

# Restart to ensure data is loaded
docker-compose restart

# Verify
docker-compose exec sentinel-agent sqlite3 /app/data/sentinel_intel.db ".tables"
```

### Manual Database Transfer

**Option 1: SQL Export/Import**
```bash
# Export from traditional
sqlite3 data/sentinel_intel.db ".dump" > dump.sql

# Import into Docker
docker-compose exec -T sentinel-agent sqlite3 /app/data/sentinel_intel.db < dump.sql

# Verify
docker-compose exec sentinel-agent sqlite3 /app/data/sentinel_intel.db ".tables"
```

**Option 2: Direct File Copy**
```bash
# Stop both versions
docker-compose down
pkill -f "python main.py"

# Copy database files
docker cp data/sentinel_intel.db sentinel-agent:/app/data/
docker cp data/threat_intel.db sentinel-agent:/app/data/
docker cp data/auth.db sentinel-agent:/app/data/
docker cp data/lists.db sentinel-agent:/app/data/
docker cp data/metrics.db sentinel-agent:/app/data/
docker cp data/anomalies.db sentinel-agent:/app/data/

# Repair/optimize databases
docker-compose exec sentinel-agent sqlite3 /app/data/sentinel_intel.db "PRAGMA integrity_check;"

# Start Docker
docker-compose up -d
```

---

##  Dual-Run Configuration

Try Docker without stopping traditional setup:

### Setup Side-by-Side

**1. Create separate compose project:**
```bash
# Create docker config for different port
cat > docker-compose.dev.yml << 'EOF'
version: '3.9'

services:
  sentinel-agent:
    ports:
      - "8001:8000"  # Different port
    environment:
      API_PORT: 8000

  ollama:
    ports:
      - "11435:11434"  # Different port
EOF
```

**2. Run both versions:**
```bash
# Terminal 1: Traditional version (if still running)
cd sentinel-agent-traditional
python main.py
python sentinel_api.py  # Runs on :8000

# Terminal 2: Docker version
docker-compose -f docker-compose.dev.yml up -d
# Runs on :8001
```

**3. Test both:**
```bash
# Traditional
curl http://localhost:8000/api/health

# Docker
curl http://localhost:8001/api/health
```

**4. Compare behavior:**
- Same system, different implementations
- Validate Docker matches traditional
- Ensure data consistency
- Check performance

**5. Switch when ready:**
```bash
# Stop traditional
pkill -f "python main.py"

# Update Docker port, restart
docker-compose down
# Edit to use :8000
docker-compose up -d
```

---

##  Validation Checklist

After migration, verify everything works:

### Data Verification
```bash
# Check data files exist
docker-compose exec sentinel-agent ls -la /app/data/

# Check database integrity
docker-compose exec sentinel-agent \
  sqlite3 /app/data/sentinel_intel.db "PRAGMA integrity_check;"

# Check log files
docker-compose exec sentinel-agent ls -la /app/logs/

# Verify count matches
du -sh data/
docker-compose exec sentinel-agent du -sh /app/data/
```

### API Verification
```bash
# Health check
curl http://localhost:8000/api/health

# Get threats (verify data loaded)
curl http://localhost:8000/api/threats

# Check metrics (verify tracking)
curl http://localhost:8000/api/metrics

# Test authentication (if enabled)
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/threats
```

### Performance Verification
```bash
# Monitor resource usage
docker stats sentinel-agent

# Check response times
time curl http://localhost:8000/api/health

# Load test (if applicable)
ab -n 100 -c 10 http://localhost:8000/api/health
```

### Log Verification
```bash
# Check application logs
docker-compose logs -f sentinel-agent

# Look for errors
docker-compose logs sentinel-agent | grep -i "error\|warning"

# Check full startup output
docker-compose logs sentinel-agent | head -50
```

---

##  Rollback Plan

If Docker migration has issues:

### Rollback to Traditional

```bash
# Stop Docker
docker-compose down

# Restore data from backup
tar xzf traditional-backup-*.tar.gz

# Restart traditional setup
source activate_env.sh
python main.py

# Verify
curl http://localhost:8000/api/health
```

### Rollback from Docker Data

If Docker data was modified:

```bash
# Export data before modification
docker-compose exec sentinel-agent \
  tar czf - /app/data > docker_data_export.tar.gz

# Stop Docker
docker-compose down

# If needed, restore Docker volumes
docker-compose up -d

# Restore data
tar xzf docker_data_export.tar.gz
docker cp ... sentinel-agent:/app/data/

# Restart
docker-compose restart
```

---

##  Migration Checklist

- [ ] **Backup** - Create backup of traditional setup data
- [ ] **Plan** - Decide on migration strategy (fresh/import/parallel)
- [ ] **Review** - Check Docker configs in docker-compose.yml
- [ ] **Test** - Run docker-test.sh to validate Docker setup
- [ ] **Start** - Launch Docker containers
- [ ] **Migrate** - Copy data if needed (strategy 2) or validate fresh (strategy 1)
- [ ] **Verify** - Run validation checklist
- [ ] **Monitor** - Watch logs for 5-10 minutes
- [ ] **Validate** - Run API tests, check data
- [ ] **Clean** - Stop traditional version if satisfied
- [ ] **Document** - Note any configuration changes

---

## ❓ Common Migration Questions

### Q: Can I run both versions simultaneously?

**A:** Yes! See "Dual-Run Configuration" section.
- Use different ports
- Different Docker projects (`-p` flag)
- Validate before switching

---

### Q: Will I lose any data?

**A:** Only if you explicitly delete it. 
- Always backup first: `tar czf backup.tar.gz data/ logs/`
- Docker volumes persist data
- Easy to restore from backup

---

### Q: How do I know Docker is using my data?

**A:** Check the data inside Docker:
```bash
docker-compose exec sentinel-agent ls -la /app/data/
docker-compose exec sentinel-agent du -sh /app/data/
```

---

### Q: What about environment variables?

**A:** Docker uses environment variables from:
1. docker-compose.yml (highest priority)
2. .env file (if exists)
3. System environment (lowest priority)

Create .env file:
```env
LOG_LEVEL=DEBUG
OLLAMA_MODEL=mistral:7b
```

---

### Q: Can I migrate back to traditional setup?

**A:** Yes, it's a Docker rollback:
1. Export data: `docker cp sentinel-agent:/app/data .`
2. Stop Docker: `docker-compose down`
3. Use exported data with traditional setup

---

### Q: What about logs?

**A:** Docker logs are in two places:
1. Container logs: `docker-compose logs`
2. Volume logs: `/app/logs/` (mounted from host)

Access both:
```bash
# Container logs (stdout/stderr)
docker-compose logs -f sentinel-agent

# Volume logs (persistent)
cat logs/sentinel.log
ls -la logs/
```

---

##  Performance Comparison

After migration, you might notice:

### Typical Performance Changes
- **Startup:** 2-3x faster (no venv activation)
- **Memory:** ±10% (depends on configuration)
- **CPU:** Slightly lower in idle state
- **Disk I/O:** Same (shared volume mount)
- **Network:** Improved (internal bridge network)

### If Everything is Slower
```bash
# Check resources
docker stats sentinel-agent

# Increase limits in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'      # Increase
      memory: 8G     # Increase
```

---

##  Related Documentation

- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - 5-minute guide
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Full deployment guide
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) - Problem solving
- [DOCKER_PROFILES_ADVANCED.md](DOCKER_PROFILES_ADVANCED.md) - Advanced configs

---

## ✅ Final Verification

Once migrated, confirm with these commands:

```bash
# Everything running?
docker-compose ps

# API responsive?
curl http://localhost:8000/api/health

# Data present?
docker-compose exec sentinel-agent ls /app/data/

# No errors?
docker-compose logs --tail=20 sentinel-agent

# Dashboard working?
open http://localhost:8501
```

---

**Migration Complete!** 

You've successfully transitioned from traditional setup to Docker. For next steps, see [DOCKER_INDEX.md](DOCKER_INDEX.md) for navigation.

---

**Last Updated:** 2024  
**Version:** Sentinel Agent v2.2
